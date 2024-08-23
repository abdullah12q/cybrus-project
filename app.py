from flask import Flask, render_template, request, redirect, url_for, session, flash
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

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']

    user = db.get_user(connection, username)
    
    if db.seed_admin_user(username, password):
      session["username"] = username
      return render_template("restaurant.html", restaurants=db.get_all_restaurants(connection) , username=session['username'])

    if user:
      if utils.is_password_match(password, user[4]):
        session['username'] = user[3]
        return redirect(url_for('index'))
      else:
        flash("Password dose not match", "danger")
        return render_template('login.html')

  else:
    flash("Invalid username", "danger")
    return render_template('login.html')

  return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def sign_up():
  if request.method == 'POST':
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    username = request.form['username']
    password = request.form['password']
    if not utils.is_strong_password(password):
      flash(
        "Sorry You Entered a weak Password Please Choose a stronger one", "danger"
      )
      return render_template('signup.html')

    user = db.get_user(connection, username)
    if user:
      flash(
        "Username already exists. Please choose a different username.", "danger"
      )
      return render_template('signup.html')
    
    else:
      db.add_user(connection, username, password , "images.png")
      return redirect(url_for('login'))

  return render_template('signup.html')

@app.route("/")
def index():
  return render_template("index.html")

if __name__ == "__main__":
  app.run(debug=True,port=8000)


