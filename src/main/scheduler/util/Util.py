import hashlib
import os
import random
import string

class Util:
    def generate_salt():
        return os.urandom(16)

    def generate_hash(password, salt):
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000,
            dklen=16
        )
        return key
    
    def generate_appointment_id():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))