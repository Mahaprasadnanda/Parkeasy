# Parking Management System

A comprehensive web-based parking management solution built with Flask, featuring real-time spot monitoring, automated billing, and intuitive dashboards for both administrators and users.

## 🚀 Features

### For Users
- **User Registration & Authentication**: Secure login system with session management
- **Real-time Parking Booking**: Book available spots with instant confirmation
- **Smart Spot Release**: Automatic cost calculation and spot release functionality
- **Complete Parking History**: View all past parking sessions with detailed information
- **Personalized Dashboard**: Interactive summary charts showing parking statistics
- **Location-based Display**: Shows primary location names instead of lot numbers

### For Administrators
- **Comprehensive Dashboard**: Real-time overview of all parking lots and spots
- **Parking Lot Management**: Add, edit, and delete parking lots with ease
- **User Management**: View all registered users and their details
- **Revenue Analytics**: Interactive pie charts showing revenue per parking lot
- **Occupancy Monitoring**: Bar charts displaying available vs. occupied spots
- **Detailed Spot Information**: Click on occupied spots to view user details (name, address)
- **Secure Admin Access**: Database-backed authentication system

## 🛠️ Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **JavaScript**: Chart.js for data visualization
- **Templates**: Jinja2 templating engine
- **Authentication**: Session-based security

## 📁 Project Structure

```
Vehicle/
├── app.py                          # Main Flask application entry point
├── controllers/
│   └── controllers.py              # All route handlers and business logic
├── models/
│   └── db.py                       # Database models and schema
├── templates/                      # HTML templates
│   ├── admin_dash.html            # Admin dashboard
│   ├── admin_add.html             # Add parking lot
│   ├── admin_edit.html            # Edit parking lot
│   ├── admin_delete.html          # Delete parking lot
│   ├── admin_occupieddetails.html # Occupied spot details
│   ├── user_dash.html             # User dashboard
│   ├── user_book.html             # Book parking spot
│   ├── user_release.html          # Release parking spot
│   ├── login.html                 # Login page
│   ├── signup.html                # Registration page
│   └── index.html                 # Landing page
├── static/                        # Static assets
│   ├── css/                       # Stylesheets
│   └── js/                        # JavaScript files
└── README.md                      # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Vehicle
   ```

2. **Install dependencies**
   ```bash
   pip install flask flask-sqlalchemy
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`
   - Default admin credentials: `admin@123` / `admin1234`

## 📊 Database Schema

The system uses a relational database with the following key entities:

- **UserDetails**: User registration information
- **Admin**: Administrator credentials
- **ParkingLot**: Parking lot information with primary locations
- **ParkingSpot**: Individual parking spots within lots
- **reservation**: Booking records with timestamps and costs

## 🔐 Security Features

- **Session Management**: Secure user sessions with automatic timeout
- **Route Protection**: All admin and user routes require authentication
- **Secure Logout**: Prevents back-button navigation to protected pages
- **Database-backed Authentication**: Admin credentials stored securely in database

## 📈 Key Features Implementation

### Real-time Spot Monitoring
- Automatic status updates when spots are booked/released
- Visual indicators for available/occupied spots
- Click-to-view detailed information for occupied spots

### Automated Billing System
- Cost calculation based on parking duration
- Automatic price computation upon spot release
- Complete billing history for users

### Data Visualization
- **Admin Charts**: Revenue distribution and occupancy statistics
- **User Charts**: Personal parking summary and usage patterns
- **Interactive Modals**: Responsive popups for detailed information

### User Experience
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Intuitive Navigation**: Clear navigation bars with logical grouping
- **Real-time Updates**: Instant feedback for all user actions

## 🎯 Usage Guide

### For Users
1. Register a new account or login with existing credentials
2. View available parking spots on the dashboard
3. Book a spot by clicking on available locations
4. Release your spot when leaving (automatic cost calculation)
5. View complete parking history and personal statistics

### For Administrators
1. Login with admin credentials
2. Monitor all parking lots and spots from the dashboard
3. Add new parking lots or modify existing ones
4. View detailed user information and parking statistics
5. Access revenue and occupancy analytics through summary charts

## 🔧 Configuration

The application can be customized by modifying:
- Database configuration in `models/db.py`
- Admin credentials in `app.py`
- Styling in CSS files
- Chart configurations in JavaScript

## 📝 License

This project is developed for educational and commercial parking management purposes.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

**Note**: This system is designed for local deployment and does not use external APIs. All functionality is self-contained within the Flask application. 