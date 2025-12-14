from app import db, app
from model import User, db
from security import hash_password
#this program was created to add users to the dtaabase so you can log in, this file has been included in submission but normally this file would not be in the repo
with app.app_context():
#if fills in each field of the registration form and makes a user, one normal and one admin
    user = User(id = 1, username="testuser", email= "test@user.com", nickname = "testUser", password_hashed=hash_password("UserPassword123!!"), role = "user",is_admin=False)
    admin = User(username="admin",email= "test@admin.com", nickname = "testAdmin",password_hashed=hash_password("AdminPassword12345!!"),role = "admin",is_admin=True)
#these are added to the database
    db.session.add(user)
    db.session.add(admin)
    db.session.commit()

    print("Users created successfully!")