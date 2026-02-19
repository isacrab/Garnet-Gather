#Chicken tinder backend
from db import getConnection

def getRestaurants():      #load restaurants into chicken tinder
    conn = getConnection()
    cursor = conn.cursor()

    #query to get all restaurants
    cursor.execute("SELECT id, name, imageUrl FROM Restaurants")

    #fetch results
    restaurants = cursor.fetchall()     #gets rows that match query & store

    cursor.close()
    conn.close()

    return restaurants  #returns restaurant list

def getVotedOnRestaurants(eventId, username):
#get all restaurants specifiic user has already voted on & return list of restaurant ids user has voted for
    conn = getConnection()
    cursor = conn.cursor()

    #query to grab restaurants user has already voted for
    cursor.execute("""
            SELECT restaurantId FROM DiningVotes WHERE eventID = %s AND username = %s """, 
            (eventId, username))
    
    #fetch results
    votes = cursor.fetchall()

    cursor.close()
    conn.close()

    #setting up list to make accessing easier later
    votedRestaurantIds = [vote[0] for vote in votes]    #loop thru each vote and take first element for id

    return votedRestaurantIds

def getRemainingRestaurants(eventId, username):
#get all restaurants user has left to vote for
    allRestaurants = getRestaurants()   #grab all restaurants

    #get ids from already voted on restaurants
    votedIds = getVotedOnRestaurants(eventId, username)

    #loop thru all restrayrant sand take voted restaurants out from all restaurants
    remainingRestaurants = []   #create empty list to house restraurants left to be voted on
    for i in allRestaurants:
        restaurantId = i[0]     #get id
        if restaurantId not in votedIds:
            remainingRestaurants.append(i)

    return remainingRestaurants

def recordVote(eventId, username, restaurantId, vote):
#record the yes or no vote on each erestaurant
    conn = getConnection()
    cursor = conn.cursor()

    #put vote in table
    cursor.execute("""
            INSERT INTO DiningVotes (eventId, username, restaurantId, vote)
            VALUES (%s, %s, %s, %s)""",
            (eventId, username, restaurantId, vote))
    
    existingVote = cursor.fetchone()

    if existingVote:
        #user already voted
        cursor.close()
        conn.closer()
        return False    #dont record vote

    conn.commit()   #commit changes to db
    cursor.close()
    conn.close()

def getResults(eventId):
#get all votes, rank by number of "yes"s
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute("""
            SELECT Restaurants.id, Restaurants.name, Restaurants.imageUrl,
                COUNT(DiningVotes.vote) as yesVotes FROM Restaurants
            LEFT JOIN DiningVotes ON Restaurants.id = DiningVotes.restaurantId
                AND DiningVotes.eventId = %s AND DiningVotes.vote = TRUE
            GROUP BY Restaurants.id, Restaurants.name, Restaurants.imageUrl
            ORDER BY yesVotes DESC""", (eventId,))
    
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results
    