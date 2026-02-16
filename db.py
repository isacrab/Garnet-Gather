#all database schema stuff in here!

#RBAC TODO: HASH PASSWORDS, Check if users already exist using email, only fsu.edu accepted,

from multiprocessing import current_process
import os
import mysql.connector
from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

def testConnectDB():   #tests connecting to database
    db = mysql.connector.connect(
        host=os.getenv("DB_host", "localhost"),
        user=os.getenv("DB_user"),
        password=os.getenv("DB_password"),
        database=os.getenv("DB_name"),
        port=os.getenv("DB_port", 3306)
    )
    cursor = db.cursor()
    cursor.close()
    db.close()

def getConnection():    #actual connecting, must return connection obj
    conn = None     
    conn = mysql.connector.connect(
        host=os.getenv("DB_host", "localhost"),
        user=os.getenv("DB_user"),
        password=os.getenv("DB_password"),
        database=os.getenv("DB_name"),
        port=os.getenv("DB_port", 3306)
    )
    return conn

def dropTables():   #to keep check our bases
    conn = getConnection()
    cursor = conn.cursor()
    #drop tables here if needed
    cursor.execute('DROP TABLE Users CASCADE')


    conn.commit()
    cursor.close()
    conn.close()

def createTables():
    conn = None
    conn = getConnection()
    cursor = conn.cursor()

    #actual creation of the tables!
    cursor.execute('CREATE TABLE IF NOT EXISTS Users (' + 
                   'username VARCHAR(50) PRIMARY KEY, ' + 
                   'passwordHash VARCHAR(250) NOT NULL,' + 
                   'email VARCHAR(100) UNIQUE NOT NULL,' + 
                   'firstName VARCHAR(50) NOT NULL,' +
                   'lastName VARCHAR(50) NOT NULL,' +
                   'role VARCHAR(20) NOT NULL DEFAULT \'Student\' '+
                   ')'
                   )
    
    print("Successfully initialized database")

    conn.commit()
    cursor.close()
    conn.close()

def createScheduleTable():
    conn=getConnection()
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS Schedules (' 
                   'id INT AUTO_INCREMENT PRIMARY KEY,'  #the auto makes it to where each new class has a different id
                   'username VARCHAR(50) NOT NULL, '
                   'classname VARCHAR(50) NOT NULL, '
                   'dayofweek ENUM(\'Mon\',\'Tue\',\'Wed\',\'Thu\',\'Fri\') NOT NULL, '
                   'startTime TIME NOT NULL, '  
                   'endTime TIME NOT NULL, '
                   'FOREIGN KEY(username) REFERENCES Users(username) ' 
                   'ON DELETE CASCADE'
                   ')'
                )
    conn.commit()
    cursor.close()
    conn.close()
    
#creates users, default param at end to determine what role it is
def createUser(username,password,email,fname,lname,role=0):
    if role!=0:
        print("user is an rso admin") #RBAC TODO: assign roles
    
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("""
            INSERT INTO Users (username, passwordHash, email, firstname, lastname, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, password, email, fname, lname, role))       #works, checked with print statements
    
    conn.commit()
    cursor.close()
    conn.close()

def createSchedules(username,classname,dayofweek,starttime,endtime):
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute("""
            INSERT INTO Schedules (username,classname,dayofweek,starttime,endtime)
            VALUES (%s, %s, %s, %s, %s)
            """, (username, classname, dayofweek, starttime, endtime))
    conn.commit()
    cursor.close()
    conn.close()
    

def startDB():
    testConnectDB() #try see if successful
    createTables()

if __name__ == '__main__':
    ans = input("Drop tables? y/n: ").lower()
    if ans == 'y':
        dropTables()

    startDB()