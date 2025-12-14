import os
from dotenv import load_dotenv

#this will load the values from the .env file
load_dotenv()

#this class will take the secret key from the secrets.env file and also use an sqlite database and links the uri
#the class sets some session cookie security settings to prevent javascript from reading any session cookies, it also sets
#the cookies for https and protects from CSRF with the samesite parameter. The encryption key uis also used here for sensitive fields
#and is acquired from the .env file.
#Flask needs the secret key for session signing, CSRF protection adn securing cookies
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = "sqlite:///bball_secure.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_ENABLED= True

    FERNET_KEY = os.getenv("FERNET_KEY")