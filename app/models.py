from app import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model,UserMixin):
    __tablename__="users"
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(200),unique=True,nullable=False)
    email=db.Column(db.String(200),unique=True,nullable=False)
    password=db.Column(db.String(200),nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    #Relationship with Scan Class
    scans=db.relationship("Scan",backref="user",lazy=True)

class Scan(db.Model):
    __tablename__="scans"
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    name=db.Column(db.String(200),nullable=False)
    age=db.Column(db.Integer,nullable=False)
    gender=db.Column(db.String(20),nullable=False)
    image_filename=db.Column(db.String(200),nullable=False)
    result=db.Column(db.String(200))
    Confidence=db.Column(db.Float())
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

  
    