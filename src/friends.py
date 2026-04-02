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
            username1   VARCHAR(50) NOT NULL,   
            username2   VARCHAR(50) NOT NULL,   
            status      ENUM('pending', 'accepted') NOT NULL DEFAULT 'pending',
            PRIMARY KEY (username1, username2), 
            FOREIGN KEY (username1) REFERENCES Users(username) ON DELETE CASCADE,
            FOREIGN KEY (username2) REFERENCES Users(username) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS FriendGroups (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            groupName     VARCHAR(100) NOT NULL,
            adminUsername VARCHAR(50) NOT NULL,
            FOREIGN KEY (adminUsername) REFERENCES Users(username) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS FriendGroupMembers (
            groupId  INT NOT NULL,
            username VARCHAR(50) NOT NULL,
            PRIMARY KEY (groupId, username),
            FOREIGN KEY (groupId)  REFERENCES FriendGroups(id) ON DELETE CASCADE,
            FOREIGN KEY (username) REFERENCES Users(username)  ON DELETE CASCADE
        )
    """)
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
        SELECT 1 FROM Friends  
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
#create a new friend group, every person in the group, including admin must be friends with everyone else
#returns {'groupId': int} on success or {'error': str} if the friend check fails
def createGroup(adminUsername, groupName, memberUsernames):
    #combine the admin list and member list into one list. set() will remove duplicates
    allMembers = list(set(memberUsernames + [adminUsername]))

    #loops through every possible pair of members and checks if they are frineds wiht each other
    for i in range(len(allMembers)):
        for j in range(i+1, len(allMembers)):
            if not areFriends(allMembers[i],allMembers[j]):
                return {'error': f"{allMembers[i]} and {allMembers[j]} are not friends."}

    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO FriendGroups (groupName, adminUsername) VALUES (%s, %s)
    """, (groupName, adminUsername))

    groupId = cursor.lastrowid  #grabs the generated id that mysql assigned to the new group

    #loops through every member and adds them to FriendGroupMembers. If someone is already in group, skip over them
    for member in allMembers:
        cursor.execute("""
            INSERT IGNORE INTO FriendGroupMembers (groupId, username) VALUES (%s, %s)
        """, (groupId, member))

    conn.commit()
    cursor.close()
    conn.close()
    return {'groupId': groupId}


#add a new member to an already made group, can only be done by admin
#new menber must be friends with every current member
def addToGroup(adminUsername, groupId, newMember):
    conn = getConnection()
    cursor = conn.cursor()

    #make sure the group exists and the person trying to add someone is the admin
    cursor.execute("SELECT adminUsername FROM FriendGroups WHERE id = %s", (groupId,))
    group = cursor.fetchone()
    if not group:
        cursor.close(); conn.close(); return 'group not found'
    if group[0]!= adminUsername:
        cursor.close(); conn.close(); return 'not admin'

    #gets everyone already in the group and stores their usernames in a list
    cursor.execute("SELECT username FROM FriendGroupMembers WHERE groupId = %s", (groupId,))
    currentMembers = [row[0] for row in cursor.fetchall()]
    cursor.close(); conn.close()

    if newMember in currentMembers:
        return 'already member'    #if person being added it already in group

    #checks that the new member being added is friends with every other member, if they arent friends with one person , return who 
    for member in currentMembers:
        if not areFriends(newMember,member):
            return f'not friends with {member}'

    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO FriendGroupMembers (groupId, username) VALUES (%s, %s)
    """, (groupId, newMember))
    conn.commit()
    cursor.close(); conn.close()
    return 'added'


#Leave a group
#If the admin leaves, the whole group gets deleted
def leaveGroup(username, groupId):
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT adminUsername FROM FriendGroups WHERE id = %s", (groupId,))
    group = cursor.fetchone()
    cursor.close(); conn.close()

    if not group:
        return 'group not found'

    #if person leaving is admin, yeet the whole group instead
    if group[0] == username:
        return deleteGroup(username, groupId)

    #if person leaving is not admin, remove their row from FriendGroupMembers
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM FriendGroupMembers WHERE groupId=%s AND username=%s
    """, (groupId, username))
    conn.commit()
    cursor.close(); conn.close()
    return 'you left'


#delete an entire group, can only be done by admin
#FriendGroupMembers rows are removed automatically
def deleteGroup(adminUsername, groupId):
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("SELECT adminUsername FROM FriendGroups WHERE id = %s", (groupId,))
    group = cursor.fetchone()
    if not group:
        cursor.close(); conn.close(); return 'group not found'
    if group[0] != adminUsername:
        cursor.close(); conn.close(); return 'not admin'

    cursor.execute("DELETE FROM FriendGroups WHERE id = %s", (groupId,))
    conn.commit()
    cursor.close(); conn.close()
    return 'deleted group'


#et all members of a group
def getGroupMembers(groupId):
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT U.username, U.firstName, U.lastName
        FROM FriendGroupMembers FGM
        JOIN Users U ON U.username = FGM.username
        WHERE FGM.groupId = %s
    """, (groupId,))

    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return [{'username': r[0], 'firstName': r[1], 'lastName': r[2]} for r in rows]  #looops through each row, and turns each into a dict


#get all groups a user belongs to
def getUserGroups(username):
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT FG.id, FG.groupName, FG.adminUsername
        FROM FriendGroupMembers FGM
        JOIN FriendGroups FG ON FG.id = FGM.groupId
        WHERE FGM.username = %s
    """, (username,))

    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return [{'groupId': r[0], 'groupName': r[1], 'adminUsername': r[2]} for r in rows] #loops through each row, and turns each into a dict