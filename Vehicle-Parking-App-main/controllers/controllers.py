from flask import Blueprint, render_template, request, redirect, url_for, session
from itertools import count
from models.db import db, UserDetails, ParkingLot, ParkingSpot, reservation, Admin
from collections import defaultdict

controllers_bp = Blueprint('controllers', __name__)  
counter = count(start=1, step=1)

@controllers_bp.route('/login')
def login():
    return render_template("login.html", user_summary_labels=[], user_summary_data=[])

@controllers_bp.route('/logout')
def logout():
    # Clear the session completely
    session.clear()
    # Redirect to login page
    return redirect(url_for('controllers.login'))

@controllers_bp.route('/newuser')
def register():
    return render_template("signup.html", user_summary_labels=[], user_summary_data=[])

@controllers_bp.route('/submit', methods=['POST'])
def submit():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check for admin login using database
    admin = Admin.query.filter_by(username=username, password=password).first()
    if admin:
        # Admin login successful - set admin session
        session['admin_logged_in'] = True
        session['admin_id'] = admin.id
        lots = ParkingLot.query.all()
        lot_spots = {lot.id: ParkingSpot.query.filter_by(lot_id=lot.id).all() for lot in lots}
        users = UserDetails.query.all()
        # Use primary location for lot_labels
        lot_labels = [lot.prime_location for lot in lots]
        revenue_data = [sum(res.cost or 0 for res in reservation.query.filter_by(lot_id=lot.id).all()) for lot in lots]
        status_data = {
            'available': [sum(1 for spot in lot_spots[lot.id] if spot.status == 'A') for lot in lots],
            'occupied': [sum(1 for spot in lot_spots[lot.id] if spot.status == 'O') for lot in lots]
        }
        return render_template(
            "admin_dash.html",
            lots=lots,
            lot_spots=lot_spots,
            users=users,
            revenue_data=revenue_data,
            lot_labels=lot_labels,
            status_data=status_data
        )
    else:
        # User login
        user = UserDetails.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id  # Store user id in session
            return redirect(url_for('controllers.user_dashboard'))
        else:
            return render_template("login.html", error="Invalid credentials. Please try again.", user_summary_labels=[], user_summary_data=[])

@controllers_bp.route('/registration', methods=['POST'])
def registration():
    # Get form data
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    fullname = request.form.get('fullname')
    address = request.form.get('address')
    pincode = request.form.get('pincode')

    # Check if user already exists (by username or email)
    existing_user = UserDetails.query.filter((UserDetails.username == username) | (UserDetails.email == email)).first()
    if existing_user:
        # User already exists, show error
        return render_template('signup.html', error='User already exists with this username or email.')

    # Create new user
    user = UserDetails(
        username=username,
        name=fullname,
        password=password,
        email=email,
        address=address,
        pincode=pincode
    )
    db.session.add(user)
    db.session.commit()
    # Redirect to login after successful signup
    return render_template('login.html', success='Registration successful! Please login.')

@controllers_bp.route('/addlot', methods=['GET', 'POST'])
def addlot():
    # Check if user is logged in as admin
    if 'admin_logged_in' not in session:
        return redirect(url_for('controllers.login'))
    
    lots = ParkingLot.query.all()
    lot_spots = {lot.id: ParkingSpot.query.filter_by(lot_id=lot.id).all() for lot in lots}
    users = UserDetails.query.all()
    lot_labels = [f"Lot #{lot.id}" for lot in lots]
    revenue_data = [sum(res.cost or 0 for res in reservation.query.filter_by(lot_id=lot.id).all()) for lot in lots]
    status_data = {'available': [sum(1 for spot in lot_spots[lot.id] if spot.status == 'A') for lot in lots],
                  'occupied': [sum(1 for spot in lot_spots[lot.id] if spot.status == 'O') for lot in lots]}
    if request.method == 'POST':
        prime_location = request.form.get('prime_location')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        price_per_hour = request.form.get('price_per_hour')
        max_spot = request.form.get('total_spots')
        new_lot = ParkingLot(
            prime_location=prime_location,
            address=address,
            pincode=pincode,
            price_per_hour=price_per_hour,
            max_spot=max_spot
        )
        db.session.add(new_lot)
        db.session.commit()
        for i in range(int(max_spot)):
            spot = ParkingSpot(lot_id=new_lot.id, status='A')
            db.session.add(spot)
        db.session.commit()
        return render_template('admin_add.html', success=True, users=users, revenue_data=revenue_data, lot_labels=lot_labels, status_data=status_data)
    return render_template('admin_add.html', users=users, revenue_data=revenue_data, lot_labels=lot_labels, status_data=status_data)

