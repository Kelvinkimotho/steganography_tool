from cryptography.fernet import Fernet
import base64
import hashlib

# Generate a key from a password
def generate_key(password):
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

# Encrypt message
def encrypt_message(message, password):
    key = generate_key(password)
    cipher = Fernet(key)
    return cipher.encrypt(message.encode()).decode()

# Decrypt message
def decrypt_message(encrypted_message, password):
    key = generate_key(password)
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_message.encode()).decode()
