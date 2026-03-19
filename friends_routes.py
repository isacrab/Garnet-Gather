#friends_routes.py
#need to udpate once session stuff is added


from flask import Blueprint, request,session, jsonify   #using blueprint to put routes for the friend features in its own file. request->reads data from bowser
from friends import (
    createFriendTables,
    sendFriendRequest, acceptFriendRequest, removeFriend, getFriends,getPendingRequests, 
    createGroup, addToGroup, leaveGroup, deleteGroup, getGroupMembers, getUserGroups,
)

friends_bp = Blueprint('friends', __name__,url_prefix='/api/friends')  #url_perfix basically jsut says that all the routes here start with /api/friends

#run once to create tables
createFriendTables()

@friends_bp.route('/list', methods=['GET'])   #does a get request to /api/friends/list, flaks then pulls whatever the username is in the url and passes it to fnction
def listFriends():
    username = session['username']
    return jsonify(getFriends(username))

@friends_bp.route('/pending',methods=['GET']) #does a get request to /api/friends/pending and returns all pending request
def listPending():
    username = session['username']
    return jsonify(getPendingRequests(username))

@friends_bp.route('/request', methods=['POST']) #when bowsers posts to /api/friends/request, pulls out sender and reciever from Json body, uses those in fucntion
def sendRequest():
    data =request.json
    sender = session['username']
    return jsonify({'result': sendFriendRequest(sender,data['receiver'])})

@friends_bp.route('/accept', methods=['POST'])  #same deal, reads sender and reciever from request body then calls func
def acceptRequest():
    data=request.json
    receiver=session['username']
    return jsonify({'result': acceptFriendRequest(data['sender'], receiver)})

@friends_bp.route('/remove', methods=['DELETE'])    #reads username and frinedusername from request body, calls func
def removeF():
    data = request.json
    username = session['username']
    return jsonify({'result':removeFriend(username, data['friendUsername'])})

@friends_bp.route('/groups/mine', methods=['GET'])    #get requets, pulls username from url, and returns all groups that user belongs to
def listGroups():
    username=session['username']
    return jsonify(getUserGroups(username))

@friends_bp.route('/groups/<int:groupId>/members', methods=['GET']) #get request, pulls groupid from url and returns all members. the <int:groupID> is to make sure only a number is accepted in that spot
def listMembers(groupId):
    return jsonify(getGroupMembers(groupId))

@friends_bp.route('/groups/create', methods=['POST'])   #post request, reads admin, group name, member list from request body
def createGroupRoute():
    data = request.json
    adminUsername= session['username']
    result = createGroup(adminUsername, data['groupName'],data.get('memberUsernames',[])) #empty list if no members were found so it doesnt crash
    if 'error' in result:
        return jsonify(result),400  #somethign went wrong
    return jsonify(result), 201

@friends_bp.route('/groups/<int:groupId>/add', methods=['POST'])    #post request,read admin and new member from request body, grouppid comes from url
def addMember(groupId):
    data = request.json
    adminUsername = session['username']
    return jsonify({'result':addToGroup(adminUsername, groupId, data['newMember'])})

@friends_bp.route('/groups/<int:groupId>/leave', methods=['POST'])  #post request, reads username from request body, groupid comes from url
def leaveGroupRoute(groupId):
    username = session['username']
    return jsonify({'result': leaveGroup(username,groupId)})

@friends_bp.route('/groups/<int:groupId>/delete', methods=['DELETE'])   #reads admin from request body, groupid comes from url
def deleteGroupRoute(groupId):
    adminUsername= session['username']
    return jsonify({'result': deleteGroup(adminUsername, groupId)})