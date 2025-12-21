const express = require('express');
const cors = require('cors');
const mysql = require('mysql2');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors({
    origin: 'http://localhost:3000',
    credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// MySQL Database Connection
const db = mysql.createConnection({
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'ridenaija',
    port: process.env.DB_PORT || 3306
});

db.connect((err) => {
    if (err) {
        console.error('Database connection failed:', err);
        process.exit(1);
    }
    console.log('Connected to MySQL database');
});

// Create tables if they don't exist
const createTables = () => {
    const usersTable = `
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(20),
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    `;

    const tripsTable = `
        CREATE TABLE IF NOT EXISTS trips (
            id INT PRIMARY KEY AUTO_INCREMENT,
            from_location VARCHAR(100) NOT NULL,
            to_location VARCHAR(100) NOT NULL,
            departure_time DATETIME NOT NULL,
            arrival_time DATETIME NOT NULL,
            price_per_seat DECIMAL(10, 2) NOT NULL,
            available_seats INT NOT NULL,
            driver_name VARCHAR(100) NOT NULL,
            driver_rating DECIMAL(3, 1) DEFAULT 5.0,
            car_model VARCHAR(100),
            car_plate VARCHAR(20),
            amenities JSON,
            status ENUM('scheduled', 'ongoing', 'completed', 'cancelled') DEFAULT 'scheduled',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    `;

    const bookingsTable = `
        CREATE TABLE IF NOT EXISTS bookings (
            id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            trip_id INT NOT NULL,
            seats INT NOT NULL,
            total_price DECIMAL(10, 2) NOT NULL,
            status ENUM('confirmed', 'pending', 'cancelled') DEFAULT 'confirmed',
            payment_status ENUM('pending', 'paid', 'failed') DEFAULT 'pending',
            booking_reference VARCHAR(20) UNIQUE NOT NULL,
            receipt_number VARCHAR(20) UNIQUE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (trip_id) REFERENCES trips(id)
        )
    `;

    db.query(usersTable, (err) => {
        if (err) console.error('Error creating users table:', err);
    });

    db.query(tripsTable, (err) => {
        if (err) console.error('Error creating trips table:', err);
    });

    db.query(bookingsTable, (err) => {
        if (err) console.error('Error creating bookings table:', err);
    });
};

createTables();

// Insert sample trips data
const insertSampleTrips = () => {
    const sampleTrips = [
        {
            from_location: 'Lagos',
            to_location: 'Abuja',
            departure_time: new Date(Date.now() + 86400000), // Tomorrow
            arrival_time: new Date(Date.now() + 86400000 + (10 * 3600000)), // 10 hours later
            price_per_seat: 15000.00,
            available_seats: 20,
            driver_name: 'John Adekunle',
            driver_rating: 4.8,
            car_model: 'Toyota Hiace',
            car_plate: 'LAG123XY',
            amenities: JSON.stringify(['WiFi', 'AC', 'TV', 'Charging Ports', 'Refreshments']),
            status: 'scheduled'
        },
        {
            from_location: 'Lagos',
            to_location: 'Port Harcourt',
            departure_time: new Date(Date.now() + 172800000), // Day after tomorrow
            arrival_time: new Date(Date.now() + 172800000 + (8 * 3600000)), // 8 hours later
            price_per_seat: 12000.00,
            available_seats: 15,
            driver_name: 'Michael Chukwu',
            driver_rating: 4.6,
            car_model: 'Mercedes Sprinter',
            car_plate: 'PHC456AB',
            amenities: JSON.stringify(['WiFi', 'AC', 'Charging Ports']),
            status: 'scheduled'
        },
        {
            from_location: 'Abuja',
            to_location: 'Lagos',
            departure_time: new Date(Date.now() + 86400000),
            arrival_time: new Date(Date.now() + 86400000 + (10 * 3600000)),
            price_per_seat: 15000.00,
            available_seats: 18,
            driver_name: 'Samuel Okoro',
            driver_rating: 4.7,
            car_model: 'Toyota Hiace',
            car_plate: 'ABJ789CD',
            amenities: JSON.stringify(['WiFi', 'AC', 'TV', 'Refreshments']),
            status: 'scheduled'
        }
    ];

    sampleTrips.forEach(trip => {
        const checkQuery = 'SELECT COUNT(*) as count FROM trips WHERE from_location = ? AND to_location = ? AND departure_time = ?';
        db.query(checkQuery, [trip.from_location, trip.to_location, trip.departure_time], (err, results) => {
            if (err) console.error('Error checking trip:', err);
            if (results[0].count === 0) {
                const insertQuery = 'INSERT INTO trips SET ?';
                db.query(insertQuery, trip, (err) => {
                    if (err) console.error('Error inserting trip:', err);
                });
            }
        });
    });
};

// Check and insert sample data
db.query('SELECT COUNT(*) as count FROM trips', (err, results) => {
    if (err) console.error('Error checking trips:', err);
    if (results[0].count === 0) {
        insertSampleTrips();
    }
});

// JWT Secret
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';

// Authentication Middleware
const authenticateToken = (req, res, next) => {
    const token = req.cookies?.token || req.headers['authorization']?.split(' ')[1];
    
    if (!token) {
        return res.status(401).json({ 
            success: false, 
            error: 'Access denied. No token provided.' 
        });
    }

    try {
        const verified = jwt.verify(token, JWT_SECRET);
        req.user = verified;
        next();
    } catch (error) {
        res.status(400).json({ 
            success: false, 
            error: 'Invalid token.' 
        });
    }
};

// API Routes

// Auth Routes
app.post('/api/auth/register', async (req, res) => {
    try {
        const { name, email, phone, password } = req.body;
        
        // Check if user exists
        const [existing] = await db.promise().query(
            'SELECT id FROM users WHERE email = ?',
            [email]
        );
        
        if (existing.length > 0) {
            return res.status(400).json({
                success: false,
                error: 'User already exists'
            });
        }
        
        // Hash password
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);
        
        // Insert user
        const [result] = await db.promise().query(
            'INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)',
            [name, email, phone, hashedPassword]
        );
        
        // Create token
        const token = jwt.sign(
            { id: result.insertId, email, name },
            JWT_SECRET,
            { expiresIn: '7d' }
        );
        
        // Set cookie
        res.cookie('token', token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'strict',
            maxAge: 7 * 24 * 60 * 60 * 1000 // 7 days
        });
        
        res.json({
            success: true,
            user: {
                id: result.insertId,
                name,
                email,
                phone
            }
        });
    } catch (error) {
        console.error('Registration error:', error);
        res.status(500).json({
            success: false,
            error: 'Server error'
        });
    }
});

