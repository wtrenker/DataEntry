import decimal as dec
import hashlib, binascii, os

def decimalAverage(num1, num2):
    n1 = dec.Decimal(str(num1))
    n2 = dec.Decimal(str(num2))
    average = (n1 + n2) / dec.Decimal('2.0')
    return average.quantize(dec.Decimal('.1'), rounding=dec.ROUND_UP)

def hash_password(password):
    """Hash a password for storing.
       By Alessandro Molina in https://www.vitoshacademy.com/hashing-passwords-in-python/"""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user
       By Alessandro Molina in https://www.vitoshacademy.com/hashing-passwords-in-python/"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


if __name__ == '__main__':
    storepw = hash_password('longtermsecretpassword')
    print(storepw)
