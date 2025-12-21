# backend/app.py - UPDATED VERSION
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import os
import hashlib
import hmac
import json

# Get the absolute path to the frontend folder
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(current_dir, '..', 'frontend')

app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
app.config['SECRET_KEY'] = 'ridenaija-secret-key-2024-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ridenaija.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize extensions
db = SQLAlchemy(app)
CORS(app, supports_credentials=True)

# ==================== DATABASE MODELS ====================

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='passenger')
    rating = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    trips = db.relationship('Trip', backref='driver', lazy=True, foreign_keys='Trip.driver_id')
    bookings = db.relationship('Booking', backref='passenger', lazy=True)
    
    def set_password(self, password):
        salt = os.urandom(16).hex()
        hash_obj = hashlib.sha256((password + salt).encode())
        self.password_hash = salt + ':' + hash_obj.hexdigest()
    
    def check_password(self, password):
        if ':' not in self.password_hash:
            return False
        salt, stored_hash = self.password_hash.split(':')
        hash_obj = hashlib.sha256((password + salt).encode())
        return hmac.compare_digest(hash_obj.hexdigest(), stored_hash)

class Trip(db.Model):
    __tablename__ = 'trips'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    driver_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    price_per_seat = db.Column(db.Float, nullable=False)
    car_model = db.Column(db.String(100))
    car_plate = db.Column(db.String(20))
    car_type = db.Column(db.String(50), default='Sedan')
    amenities = db.Column(db.Text, default='[]')
    status = db.Column(db.String(20), default='scheduled')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    bookings = db.relationship('Booking', backref='trip', lazy=True)
    
    def get_amenities(self):
        try:
            return json.loads(self.amenities)
        except:
            return []

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id = db.Column(db.String(36), db.ForeignKey('trips.id'), nullable=False)
    passenger_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='confirmed')
    payment_status = db.Column(db.String(20), default='pending')
    notes = db.Column(db.Text)
    booking_reference = db.Column(db.String(20), unique=True)
    receipt_number = db.Column(db.String(20), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def generate_reference(self):
        import random
        import string
        letters = string.ascii_uppercase
        return 'RNJ' + ''.join(random.choice(letters) for i in range(6))
    
    def generate_receipt(self):
        import random
        import string
        letters = string.ascii_uppercase + string.digits
        return 'RCT' + ''.join(random.choice(letters) for i in range(8))

# ==================== HELPER FUNCTIONS ====================

def login_required(f):
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"success": False, "error": "Authentication required"}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 401
        
        kwargs['current_user'] = user
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def create_sample_data():
    if User.query.count() == 0:
        print("Creating sample users...")
        
        users = [
            {
                "name": "Admin User",
                "email": "admin@ridenaija.com",
                "phone": "08011112222",
                "role": "admin",
                "password": "password123",
                "rating": 5.0
            },
            {
                "name": "John Driver",
                "email": "driver@ridenaija.com",
                "phone": "08012345678",
                "role": "driver",
                "password": "password123",
                "rating": 4.8
            },
            {
                "name": "Sarah Passenger",
                "email": "passenger@ridenaija.com",
                "phone": "08087654321",
                "role": "passenger",
                "password": "password123",
                "rating": 4.9
            }
        ]
        
        for user_data in users:
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                phone=user_data["phone"],
                role=user_data["role"],
                rating=user_data["rating"]
            )
            user.set_password(user_data["password"])
            db.session.add(user)
        
        db.session.commit()
        print("✅ Sample users created!")

