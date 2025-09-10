from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

class UserDetails(db.Model):
    __tablename__ = 'user_details'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    address = db.Column(db.String(100))
    pincode = db.Column(db.Integer)

class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'
    id = db.Column(db.Integer, primary_key=True)
    prime_location = db.Column(db.String(100))
    address = db.Column(db.String(100))
    pincode = db.Column(db.Integer)
    price_per_hour = db.Column(db.Integer)
    max_spot = db.Column(db.Integer)

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'))
    status = db.Column(db.String(1), default='A')  # 'A' for available, 'O' for occupied

class reservation(db.Model):
    __tablename__='reservation'
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user_details.id'))
    spot_id=db.Column(db.Integer,db.ForeignKey('parking_spot.id'))
    lot_id=db.Column(db.Integer,db.ForeignKey('parking_lot.id'))
    vehicle_number=db.Column(db.String(20))  # Store vehicle number
    parking_time=db.Column(db.String(100))
    park_out_time=db.Column(db.String(100))  # Track when user parks out
    leaving_time=db.Column(db.String(100))
    cost=db.Column(db.Integer)