app.post('/api/auth/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        
        // Find user
        const [users] = await db.promise().query(
            'SELECT * FROM users WHERE email = ?',
            [email]
        );
        
        if (users.length === 0) {
            return res.status(400).json({
                success: false,
                error: 'Invalid credentials'
            });
        }
        
        const user = users[0];
        
        // Check password
        const validPassword = await bcrypt.compare(password, user.password);
        if (!validPassword) {
            return res.status(400).json({
                success: false,
                error: 'Invalid credentials'
            });
        }
        
        // Create token
        const token = jwt.sign(
            { id: user.id, email: user.email, name: user.name },
            JWT_SECRET,
            { expiresIn: '7d' }
        );
        
        // Set cookie
        res.cookie('token', token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'strict',
            maxAge: 7 * 24 * 60 * 60 * 1000
        });
        
        res.json({
            success: true,
            user: {
                id: user.id,
                name: user.name,
                email: user.email,
                phone: user.phone
            }
        });
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({
            success: false,
            error: 'Server error'
        });
    }
});

app.get('/api/auth/check', authenticateToken, (req, res) => {
    res.json({
        success: true,
        authenticated: true,
        user: req.user
    });
});

app.post('/api/auth/logout', (req, res) => {
    res.clearCookie('token');
    res.json({
        success: true,
        message: 'Logged out successfully'
    });
});

// Trip Routes
app.get('/api/trips', async (req, res) => {
    try {
        const { from, to, date } = req.query;
        
        let query = 'SELECT * FROM trips WHERE status = "scheduled"';
        const params = [];
        
        if (from) {
            query += ' AND from_location = ?';
            params.push(from);
        }
        
        if (to) {
            query += ' AND to_location = ?';
            params.push(to);
        }
        
        if (date) {
            const searchDate = new Date(date);
            const nextDay = new Date(searchDate);
            nextDay.setDate(nextDay.getDate() + 1);
            
            query += ' AND departure_time >= ? AND departure_time < ?';
            params.push(searchDate.toISOString().split('T')[0] + ' 00:00:00');
            params.push(nextDay.toISOString().split('T')[0] + ' 00:00:00');
        }
        
        query += ' ORDER BY departure_time ASC';
        
        const [trips] = await db.promise().query(query, params);
        
        // Parse JSON amenities
        const parsedTrips = trips.map(trip => ({
            ...trip,
            amenities: trip.amenities ? JSON.parse(trip.amenities) : []
        }));
        
        res.json({
            success: true,
            trips: parsedTrips
        });
    } catch (error) {
        console.error('Error fetching trips:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to fetch trips'
        });
    }
});

app.get('/api/trips/:id', async (req, res) => {
    try {
        const [trips] = await db.promise().query(
            'SELECT * FROM trips WHERE id = ?',
            [req.params.id]
        );
        
        if (trips.length === 0) {
            return res.status(404).json({
                success: false,
                error: 'Trip not found'
            });
        }
        
        const trip = {
            ...trips[0],
            amenities: trips[0].amenities ? JSON.parse(trips[0].amenities) : []
        };
        
        res.json({
            success: true,
            trip
        });
    } catch (error) {
        console.error('Error fetching trip:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to fetch trip'
        });
    }
});

