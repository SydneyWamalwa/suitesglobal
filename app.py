from flask import Flask, render_template, request, redirect, session,jsonify,url_for
from flask_mail import Mail, Message
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
import sqlite3
import os
import logging

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key'  # Change this to a secure secret key
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # or your mail server's port
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'sydneywamalwa@gmail.com'
app.config['MAIL_PASSWORD'] = 'yhww wxbu bksr tvee'
app.config['MAIL_DEFAULT_SENDER'] = 'sydneywamalwa@gmail.com'

bcrypt = Bcrypt(app)
mail = Mail(app)
try:
    # Create the users table if it doesn't exist
    with sqlite3.connect('users.db') as connection:
        cursor = connection.cursor()
        app.logger.debug('Executing SQL statements...')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Team (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                image BLOB NOT NULL,
                description TEXT NOT NULL,
                thumbnail BLOB NOT NULL,
                interiorimg1 BLOB NOT NULL,
                interiorimg2 BLOB NOT NULL,
                interiorimg3 BLOB NOT NULL,
                interiorimg4 BLOB NOT NULL,
                Price INTEGER NOT NULL,
                Amenities TEXT NOT NULL,
                admin_id INTEGER NOT NULL,
                property_type TEXT NOT NULL,
                FOREIGN KEY (admin_id) REFERENCES admins (id)
            )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            guest_name TEXT NOT NULL,
            property_id INTEGER,
            property_name TEXT NOT NULL,
            check_in DATE NOT NULL,
            check_out DATE NOT NULL,
            guests INTEGER NOT NULL,
            amount VARCHAR NOT NULL,
            user_id INTEGER NOT NULL,
            contacts TEXT NOT NULL,
            property_type TEXT NOT NULL,
            FOREIGN KEY (property_type) REFERENCES properties(property_type),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (property_id) REFERENCES properties (id)
        )
    ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS destinations (
            id INTEGER PRIMARY KEY,
            destination_name TEXT NOT NULL,
            destination_image BLOB NOT NULL,
            description TEXT NOT NULL,
            thumbnail BLOB NOT NULL,
            img1 BLOB NOT NULL,
            img2 BLOB NOT NULL,
            img3 BLOB NOT NULL,
            img4 BLOB NOT NULL,
            Price INTEGER NOT NULL,
            Amenities TEXT NOT NULL,
            admin_id INTEGER NOT NULL,
            Type TEXT NOT NULL,
            FOREIGN KEY (admin_id) REFERENCES admins (id)
        )
    ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS destination_bookings (
            id INTEGER PRIMARY KEY,
            destination_name TEXT NOT NULL,
            guest_name TEXT NOT NULL,
            destination_booking_id INTEGER NOT NULL,
            check_in DATE NOT NULL,
            check_out DATE NOT NULL,
            guests INTEGER NOT NULL,
            amount VARCHAR NOT NULL,
            user_id INTEGER NOT NULL,
            contacts TEXT NOT NULL,
            Type TEXT NOT NULL,
            FOREIGN KEY (Type) REFERENCES destinations (Type),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (destination_booking_id) REFERENCES destinations (id)
        )
    ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   email TEXT NOT NULL,
                   message TEXT NOT NULL,
                   user_id INTEGER NOT NULL,
                   FOREIGN KEY (user_id) REFERENCES users(id)
               )''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            reply_text TEXT NOT NULL,
            team_id INTEGER NOT NULL,
            status INTEGER DEFAULT 0, -- 0 for pending, 1 for replied
            FOREIGN KEY (message_id) REFERENCES contacts(id),
            FOREIGN KEY (team_id) REFERENCES Team(id)
        )
    ''')


        app.logger.debug('Committing changes to the database...')
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
        next_url = request.args.get('next', '/')  # Get the 'next' parameter from the URL, default to '/'

        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email=?", (email,))
            user = cursor.fetchone()

        if user and check_password_hash(user[3], password):
            # If the user exists, store user information in the session
            session['user_id'] = user[0]
            session['user_name'] = user[1]

            # Redirect to the original requested page or the home page
            return redirect(next_url)

        else:
            # If login fails, you can display an error message or redirect to the login page
            return render_template('Login.html', error='Invalid credentials', next=next_url)

    return render_template('Login.html')

@app.route('/SignupTeam', methods=['GET', 'POST'])
def signupteam():
    if request.method == 'POST':
        # Process the form data here (save to database, perform validation, etc.)
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # Hash the password before storing it in the database
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Insert the user into the users table
            with sqlite3.connect('users.db') as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO Team (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
                connection.commit()

            # Store the user's name in the session
            session['name'] = name
            session['email'] = email

            # Redirect to the index page with the user's name as a parameter
            return redirect('/Teamdashboard')

        except sqlite3.IntegrityError:
            # Handle the case where the email is not unique (already exists in the database)
            return render_template('SignupTeam.html', error='Email already exists. Please use a different email.')

    return render_template('SignupTeam.html')

@app.route('/LoginTeam', methods=['GET', 'POST'])
def loginteam():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Team WHERE email=?", (email,))
            user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user[3], password):
            # If the user exists and the password is correct, store user information in the session
            session['user_id'] = user[0]
            session['user_name'] = user[1]

            # Pass the admin_name to the template
            return render_template('Teamdashboard.html', admin_name=user[1])

        else:
            # If login fails, you can display an error message or redirect to the login page
            return render_template('TeamLogin.html', error='Invalid credentials')

    return render_template('TeamLogin.html')


@app.route('/Signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Process the form data here (save to database, perform validation, etc.)
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # Hash the password before storing it in the database
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Insert the user into the users table
            with sqlite3.connect('users.db') as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
                connection.commit()

            # Store the user's name in the session
            session['name'] = name
            session['email'] = email

            # Redirect to the index page with the user's name as a parameter
            return redirect('/Success')

        except sqlite3.IntegrityError:
            # Handle the case where the email is not unique (already exists in the database)
            return render_template('signup.html', error='Email already exists. Please use a different email.')

    return render_template('Signup.html')

@app.route('/Success')
def success():
    # Get the user's name from the session
    user_name = session.get('name', 'Guest')
    return render_template('Success.html', user_name=user_name)


@app.route('/properties')
def properties():
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT name, thumbnail FROM properties")
            properties_data = cursor.fetchall()

        return render_template('properties.html', properties_data=properties_data)

    except Exception as e:
        print(f"Error fetching properties: {e}")
        properties_data = []
        return render_template('properties.html', properties_data=properties_data, error=str(e))

@app.route('/type/Apartment')
def apartment():
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT name, thumbnail FROM properties WHERE property_type = 'Apartment'")
            apartment_properties = cursor.fetchall()

        return render_template('properties.html', properties_data=apartment_properties)

    except Exception as e:
        print(f"Error fetching apartment properties: {e}")
        apartment_properties = []
        return render_template('properties.html', properties_data=apartment_properties, error=str(e))

@app.route('/type/Own Compound')
def OwnCompound():
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT name, thumbnail FROM properties WHERE property_type = 'Own Compound'")
            apartment_properties = cursor.fetchall()

        return render_template('properties.html', properties_data=apartment_properties)

    except Exception as e:
        print(f"Error fetching apartment properties: {e}")
        apartment_properties = []
        return render_template('properties.html', properties_data=apartment_properties, error=str(e))





@app.route('/list_property', methods=['GET', 'POST'])
def property_listing():
    if request.method == 'POST':
        property_name = request.form.get('property_name')
        property_description = request.form.get('property_description')
        Price = request.form.get('Price')
        amenities = request.form.getlist('amenities[]')
        property_type = request.form.get('property_type')
        admin_id = session['admin_id']  # Assuming you have admin_id stored in session

        # Check if the POST request has the file part
        if 'property_image' in request.files and 'thumbnail_image' in request.files:
            property_image = request.files['property_image']
            thumbnail_image = request.files['thumbnail_image']
            interior1 = request.files['Additional Image1']
            interior2 = request.files['Additional Image2']
            interior3 = request.files['Additional Image3']
            interior4 = request.files['Additional Image4']

            # Save the images to a folder within the 'static' directory
            property_image_path = os.path.join('static', 'uploads', property_image.filename)
            thumbnail_image_path = os.path.join('static', 'uploads', thumbnail_image.filename)
            ipath1 = os.path.join('static', 'uploads', interior1.filename)
            ipath2 = os.path.join('static', 'uploads', interior2.filename)
            ipath3 = os.path.join('static', 'uploads', interior3.filename)
            ipath4 = os.path.join('static', 'uploads', interior4.filename)

            # Replace backslashes with forward slashes
            property_image_path = property_image_path.replace('\\', '/')
            thumbnail_image_path = thumbnail_image_path.replace('\\', '/')
            ipath1 = ipath1.replace('\\', '/')
            ipath2 = ipath2.replace('\\', '/')
            ipath3 = ipath3.replace('\\', '/')
            ipath4 = ipath4.replace('\\', '/')

            # Save the file objects
            property_image.save(property_image_path)
            thumbnail_image.save(thumbnail_image_path)
            interior1.save(ipath1)
            interior2.save(ipath2)
            interior3.save(ipath3)
            interior4.save(ipath4)

        amenities_str = ', '.join(amenities)

        try:
            # Insert the property into the properties table
            with sqlite3.connect('users.db') as connection:
                cursor = connection.cursor()
                cursor.execute(
                                        "INSERT INTO properties (name, image, description, thumbnail,interiorimg1,interiorimg2,interiorimg3,interiorimg4,Price, Amenities, admin_id,property_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)",
                    (property_name, property_image_path, property_description, thumbnail_image_path, ipath1,
                      ipath2, ipath3, ipath4, Price, amenities_str, admin_id,property_type))
                connection.commit()

            # Redirect to a success page or do other necessary actions
            return render_template('property_listing_success.html', property_name=property_name)

        except Exception as e:
            # Handle exceptions (e.g., database errors)
            return render_template('property_listing.html', error=str(e))

    # If it's a GET request, simply render the property_listing.html template
    return render_template('property_listing.html')


@app.route('/booking/', defaults={'property_id': None})
@app.route('/booking/<int:property_id>')
def booking(property_id):
    if 'user_id' not in session:
        return redirect(url_for('login', next=request.url))
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()

            if property_id is None:
                # Fetch the first available property id if no ID is provided
                cursor.execute("SELECT id FROM properties ORDER BY RANDOM() LIMIT 1")
                property_id = cursor.fetchone()[0]

            # Fetch the property with the provided ID
            cursor.execute("SELECT * FROM properties WHERE id=?", (property_id,))
            property_data = cursor.fetchone()

        if property_data:
            # Property information found, pass it to the booking_details.html template
            return render_template('booking_details.html', property_data=property_data)
        else:
            # Property not found, you may want to handle this case
            return render_template('error.html', error='Property not found')

    except Exception as e:
        print(f"Error fetching property information: {e}")
        return render_template('error.html', error=str(e))

@app.route('/submit_booking', methods=['POST'])
def submit_booking():
    if 'user_id' not in session:
        return redirect(url_for('login', next=request.url))

    # Extract data from the request
    property_name = request.form.get('property_name')
    guest_name = request.form.get('guest_name')
    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')
    guests = request.form.get('guests')
    amount = request.form.get('amount')
    contacts = request.form.get('contacts')
    if not contacts:
        return jsonify({'status': 'error', 'message': 'Contacts is required'})

    amount = request.form.get('amount')

    try:
        # Connect to the database
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            # Get the user_id from the session
            user_id = session['user_id']
            # Get the property ID based on the property name
            cursor.execute("SELECT id FROM properties WHERE name=?", (property_name,))
            property_id = cursor.fetchone()


            if property_id:
                # Insert booking information into the bookings table
                cursor.execute("""
                    INSERT INTO bookings (property_id, property_name, check_in, check_out, guests, guest_name, amount, user_id, contacts, property_type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, (SELECT property_type FROM properties WHERE id = ?))
""", (property_id[0], property_name, check_in, check_out, guests, guest_name, amount, user_id, contacts, property_id[0]))

                # Commit the changes to the database
                connection.commit()

                # Respond with a success message
                return jsonify({'status': 'success', 'message': 'Booking submitted successfully'})
            else:
                return jsonify({'status': 'error', 'message': 'Property not found'})

    except Exception as e:
        # Handle database errors
        return jsonify({'status': 'error', 'message': str(e)})

#Destinations Code
@app.route('/Destinations')
def destinations():
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT destination_name, thumbnail FROM destinations")
            destinations_data = cursor.fetchall()

        return render_template('Destinations.html', destinations_data=destinations_data)

    except Exception as e:
        print(f"Error fetching properties: {e}")
        destinations_data = []
        return render_template('Destinations.html', destinations_data=destinations_data, error=str(e))

@app.route('/list_destination', methods=['GET', 'POST'])
def destinations_listing():
    if 'admin_id' not in session:
        return redirect(url_for('login', next=request.url))

    if request.method == 'POST':
        destination_name = request.form.get('destination_name')
        destination_description = request.form.get('destination_description')
        destination_type= request.form.get('destination_type')
        Price = request.form.get('Price')
        amenities = request.form.getlist('amenities[]')
        admin_id = session['admin_id']

        # Check if the POST request has the file part
        if 'destination_image' in request.files and 'thumbnail_image' in request.files:
            destination_image = request.files['destination_image']
            thumbnail_image = request.files['thumbnail_image']
            destination1 = request.files['Additional Image1']
            destination2 = request.files['Additional Image2']
            destination3 = request.files['Additional Image3']
            destination4 = request.files['Additional Image4']

            # Save the images to a folder within the 'static' directory
            destination_image_path = os.path.join('static', 'uploads', destination_image.filename)
            thumbnail_image_path = os.path.join('static', 'uploads', thumbnail_image.filename)
            ipath1 = os.path.join('static', 'uploads', destination1.filename)
            ipath2 = os.path.join('static', 'uploads', destination2.filename)
            ipath3 = os.path.join('static', 'uploads', destination3.filename)
            ipath4 = os.path.join('static', 'uploads', destination4.filename)

            # Replace backslashes with forward slashes
            destination_image_path = destination_image_path.replace('\\', '/')
            thumbnail_image_path = thumbnail_image_path.replace('\\', '/')
            ipath1 = ipath1.replace('\\', '/')
            ipath2 = ipath2.replace('\\', '/')
            ipath3 = ipath3.replace('\\', '/')
            ipath4 = ipath4.replace('\\', '/')

            # Save the file objects
            destination_image.save(destination_image_path)
            thumbnail_image.save(thumbnail_image_path)
            destination1.save(ipath1)
            destination2.save(ipath2)
            destination3.save(ipath3)
            destination4.save(ipath4)

        amenities_str = ', '.join(amenities)

        try:
            # Insert the destination into the destinations table
            with sqlite3.connect('users.db') as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO destinations (destination_name, destination_image, description, thumbnail, img1, img2, img3, img4, Price, Amenities, admin_id,Type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)",
                    (destination_name, destination_image_path, destination_description, thumbnail_image_path, ipath1,
                     ipath2, ipath3, ipath4, Price, amenities_str, admin_id,destination_type))
                connection.commit()

            # Redirect to a success page or do other necessary actions
            return render_template('destination_listing_success.html', destination_name=destination_name)

        except Exception as e:
            # Handle exceptions (e.g., database errors)
            return render_template('destinations_listing.html', error=str(e))

    # If it's a GET request, simply render the destinations_listing.html template
    return render_template('destinations_listing.html')


@app.route('/booking_destination/', defaults={'destination_id': None})
@app.route('/booking_destination/<int:destination_id>')
def destination_booking(destination_id):
    if 'user_id' not in session:
        return redirect(url_for('login', next=request.url))
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()

            if destination_id is None:
                # Fetch the first available property id if no ID is provided
                cursor.execute("SELECT id FROM destinations ORDER BY RANDOM() LIMIT 1")
                destination_id = cursor.fetchone()[0]

            # Fetch the property with the provided ID
            cursor.execute("SELECT * FROM destinations WHERE id=?", (destination_id,))
            destinations_data = cursor.fetchone()

        if destinations_data:
            # Property information found, pass it to the booking_details.html template
            return render_template('destination_booking.html', destinations_data=destinations_data)
        else:
            # Property not found, you may want to handle this case
            return render_template('error.html', error='destination not found')

    except Exception as e:
        print(f"Error fetching destination information: {e}")
        return render_template('error.html', error=str(e))

@app.route('/submit_destination_booking', methods=['POST'])
def submit_destination_booking():
    if 'user_id' not in session:
        return redirect(url_for('login', next=request.url))

    # Extract data from the request
    destination_name = request.form.get('destination_name')
    guest_name = request.form.get('guest_name')
    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')
    guests = request.form.get('guests')
    amount = request.form.get('amount')
    user_id = session['user_id']  # Assuming you have stored user_id in session
    contacts=request.form.get('contacts')
    try:
        # Connect to the database
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()

            # Get the destination ID based on the destination name
            cursor.execute("SELECT id FROM destinations WHERE destination_name=?", (destination_name,))
            destination_id = cursor.fetchone()

            if destination_id:
                # Insert booking information into the bookings table
                cursor.execute("""
                     INSERT INTO destination_bookings (destination_booking_id, destination_name, check_in, check_out, guests, guest_name, amount, contacts, user_id, Type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, (SELECT Type FROM destinations WHERE destination_name = ?))
""", (destination_id[0], destination_name, check_in, check_out, guests, guest_name, amount, contacts, user_id, destination_name))

                # Commit the changes to the database
                connection.commit()

                # Respond with a success message
                return jsonify({'status': 'success', 'message': 'Booking submitted successfully'})
            else:
                return jsonify({'status': 'error', 'message': 'Property not found'})

    except Exception as e:
        # Handle database errors
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/type/Safari')
def Safari():
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT destination_name, thumbnail FROM destinations WHERE Type = 'Safari'")
            apartment_properties = cursor.fetchall()

        return render_template('Destinations.html', destinations_data=apartment_properties)

    except Exception as e:
        print(f"Error fetching apartment properties: {e}")
        apartment_properties = []
        return render_template('Destinations.html', destinations_data=apartment_properties, error=str(e))

@app.route('/type/Ocean_Safari')
def Ocean():
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT destination_name, thumbnail FROM destinations WHERE Type = 'Ocean Safari'")
            apartment_properties = cursor.fetchall()

        return render_template('Destinations.html', destinations_data=apartment_properties)

    except Exception as e:
        print(f"Error fetching apartment properties: {e}")
        apartment_properties = []
        return render_template('Destinations.html', destinations_data=apartment_properties, error=str(e))

@app.route('/type/City')
def City():
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT destination_name, thumbnail FROM destinations WHERE Type = 'City'")
            apartment_properties = cursor.fetchall()

        return render_template('Destinations.html', destinations_data=apartment_properties)

    except Exception as e:
        print(f"Error fetching apartment properties: {e}")
        apartment_properties = []
        return render_template('Destinations.html', destinations_data=apartment_properties, error=str(e))

@app.route('/type/Conservancy')
def Conservancy():
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT destination_name, thumbnail FROM destinations WHERE Type = 'Conservancy'")
            apartment_properties = cursor.fetchall()

        return render_template('Destinations.html', destinations_data=apartment_properties)

    except Exception as e:
        print(f"Error fetching apartment properties: {e}")
        apartment_properties = []
        return render_template('Destinations.html', destinations_data=apartment_properties, error=str(e))

#Admin Routes
@app.route('/Admin_Panel',methods=['GET','POST'])
def Admin_Panel():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM admins WHERE email=? AND password=?", (email, password))
            admin = cursor.fetchone()

        if admin:
            # If the user exists, store user information in the session
            session['admin_id'] = admin[0]
            session['admin_name'] = admin[1]

            # Redirect to the index page with a welcome message
            return redirect('/dashboard')

        else:
            return render_template('Admin_Panel.html', error="Invalid Credentials")
    return render_template('Admin_Panel.html')

@app.route('/adminsignup', methods=['GET', 'POST'])
def adminsignup():
    if request.method == 'POST':
        # Process the form data here (save to database, perform validation, etc.)
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # Insert the new admin into the admins table
            with sqlite3.connect('users.db') as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO admins (name, email, password) VALUES (?, ?, ?)", (name, email, password))
                connection.commit()

            # Retrieve the admin_id of the newly inserted admin
            cursor.execute("SELECT id FROM admins WHERE email=?", (email,))
            new_admin_id = cursor.fetchone()[0]

            # Store the admin_id in the session
            session['admin_id'] = new_admin_id
            session['name'] = name
            session['email'] = email
            session['password'] = password

            # Redirect to the dashboard or another page
            return redirect('/dashboard')

        except sqlite3.IntegrityError:
            # Handle the case where the email is not unique (already exists in the database)
            return render_template('Admin_Signup.html', error='Email already exists. Please use a different email.')

    return render_template('Admin_Signup.html')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/Admin_destinations')
def admindestinations():
    try:
        admin_id = session['admin_id']  # Assuming you have stored admin_id in session
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, destination_name, thumbnail FROM destinations WHERE admin_id = ?", (admin_id,))
            destinations_data = cursor.fetchall()

        return render_template('Admin_destinations.html', destinations_data=destinations_data)

    except Exception as e:
        print(f"Error fetching properties: {e}")
        destinations_data = []
        return render_template('Admin_destinations.html', destinations_data=destinations_data, error=str(e))


@app.route('/viewbookings/<destination_id>')
def viewbooking(destination_id):
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM destination_bookings WHERE destination_booking_id = ?", (destination_id,))
            bookings_data = cursor.fetchall()

        return render_template('admin_view_booking.html', bookings_data=bookings_data)

    except Exception as e:
        print(f"Error fetching bookings: {e}")
        bookings_data = []
        return render_template('admin_view_booking.html', bookings_data=bookings_data, error=str(e))

#Admin Properties Routes

@app.route('/Admin_properties')
def adminproperties():
    try:
        admin_id = session['admin_id']  # Assuming you have stored admin_id in session
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, thumbnail FROM properties WHERE admin_id = ?", (admin_id,))
            destinations_data = cursor.fetchall()

        return render_template('Admin_properties.html', destinations_data=destinations_data)

    except Exception as e:
        print(f"Error fetching properties: {e}")
        destinations_data = []
        return render_template('Admin_properties.html', destinations_data=destinations_data, error=str(e))


@app.route('/viewpropertybookings/<destination_id>')
def viewpropertybooking(destination_id):
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM bookings WHERE property_id = ?", (destination_id,))
            bookings_data = cursor.fetchall()

        return render_template('admin_property_booking.html', bookings_data=bookings_data)

    except Exception as e:
        print(f"Error fetching bookings: {e}")
        bookings_data = []
        return render_template('admin_property_booking.html', bookings_data=bookings_data, error=str(e))

@app.route('/mybookings/')
def user_bookings():
    if 'user_id' not in session:
        return redirect(url_for('login', next=request.url))

    user_id = session['user_id']

    try:
        # Connect to the database
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()

            # Fetch regular property bookings for the specific user
            cursor.execute("SELECT * FROM bookings WHERE user_id = ?", (user_id,))
            bookings = cursor.fetchall()

            # Fetch destination bookings for the specific user
            cursor.execute("SELECT * FROM destination_bookings WHERE user_id = ?", (user_id,))
            destination_bookings = cursor.fetchall()

        return render_template('Booking.html', bookings=bookings, destination_bookings=destination_bookings)

    except Exception as e:
        # Handle database errors
        return render_template('error.html', error=str(e))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()

            # Retrieve the user from the database (assuming you have a users table)
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()

            if user:
                # If the user exists, store user information in the session
                session['id'] = user[0]
                session['user_name'] = user[1]

                # Insert into the contacts table with the user_id
                cursor.execute("INSERT INTO contacts (name, email, message, user_id) VALUES (?, ?, ?, ?)", (name, email, message, user[0]))
                connection.commit()
            else:
                # If the user does not exist, redirect to the login page
                return render_template('Login.html')

    return render_template('contact.html', user_name=session.get('user_name'), id=session.get('id'))

@app.route('/Teamdashboard')
def teamdashboard():
    return render_template('Teamdashboard.html')

@app.route('/Messages')
def messages():
    # Fetch messages from the contacts table
    with sqlite3.connect('users.db') as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM contacts")
        messages = cursor.fetchall()

    return render_template('Messages.html', messages=messages)

@app.route('/update_status', methods=['POST'])
def update_status():
    try:
        message_id = request.form.get('messageId')

        # Connect to the database
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()

            # Update the status in the 'contacts' table
            cursor.execute("UPDATE contacts SET status = 1 WHERE id = ?", (message_id,))

            # You may also want to update the 'replies' table if needed
            # Example: cursor.execute("UPDATE replies SET status = 1 WHERE message_id = ?", (message_id,))

            # Commit the changes to the database
            connection.commit()

            # Return a success response
            return jsonify({'status': 'success'})

    except Exception as e:
        # Handle exceptions
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/save_reply', methods=['POST'])
def save_reply():
    try:
        message_id = request.form.get('messageId')
        reply_text = request.form.get('replyText')

        # Connect to the database
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()

            # Get the team_id from the Team table
            cursor.execute("SELECT id FROM Team WHERE id = ?", (message_id,))

            team_id = cursor.fetchone()[0]

            # Save the reply in the 'replies' table
            cursor.execute("INSERT INTO replies (message_id, reply_text, status, team_id) VALUES (?, ?, 1, ?)", (message_id, reply_text, team_id))

            # Get the contact's email address
            cursor.execute("SELECT email FROM contacts WHERE id = ?", (message_id,))
            contact_email = cursor.fetchone()[0]

            # Send the email reply
            send_email(contact_email, 'Reply from B&N INTERNATIONAL LTD', reply_text, message_id)

            # Commit the changes to the database
            connection.commit()

            # Return a success response
            return jsonify({'status': 'success'})

    except Exception as e:
        # Handle exceptions
        return jsonify({'status': 'error', 'message': str(e)})


def send_email(recipient, subject, reply_text, message_id):
    # Connect to the database to get the original message
    with sqlite3.connect('users.db') as connection:
        cursor = connection.cursor()

        # Get the original message from the contacts table
        cursor.execute("SELECT message FROM contacts WHERE id = ?", (message_id,))
        original_message = cursor.fetchone()[0]

    # Build the email body with the original message and the reply text
    body = f"Your Message:\n{original_message}\n\nReply:\n{reply_text}"

    # Create and send the email
    msg = Message(subject, recipients=[recipient])
    msg.body = body
    mail.send(msg)

@app.route('/Team_properties')
def teamproperties():
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, name, thumbnail FROM properties")
            destinations_data = cursor.fetchall()

        return render_template('Admin_properties.html', destinations_data=destinations_data)

    except Exception as e:
        print(f"Error fetching properties: {e}")
        destinations_data = []
        return render_template('Admin_properties.html', destinations_data=destinations_data, error=str(e))


@app.route('/Teamviewpropertybookings/<destination_id>')
def Teampropertybooking(destination_id):
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM bookings WHERE property_id = ?", (destination_id,))
            bookings_data = cursor.fetchall()

        return render_template('admin_property_booking.html', bookings_data=bookings_data)

    except Exception as e:
        print(f"Error fetching bookings: {e}")
        bookings_data = []
        return render_template('admin_property_booking.html', bookings_data=bookings_data, error=str(e))

@app.route('/Team_destinations')
def Teamdestinations():
    try:
        admin_id = session['admin_id']  # Assuming you have stored admin_id in session
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, destination_name, thumbnail FROM destinations ")
            destinations_data = cursor.fetchall()

        return render_template('Admin_destinations.html', destinations_data=destinations_data)

    except Exception as e:
        print(f"Error fetching properties: {e}")
        destinations_data = []
        return render_template('Admin_destinations.html', destinations_data=destinations_data, error=str(e))


@app.route('/Teamviewbookings/<destination_id>')
def Teamviewbooking(destination_id):
    try:
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM destination_bookings WHERE destination_booking_id = ?", (destination_id,))
            bookings_data = cursor.fetchall()

        return render_template('admin_view_booking.html', bookings_data=bookings_data)

    except Exception as e:
        print(f"Error fetching bookings: {e}")
        bookings_data = []
        return render_template('admin_view_booking.html', bookings_data=bookings_data, error=str(e))

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
