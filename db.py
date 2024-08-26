import utils

def connect_to_database(name='database.db'):
	import sqlite3
	return sqlite3.connect(name, check_same_thread=False)


# --------------------------------- DATABASE FOR USERS ----------------------------------


def init_db(connection):
	cursor = connection.cursor()

	cursor.execute('''
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
			username TEXT NOT NULL UNIQUE,
			password TEXT NOT NULL,
            photo_name TEXT
		)
	''')

	connection.commit()

def seed_admin_user(connection):
    admin_username = 'admin'
    admin_password = 'admin'

    # Check if admin user exists
    admin_user = get_user(connection, admin_username)
    if not admin_user:
        add_user(connection, '', '', admin_username, admin_password)
        print("Admin user seeded successfully.")

def add_user(connection,first_name,last_name,username,password):
    cursor = connection.cursor()
    hashed_password = utils.hash_password(password)
    query = '''INSERT INTO users (first_name,last_name,username,password) VALUES (?,?,?,?)'''
    cursor.execute(query, (first_name,last_name,username, hashed_password))
    connection.commit()

def get_user(connection,username):
    cursor = connection.cursor()
    query = '''SELECT * FROM users WHERE username =?'''
    cursor.execute(query, (username,))
    return cursor.fetchone()

def delete_user(connection,user_id):
    cursor = connection.cursor()
    query = 'DELETE FROM users WHERE id = (?) '
    cursor.execute(query, (user_id,))
    connection.commit()

def get_all_users(connection):
	cursor = connection.cursor()
	query = 'SELECT * FROM users'
	cursor.execute(query)
	return cursor.fetchall()

def update_user(connection , user_data):
    cursor = connection.cursor()
    query = ''' UPDATE users set first_name = ? , last_name = ? WHERE username = ? '''
    cursor.execute(query,(user_data['first_name'] , user_data['last_name'] , user_data['username']))
    connection.commit() 


def update_photo(connection, filename , username):
    cursor = connection.cursor()  
    query = '''UPDATE users SET photo_name = ? WHERE username = ?'''
    cursor.execute(query, (filename,username))  
    connection.commit() 

# --------------------------------- DATABASE FOR PRODUCTS ----------------------------------

def init_product(connection):
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            image_url TEXT
        )
    ''')

    connection.commit()

def add_product(connection, name, price ,image_url=None):
    cursor = connection.cursor()
    query = '''INSERT INTO products ( name, price, image_url) VALUES (?, ?, ?)'''
    cursor.execute(query, ( name, price, image_url ))
    connection.commit()

def get_product(connection, product_id):
    cursor = connection.cursor()
    query = '''SELECT * FROM products WHERE id = ?'''
    cursor.execute(query, (product_id,))
    return cursor.fetchone()

def get_all_products(connection):
    cursor = connection.cursor()
    query = '''SELECT * FROM products'''
    cursor.execute(query)
    return cursor.fetchall()

def delete_product(connection, product_id):
    cursor = connection.cursor()
    query = '''
        DELETE FROM products
        WHERE id = (?)
    '''
    cursor.execute(query, (product_id,))
    connection.commit()

# --------------------------------- DATABASE FOR BUYING ----------------------------------

def init_cart(connection):
    cursor = connection.cursor()

    create_table_query = '''
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    '''

    cursor.execute(create_table_query)
    connection.commit()

def add_to_cart(connection, user_id, product_id, quantity=1):
    cursor = connection.cursor()

    insert_query = "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)" 
    cursor.execute(insert_query, (user_id, product_id, quantity))

    connection.commit()

def remove_from_cart(connection, user_id, product_id):
    cursor = connection.cursor()

    delete_query = "DELETE FROM cart WHERE user_id = ? AND product_id = ?"
    cursor.execute(delete_query, (user_id, product_id))

    connection.commit()

def get_cart(connection, user_id):
    cursor = connection.cursor()

    select_query = '''        
        SELECT  cart.product_id, products.name, products.price, products.image_url
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id = ?
    '''
    cursor.execute(select_query, (user_id,))
    cart_items = cursor.fetchall()

    return cart_items

def clear_cart(connection, user_id):
    cursor = connection.cursor()

    delete_query = "DELETE FROM cart WHERE user_id = ?"
    cursor.execute(delete_query, (user_id,))

    connection.commit()