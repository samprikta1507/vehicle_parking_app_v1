# App routes
from flask import Flask,render_template,request
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
            return render_template("admin_dashboard.html")
        elif usr and usr.role==1: #Existed and normal user
            return render_template("user_dashboard.html")
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