# Data models

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# first entity
class User(db.model):
    __tablename__="user"
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True,nullable=False)
    


