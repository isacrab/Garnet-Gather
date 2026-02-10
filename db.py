#all database schema stuff in here!
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


def startDB():
    #here ask if we want to drop tables?

    testConnectDB() #try see if successful
    createTables()

if __name__ == '__main__':
    startDB()