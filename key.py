#file used to create an encryption key used throughout the web app for security
from cryptography.fernet import Fernet
#print(Fernet.generate_key().decode())

# import secrets
# print(secrets.token_hex(32))