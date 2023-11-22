from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# Create the users table if it doesn't exist
with sqlite3.connect('users.db') as connection:
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    connection.commit()

# Sample SQLite schema for properties and bookings
with sqlite3.connect('users.db') as connection:
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            image BLOB NOT NULL,
            thumbnail BLOB NOT Null
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            property_id INTEGER,
            check_in DATE NOT NULL,
            check_out DATE NOT NULL,
            guests INTEGER NOT NULL,
            FOREIGN KEY (property_id) REFERENCES properties (id)
        )
    ''')

# Define routes
@app.route('/')
def home():
    user_name = session.get('name', 'Guest')
    return render_template('index.html', user_name=user_name)

@app.route('/Login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
            user = cursor.fetchone()

        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return redirect('/')

        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route('/Signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            with sqlite3.connect('users.db') as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
                connection.commit()

            session['name'] = name
            session['email'] = email
            session['password'] = password

            return redirect('/Success')

        except sqlite3.IntegrityError:
            return render_template('signup.html', error='Email already exists. Please use a different email.')

    return render_template('signup.html')

@app.route('/Success')
def success():
    user_name = session.get('name', 'Guest')
    return render_template('success.html', user_name=user_name)

@app.route('/properties')
def properties():
    return render_template('properties.html')

@app.route('/list_property', methods=['GET', 'POST'])
def list_property():
    if request.method == 'POST':
        # Process the form data here (save to database, perform validation, etc.)
        property_name = request.form.get('property_name')
        property_description = request.form.get('property_description')

        # Save property image
        property_image = request.files['property_image']
        property_image_path = os.path.join('static/images/properties', property_image.filename)
        property_image.save(property_image_path)

        # Save thumbnail image
        thumbnail_image = request.files['thumbnail_image']
        thumbnail_image_path = os.path.join('static/images/thumbnails', thumbnail_image.filename)
        thumbnail_image.save(thumbnail_image_path)

        try:
            # Insert the property into the properties table
            with sqlite3.connect('your_database.db') as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO properties (name, description, image, thumbnail) VALUES (?, ?, ?, ?)",
                               (property_name, property_description, property_image_path, thumbnail_image_path))
                connection.commit()

            # Return a response to the client
            return jsonify({'status': 'success', 'message': 'Property listed successfully'})

        except Exception as e:
            # Handle exceptions (e.g., database errors)
            return jsonify({'status': 'error', 'message': str(e)})

    return render_template('list_property.html')


if __name__ == '__main__':
    app.run(debug=True)