@controllers_bp.route('/admin_dashboard')
def admin_dashboard():
    # Check if user is logged in as admin
    if 'admin_logged_in' not in session:
        return redirect(url_for('controllers.login'))
    
    lots = ParkingLot.query.all()
    lot_spots = {}
    for lot in lots:
        spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        lot_spots[lot.id] = spots
    users = UserDetails.query.all()
    # Use primary location for lot_labels
    lot_labels = [lot.prime_location for lot in lots]
    revenue_data = []
    for lot in lots:
        lot_reservations = reservation.query.filter_by(lot_id=lot.id).all()
        revenue = sum(res.cost or 0 for res in lot_reservations)
        revenue_data.append(revenue)
    status_data = {'available': [], 'occupied': []}
    for lot in lots:
        available = sum(1 for spot in lot_spots[lot.id] if spot.status == 'A')
        occupied = sum(1 for spot in lot_spots[lot.id] if spot.status == 'O')
        status_data['available'].append(available)
        status_data['occupied'].append(occupied)
    return render_template("admin_dash.html", lots=lots, lot_spots=lot_spots, users=users, revenue_data=revenue_data, lot_labels=lot_labels, status_data=status_data)

@controllers_bp.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    # Check if user is logged in as admin
    if 'admin_logged_in' not in session:
        return redirect(url_for('controllers.login'))
    
    lots = ParkingLot.query.all()
    lot_spots = {lot.id: ParkingSpot.query.filter_by(lot_id=lot.id).all() for lot in lots}
    users = UserDetails.query.all()
    lot_labels = [f"Lot #{lot.id}" for lot in lots]
    revenue_data = [sum(res.cost or 0 for res in reservation.query.filter_by(lot_id=lot.id).all()) for lot in lots]
    status_data = {'available': [sum(1 for spot in lot_spots[lot.id] if spot.status == 'A') for lot in lots],
                  'occupied': [sum(1 for spot in lot_spots[lot.id] if spot.status == 'O') for lot in lots]}
    lot = ParkingLot.query.get(lot_id)
    if request.method == 'POST':
        # Update lot details from form
        lot.prime_location = request.form.get('prime_location')
        lot.address = request.form.get('address')
        lot.pincode = request.form.get('pincode')
        lot.price_per_hour = request.form.get('price_per_hour')
        new_max_spot = int(request.form.get('total_spots'))
        old_max_spot = lot.max_spot
        # Count occupied spots
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        occupied_count = sum(1 for s in spots if s.status == 'O')
        if new_max_spot < occupied_count:
            return render_template('admin_edit.html', lot=lot, error='Updated spot count is less than the number of occupied spots!', users=users, revenue_data=revenue_data, lot_labels=lot_labels, status_data=status_data)
        # If increasing, add new available spots
        if new_max_spot > old_max_spot:
            for _ in range(new_max_spot - old_max_spot):
                db.session.add(ParkingSpot(lot_id=lot_id, status='A'))
        # If decreasing, only allow if all to-be-removed spots are available
        elif new_max_spot < old_max_spot:
            # Get all spots, remove the last N if they are available
            to_remove = spots[new_max_spot:]
            if any(s.status == 'O' for s in to_remove):
                return render_template('admin_edit.html', lot=lot, error='Cannot remove occupied spots!', users=users, revenue_data=revenue_data, lot_labels=lot_labels, status_data=status_data)
            for s in to_remove:
                db.session.delete(s)
        lot.max_spot = new_max_spot
        db.session.commit()
        return render_template('admin_edit.html', lot=lot, success=True, users=users, revenue_data=revenue_data, lot_labels=lot_labels, status_data=status_data)
    return render_template('admin_edit.html', lot=lot, users=users, revenue_data=revenue_data, lot_labels=lot_labels, status_data=status_data)

@controllers_bp.route('/delete_lot/<int:lot_id>', methods=['GET', 'POST'])
def delete_lot(lot_id):
    # Check if user is logged in as admin
    if 'admin_logged_in' not in session:
        return redirect(url_for('controllers.login'))
    
    lots = ParkingLot.query.all()
    lot_spots = {lot.id: ParkingSpot.query.filter_by(lot_id=lot.id).all() for lot in lots}
    users = UserDetails.query.all()
    lot_labels = [f"Lot #{lot.id}" for lot in lots]
    revenue_data = [sum(res.cost or 0 for res in reservation.query.filter_by(lot_id=lot.id).all()) for lot in lots]
    status_data = {'available': [sum(1 for spot in lot_spots[lot.id] if spot.status == 'A') for lot in lots],
                  'occupied': [sum(1 for spot in lot_spots[lot.id] if spot.status == 'O') for lot in lots]}
    lot = ParkingLot.query.get(lot_id)
    if request.method == 'POST':
        # Check if all spots are available
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        all_available = all(spot.status == 'A' for spot in spots)
        if all_available:
            # Delete all spots first, then the lot
            for spot in spots:
                db.session.delete(spot)
            db.session.delete(lot)
            db.session.commit()
            # Show a success alert and redirect to dashboard
            return render_template('admin_dash.html', lots=ParkingLot.query.all(), lot_spots={l.id: ParkingSpot.query.filter_by(lot_id=l.id).all() for l in ParkingLot.query.all()}, delete_success=True, users=users, revenue_data=revenue_data, lot_labels=lot_labels, status_data=status_data)
        else:
            # Show an error alert
            return render_template('admin_delete.html', lot=lot, error="Cannot delete: Some spots are still occupied.", users=users, revenue_data=revenue_data, lot_labels=lot_labels, status_data=status_data)
    return render_template('admin_delete.html', lot=lot, users=users, revenue_data=revenue_data, lot_labels=lot_labels, status_data=status_data)

