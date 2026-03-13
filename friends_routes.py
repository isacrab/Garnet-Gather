#friends_routes.py
#need to udpate once session stuff is added


from flask import Blueprint, request, jsonify   #using blueprint to put routes for the friend features in its own file. request->reads data from bowser
from friends import (
    createFriendTables,
    sendFriendRequest, acceptFriendRequest, removeFriend, getFriends,getPendingRequests,
)

friends_bp = Blueprint('friends', __name__,url_prefix='/api/friends')  #url_perfix basically jsut says that all the routes here start with /api/friends

#run once to create tables
createFriendTables()

@friends_bp.route('/<username>', methods=['GET'])   #does a get request to /api/friends/<username>, flaks then pulls whatever the username is in the url and passes it to fnction
def listFriends(username):
    return jsonify(getFriends(username))

@friends_bp.route('/pending/<username>',methods=['GET']) #does a get request to /api/friends/pending/<username> and returns all pending request
def listPending(username):
    return jsonify(getPendingRequests(username))

@friends_bp.route('/request', methods=['POST']) #when bowsers posts to /api/friends/request, pulls out sender and reciever from Json body, uses those in fucntion
def sendRequest():
    data = request.json
    return jsonify({'result': sendFriendRequest(data['sender'],data['receiver'])})

@friends_bp.route('/accept', methods=['POST'])  #same deal, reads sender and reciever from request body then calls func
def acceptRequest():
    data =request.json
    return jsonify({'result': acceptFriendRequest(data['sender'], data['receiver'])})

@friends_bp.route('/remove', methods=['DELETE'])    #reads username and frinedusername from request body, calls func
def removeF():
    data = request.jsonm
    return jsonify({'result':removeFriend(data['username'], data['friendUsername'])})