from cryptography import fernet
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from cryptography.fernet import Fernet
import os

db = SQLAlchemy()
key = Fernet(os.getenv("FERNET_KEY")) #this will load the key from the .env file

#creates a database model for the user accounts for the web app, for the username, email, nickname, password and account role, and a check for admin
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    password_hashed = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False) # this is the user or admin role
    is_admin = db.Column(db.Boolean, nullable=False, default=False)#this is to check if the user is an admin or user

    def __repr__(self):
        return f"<User {self.username}>"

#this is the same, this model is for players which have a form and can be added tot he database, each entry is created here in the model
class Player(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(20), nullable=False)
    ppg = db.Column(db.Float, nullable=False)
    bio = db.Column(db.Text, nullable=False) #true?
    contract = db.Column(db.LargeBinary, nullable=True)#this will be encrypted and only admin can see this encrypted field

    #this will encrypt the players salary so it is not viewable by anyone which is a security function
    def secure_salary(self, salary: str):
        self.contract = key.encrypt(salary.encode())

class Game(db.Model):
    __tablename__ = "games"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), unique=True, nullable=False)
    opponent = db.Column(db.String(80), unique=True, nullable=False)
    venue = db.Column(db.String(80), unique=True, nullable=False)
    notes = db.Column(db.Text, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    