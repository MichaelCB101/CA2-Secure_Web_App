import bcrypt
import bleach
from cryptography.fernet import Fernet
from flask import abort

#this function will hash passwords using bcrypt
def hash_password(password: str) -> str:
    passw = password.encode('utf-8')
    hashed_pw = bcrypt.hashpw(passw, bcrypt.gensalt())
    return hashed_pw.decode('utf-8')

#this function will comapre the plaintext password to the stored hash that bcrypt generates
def verify_password(plain_password: str, hashed_pw: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_pw.encode('utf-8'))

#this function is used to sanitise inputs in order to prevent XSS on the web app
#it cleans any user inputted text using the bleach feature
#it then removes all html tags to prevent a stored or reflected XSS
def sanitize_text(text: str) -> str:
    if not text:
        return text
    return bleach.clean(text, tags=[], attributes=[], strip=True)

#this function here checks if the user that has logged in is an admin or not
def isAdmin(user):
    if not user.is_authenticated or user.role != 'admin':
        abort(403)

#this function adds recommended HTTP security headers to every reposnse in order to mitigate XSS, clickjacking, MIME sniffing, and referer leakage
def sec_headers(response):
    response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; script-src 'self'" #this will prevent most XSS
    response.headers["X-Content-Type-Options"] = "nosniff" # this will prevebt MIME sniffing
    response.headers["X-Frame-Options"] = "DENY" # this will prevent clickjacking
    response.headers["X-XSS-Protection"] = "1; mode=block" # this will help protect against XSS
    response.headers["Referrer-Policy"] = "no-referrer" # this will hude sensitive URLS
    return response

#this class has hepler functions to use the symmetric encryption for sensitive fields like the player salary
class Encryption:

    def __init__(self, key: str):
        self.fernet = Fernet(key.encode('utf-8'))

    #this function will encrypt the plaintext and return a string in base64
    def encrypt(self, data: str) -> str:
        token = self.fernet.encrypt(data.encode('utf-8'))
        return token.decode('utf-8')

    #this function does the opposite, it willl decrypt the base64 string generated and then return the plaintext
    def decrypt(self, token: str) -> str:
        return self.fernet.decrypt(token.encode("utf-8")).decode('utf-8')


