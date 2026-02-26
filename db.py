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

    #cursor.execute('DROP TABLE Users CASCADE')

    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    cursor.execute('DROP TABLE IF EXISTS DiningVotes')
    cursor.execute('DROP TABLE IF EXISTS DiningMembers')
    cursor.execute('DROP TABLE IF EXISTS DiningSessions')
    cursor.execute('DROP TABLE IF EXISTS EventMembers') 
    cursor.execute('DROP TABLE IF EXISTS OrgMembers')
    cursor.execute('DROP TABLE IF EXISTS Events')
    cursor.execute('DROP TABLE IF EXISTS Organizations')
    cursor.execute('DROP TABLE IF EXISTS Restaurants')
    cursor.execute('DROP TABLE IF EXISTS Schedules')    
    cursor.execute('DROP TABLE IF EXISTS Users')
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")


    conn.commit()
    cursor.close()
    conn.close()

def createUsersTables():
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
            INSERT INTO Users (username, passwordHash, email, firstName, lastName, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, password, email, fname, lname, role))       #works, checked with print statements
    
    conn.commit()
    cursor.close()
    conn.close()

def createSchedules(username,classname,dayofweek,starttime,endtime):
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute("""
            INSERT INTO Schedules (username, classname, dayofweek, starttime, endtime)
            VALUES (%s, %s, %s, %s, %s)
            """, (username, classname, dayofweek, starttime, endtime))
    conn.commit()
    cursor.close()
    conn.close()

#chicken tinder 
def createDiningTables():
    conn = getConnection()
    cursor = conn.cursor()
    
    #Restaurant creation table
    cursor.execute('CREATE TABLE IF NOT EXISTS Restaurants (' +
                    'id INT PRIMARY KEY, ' +     #autoincrement to assign id to each restaurant
                    'name VARCHAR(100) NOT NULL, ' +
                    'imageUrl VARCHAR(250) ' +
                    ')'
                    )

    #Dining session table (per event)
    cursor.execute('CREATE TABLE IF NOT EXISTS DiningSessions (' +
                    'id INT AUTO_INCREMENT PRIMARY KEY, ' +
                    'eventId INT NOT NULL,' +
                    'FOREIGN KEY (eventId) REFERENCES Events(id) ON DELETE CASCADE' +
                    ')')

    #Table to track those coming to dining session
    cursor.execute('CREATE TABLE IF NOT EXISTS DiningMembers (' +
                    'eventId INT NOT NULL,' +
                    'username VARCHAR(50) NOT NULL,' +
                    'PRIMARY KEY (eventId, username), ' +
                    'FOREIGN KEY (eventId) REFERENCES Events(id) ON DELETE CASCADE, '+
                    'FOREIGN KEY (username) REFERENCES Users(username) ON DELETE CASCADE' +
                    ')')
    
    #Table to track people's votes for restaurants
    cursor.execute('CREATE TABLE IF NOT EXISTS DiningVotes (' +
                    'id INT AUTO_INCREMENT PRIMARY KEY, ' +
                    'eventId INT NOT NULL, ' +
                    'username VARCHAR(50) NOT NULL, ' +
                    'restaurantId INT NOT NULL, ' +
                    'vote BOOLEAN NOT NULL, ' +
                    'FOREIGN KEY (eventId) REFERENCES Events(id) ON DELETE CASCADE, ' +
                    'FOREIGN KEY (username) REFERENCES Users(username) ON DELETE CASCADE, ' +
                    'FOREIGN KEY (restaurantId) REFERENCES Restaurants(id) ON DELETE CASCADE ' +
                    ')')
    conn.commit()
    cursor.close()
    conn.close()

def createEventTables():
    conn = getConnection()
    cursor = conn.cursor()

    #Org table
    cursor.execute('CREATE TABLE IF NOT EXISTS Organizations (' +
                    'id INT AUTO_INCREMENT PRIMARY KEY, ' +
                    'orgName VARCHAR(50) NOT NULL UNIQUE ' +
                    ')')

    #Main event table
    cursor.execute('CREATE TABLE IF NOT EXISTS Events (' +
                    'id INT AUTO_INCREMENT PRIMARY KEY, ' +
                    'eventName VARCHAR(100) NOT NULL, ' +
                    'location VARCHAR(150) NOT NULL, ' +
                    'eventDate DATE NOT NULL, ' +
                    'startTime TIME NOT NULL, ' +
                    'endTime TIME NOT NULL, ' +
                    'description TEXT, ' +
                    'eventType VARCHAR(50) NOT NULL, ' +
                    'eventStatus VARCHAR(25) NOT NULL, ' +
                    'orgName VARCHAR(50) NOT NULL, ' +
                    'createdBy VARCHAR(50) NOT NULL, ' +
                    'isDiningEvent BOOLEAN DEFAULT FALSE, ' +   #should chicken tinder be included 
                    'FOREIGN KEY(createdBy) REFERENCES Users(username) ON DELETE CASCADE , ' +
                    'FOREIGN KEY(orgName) REFERENCES Organizations(orgName) ON DELETE CASCADE ' +
                    ')')

    #Event members table
    cursor.execute('CREATE TABLE IF NOT EXISTS EventMembers (' +
                    'id INT AUTO_INCREMENT PRIMARY KEY, ' +
                    'eventId INT NOT NULL, ' +
                    'username VARCHAR(50) NOT NULL, ' +
                    'FOREIGN KEY (eventId) REFERENCES Events(id) ON DELETE CASCADE, ' +
                    'FOREIGN KEY (username) REFERENCES Users(username) ON DELETE CASCADE ' +
                    ')')

    #Org members table
    cursor.execute('CREATE TABLE IF NOT EXISTS OrgMembers (' +
                    'id INT AUTO_INCREMENT PRIMARY KEY, ' +
                    'orgId INT NOT NULL, ' +
                    'username VARCHAR(50) NOT NULL, ' +
                    'FOREIGN KEY (orgId) REFERENCES Organizations(id) ON DELETE CASCADE, ' +
                    'FOREIGN KEY (username) REFERENCES Users(username) ON DELETE CASCADE ' +
                    ')')

    conn.commit()
    cursor.close()
    conn.close()

