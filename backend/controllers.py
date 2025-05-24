# App routes
from flask import Flask,render_template,request,redirect,url_for
from flask import current_app as app
from datetime import datetime, timedelta
from .models import *

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login",methods=["GET","POST"])
def signin():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password")
        usr=User.query.filter_by(email=uname,password=pwd).first()
        if usr and usr.role==0: #Existed and admin
            return redirect(url_for("admin_dashboard",name=uname))
        elif usr and usr.role==1: #Existed and normal user
            return redirect(url_for("user_dashboard",name=uname))
        else:
            return render_template("login.html",msg="Invalid user...!!!")
    return render_template("login.html",msg="")


@app.route("/register",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password") #pt
        full_name=request.form.get("full_name")
        address=request.form.get("address")
        pin_code=request.form.get("pin_code")
        usr=User.query.filter_by(email=uname).first()
        if usr:
            return render_template("signup.html",msg="Sorry, this mail already registered!!!")
        new_usr=User(email=uname,password=pwd,full_name=full_name,address=address,pin_code=pin_code)
        db.session.add(new_usr)
        db.session.commit()
        return render_template("login.html",msg="Registration successful, try login now!")
    return render_template("signup.html",msg="")

#def my_encrypt():
    # code here

# common route for admin dashboard
@app.route("/admin/<name>")
def admin_dashboard(name):
    parking_lots=get_parking_lots()
    
    for parking_lot in parking_lots:
        parking_lot.spots = Parking_spot.query.filter_by(lot_id=parking_lot.id).all()
    return render_template("admin_dashboard.html",name=name,parking_lots=parking_lots)

# common route for user dashboard
@app.route("/user/<name>")
def user_dashboard(name):
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
def add_parking_lot(name):
    if request.method=="POST":
        lname=request.form.get("name")
        address=request.form.get("address")
        pin_code=request.form.get("pin_code")
        price=request.form.get("price")
        max_spots=int(request.form.get("max_spots"))

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

        return redirect(url_for("admin_dashboard",name=name))


    return render_template("add_parking_lot.html",name=name)

# for edit parking lots
@app.route("/edit_parking_lot/<int:lot_id>/<name>", methods=["GET", "POST"])
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

        return redirect(url_for("admin_dashboard", name=name))

    return render_template("edit_parking_lot.html", lot=lot, name=name)

# for delete parking lots
@app.route("/delete_parking_lot/<int:lot_id>/<name>")
def delete_parking_lot(lot_id, name):
    lot = Parking_lot.query.get_or_404(lot_id)
    db.session.delete(lot)  # Will also delete spots due to cascade
    db.session.commit()
    return redirect(url_for("admin_dashboard", name=name))

# for managing spots
@app.route("/manage_spot/<int:spot_id>", methods=["POST"])
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
    return redirect(url_for("admin_dashboard", name=name))  # or use dynamic name if needed


# for view spots


@app.route("/view_spot/<int:spot_id>/<int:lot_id>/<name>")
def view_spot(spot_id, lot_id, name):
    spot = Parking_spot.query.get_or_404(spot_id)
    return render_template("view_spot.html", spot=spot, lot_id=lot_id, name=name)

# for delete spot
@app.route("/delete_spot/<int:spot_id>/<int:lot_id>/<name>")
def delete_spot(spot_id, lot_id, name):
    spot = Parking_spot.query.get_or_404(spot_id)

    if spot.status != 'A':

        return redirect(url_for("view_spot", lot_id=lot_id, name=name))

    db.session.delete(spot)
    lot = Parking_lot.query.get_or_404(lot_id)
    if lot.max_spots > 0:
        lot.max_spots -= 1
    db.session.commit()
   
    return redirect(url_for("admin_dashboard", name=name))

# other supported function
def get_parking_lots():
    parking_lots=Parking_lot.query.all()
    return parking_lots



# done the auth today too

@app.route("/admin/<name>/users")
def admin_users(name):
    users = User.query.all()
    return render_template("users.html", name=name, users=users)

@app.route("/admin/<name>/summary")
def admin_summary(name):
    return render_template("admin_summary.html", name=name)


# for book spot

@app.route("/book/<int:lot_id>/<name>", methods=["POST"])
def book_spot(lot_id, name):
    user = User.query.filter_by(email=name).first()
    if not user:
        return "User not found", 404

    # Get available spot
    spot = Parking_spot.query.filter_by(lot_id=lot_id, status='A').first()
    if not spot:
        return "No available spots", 400

    # Parse time inputs
    try:
        start_time_str = request.form.get("start_time")
        if not start_time_str:
            park_time = datetime.utcnow()  # fallback to now
        else:
            park_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")

        duration_hours = int(request.form.get("duration"))
        park_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")
        end_time = park_time + timedelta(hours=duration_hours)

        if park_time < datetime.now():
            return "Start time cannot be in the past.", 400
        
    except Exception as e:
        return f"Invalid time input: {e}", 400

    # Mark spot and create reservation
    spot.status = 'O'
    lot = Parking_lot.query.get(lot_id)
    reservation = Reservation(
        park_time=park_time,
        end_time=end_time,
        cost=lot.price * duration_hours,
        lot_id=lot_id,
        spot_id=spot.id,
        user_id=user.id
    )
    db.session.add(reservation)
    db.session.commit()

    return redirect(url_for("user_dashboard", name=name))

# for relese spot

@app.route("/release/<int:reservation_id>/<name>", methods=["POST"])
def release_reservation(reservation_id, name):
    reservation = Reservation.query.get_or_404(reservation_id)
    reservation.end_time = datetime.utcnow()
    
    spot = Parking_spot.query.get(reservation.spot_id)
    spot.status = 'A'
    
    db.session.commit()
    return redirect(url_for("user_dashboard", name=name))

@app.route("/user/<name>/summary")
def user_summary(name):
    return render_template("user_summary.html", name=name)