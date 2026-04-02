#functions for everything role based/auth based 
import mysql.connector
import os
import bcrypt
from db import *
from db import getConnection


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
    pw = password
    byte = pw.encode('utf-8')
    salt = bcrypt.gensalt()

    hash= bcrypt.hashpw(byte, salt)

    return hash

def userExist(username,password):
    conn = getConnection()
    cursor = conn.cursor()

    given=password 
    
    cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
    resultu = cursor.fetchone()
    cursor.execute("SELECT passwordHash FROM users WHERE username = %s", (username,))
    resultp = cursor.fetchone()
    
    
    
    if resultu is None:
        print("no username found")
        return False
    
 
    if resultp is None:
        print("no password found")
        return False
    
    stored=resultp[0]

    
    if bcrypt.checkpw(given.encode('utf-8'), stored.encode('utf-8')):
        print("password match")
        return True
    cursor.close()
    conn.close()
    return False