def generate_trips():
    today = datetime.utcnow()
    end_date = datetime(2024, 3, 29, 23, 59, 59)
    
    routes = [
        {"from": "Lagos", "to": "Abuja", "duration_hours": 11, "price": 15000},
        {"from": "Lagos", "to": "Port Harcourt", "duration_hours": 9, "price": 12000},
        {"from": "Lagos", "to": "Ibadan", "duration_hours": 2.5, "price": 3500},
        {"from": "Lagos", "to": "Kano", "duration_hours": 16, "price": 18000},
        {"from": "Lagos", "to": "Enugu", "duration_hours": 8, "price": 11000},
        {"from": "Lagos", "to": "Calabar", "duration_hours": 13, "price": 14000},
        {"from": "Lagos", "to": "Abeokuta", "duration_hours": 2, "price": 2500},
        {"from": "Lagos", "to": "Akure", "duration_hours": 5, "price": 5500},
        {"from": "Abuja", "to": "Lagos", "duration_hours": 11, "price": 15000},
        {"from": "Abuja", "to": "Kano", "duration_hours": 6, "price": 8000},
        {"from": "Abuja", "to": "Jos", "duration_hours": 4, "price": 6000},
        {"from": "Abuja", "to": "Ilorin", "duration_hours": 5, "price": 7000},
        {"from": "Abuja", "to": "Port Harcourt", "duration_hours": 9, "price": 13000},
        {"from": "Ibadan", "to": "Lagos", "duration_hours": 2.5, "price": 3500},
        {"from": "Ibadan", "to": "Abuja", "duration_hours": 9, "price": 13500},
        {"from": "Port Harcourt", "to": "Lagos", "duration_hours": 9, "price": 12000},
        {"from": "Port Harcourt", "to": "Enugu", "duration_hours": 4, "price": 6000},
        {"from": "Kano", "to": "Lagos", "duration_hours": 16, "price": 18000},
        {"from": "Kano", "to": "Abuja", "duration_hours": 6, "price": 8000},
        {"from": "Enugu", "to": "Lagos", "duration_hours": 8, "price": 11000},
    ]
    
    driver = User.query.filter_by(role='driver').first()
    if not driver:
        driver = User(
            name="Default Driver",
            email="default.driver@ridenaija.com",
            phone="08000000000",
            role="driver",
            rating=4.5
        )
        driver.set_password("password123")
        db.session.add(driver)
        db.session.commit()
    
    trip_count = 0
    current_date = today
    
    # Clear existing trips
    Trip.query.delete()
    
    while current_date <= end_date:
        for route in routes:
            for time_slot in [8, 12, 16]:
                departure_time = current_date.replace(
                    hour=time_slot,
                    minute=0,
                    second=0,
                    microsecond=0
                )
                
                if departure_time < datetime.utcnow():
                    continue
                
                arrival_time = departure_time + timedelta(hours=route['duration_hours'])
                
                import random
                available_seats = random.randint(8, 14)
                
                trip = Trip(
                    driver_id=driver.id,
                    from_location=route['from'],
                    to_location=route['to'],
                    departure_time=departure_time,
                    arrival_time=arrival_time,
                    available_seats=available_seats,
                    price_per_seat=route['price'],
                    car_model="Toyota Hiace",
                    car_plate=f"RNJ{trip_count:03}",
                    car_type="Bus",
                    amenities=json.dumps(["AC", "Comfortable Seats", "Charging Ports"]),
                    status="scheduled"
                )
                
                db.session.add(trip)
                trip_count += 1
        
        current_date += timedelta(days=1)
    
    try:
        db.session.commit()
        print(f"✅ Generated {trip_count} trips")
        return trip_count
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
        return 0

# ==================== API ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    try:
        data = request.json
        
        required_fields = ['name', 'email', 'phone', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"success": False, "error": f"{field} is required"}), 400
        
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({"success": False, "error": "Email already registered"}), 409
        
        new_user = User(
            name=data['name'].strip(),
            email=data['email'].lower().strip(),
            phone=data['phone'].strip(),
            role=data.get('role', 'passenger')
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        session['user_id'] = new_user.id
        
        return jsonify({
            "success": True,
            "message": "Registration successful",
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email,
                "role": new_user.role,
                "rating": new_user.rating
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    try:
        data = request.json
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"success": False, "error": "Email and password required"}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if user and user.check_password(data['password']):
            session['user_id'] = user.id
            
            return jsonify({
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "rating": user.rating
                }
            }), 200
        
        return jsonify({"success": False, "error": "Invalid email or password"}), 401
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.pop('user_id', None)
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    }), 200

@app.route('/api/auth/check', methods=['GET'])
def api_check_auth():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify({
                "success": True,
                "authenticated": True,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "rating": user.rating
                }
            }), 200
    
    return jsonify({"success": True, "authenticated": False}), 200

