#friends.py
#handles all friend stuff
#routes are handled separately in friends_routes.py, not app.py cause i dont want app.py to look messy

from db import getConnection


#creates table if it dont already exist
#call this once, handled by friends_routes.py
def createFriendTables():
    conn= getConnection()
    cursor = conn.cursor()

    #stores friend relationships between users
    #status is either pending so request was sent or accepted if already friends
    #we store btoh directions A->B and B->A once accepted so lookups are easy
    #foreign make sure like both usernames must exist in Users table, so if a user gets yeeted, their friend row gets tossed too
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Friends (
            username1   VARCHAR(50) NOT NULL,   #person who sent the request
            username2   VARCHAR(50) NOT NULL,   #person who recieved request
            status      ENUM('pending', 'accepted') NOT NULL DEFAULT 'pending',
            PRIMARY KEY (username1, username2), #combo must be unique
            FOREIGN KEY (username1) REFERENCES Users(username) ON DELETE CASCADE,
            FOREIGN KEY (username2) REFERENCES Users(username) ON DELETE CASCADE
        )
    """)
    #TODO: prob should add group stuff too
    conn.commit()
    cursor.close()
    conn.close()
    print("Friend table created.") #shows that it ran for me


#check if two users are confirmed mutual friends
#used as a check before adding someone to group
def areFriends(user1, user2):
    #opens a connection and runs a query looking for row where user1 sent a request to user2 anjd its accepted
    conn = getConnection()  
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM Friends   #want to know if a row exists
        WHERE username1 = %s AND username2 = %s AND status = 'accepted'
    """, (user1, user2))
    isFriends = cursor.fetchone()      #gets first result. If row was found True, if not False
    if isFriends is not None:
        isFriends = True
    else:
        isFriends = False
    cursor.close()
    conn.close()
    return isFriends

#send a friend request from sender to receiver
#reeturns a string describing what happened so the frontend can react
def sendFriendRequest(sender, receiver):
    if sender == receiver:
        return 'you cannot send request to yourself'                           #cant friend yourself obv
    if areFriends(sender, receiver):
        return 'already friends'        #if already friends

    conn = getConnection()
    cursor = conn.cursor()

    #checks both directions. for example, maybe sender already sent one or reciever already sent one to sender. no duplicate requests going opposite ways
    cursor.execute("""
        SELECT 1 FROM Friends
        WHERE (username1=%s AND username2=%s) OR (username1=%s AND username2=%s)
    """, (sender, receiver, receiver, sender))

    if cursor.fetchone():   #if row came back, a request already exists
        cursor.close()
        conn.close()
        return 'already sent friend request'

    #no existing request has been found, so insert the new row as pending, save it, then close everythign
    cursor.execute("""
        INSERT INTO Friends (username1, username2, status) VALUES (%s, %s, 'pending')
    """, (sender, receiver))

    conn.commit()
    cursor.close()
    conn.close()
    return 'sent friend request'


#accept a pending friend request
#marks the original row as accepted and inserts the reverse row, so areFriends works no matter which order you check
def acceptFriendRequest(sender, receiver):
    conn = getConnection()
    cursor = conn.cursor()

    #find the row where sender sent reciever request and if it is still pending, flip it to accepted
    cursor.execute("""
        UPDATE Friends SET status = 'accepted'
        WHERE username1 = %s AND username2 = %s AND status = 'pending'
    """, (sender, receiver))

    if cursor.rowcount == 0:    #how many rows were updated, if 0 no matching row was found
        cursor.close(); conn.close()
        return 'friend request not found'                      #request did not exist

    #insert reverse direction so both users show each other as friends
    cursor.execute("""
        INSERT IGNORE INTO Friends (username1, username2, status) VALUES (%s, %s, 'accepted')
    """, (receiver, sender))

    conn.commit()
    cursor.close()
    conn.close()
    return 'accepted friend request'


#remove a friendship between two users, deletes in both directions
def removeFriend(username, friendUsername):
    if not areFriends(username, friendUsername):
        return 'not friends'

    conn = getConnection()
    cursor = conn.cursor()

    #delete both directions at once
    cursor.execute("""
        DELETE FROM Friends
        WHERE (username1=%s AND username2=%s) OR (username1=%s AND username2=%s)
    """, (username, friendUsername,friendUsername,username))

    conn.commit()
    cursor.close()
    conn.close()
    return 'removed'


#get the full friends, who accepted, list for a user
def getFriends(username):
    conn = getConnection()
    cursor = conn.cursor()

    #gets all accepted friends for user. join pulls actual name from users tabel since Friends only stores usernames. F.username2 is everyone that username is friends with
    cursor.execute("""
        SELECT U.username, U.firstName, U.lastName
        FROM Friends F
        JOIN Users U ON U.username = F.username2
        WHERE F.username1 = %s AND F.status = 'accepted'
    """, (username,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{'username': r[0], 'firstName': r[1], 'lastName': r[2]}for r in rows] #turns each database row into a dict

#gets all incoming pending friend requests for a user
def getPendingRequests(username):
    conn=getConnection()
    cursor= conn.cursor()

    #looks for rows where username2 is you and status is still pending. like someone sent current user a request and they havent responded. username 1 is grabbed and we join their names from Users
    cursor.execute("""
        SELECT F.username1, U.firstName, U.lastName
        FROM Friends F
        JOIN Users U ON U.username = F.username1
        WHERE F.username2 = %s AND F.status= 'pending'
    """, (username,))

    rows = cursor.fetchall()    #gets every friend row and stores them in rows
    cursor.close()
    conn.close()
    return [{'username': r[0], 'firstName': r[1], 'lastName': r[2]} for r in rows] #loops through every row in rows and converts each from tuple into a dict
    #doing this so frontend gets list as JSON

    #TODO: need to add friend group stuff
