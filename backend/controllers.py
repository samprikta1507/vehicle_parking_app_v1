# App routes
from flask import Flask,render_template,request,redirect,url_for,flash, session,jsonify
from flask import current_app as app
from datetime import datetime, timedelta
from .models import *
import math
from app import login_manager
from flask_login import login_user, login_required, logout_user, current_user

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        uname = request.form.get("user_name")
        pwd = request.form.get("password")
        if not uname or not pwd:
            flash("Both email and password are required.", "error")
            return render_template("login.html", msg="")

        if "@" not in uname or "." not in uname:
            flash("Invalid email format.", "error")
            return render_template("login.html", msg="")

        usr = User.query.filter_by(email=uname, password=pwd).first()
        if usr:
            login_user(usr)
            session.pop('_flashes', None)
            flash("Login successful!", "success")
            if usr.role == 0:
                return redirect(url_for("admin_dashboard", name=usr.email))
            else:
                return redirect(url_for("user_dashboard", name=usr.email))
        else:
            flash("Invalid credentials. Please try again.", "error")
    return render_template("login.html",msg="")


@app.route("/register",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password") #pt
        full_name=request.form.get("full_name")
        address=request.form.get("address")
        pin_code=request.form.get("pin_code")
        if not all([uname, pwd, full_name, address, pin_code]):
            flash("All fields are required.", "error")
            return redirect(url_for("signup"))

        if "@" not in uname or "." not in uname:
            flash("Invalid email format.", "error")
            return redirect(url_for("signup"))

        if len(pwd) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("signup"))

        if not pin_code.isdigit() or len(pin_code) != 6:
            flash("Pin code must be a 6-digit number.", "error")
            return redirect(url_for("signup"))
        usr=User.query.filter_by(email=uname).first()
        if usr:
            flash("Email already registered.", "warning")
            return redirect(url_for("signup"))
        new_usr=User(email=uname,password=pwd,full_name=full_name,address=address,pin_code=pin_code)
        db.session.add(new_usr)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")        
        return redirect(url_for("signin"))
    return render_template("signup.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear() 
    flash("You have been logged out.", "info")
    return redirect(url_for("signin"))


# common route for admin dashboard
@app.route("/admin/<name>")
@login_required
def admin_dashboard(name):
    if current_user.role != 0:
        flash("Unauthorized access to admin dashboard.", "danger")
        return redirect(url_for("user_dashboard", name=current_user.email))
    parking_lots=get_parking_lots()
    
    for parking_lot in parking_lots:
        parking_lot.spots = Parking_spot.query.filter_by(lot_id=parking_lot.id).all()
    return render_template("admin_dashboard.html",name=name,parking_lots=parking_lots)

# common route for user dashboard
@app.route("/user/<name>")
@login_required
def user_dashboard(name):
    if current_user.role != 1:
        flash("Unauthorized access to user dashboard.", "danger")
        return redirect(url_for("admin_dashboard", name=current_user.email))
    user = User.query.filter_by(email=name).first()
    if not user:
        return "User not found", 404

    reservations = Reservation.query.filter_by(user_id=user.id).order_by(Reservation.park_time.desc()).limit(5).all()
    current_time = datetime.now()
    active_reservations = Reservation.query.filter(Reservation.user_id == user.id,Reservation.end_time > datetime.utcnow()).order_by(Reservation.park_time.desc()).all()
    ended_reservations = Reservation.query.filter(Reservation.user_id == user.id,Reservation.end_time <= datetime.utcnow()).order_by(Reservation.park_time.desc()).all()

    # Search logic
    search_query = request.form.get("location") if request.method == "POST" else "place name"
    parking_lots = Parking_lot.query.filter(Parking_lot.address.ilike(f"%{search_query}%")).all()

    # Add available spot count to each lot

    all_lots = Parking_lot.query.all()
    available_data = []
    for lot in all_lots:
        total_spots = len(lot.spots)
        available_spots = len([s for s in lot.spots if s.status == 'A'])
        available_data.append({
            "id": lot.id,
            "name": lot.name,
            "address": lot.address,
            "available_spots": available_spots,
            "total_spots": total_spots
        })

    return render_template("user_dashboard.html",name=name,reservations=reservations,search_query=search_query,parking_lots=parking_lots, available_data=available_data,now=current_time,active_reservations=active_reservations, ended_reservations=ended_reservations)

@app.route("/parking_lot/<name>",methods=["GET","POST"])
@login_required
def add_parking_lot(name):
    if request.method=="POST":
        lname=request.form.get("name")
        address=request.form.get("address")
        pin_code=request.form.get("pin_code")
        price=request.form.get("price")
        max_spots=int(request.form.get("max_spots"))
        if not all([lname, address, pin_code, price, max_spots]):
            flash("All fields are required.", "error")
            return render_template("add_parking_lot.html", name=name)

        if not pin_code.isdigit() or len(pin_code) != 6:
            flash("Pin code must be a 6-digit number.", "error")
            return render_template("add_parking_lot.html", name=name)

        if not price.isdigit() or int(price) < 0:
            flash("Price must be a non-negative number.", "error")
            return render_template("add_parking_lot.html", name=name)

        if not max_spots.isdigit() or int(max_spots) <= 0:
            flash("Max spots must be a positive number.", "error")
            return render_template("add_parking_lot.html", name=name)

        price = int(price)
        max_spots = int(max_spots)
        new_lot=Parking_lot(name=lname,address=address,pin_code=pin_code,price=price,max_spots=max_spots)
        db.session.add(new_lot)
        db.session.commit()

         # Auto-generate parking spots after lot is added
        for _ in range(max_spots):
            new_spot = Parking_spot(
                lot_id=new_lot.id,
                status='A'  # A = Available
            )
            db.session.add(new_spot)

        db.session.commit()  # Commit the spots to the DB
        print(f"Generated {max_spots} spots for lot id {new_lot.id}")
        flash(f"Parking lot '{lname}' added successfully with {max_spots} spots.", "success")

        return redirect(url_for("admin_dashboard",name=name))


    return render_template("add_parking_lot.html",name=name)

# for edit parking lots
@app.route("/edit_parking_lot/<int:lot_id>/<name>", methods=["GET", "POST"])
@login_required
def edit_parking_lot(lot_id, name):
    lot = Parking_lot.query.get_or_404(lot_id)
    
    if request.method == "POST":
        lot.name = request.form.get("name")
        lot.address = request.form.get("address")
        lot.pin_code = request.form.get("pin_code")
        lot.price = request.form.get("price")

        new_max_spots = int(request.form.get("max_spots"))
        old_spots = Parking_spot.query.filter_by(lot_id=lot.id).all()
        current_spots = len(old_spots)

        if new_max_spots > current_spots:
            for _ in range(new_max_spots - current_spots):
                new_spot = Parking_spot(lot_id=lot.id, status='A')
                db.session.add(new_spot)
        elif new_max_spots < current_spots:
            # delete extra spots
            to_delete = old_spots[new_max_spots:]
            for s in to_delete:
                db.session.delete(s)

        lot.max_spots = new_max_spots
        db.session.commit()
        flash("Parking lot updated successfully.", "success")
        return redirect(url_for("admin_dashboard", name=name))

    return render_template("edit_parking_lot.html", lot=lot, name=name)

# for delete parking lots
@app.route("/delete_parking_lot/<int:lot_id>/<name>")
@login_required
def delete_parking_lot(lot_id, name):
    lot = Parking_lot.query.get_or_404(lot_id)
    db.session.delete(lot)  # Will also delete spots due to cascade
    db.session.commit()
    flash("Parking lot deleted successfully.", "info")
    return redirect(url_for("admin_dashboard", name=name))

# for managing spots
@app.route("/manage_spot/<int:spot_id>", methods=["POST"])
@login_required
def manage_spot(spot_id):
    spot = Parking_spot.query.get(spot_id)
    if not spot:
        return "Spot not found", 404

    # Toggle the spot status as an example (A <-> O)
    if spot.status == 'A':
        spot.status = 'O'
    else:
        spot.status = 'A'

    db.session.commit()

    name = request.args.get("name")
    flash("Spot status updated.", "info")
    return redirect(url_for("admin_dashboard", name=name))  # or use dynamic name if needed


# for view spots


@app.route("/view_spot/<int:spot_id>/<int:lot_id>/<name>")
@login_required
def view_spot(spot_id, lot_id, name):
    spot = Parking_spot.query.get_or_404(spot_id)
    return render_template("view_spot.html", spot=spot, lot_id=lot_id, name=name)

# for delete spot
@app.route("/delete_spot/<int:spot_id>/<int:lot_id>/<name>")
@login_required
def delete_spot(spot_id, lot_id, name):
    spot = Parking_spot.query.get_or_404(spot_id)

    if spot.status != 'A':
        flash("Cannot delete an occupied/reserved spot.", "warning")
        return redirect(url_for("view_spot", lot_id=lot_id, name=name))

    db.session.delete(spot)
    lot = Parking_lot.query.get_or_404(lot_id)
    if lot.max_spots > 0:
        lot.max_spots -= 1
    db.session.commit()
    flash("Spot deleted successfully.", "info")   
    return redirect(url_for("admin_dashboard", name=name))

# other supported function
def get_parking_lots():
    parking_lots=Parking_lot.query.all()
    return parking_lots



# done the auth today too

@app.route("/admin/<name>/users")
@login_required
def admin_users(name):
    users = User.query.all()
    return render_template("users.html", name=name, users=users)

@app.route("/admin/<name>/summary")
@login_required
def admin_summary(name):
    reservations = Reservation.query.order_by(Reservation.park_time.desc()).all()


    for r in reservations:
        if r.park_time and r.release_time:
            duration_sec = (r.release_time - r.park_time).total_seconds()
            minutes = duration_sec / 60

            price_per_hour = r.parking_lot.price 
            cost_per_minute = price_per_hour / 60

            r.cost = round(minutes * cost_per_minute, 2)
        else:
            r.cost = 0  
    return render_template("admin_summary.html", name=name,reservations=reservations)

# for admin summary charts

@app.route('/admin/summary/chart')
@login_required
def admin_summary_chart():
    reservations = Reservation.query.all()

    daily_counts = {}
    for r in reservations:
        date = r.start_time.strftime("%Y-%m-%d")
        daily_counts[date] = daily_counts.get(date, 0) + 1

    data = [{"date": date, "count": count} for date, count in sorted(daily_counts.items())]
    return jsonify(data)
@app.route('/admin/revenue/chart')
@login_required
def admin_revenue_chart():
    reservations = Reservation.query.all()
    revenue = {}

    for r in reservations:
        lot_name = r.parking_lot.name
        revenue[lot_name] = revenue.get(lot_name, 0) + (r.cost or 0)

    data = [{"lot": lot, "revenue": rev} for lot, rev in revenue.items()]
    return jsonify(data)



@app.route("/user/<name>/summary")
@login_required
def user_summary(name):
    user = User.query.filter_by(email=name).first()
    if not user:
        return redirect(url_for('login'))

    history = Reservation.query.filter_by(user_id=user.id)\
        .filter(Reservation.park_time.isnot(None))\
        .filter(Reservation.release_time.isnot(None))\
        .order_by(Reservation.park_time.desc()).all()

    total_minutes = 0
    total_cost = 0

    for reservation in history:
        if reservation.park_time and reservation.release_time:
            duration_sec = (reservation.release_time - reservation.park_time).total_seconds()
            minutes = duration_sec / 60
            total_minutes += minutes

            price_per_hour = reservation.parking_lot.price 
            cost_per_minute = price_per_hour / 60
            reservation.cost = round(minutes * cost_per_minute, 2)
            total_cost += reservation.cost

    return render_template("user_summary.html", user=user, name=name, history=history, total_minutes=int(total_minutes), total_cost=round(total_cost, 2))

# for user summary chart
@app.route('/user/history/chart')
@login_required
def user_history_chart():
    user_id = current_user.id
    reservations = Reservation.query.filter_by(user_id=user_id).all()

    data = [
        {
            "date": r.park_time.strftime("%Y-%m-%d") if r.park_time else "N/A",
            "duration": int((r.release_time - r.park_time).total_seconds() // 60)
        }
        for r in reservations if r.park_time and r.release_time
    ]
    return jsonify(data)

@app.route('/user/spot-usage/chart')
@login_required
def user_spot_usage_chart():
    user_id = current_user.id
    reservations = Reservation.query.filter_by(user_id=user_id).all()
    
    spot_usage = {}
    for r in reservations:
        spot_id = f"Spot {r.parking_spot.id}"
        spot_usage[spot_id] = spot_usage.get(spot_id, 0) + 1

    data = [{"spot": spot, "count": count} for spot, count in spot_usage.items()]
    return jsonify(data)

# for book spot

@app.route('/book_spot/<int:lot_id>/<string:name>', methods=['POST'])
@login_required
def book_spot(lot_id, name):
    user = User.query.filter_by(email=name).first()
    if not user:
        return redirect(url_for('user_dashboard', name=name))
    
    lot = Parking_lot.query.get_or_404(lot_id)

    start_time_str = request.form['start_time']
    duration = int(request.form['duration'])

    start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
    end_time = start_time + timedelta(hours=duration)


    spot = Parking_spot.query.filter_by(lot_id=lot_id, status='A').first()
    if not spot:
        return redirect(url_for('user_dashboard', name=name))

    reservation = Reservation(
        start_time=start_time,
        end_time=end_time,
        park_time=None,  
        release_time=None, 
        lot_id=lot_id,
        spot_id=spot.id,
        user_id=user.id
    )


    spot.status = 'R'  
    
    db.session.add(reservation)
    db.session.commit()
    flash("Booked spot successful.", "success")
    return redirect(url_for('user_dashboard', name=name))



# for start parking in spot
@app.route('/start_parking/<int:reservation_id>/<string:name>', methods=['POST'])
@login_required
def start_parking(reservation_id, name):
    reservation = Reservation.query.get_or_404(reservation_id)

    if reservation.park_time is None:
        reservation.park_time = datetime.now()

        spot = Parking_spot.query.get(reservation.spot_id)
        spot.status = 'O'  
        db.session.commit()
    flash("car parked.", "success")
    return redirect(url_for('user_dashboard', name=name))

# for relese spot
@app.route('/release_reservation/<int:reservation_id>/<string:name>', methods=['POST'])
@login_required
def release_reservation(reservation_id, name):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    if reservation.park_time is None:
        return redirect(url_for('user_dashboard', name=name))
    
    if reservation.release_time is not None:
        return redirect(url_for('user_dashboard', name=name))

    reservation.release_time = datetime.now()

    duration_sec = (reservation.release_time - reservation.park_time).total_seconds()
    hours = math.ceil(duration_sec / 3600)
    
    rate = reservation.parking_lot.price
    reservation.cost = hours * rate

    spot = Parking_spot.query.get(reservation.spot_id)
    spot.status = 'A' 

    db.session.commit()
    flash("Released spot successful.", "success")

    return redirect(url_for('user_dashboard', name=name))



# for edit ptofile for both user and admin dashboard 

@app.route('/edit_profile/<string:name>', methods=['GET', 'POST'])
@login_required
def edit_profile(name):
    user = User.query.filter_by(email=name).first_or_404()
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("signin"))
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')

        if not full_name or not address or not pin_code.isdigit():
            return redirect(url_for('edit_profile', name=name))
        
        if not pin_code.isdigit() or len(pin_code) != 6:
            flash("Pin code must be a 6-digit number.", "error")
            return redirect(url_for('edit_profile', name=name))

        user.full_name = full_name
        user.address = address
        user.pin_code = int(pin_code)
        db.session.commit()
        flash("Profile updated successfully.", "success")
        if user.role == 0:
            return redirect(url_for('admin_dashboard', name=name))
        else:
            return redirect(url_for('user_dashboard', name=name))

    return render_template('edit_profile.html', user=user, name=name)

# for search funtion in user_dashboard 
@app.route("/user/<name>/dashboard/search", methods=["GET"])
@login_required
def user_dashboard_search(name):
    user = User.query.filter_by(email=name).first()
    if not user:
        return redirect(url_for('signin'))

    search_query = request.args.get("location", "").strip().lower()

    now = datetime.now()

    active_reservations = Reservation.query.filter_by(user_id=user.id)\
        .filter(Reservation.release_time.is_(None))\
        .order_by(Reservation.park_time.desc()).all()

    parking_lots = Parking_lot.query.all()
    filtered_lots = []
    for lot in parking_lots:
        if search_query in lot.name.lower() or search_query in lot.address.lower():
            total_spots = lot.max_spots
            occupied_spots = Parking_spot.query.filter_by(lot_id=lot.id, status="occupied").count()
            lot.available_spots = total_spots - occupied_spots
            lot.total_spots = total_spots
            filtered_lots.append(lot)

    return render_template("user_dashboard.html", name=name, active_reservations=active_reservations, available_data=filtered_lots, now=now, search_query=search_query)

# for search function in admin_dashboard

@app.route("/admin/<name>/dashboard/search")
@login_required
def admin_dashboard_search(name):
    filter_by = request.args.get("filter_by")
    query = request.args.get("query")

    parking_lots = []

    if filter_by == "location":
        parking_lots = Parking_lot.query.filter(Parking_lot.address.ilike(f"%{query}%")).all()

    elif filter_by == "name":
        parking_lots = Parking_lot.query.filter(Parking_lot.name.ilike(f"%{query}%")).all()

    elif filter_by == "user":
        parking_lots = (
            db.session.query(Parking_lot)
            .join(Parking_spot)
            .join(Reservation)
            .filter(Reservation.user_id.ilike(f"%{query}%"))
            .distinct()
            .all()
        )

    return render_template("admin_dashboard.html", parking_lots=parking_lots, name=name)

