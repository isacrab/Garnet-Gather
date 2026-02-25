#functions for everything role based/auth based 
import mysql.connector
import os
from db import *

#creates users, default param at end to determine what role it is
def createUser(username,password,email,fname,lname,role=0):
    if role!=0:
        print("user is an rso admin") #RBAC TODO: assign roles
    
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("""
            INSERT INTO Users (username, passwordHash, email, firstName, lastName, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, password, email, fname, lname, role))       #works, checked with print statements
    
    cursor.execute("SELECT * FROM Users")

    rows = cursor.fetchall()
    for r in rows:
        print(r)

    conn.commit()
    cursor.close()
    conn.close()