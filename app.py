from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

try:
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
except Exception as e:
    print(f"Error connecting to the database: {e}")

# Define routes
@app.route('/')
def home():
    # Get the user's name from the session
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
            # If the user exists, store user information in the session
            session['user_id'] = user[0]
            session['user_name'] = user[1]

            # Redirect to the index page with a welcome message
            return redirect('/')

        else:
            # If login fails, you can display an error message or redirect to the login page
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route('/Signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Process the form data here (save to database, perform validation, etc.)
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # Insert the user into the users table
            with sqlite3.connect('users.db') as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
                connection.commit()

            # Store the user's name in the session
            session['name'] = name
            session['email']= email
            session['password']= password

            # Redirect to the index page with the user's name as a parameter
            return redirect('/Success')

        except sqlite3.IntegrityError:
            # Handle the case where the email is not unique (already exists in the database)
            return render_template('signup.html', error='Email already exists. Please use a different email.')

    return render_template('signup.html')

@app.route('/Success')
def success():
    # Get the user's name from the session
    user_name = session.get('name', 'Guest')
    return render_template('success.html', user_name=user_name)

@app.route('/properties')
def properties():
    return render_template('properties.html')

if __name__ == '__main__':
    app.run(debug=True)