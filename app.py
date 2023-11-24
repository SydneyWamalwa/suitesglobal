from flask import Flask, render_template, request, redirect, session,jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

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
                Amenities TEXT NOT NULL
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
            Amenities TEXT NOT NULL
        )
    ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS destination_bookings (
            id INTEGER PRIMARY KEY,
            destination_name TEXT NOT NULL,
            guest_name TEXT NOT NULL,
            destination_id INTEGER,
            check_in DATE NOT NULL,
            check_out DATE NOT NULL,
            guests INTEGER NOT NULL,
            amount VARCHAR NOT NULL,
            FOREIGN KEY (destination_id) REFERENCES properties (id)
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






@app.route('/list_property', methods=['GET', 'POST'])
def property_listing():
    if request.method == 'POST':
        property_name = request.form.get('property_name')
        property_description = request.form.get('property_description')
        Price = request.form.get('Price')
        amenities = request.form.getlist('amenities[]')

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
                    "INSERT INTO properties (name, image, description, thumbnail,interiorimg1,interiorimg2,interiorimg3,interiorimg4,Price, Amenities) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (property_name, property_image_path, property_description, thumbnail_image_path, ipath1,
                     ipath2, ipath3, ipath4, Price, amenities_str))
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
    # Extract data from the request
    property_name = request.form.get('property_name')
    guest_name = request.form.get('guest_name')
    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')
    guests = request.form.get('guests')
    amount = request.form.get('amount')

    try:
        # Connect to the database
        with sqlite3.connect('users.db') as connection:
            cursor = connection.cursor()

            # Get the property ID based on the property name
            cursor.execute("SELECT id FROM properties WHERE name=?", (property_name,))
            property_id = cursor.fetchone()

            if property_id:
                # Insert booking information into the bookings table
                cursor.execute("""
                    INSERT INTO bookings (property_id, property_name, check_in, check_out, guests, guest_name, amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (property_id[0], property_name, check_in, check_out, guests, guest_name, amount))

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
    if request.method == 'POST':
        destination_name = request.form.get('destination_name')
        destination_description = request.form.get('destination_description')
        Price = request.form.get('Price')
        amenities = request.form.getlist('amenities[]')

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
            # Insert the destination into the properties table
            with sqlite3.connect('users.db') as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO destinations (destination_name,destination_image,description, thumbnail,img1,img2,img3,img4,Price, Amenities) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?)",
                    (destination_name, destination_image_path, destination_description, thumbnail_image_path, ipath1,
                     ipath2, ipath3, ipath4, Price, amenities_str))
                connection.commit()

            # Redirect to a success page or do other necessary actions
            return render_template('destination_listing_success.html', destination_name=destination_name)

        except Exception as e:
            # Handle exceptions (e.g., database errors)
            return render_template('destinations_listing.html', error=str(e))

    # If it's a GET request, simply render the property_listing.html template
    return render_template('destinations_listing.html')

@app.route('/booking_destination/', defaults={'destination_id': None})
@app.route('/booking_destination/<int:destination_id>')
def destination_booking(destination_id):
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
    # Extract data from the request
    destination_name = request.form.get('destination_name')
    guest_name = request.form.get('guest_name')
    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')
    guests = request.form.get('guests')
    amount = request.form.get('amount')

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
                    INSERT INTO destination_bookings (destination_id, destination_name, check_in, check_out, guests, guest_name, amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (destination_id[0], destination_name, check_in, check_out, guests, guest_name, amount))

                # Commit the changes to the database
                connection.commit()

                # Respond with a success message
                return jsonify({'status': 'success', 'message': 'Booking submitted successfully'})
            else:
                return jsonify({'status': 'error', 'message': 'Property not found'})

    except Exception as e:
        # Handle database errors
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