@app.route('/api/trips', methods=['GET'])
def api_get_trips():
    try:
        from_loc = request.args.get('from', '').strip()
        to_loc = request.args.get('to', '').strip()
        date = request.args.get('date', '')
        
        query = Trip.query.filter(Trip.status == 'scheduled', Trip.available_seats > 0)
        
        if from_loc:
            query = query.filter(Trip.from_location.ilike(f'%{from_loc}%'))
        if to_loc:
            query = query.filter(Trip.to_location.ilike(f'%{to_loc}%'))
        if date:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                query = query.filter(db.func.date(Trip.departure_time) == date_obj.date())
            except:
                pass
        
        query = query.filter(Trip.departure_time >= datetime.utcnow())
        
        trips = query.order_by(Trip.departure_time).all()
        
        trips_data = []
        for trip in trips:
            driver = User.query.get(trip.driver_id)
            trips_data.append({
                "id": trip.id,
                "driver_name": driver.name if driver else "Unknown Driver",
                "driver_rating": driver.rating if driver else 0.0,
                "from_location": trip.from_location,
                "to_location": trip.to_location,
                "departure_time": trip.departure_time.isoformat(),
                "arrival_time": trip.arrival_time.isoformat(),
                "available_seats": trip.available_seats,
                "price_per_seat": trip.price_per_seat,
                "car_model": trip.car_model,
                "car_plate": trip.car_plate,
                "car_type": trip.car_type,
                "amenities": trip.get_amenities(),
                "status": trip.status
            })
        
        return jsonify({
            "success": True,
            "count": len(trips_data),
            "trips": trips_data
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/bookings', methods=['POST'])
@login_required
def api_create_booking(current_user):
    try:
        data = request.json
        
        if 'trip_id' not in data:
            return jsonify({"success": False, "error": "Trip ID is required"}), 400
        
        seats = data.get('seats', 1)
        if seats < 1:
            return jsonify({"success": False, "error": "At least 1 seat required"}), 400
        
        trip = Trip.query.get(data['trip_id'])
        if not trip:
            return jsonify({"success": False, "error": "Trip not found"}), 404
        
        if trip.available_seats < seats:
            return jsonify({"success": False, "error": "Not enough seats available"}), 400
        
        if trip.status != 'scheduled':
            return jsonify({"success": False, "error": "Trip is not available for booking"}), 400
        
        if trip.departure_time < datetime.utcnow():
            return jsonify({"success": False, "error": "Cannot book past trips"}), 400
        
        # Generate unique reference and receipt
        import random
        import string
        
        booking_reference = 'RNJ' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        receipt_number = 'RCT' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        new_booking = Booking(
            trip_id=data['trip_id'],
            passenger_id=current_user.id,
            seats=seats,
            total_price=seats * trip.price_per_seat,
            status="confirmed",
            payment_status="paid",
            notes=data.get('notes', ''),
            booking_reference=booking_reference,
            receipt_number=receipt_number
        )
        
        trip.available_seats -= seats
        
        db.session.add(new_booking)
        db.session.commit()
        
        # Prepare booking details for response
        booking_details = {
            "id": new_booking.id,
            "trip_id": new_booking.trip_id,
            "seats": new_booking.seats,
            "total_price": new_booking.total_price,
            "status": new_booking.status,
            "payment_status": new_booking.payment_status,
            "booking_reference": new_booking.booking_reference,
            "receipt_number": new_booking.receipt_number,
            "created_at": new_booking.created_at.isoformat(),
            "trip_details": {
                "from_location": trip.from_location,
                "to_location": trip.to_location,
                "departure_time": trip.departure_time.isoformat(),
                "arrival_time": trip.arrival_time.isoformat(),
                "price_per_seat": trip.price_per_seat,
                "driver_name": trip.driver.name if trip.driver else "Unknown Driver"
            }
        }
        
        return jsonify({
            "success": True,
            "message": "Booking created successfully",
            "booking": booking_details,
            "redirect": f"/payment?booking_id={new_booking.id}"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/bookings/user', methods=['GET'])
@login_required
def api_get_user_bookings(current_user):
    try:
        bookings = Booking.query.filter_by(passenger_id=current_user.id).order_by(Booking.created_at.desc()).all()
        
        bookings_data = []
        for booking in bookings:
            trip = Trip.query.get(booking.trip_id)
            driver = User.query.get(trip.driver_id) if trip else None
            
            bookings_data.append({
                "id": booking.id,
                "trip_id": booking.trip_id,
                "seats": booking.seats,
                "total_price": booking.total_price,
                "status": booking.status,
                "payment_status": booking.payment_status,
                "notes": booking.notes,
                "booking_reference": booking.booking_reference,
                "receipt_number": booking.receipt_number,
                "created_at": booking.created_at.isoformat() if booking.created_at else None,
                "trip_details": {
                    "from_location": trip.from_location if trip else "Unknown",
                    "to_location": trip.to_location if trip else "Unknown",
                    "departure_time": trip.departure_time.isoformat() if trip else None,
                    "arrival_time": trip.arrival_time.isoformat() if trip else None,
                    "price_per_seat": trip.price_per_seat if trip else 0,
                    "driver_name": driver.name if driver else "Unknown Driver"
                }
            })
        
        return jsonify({
            "success": True,
            "count": len(bookings_data),
            "bookings": bookings_data
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/bookings/<booking_id>', methods=['GET'])
@login_required
def api_get_booking(current_user, booking_id):
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({"success": False, "error": "Booking not found"}), 404
        
        # Check if booking belongs to current user
        if booking.passenger_id != current_user.id:
            return jsonify({"success": False, "error": "Unauthorized"}), 403
        
        trip = Trip.query.get(booking.trip_id)
        driver = User.query.get(trip.driver_id) if trip else None
        
        booking_data = {
            "id": booking.id,
            "trip_id": booking.trip_id,
            "seats": booking.seats,
            "total_price": booking.total_price,
            "status": booking.status,
            "payment_status": booking.payment_status,
            "notes": booking.notes,
            "booking_reference": booking.booking_reference,
            "receipt_number": booking.receipt_number,
            "created_at": booking.created_at.isoformat() if booking.created_at else None,
            "trip_details": {
                "from_location": trip.from_location if trip else "Unknown",
                "to_location": trip.to_location if trip else "Unknown",
                "departure_time": trip.departure_time.isoformat() if trip else None,
                "arrival_time": trip.arrival_time.isoformat() if trip else None,
                "price_per_seat": trip.price_per_seat if trip else 0,
                "driver_name": driver.name if driver else "Unknown Driver",
                "car_model": trip.car_model if trip else "",
                "car_plate": trip.car_plate if trip else ""
            }
        }
        
        return jsonify({
            "success": True,
            "booking": booking_data
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/cities', methods=['GET'])
def api_get_cities():
    cities = [
        {"id": 1, "name": "Lagos", "slug": "lagos", "region": "south-west"},
        {"id": 2, "name": "Abuja", "slug": "abuja", "region": "north-central"},
        {"id": 3, "name": "Port Harcourt", "slug": "portharcourt", "region": "south-south"},
        {"id": 4, "name": "Ibadan", "slug": "ibadan", "region": "south-west"},
        {"id": 5, "name": "Kano", "slug": "kano", "region": "north-west"},
        {"id": 6, "name": "Enugu", "slug": "enugu", "region": "south-east"},
        {"id": 7, "name": "Benin City", "slug": "benin", "region": "south-south"},
        {"id": 8, "name": "Calabar", "slug": "calabar", "region": "south-south"},
        {"id": 9, "name": "Ilorin", "slug": "ilorin", "region": "north-central"},
        {"id": 10, "name": "Jos", "slug": "jos", "region": "north-central"},
        {"id": 11, "name": "Maiduguri", "slug": "maiduguri", "region": "north-east"},
        {"id": 12, "name": "Sokoto", "slug": "sokoto", "region": "north-west"},
        {"id": 13, "name": "Oyo", "slug": "oyo", "region": "south-west"},
        {"id": 14, "name": "Abeokuta", "slug": "abeokuta", "region": "south-west"},
        {"id": 15, "name": "Owerri", "slug": "owerri", "region": "south-east"},
        {"id": 16, "name": "Akure", "slug": "akure", "region": "south-west"},
        {"id": 17, "name": "Minna", "slug": "minna", "region": "north-central"},
        {"id": 18, "name": "Bauchi", "slug": "bauchi", "region": "north-east"}
    ]
    
    return jsonify({
        "success": True,
        "cities": cities
    }), 200

@app.route('/api/routes', methods=['GET'])
def api_get_routes():
    routes = [
        {"from": "Lagos", "to": "Abuja", "distance": "700km", "duration": "10-12 hours", "price": 15000, "region": "all"},
        {"from": "Lagos", "to": "Port Harcourt", "distance": "600km", "duration": "8-10 hours", "price": 12000, "region": "all"},
        {"from": "Lagos", "to": "Ibadan", "distance": "150km", "duration": "2-3 hours", "price": 3500, "region": "south-west"},
        {"from": "Lagos", "to": "Kano", "distance": "1100km", "duration": "15-18 hours", "price": 18000, "region": "all"},
        {"from": "Lagos", "to": "Enugu", "distance": "550km", "duration": "7-9 hours", "price": 11000, "region": "all"},
        {"from": "Lagos", "to": "Calabar", "distance": "800km", "duration": "12-14 hours", "price": 14000, "region": "all"},
        {"from": "Lagos", "to": "Abeokuta", "distance": "100km", "duration": "1.5-2 hours", "price": 2500, "region": "south-west"},
        {"from": "Lagos", "to": "Akure", "distance": "300km", "duration": "4-5 hours", "price": 5500, "region": "south-west"},
        {"from": "Abuja", "to": "Lagos", "distance": "700km", "duration": "10-12 hours", "price": 15000, "region": "all"},
        {"from": "Abuja", "to": "Kano", "distance": "400km", "duration": "6-7 hours", "price": 8000, "region": "north-central"},
        {"from": "Abuja", "to": "Jos", "distance": "250km", "duration": "4-5 hours", "price": 6000, "region": "north-central"},
        {"from": "Abuja", "to": "Ilorin", "distance": "300km", "duration": "5-6 hours", "price": 7000, "region": "north-central"},
        {"from": "Abuja", "to": "Port Harcourt", "distance": "600km", "duration": "9-11 hours", "price": 13000, "region": "all"},
        {"from": "Ibadan", "to": "Lagos", "distance": "150km", "duration": "2-3 hours", "price": 3500, "region": "south-west"},
        {"from": "Ibadan", "to": "Abuja", "distance": "600km", "duration": "9-11 hours", "price": 13500, "region": "all"},
        {"from": "Ibadan", "to": "Enugu", "distance": "450km", "duration": "6-8 hours", "price": 9500, "region": "all"},
        {"from": "Port Harcourt", "to": "Lagos", "distance": "600km", "duration": "8-10 hours", "price": 12000, "region": "all"},
        {"from": "Port Harcourt", "to": "Enugu", "distance": "250km", "duration": "4-5 hours", "price": 6000, "region": "south-east"},
        {"from": "Kano", "to": "Lagos", "distance": "1100km", "duration": "15-18 hours", "price": 18000, "region": "all"},
        {"from": "Kano", "to": "Abuja", "distance": "400km", "duration": "6-7 hours", "price": 8000, "region": "north-central"},
    ]
    
    return jsonify({
        "success": True,
        "routes": routes
    }), 200

@app.route('/api/payment/process', methods=['POST'])
@login_required
def api_process_payment(current_user):
    try:
        data = request.json
        
        if 'booking_id' not in data:
            return jsonify({"success": False, "error": "Booking ID is required"}), 400
        
        booking = Booking.query.get(data['booking_id'])
        if not booking:
            return jsonify({"success": False, "error": "Booking not found"}), 404
        
        # Check if booking belongs to current user
        if booking.passenger_id != current_user.id:
            return jsonify({"success": False, "error": "Unauthorized"}), 403
        
        # Update payment status
        booking.payment_status = 'paid'
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Payment processed successfully",
            "receipt": {
                "booking_reference": booking.booking_reference,
                "receipt_number": booking.receipt_number,
                "total_amount": booking.total_price,
                "payment_date": datetime.utcnow().isoformat()
            },
            "redirect": "/bookings"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({
        "success": True,
        "status": "healthy",
        "service": "RideNaija",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

# ==================== FRONTEND ROUTES ====================

@app.route('/')
def serve_index():
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/dashboard')
def serve_dashboard():
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/bookings')
def serve_bookings():
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/payment')
def serve_payment():
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory(frontend_dir, path)
    except:
        return send_from_directory(frontend_dir, 'index.html')

# ==================== APPLICATION STARTUP ====================

def initialize_database():
    print("Initializing database...")
    with app.app_context():
        db.create_all()
        create_sample_data()
        generate_trips()
        print("✅ Database initialization complete!")

if __name__ == '__main__':
    print("=" * 60)
    print("🚗 RideNaija - Road Trip Booking System")
    print("=" * 60)
    print(f"📁 Frontend directory: {frontend_dir}")
    print(f"🌐 Server URL: http://localhost:5000")
    print(f"🌐 API Base URL: http://localhost:5000/api")
    print(f"👤 Admin: admin@ridenaija.com / password123")
    print(f"🚗 Driver: driver@ridenaija.com / password123")
    print(f"👤 Passenger: passenger@ridenaija.com / password123")
    print("-" * 60)
    print("📅 Generating trips until March 29th, 2024...")
    print("=" * 60)
    
    initialize_database()
    
    app.run(debug=True, host='0.0.0.0', port=5000)