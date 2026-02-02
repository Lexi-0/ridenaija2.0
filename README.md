# NaijaTransit - Road Transport Booking Platform

A full-stack web application for booking affordable road trips across Nigeria. This platform allows users to search, compare, and book trips from various transport companies with integrated payment processing.

---

## 🎯 Features

- **User Authentication** - Secure login and registration system
- **Trip Search & Booking** - Search trips by route, date, and price
- **Seat Selection** - Choose specific seats before booking
- **Payment Integration** - Paystack payment gateway for secure transactions
- **Admin Dashboard** - Manage trips, bookings, and transport companies
- **Email Notifications** - Automated confirmation and booking emails
- **Responsive Design** - Works on desktop, tablet, and mobile devices
- **Transport Company Management** - Add and manage multiple transport operators
- **Booking History** - Users can view their past and upcoming trips

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, JavaScript |
| **Backend** | Python Flask |
| **Database** | SQLite (ridenaija.db) |
| **Payment** | Paystack API |
| **Email** | Flask-Mail with SMTP |
| **Server** | Flask Development Server |

---

## 📋 Prerequisites

Before you start, make sure you have:
- **Python 3.8 or higher** - [Download here](https://www.python.org/downloads/)
- **macOS, Windows, or Linux** operating system
- **Text Editor** - VS Code, Sublime Text, or similar
- **Web Browser** - Chrome, Firefox, Safari, or Edge
- **Git** (optional, for version control)

---

## 📁 Project Structure

```
NaijaTransit/
├── app.py                 # Flask backend application
├── ridenaija.db          # SQLite database (stores all data)
├── requirements.txt      # Python package dependencies
├── index.html            # Home page
├── login.html            # User login page
├── booking.html          # Trip booking page
├── payment.html          # Payment page
├── script.js             # Frontend JavaScript logic
├── style.css             # Frontend styling
└── README.md             # This file
```

---

## 🚀 Quick Start Guide

### Step 1: Set Up Your Project Folder

On macOS, open Terminal and run:

```bash
# Create a project folder
mkdir NaijaTransit
cd NaijaTransit

# Copy all your files into this folder
# (Place app.py, requirements.txt, HTML files, CSS, JS, and ridenaija.db here)
```

### Step 2: Install Python Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- Flask-CORS (handle cross-origin requests)
- Flask-SQLAlchemy (database management)
- Flask-Mail (email sending)
- python-dotenv (environment variables)
- And other dependencies listed in requirements.txt

### Step 3: Run the Flask Application

```bash
# Start the Flask server
python app.py
```

You should see output like:
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Step 4: Open in Your Browser

Open your web browser and go to:
```
http://localhost:5000
```

You should see the NaijaTransit home page!

---

## 💾 How Data is Saved

Your application uses **SQLite database** (`ridenaija.db`):

- **User accounts** - Names, emails, passwords, phone numbers
- **Trip information** - Routes, schedules, prices, available seats
- **Bookings** - Passenger bookings, seat selections, payment status
- **Transport companies** - Company details and ratings

All data entered through the web forms is automatically saved to `ridenaija.db`.

---

## 👤 Default Admin Account

The database comes with a default admin account:

```
Email: admin@ridenaija.ng
Password: admin123
```

⚠️ **Important:** Change this password immediately after first login!

---

## 🔐 How to Update Your Code and Push to Git

### Make Changes Locally

1. Edit your files (HTML, CSS, JavaScript, Python)
2. Test in your browser to make sure everything works

### Push Changes to Git

```bash
# Stage all changes
git add .

# Commit your changes with a message
git commit -m "Update: describe what you changed"

# Push to your repository
git push origin main
```

Example commit messages:
```bash
git commit -m "Update: added new booking features"
git commit -m "Fix: corrected login validation"
git commit -m "Feature: integrated Paystack payment"
```

---

## 📖 Using the Application

### For Passengers

1. **Register/Login** - Create an account or login with existing credentials
2. **Search Trips** - Enter departure and arrival locations, select date
3. **View Options** - See available trips with prices and ratings
4. **Book Trip** - Select seats and confirm booking
5. **Make Payment** - Complete payment via Paystack
6. **Confirmation** - Receive booking confirmation via email

### For Admins

1. Login with admin credentials
2. Access admin dashboard
3. **Manage Trips** - Add, edit, or cancel trips
4. **Manage Companies** - Add transport companies
5. **View Bookings** - Monitor all passenger bookings
6. **Generate Reports** - View revenue and occupancy statistics

---

## 🔧 Configuration Files

### `requirements.txt`
Lists all Python packages needed. If you add new packages, update this file:

```bash
pip freeze > requirements.txt
```

### `app.py`
Main Flask application. Contains:
- Routes (URLs)
- Database connections
- API endpoints
- Business logic

### `style.css`
Frontend styling with purple theme:
- Buttons
- Forms
- Navigation bar
- Responsive design

### `script.js`
Frontend JavaScript:
- Form validation
- API calls
- User interactions
- Payment processing

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask'"
**Solution:** Install requirements
```bash
pip install -r requirements.txt
```

### Issue: Database file not found
**Solution:** Make sure `ridenaija.db` is in the same folder as `app.py`

### Issue: Port 5000 already in use
**Solution:** Use a different port
```bash
python app.py --port 5001
```

### Issue: Changes not showing in browser
**Solution:** Hard refresh (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows/Linux)

---

## 📧 Email Configuration

To enable email notifications, set up environment variables:

Create a `.env` file in your project folder:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@ridenaija.ng
```

Then enable in `app.py`:
```python
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
# ... etc
```

---

## 💳 Payment Integration (Paystack)

To enable Paystack payments:

1. Sign up at [Paystack.co](https://paystack.co)
2. Get your Public Key and Secret Key
3. Add to `.env` file:
```
PAYSTACK_PUBLIC_KEY=pk_live_xxxxxxxxxxxx
PAYSTACK_SECRET_KEY=sk_live_xxxxxxxxxxxx
```

4. Update `script.js` with your public key:
```javascript
const PAYSTACK_PUBLIC_KEY = process.env.PAYSTACK_PUBLIC_KEY;
```

---

## 📱 Deployment Options

### Option 1: Heroku (Free tier available)
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Deploy
git push heroku main
```

### Option 2: PythonAnywhere
1. Sign up at [PythonAnywhere.com](https://www.pythonanywhere.com)
2. Upload your files
3. Configure web app settings
4. Your app goes live!

### Option 3: DigitalOcean
1. Create a droplet
2. SSH into server
3. Clone your Git repo
4. Install dependencies
5. Use Gunicorn + Nginx to run

---

## 📚 Useful Resources

- **Flask Documentation** - https://flask.palletsprojects.com/
- **SQLite Documentation** - https://www.sqlite.org/docs.html
- **Paystack API Docs** - https://paystack.com/docs/api/
- **Bootstrap (CSS Framework)** - https://getbootstrap.com/
- **Font Awesome (Icons)** - https://fontawesome.com/

---

## 🤝 Contributing

To contribute to this project:

1. Create a new branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Commit: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Submit a pull request

---

## 📄 Files to Keep/Remove

### ✅ Keep These:
- `app.py` - Your Flask backend
- `requirements.txt` - Python dependencies
- `ridenaija.db` - Your database
- All `.html` files (index, login, booking, payment)
- `script.js` - JavaScript functionality
- `style.css` - Styling

### ❌ Remove These:
- `db_config.php` - It's PHP, you're using Python
- Duplicate `README.md` files - Keep only one
- `LICENSE` - Only if not open-sourcing
- `database.sql` - Already in your SQLite database

---

## 🔒 Security Best Practices

1. **Never commit sensitive data:**
   - Create `.gitignore` file with:
     ```
     .env
     *.db
     __pycache__/
     .venv/
     ```

2. **Change default passwords immediately**

3. **Use HTTPS in production**

4. **Validate all user inputs**

5. **Keep dependencies updated:**
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review Flask documentation
3. Check database integrity with DB Browser for SQLite
4. Look at browser console for JavaScript errors (F12)

---

## 📝 License

This project is proprietary. All rights reserved.

---

## ✨ Version History

- **v1.0.0** (Current) - Initial release with core features
  - User authentication
  - Trip booking system
  - Payment integration
  - Admin dashboard

---

**Happy coding! 🚀**

For updates, always remember to:
```bash
git add .
git commit -m "Your changes"
git push origin main
```
