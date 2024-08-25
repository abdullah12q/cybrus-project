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
			password TEXT NOT NULL
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

def delete_user(connection,username):
    cursor = connection.cursor()
    query = 'DELETE FROM users WHERE username =?'
    cursor.execute(query, (username,))
    connection.commit()

def get_all_users(connection):
	cursor = connection.cursor()
	query = 'SELECT * FROM users'
	cursor.execute(query)
	return cursor.fetchall()


# --------------------------------- DATABASE FOR PRODUCTS ----------------------------------


def init_product(connection):
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
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















# def init_reviews(connection):
#     cursor = connection.cursor()

#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS reviews (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             user_id INTEGER NOT NULL,
#             restaurant_id INTEGER NOT NULL,
#             rating INTEGER NOT NULL,
#             review TEXT NOT NULL,
#             timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             FOREIGN KEY (user_id) REFERENCES users (id),
#             FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
#         )
#     ''')

#     connection.commit()

# def add_review(connection, user_id, restaurant_id, rating, review):
#     cursor = connection.cursor()
#     query = '''INSERT INTO reviews (user_id, restaurant_id, rating, review) VALUES (?, ?, ?, ?)'''
#     cursor.execute(query, (user_id, restaurant_id, rating, review))
#     connection.commit()

# def get_reviews_for_restaurant(connection, restaurant_id):
#     cursor = connection.cursor()
#     query = '''
#         SELECT  users.first_name, users.last_name, reviews.review, reviews.rating, reviews.timestamp
#         FROM reviews
#         JOIN users ON reviews.user_id = users.id
#         WHERE reviews.restaurant_id = ?
#     '''
#     cursor.execute(query, (restaurant_id,))
#     return cursor.fetchall()

# def search_restaurants(connection, searchkey):
#     cursor = connection.cursor()
#     query = '''
#         SELECT * FROM restaurants
#         WHERE title like '%' || (?) || '%' or description like '%' || (?) || '%'
#     '''
#     cursor.execute(query, (searchkey,searchkey))
#     return cursor.fetchall()