def createEvent(eventName, location, eventDate, startTime, endTime, description, eventType, eventStatus, orgName, createdBy, isDiningEvent, eventId, username, orgId):
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("""
            INSERT INTO Events(eventName, location, eventDate, startTime, endTime, description, eventType, eventStatus, orgName, createdBy, isDiningEvent)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (eventName, location, eventDate, startTime, endTime, description, eventType, eventStatus, orgName, createdBy, isDiningEvent ))

    cursor.execute("""
            INSERT INTO EventMembers(eventId, username)
            VALUES (%s, %s)""",
            (eventId, username))

    cursor.execute("""
            INSERT INTO Organizations(orgName)
            VALUES (%s)""",
            (orgName,))  

    cursor.execute("""  
            INSERT INTO OrgMembers(orgId, username)
            VALUES (%s, %s)""",
            (orgId, username))  

    conn.commit()
    cursor.close()
    conn.close()


def createDining(id, name, imageUrl, eventId, username, restaurantId, vote):
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("""
            INSERT INTO Restaurants(id,name, imageUrl) 
            VALUES (%s, %s, %s)""", 
            (id,name, imageUrl))

    cursor.execute("""
            INSERT INTO DiningSessions(eventId)
            VALUES (%s)""",
            (eventId,))

    cursor.execute("""
            INSERT INTO DiningMembers(eventId,username)
            VALUES (%s, %s)""",
            (eventId, username))

    cursor.execute("""
            INSERT INTO DiningVotes(eventId, username, restaurantId, vote)
            VALUEs (%s, %s, %s, %s)""",
            (eventId, username, restaurantId, vote))


    conn.commit()
    cursor.close()
    conn.close()

#hardcode restaurants
def seedRestaurants():
    conn = getConnection()
    cursor = conn.cursor()
    restaurant = [
        #urls will be added later or replaced w/ smth else
        (1, 'Chick-Fil-A', None),
        (2, '4 Rivers', None),
        (3, 'Panera Bread', None),
        (4, 'Panda Express', None),
        (5, 'Proof', None),
        (6, 'Suwannee', None),
        (7, 'Seminole Cafe', None),
        (8, 'Argo Tea', None),
        (9, 'Bento Sushi', None),
        (10, 'Brooklyn Pizza', None),
        (11, 'The Den', None),
        (12, 'Einstein Bros. Bagels', None),
        (13, 'Pollo Tropical', None),
        (14, 'Starbucks (Dirac)', None),
        (15, 'Starbucks (Stroz)', None),
        (16, 'Starbucks (Union)', None),
        (17, 'Starbucks (1851)', None),
        (18, 'Halal Shack', None),
        (19, 'Subway', None),
        (20, 'Tally-Mac-Shack', None),
        (21, 'Three Torches', None),
        (22, 'Joe Mama\'s', None),
        (23, 'Vato Tacos', None),
        (24, 'Shake Smart', None)
        ]
    cursor.executemany("""
            INSERT IGNORE INTO Restaurants(id, name, imageUrl) 
            VALUES (%s, %s, %s)""", restaurant)
    conn.commit()
    cursor.close()
    conn.close()


#THIS IS SO KAY CAN TEST CHICKEN TINDER REMOVE LATER
def seedTestEvent():
    conn = getConnection()
    cursor = conn.cursor()
    
    #create test org
    cursor.execute("""
        INSERT IGNORE INTO Organizations (id, orgName) 
        VALUES (1, 'Test Organization')
    """)
    
    #create test user
    cursor.execute("""
        INSERT IGNORE INTO Users (username, passwordHash, email, firstName, lastName, role)
        VALUES ('testuser', 'testpass', 'test@fsu.edu', 'Test', 'User', 'Student')
    """)
    
    #create test event
    cursor.execute("""
        INSERT IGNORE INTO Events (id, eventName, location, eventDate, startTime, endTime, 
                                   description, eventType, eventStatus, orgName, createdBy, isDiningEvent)
        VALUES (1, 'Test Dining Event', 'Student Union', '2026-03-01', '12:00:00', '13:00:00',
                'Test event for chicken tinder', 'Dining', 'Active', 'Test Organization', 'testuser', TRUE)
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    

def startDB():
    testConnectDB() #try see if successful
    createUsersTables()
    createEventTables()
    createDiningTables()
    seedRestaurants()
    seedTestEvent()
   

if __name__ == '__main__':
    ans = input("Drop tables? y/n: ").lower()
    if ans == 'y':
        dropTables()
    ans = input("Clear votes? y/n: ").lower()
    if ans == 'y':
        conn = getConnection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM DiningVotes WHERE username = 'testuser'")

        conn.commit()
        cursor.close()
        conn.close()

    startDB()

