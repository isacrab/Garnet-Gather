#functions for everything role based/auth based 
import mysql.connector
import os
from db import *

#authentication function to check if the entered email is an @fsu.edu email
def realEmail(email):
    email=email.strip().lower() #case sensistive and remove whitespace 
    return email.endswith('@fsu.edu')

def validPassword(password): #password needs to be at least 8 characters but at most 25, with a number and uppercase letter
    valid = True
    if len(password) < 8 or len(password) > 25: #checking for length
        valid = False
    if not any(char.isdigit() for char in password): #verifying num exists within pass
        valid = False
    if not any(char.isupper() for char in password): #verifying uppercase letter exists within pass
        valid = False
    return valid
    
def validUser(username):
    from db import getConnection
    conn = getConnection()
    cursor = conn.cursor()

    valid = True
    cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    if result is not None:
        valid = False
    
    cursor.close()
    conn.close()
    return valid

def validEmail(email):
    from db import getConnection
    conn = getConnection()
    cursor = conn.cursor()

    valid = True
    cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    if result is not None:
        valid = False
    
    cursor.close()
    conn.close()
    return valid

def hashPassword(password):
    import bcrypt
    pw = password
    byte = pw.encode('utf-8')
    salt = bcrypt.gensalt()

    hash= bcrypt.hashpw(byte, salt)
    print(password)
    print(hash)
    return hash
 