@controllers_bp.route('/user_dashboard')
def user_dashboard():
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('controllers.login'))
    
    # Always fetch the latest reservations and spot statuses for the user
    search_query = request.args.get('search', '')
    lots = []
    lot_spots = {}
    if search_query:
        all_lots = ParkingLot.query.all()
        for lot in all_lots:
            if (search_query.lower() in lot.prime_location.lower() or 
                search_query in str(lot.pincode)):
                lots.append(lot)
        for lot in lots:
            spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
            available_spots = sum(1 for spot in spots if spot.status == 'A')
            lot_spots[lot.id] = {'total': len(spots), 'available': available_spots}
    # Get all reservations for the user, most recent first
    all_reservations = reservation.query.filter_by(user_id=user_id).order_by(reservation.id.desc()).all()
    # Prepare summary data for the user
    from collections import Counter
    lot_counts = Counter(res.lot_id for res in all_reservations)
    user_summary_labels = [f"Lot #{lid}" for lid in lot_counts.keys()]
    user_summary_data = list(lot_counts.values())
    # Pass all reservations directly to the template for full history
    all_lots_for_history = ParkingLot.query.all()
    lot_id_to_location = {lot.id: lot.prime_location for lot in all_lots_for_history}
    user_summary_labels = [lot_id_to_location.get(lid, f"Lot #{lid}") for lid in lot_counts.keys()]
    user_summary_data = list(lot_counts.values())
    return render_template('user_dash.html', 
                         lots=lots, 
                         lot_spots=lot_spots, 
                         search_query=search_query,
                         reservations=all_reservations,
                         all_lots=all_lots_for_history,
                         user_id=user_id,
                         user_summary_labels=user_summary_labels,
                         user_summary_data=user_summary_data)

@controllers_bp.route('/book_parking/<int:lot_id>', methods=['GET', 'POST'])
def book_parking(lot_id):
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('controllers.login'))
    
    lot = ParkingLot.query.get(lot_id)
    all_reservations = reservation.query.filter_by(user_id=user_id).order_by(reservation.id.desc()).all()
    all_lots_for_history = ParkingLot.query.all()
    lot_id_to_location = {lot.id: lot.prime_location for lot in all_lots_for_history}
    from collections import Counter
    lot_counts = Counter(res.lot_id for res in all_reservations)
    user_summary_labels = [lot_id_to_location.get(lid, f"Lot #{lid}") for lid in lot_counts.keys()]
    user_summary_data = list(lot_counts.values())
    if request.method == 'POST':
        vehicle_number = request.form.get('vehicle_number')
        user_id = session.get('user_id')

        # Find first available spot that does not have an active reservation
        available_spot = None
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        for spot in spots:
            # Check if this spot is available and has no active reservation
            active_res = reservation.query.filter_by(spot_id=spot.id, leaving_time=None).first()
            if spot.status == 'A' and not active_res:
                available_spot = spot
                break
        
        # Additional check: make sure we don't have multiple active reservations for the same spot
        if available_spot:
            existing_active = reservation.query.filter_by(spot_id=available_spot.id, leaving_time=None).first()
            if existing_active:
                return render_template('user_book.html', lot=lot, error='This spot is already reserved!', user_summary_labels=user_summary_labels, user_summary_data=user_summary_data)
        if not available_spot:
            return render_template('user_book.html', lot=lot, error='No spots available or spot already reserved!', user_summary_labels=user_summary_labels, user_summary_data=user_summary_data)

        # Mark spot as occupied
        available_spot.status = 'O'

        from datetime import datetime
        new_reservation = reservation(
            user_id=user_id,
            spot_id=available_spot.id,
            lot_id=lot_id,
            vehicle_number=vehicle_number,
            parking_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            leaving_time=None,
            cost=0
        )
        db.session.add(new_reservation)
        db.session.commit()

        return render_template('user_book.html', lot=lot, success='Parking booked successfully!', user_summary_labels=user_summary_labels, user_summary_data=user_summary_data)
    return render_template('user_book.html', lot=lot, user_summary_labels=user_summary_labels, user_summary_data=user_summary_data)

