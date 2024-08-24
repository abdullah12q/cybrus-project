from flask import Flask, render_template, request, redirect, url_for, session, flash
from markupsafe import escape
import db
import utils
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import validators         
import os

app = Flask(__name__)
connection = db.connect_to_database()
app.secret_key = "d5afjsfgsatkd7aea7dfidfk6rdsj9od"
limiter = Limiter(
  app=app, key_func=get_remote_address,
default_limits=["50 per minute"], storage_uri="memory://"
)

@app.route("/")
def index():
  return render_template("index.html")

@app.route('/signup', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def sign_up():
  if request.method == 'POST':
    first_name = escape(request.form["first_name"])
    last_name = escape(request.form["last_name"])
    username = escape(request.form['username'])
    password = request.form['password']

    if not utils.is_strong_password(password):
      flash(
        "Sorry You Entered A Weak Password Please Choose A Stronger One", "danger"
      )
      return render_template('signup.html')

    user = db.get_user(connection, username)
    if user:
      flash(
        "Username Already Exists. Please Choose A Different Username.", "danger"
      )
      return render_template('signup.html')
    
    else:
      db.add_user(connection,first_name,last_name, username, password)
      return redirect(url_for('login'))

  return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']

    user = db.get_user(connection, username)
    
    if db.seed_admin_user(username, password):
      session["username"] = username
      return render_template("products.html", products=db.get_all_products(connection) , username=session['username'])

    if user:
      if utils.is_password_match(password, user[4]):
        session['username'] = user[3]
        return redirect(url_for('products'))
      else:
        flash("Password does not match", "danger")
        return render_template('login.html')

    else:
      flash("Invalid username", "danger")
      return render_template('login.html')

  return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def products():
  if ('username' in session) or (session['username'] =='admin'):
    if request.method == 'POST':
      return render_template('products.html', products = db.get_all_products(connection), username = session['username'])
  return redirect(url_for(login))

# @app.route('/addproduct', methods=['GET', 'POST'])
# def add_product():


# @app.route('/product/id=<product_id>')
# def get_product(product_id):


@app.route('/delete-product/id=<product_id>')
def delete_product(product_id):
  db.delete_product(connection, product_id)
  return redirect(url_for('products'))

@app.route("/logout")
def logout():
  session.pop("username", None)
  return redirect(url_for("login"))


if __name__ == "__main__":
  db.init_db(connection)
  db.init_product(connection)
  app.run(debug=True,port=8000)


#test comment