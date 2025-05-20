# App routes
from flask import Flask,render_template,request,redirect,url_for
from flask import current_app as app
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
    return render_template("user_dashboard.html",name=name)

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

    # Redirect back to admin dashboard after change
    # You'll need to pass the admin name again if necessary
    return redirect(url_for("admin_dashboard"))  # or use dynamic name if needed

# other supported function
def get_parking_lots():
    parking_lots=Parking_lot.query.all()
    return parking_lots



# done the auth today too