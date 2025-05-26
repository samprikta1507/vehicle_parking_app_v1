# Data models

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# first entity
class User(db.Model):
    __tablename__="user"
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    role=db.Column(db.Integer,default=1)
    full_name=db.Column(db.String,nullable=False)
    address=db.Column(db.String,nullable=False)
    pin_code=db.Column(db.Integer,nullable=False)
    # reletion
    reservations=db.relationship("Reservation",cascade="all,delete",backref="user",lazy=True) #user can access their all reservation

# 2nd entity
class Parking_lot(db.Model):
    __tablename__="parking_lot"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,nullable=False)
    address=db.Column(db.String,nullable=False)
    pin_code=db.Column(db.Integer,nullable=False)
    price=db.Column(db.Float,default=0.0)
    max_spots=db.Column(db.Integer,nullable=False)
    # reletions
    spots=db.relationship("Parking_spot",cascade="all,delete",backref="parking_lot",lazy=True) # parking lot can access it's all spots
    reservations=db.relationship("Reservation",cascade="all,delete",backref="parking_lot",lazy=True) # parking lot can access it's all reservation

# 3rd entity
class Parking_spot(db.Model):
    __tablename__="parking_spot"
    id=db.Column(db.Integer,primary_key=True)
    status=db.Column(db.String,nullable=False)
    lot_id=db.Column(db.Integer, db.ForeignKey("parking_lot.id"),nullable=False)
    # reletion
    reservations=db.relationship("Reservation",cascade="all,delete",backref="parking_spot",lazy=True) # parking spot can access it's all reservation

# 4th entity
class Reservation(db.Model):
    __tablename__="reservation"
    id=db.Column(db.Integer,primary_key=True)
    start_time =db.Column(db.DateTime,nullable=False) # scheduled start
    end_time=db.Column(db.DateTime,nullable=False) # scheduled end
    park_time=db.Column(db.DateTime,nullable=True) # actual start
    release_time=db.Column(db.DateTime,nullable=True) # actual end
    cost=db.Column(db.Float,default=0.0)
    lot_id=db.Column(db.Integer, db.ForeignKey("parking_lot.id"),nullable=False)
    spot_id=db.Column(db.Integer, db.ForeignKey("parking_spot.id"),nullable=False)
    user_id=db.Column(db.Integer, db.ForeignKey("user.id"),nullable=False)