// Booking Routes
app.post('/api/bookings', authenticateToken, async (req, res) => {
    try {
        const { trip_id, seats, notes } = req.body;
        const user_id = req.user.id;
        
        // Get trip details
        const [trips] = await db.promise().query(
            'SELECT * FROM trips WHERE id = ?',
            [trip_id]
        );
        
        if (trips.length === 0) {
            return res.status(404).json({
                success: false,
                error: 'Trip not found'
            });
        }
        
        const trip = trips[0];
        
        // Check available seats
        if (trip.available_seats < seats) {
            return res.status(400).json({
                success: false,
                error: `Only ${trip.available_seats} seats available`
            });
        }
        
        // Calculate total price
        const total_price = trip.price_per_seat * seats;
        
        // Generate unique booking reference
        const booking_reference = 'RN' + Date.now().toString().slice(-8);
        const receipt_number = 'RCT' + Date.now().toString().slice(-8);
        
        // Create booking
        const [result] = await db.promise().query(
            `INSERT INTO bookings 
             (user_id, trip_id, seats, total_price, booking_reference, receipt_number, notes) 
             VALUES (?, ?, ?, ?, ?, ?, ?)`,
            [user_id, trip_id, seats, total_price, booking_reference, receipt_number, notes]
        );
        
        // Update available seats
        await db.promise().query(
            'UPDATE trips SET available_seats = available_seats - ? WHERE id = ?',
            [seats, trip_id]
        );
        
        res.json({
            success: true,
            booking_id: result.insertId,
            booking_reference,
            receipt_number,
            redirect: `/payment?booking_id=${result.insertId}`
        });
    } catch (error) {
        console.error('Booking error:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to create booking'
        });
    }
});

app.get('/api/bookings/user', authenticateToken, async (req, res) => {
    try {
        const [bookings] = await db.promise().query(
            `SELECT b.*, t.* 
             FROM bookings b 
             JOIN trips t ON b.trip_id = t.id 
             WHERE b.user_id = ? 
             ORDER BY b.created_at DESC`,
            [req.user.id]
        );
        
        const formattedBookings = bookings.map(booking => ({
            ...booking,
            trip_details: {
                from_location: booking.from_location,
                to_location: booking.to_location,
                departure_time: booking.departure_time,
                arrival_time: booking.arrival_time,
                price_per_seat: booking.price_per_seat,
                driver_name: booking.driver_name,
                driver_rating: booking.driver_rating,
                car_model: booking.car_model,
                car_plate: booking.car_plate,
                amenities: booking.amenities ? JSON.parse(booking.amenities) : []
            }
        }));
        
        res.json({
            success: true,
            bookings: formattedBookings
        });
    } catch (error) {
        console.error('Error fetching bookings:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to fetch bookings'
        });
    }
});

app.get('/api/bookings/:id', authenticateToken, async (req, res) => {
    try {
        const [bookings] = await db.promise().query(
            `SELECT b.*, t.* 
             FROM bookings b 
             JOIN trips t ON b.trip_id = t.id 
             WHERE b.id = ? AND b.user_id = ?`,
            [req.params.id, req.user.id]
        );
        
        if (bookings.length === 0) {
            return res.status(404).json({
                success: false,
                error: 'Booking not found'
            });
        }
        
        const booking = bookings[0];
        const formattedBooking = {
            ...booking,
            trip_details: {
                from_location: booking.from_location,
                to_location: booking.to_location,
                departure_time: booking.departure_time,
                arrival_time: booking.arrival_time,
                price_per_seat: booking.price_per_seat,
                driver_name: booking.driver_name,
                driver_rating: booking.driver_rating,
                car_model: booking.car_model,
                car_plate: booking.car_plate,
                amenities: booking.amenities ? JSON.parse(booking.amenities) : []
            }
        };
        
        res.json({
            success: true,
            booking: formattedBooking
        });
    } catch (error) {
        console.error('Error fetching booking:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to fetch booking'
        });
    }
});

// Routes for frontend
app.get('/api/routes', async (req, res) => {
    try {
        const [routes] = await db.promise().query(
            `SELECT DISTINCT from_location, to_location 
             FROM trips 
             WHERE status = 'scheduled'
             ORDER BY from_location, to_location`
        );
        
        // Add static route data
        const staticRoutes = [
            {"from": "lagos", "to": "abuja", "distance": "700km", "duration": "10-12 hours", "price": 15000, "region": "all"},
            {"from": "lagos", "to": "portharcourt", "distance": "600km", "duration": "8-10 hours", "price": 12000, "region": "all"},
            {"from": "lagos", "to": "ibadan", "distance": "150km", "duration": "2-3 hours", "price": 3500, "region": "south-west"},
            {"from": "lagos", "to": "kano", "distance": "1100km", "duration": "15-18 hours", "price": 18000, "region": "all"},
            {"from": "lagos", "to": "enugu", "distance": "550km", "duration": "7-9 hours", "price": 11000, "region": "all"}
        ];
        
        res.json({
            success: true,
            routes: staticRoutes
        });
    } catch (error) {
        console.error('Error fetching routes:', error);
        res.status(500).json({
            success: false,
            error: 'Failed to fetch routes'
        });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`API available at http://localhost:${PORT}/api`);
});