@controllers_bp.route('/park_out/<int:res_id>')
def park_out(res_id):
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('controllers.login'))
    
    # Get reservation and record park out timestamp
    res = reservation.query.get(res_id)
    if res:
        # Record park out timestamp
        from datetime import datetime
        res.park_out_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.session.commit()
    
    return redirect(url_for('controllers.user_dashboard'))

@controllers_bp.route('/release_spot/<int:res_id>')
def release_spot(res_id):
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('controllers.login'))
    
    res = reservation.query.get(res_id)
    if res:
        spot = ParkingSpot.query.get(res.spot_id)
        if spot:
            spot.status = 'A'
            from datetime import datetime
            leaving_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            res.leaving_time = leaving_time  # Ensure it's a valid timestamp string
            db.session.commit()
    return redirect(url_for('controllers.user_dashboard'))

@controllers_bp.route('/release_parking/<int:res_id>', methods=['GET', 'POST'])
def release_parking(res_id):
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('controllers.login'))
    
    from datetime import datetime
    res = reservation.query.get(res_id)
    if not res:
        return redirect(url_for('controllers.user_dashboard'))
    
    lot = ParkingLot.query.get(res.lot_id)
    spot = ParkingSpot.query.get(res.spot_id)
    now = datetime.now()
    releasing_time = now.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        fmt = '%Y-%m-%d %H:%M:%S'
        start = datetime.strptime(res.parking_time, fmt)
        duration = (now - start).total_seconds() / 3600
        hours = max(1, int(duration + 0.999))
    except Exception:
        hours = 1
    
    total_cost = (lot.price_per_hour if lot else 0) * hours
    
    # Prepare summary data for the user
    user_id = res.user_id if res else 1
    all_reservations = reservation.query.filter_by(user_id=user_id).order_by(reservation.id.desc()).all()
    all_lots_for_history = ParkingLot.query.all()
    lot_id_to_location = {lot.id: lot.prime_location for lot in all_lots_for_history}
    from collections import Counter
    lot_counts = Counter(r.lot_id for r in all_reservations)
    user_summary_labels = [lot_id_to_location.get(lid, f"Lot #{lid}") for lid in lot_counts.keys()]
    user_summary_data = list(lot_counts.values())

    if request.method == 'POST':
        # Update spot status
        if spot:
            spot.status = 'A'
        
        # Update reservation - ensure leaving_time is a valid timestamp string
        res.leaving_time = releasing_time  # This should be a valid timestamp string
        res.cost = total_cost
        
        # Commit all changes
        db.session.commit()
        
        return redirect(url_for('controllers.user_dashboard'))
    
    return render_template('user_release.html',
        res_id=res.id,
        spot_id=res.spot_id,
        vehicle_number=res.vehicle_number,
        parking_time=res.parking_time,
        releasing_time=releasing_time,
        total_cost=total_cost,
        user_summary_labels=user_summary_labels,
        user_summary_data=user_summary_data)

@controllers_bp.route('/occupied_details/<int:spot_id>')
def occupied_details(spot_id):
    # Check if user is logged in as admin
    if 'admin_logged_in' not in session:
        return redirect(url_for('controllers.login'))
    
    from datetime import datetime
    lots = ParkingLot.query.all()
    lot_spots = {lot.id: ParkingSpot.query.filter_by(lot_id=lot.id).all() for lot in lots}
    users = UserDetails.query.all()
    lot_labels = [f"Lot #{lot.id}" for lot in lots]
    revenue_data = [sum(res.cost or 0 for res in reservation.query.filter_by(lot_id=lot.id).all()) for lot in lots]
    status_data = {'available': [sum(1 for spot in lot_spots[lot.id] if spot.status == 'A') for lot in lots],
                  'occupied': [sum(1 for spot in lot_spots[lot.id] if spot.status == 'O') for lot in lots]}
    res = reservation.query.filter_by(spot_id=spot_id).order_by(reservation.id.desc()).first()
    lot = ParkingLot.query.get(res.lot_id) if res else None
    user = UserDetails.query.get(res.user_id) if res else None
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    # Calculate estimated price
    estimated_price = 0
    if res and lot:
        try:
            fmt = '%Y-%m-%d %H:%M:%S'
            start = datetime.strptime(res.parking_time, fmt)
            duration = (now - start).total_seconds() / 3600
            hours = max(1, int(duration + 0.999))
            estimated_price = lot.price_per_hour * hours
        except Exception:
            estimated_price = lot.price_per_hour
    return render_template('admin_occupieddetails.html', res=res, lot=lot, user=user, estimated_price=estimated_price, checked_time=now_str, users=users, revenue_data=revenue_data, lot_labels=lot_labels, status_data=status_data)