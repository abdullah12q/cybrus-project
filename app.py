from flask import Flask, render_template, request, redirect, url_for, session, flash
from markupsafe import escape
import db
import utils
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import validators         
import os
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
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
      db.add_user(connection,first_name,last_name, username, password,"images.png")
      return redirect(url_for('login'))

  return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']

    user = db.get_user(connection, username)

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

@app.route('/users')
def users():
  if session['username'] == 'admin':
    users = db.get_all_users(connection)
    if len(users) <= 1:
      flash("No users found", "info")
      return redirect(url_for('products'))
    return render_template('users.html', users=users)

@app.route('/delete-user/id=<user_id>')
def delete_user(user_id):
  if 'username' in session and session['username'] == 'admin':
    db.delete_user(connection, user_id)
    flash('User deleted successfully', 'success')
    return redirect(url_for('users'))
  else:
    flash('Unauthorized access', 'danger')
    return redirect(url_for('login'))

@app.route('/home')
def products():
  if 'username' in session:
    return render_template('products.html', products = db.get_all_products(connection), username = session['username'])
  return redirect(url_for('login'))

#-------------------------------------------------------Cart Routes-------------------------------------------------------
@app.route('/cart')
def cart():
  if 'username' in session:
    user = db.get_user(connection, session['username'])
    cart_products = db.get_cart(connection, user[0])
    
    subtotal = sum(product[2] for product in cart_products)
    return render_template('cart.html', cart_products = cart_products, subtotal=subtotal)
  
  return redirect(url_for('login'))

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
  if 'username' not in session:
    return redirect(url_for('login'))
  
  user = db.get_user(connection, session['username'])
  
  cart_products = db.get_cart(connection, user[0])
  cart_product_ids = [item[0] for item in cart_products]
  
  if product_id in cart_product_ids:
    flash('This product already exists in your cart', 'warning')
    return redirect(url_for('products'))

  else:
    db.add_to_cart(connection, user[0], product_id)
    flash('The product added to cart successfully', 'success')
    return redirect(url_for('products'))


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
  user = db.get_user(connection, session['username'])
  db.remove_from_cart(connection,user[0], product_id)
  
  if not session.pop('bought_product', False):
    flash('The product removed from cart successfully', 'success')
  return redirect(url_for('cart'))

@app.route('/buy_product/<int:product_id>', methods=['POST'])
def buy_product(product_id):
    if 'username' in session:
        flash(f'Purchase successful! You paid ${db.get_product(connection, product_id)[2]}!', 'success')
        
        session['bought_product'] = True
        
        return redirect(url_for('remove_from_cart', product_id=product_id))

    else:
        flash('You need to login to buy products.', 'danger')
        return redirect(url_for('login'))      

@app.route('/buy_cart/<int:total_price>')
def buy_cart(total_price):
  if 'username' in session:
    if total_price <= 45:
      flash("No items in your cart", 'danger')
      return redirect(url_for('cart'))
    else:
      username = session['username']
      user = db.get_user(connection, username)
      db.clear_cart(connection, user[0])
      flash(f'Check Out Successful! You Paid ${total_price}', 'success')
      return redirect(url_for('cart'))
  return redirect(url_for('login'))
#-------------------------------------------------------End Cart Routes-------------------------------------------------------



@app.route('/addProduct', methods=['GET', 'POST'])
def add_product():
  if not 'username' in session:
    flash("You Are Not Logged In", "danger")
    return redirect(url_for('login'))
  
  if session['username'] != 'admin':
    flash("Unauthorized User...", "danger")
    return redirect(url_for("products"))
  
  if request.method == "POST":
    
    image = request.files['product-image']
    if not image or image.filename == '':
      flash("No product image provided", "danger")
      return render_template("addProduct.html")
    
    if not (validators.allowed_file(image.filename)) or not (validators.allowed_file_size(image)):
      flash("Invalid file type or size", "danger")
      return render_template("addProduct.html")
    
    name = escape(request.form['product-name'])
    price = escape(request.form['product-price'])
    image_url = f"uploads/{image.filename}"
    image.save(os.path.join("static", image_url))

    db.add_product(connection, name, price, image_url)
    flash("Added product", "success")
    return redirect(url_for("products"))
  return render_template("addProduct.html")

@app.route('/delete-product/id=<product_id>')
def delete_product(product_id):
  if 'username' in session and session['username'] == 'admin':
    db.delete_product(connection, product_id)
    flash('Product deleted successfully', 'success')
    return redirect(url_for('products'))
  else:
    flash('Unauthorized access', 'danger')
    return redirect(url_for('login'))

@app.route('/account', methods=['GET', 'POST'])
def account():
  if 'username' in session:
    if request.method == 'GET':
      username = escape(request.args.get('username', session['username']))
      if username != session['username']:
        return "Unauthorized access"
      data = db.get_user(connection, username)
      if data:
        logging.debug(f"User data: {data}")  # or log the data to see its structure
        return render_template('account.html', data=data)
      else:
        return "user not found"
    elif request.method == 'POST':
      form_type = request.form.get('form_name')
      username = escape(request.args.get('username', session['username']))
      if username != session['username']:
        return 'unathoruzed'
      if form_type == 'upload_photo':
        photo = request.files.get('profile_picture')

        if photo:
          if not validators.allowed_file_size(photo):
            return f"Unallowed size."
          elif not validators.allowed_file(photo.filename):
            return f"Unallowed extention."
          else:
            db.update_photo(connection, photo.filename, username)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo.filename))# static/uploads/xyz.png

      elif form_type == 'update_user_data':
        user_data = { 
          "username": escape(request.form.get('username')), 
          "first_name": escape(request.form.get('first_name')),
          "last_name": escape(request.form.get('last_name'))
        }
        db.update_user(connection , user_data)

      data = db.get_user(connection, username)
      return render_template('account.html', data=data) 
  else:
    return redirect(url_for('login'))

@app.route("/logout")
def logout():
  session.pop("username", None)
  return redirect(url_for("login"))


if __name__ == "__main__":
  db.init_db(connection)
  db.init_product(connection)
  db.init_cart(connection)
  db.seed_admin_user(connection)
  app.run(debug=True,port=8000)