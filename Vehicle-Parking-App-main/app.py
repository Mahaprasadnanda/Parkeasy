from flask import Flask, render_template
from controllers.controllers import controllers_bp  
from models.db import db 
from models.db import UserDetails, ParkingLot, ParkingSpot, reservation, Admin  

app = Flask(__name__)
app.secret_key = '4544adswqe465w7997dsfr7'  # Set a strong secret key for session
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    
    # Create default admin user if it doesn't exist
    default_admin = Admin.query.filter_by(username='admin@123').first()
    if not default_admin:
        admin = Admin(
            username='admin@123',
            password='admin1234',
            name='System Administrator',
            email='admin@parkeasy.com'
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created successfully!")

app.register_blueprint(controllers_bp) 

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)

