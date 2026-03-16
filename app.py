#all things to make the app actually run
from flask import Flask,render_template, request,redirect, url_for, jsonify, session
from db import *
from chicken_tinder import recordVote, getRemainingRestaurants, getResults
from events import createAnEvent, getEvent, getEvents, joinAnEvent
from schedule import *

app = Flask(__name__)
#secret key for testing
app.secret_key = 'temp_key'

@app.route('/') #home page for now
def homepage():
    return render_template('home.html')

@app.route('/login')    #login page for right now, that name /... name matches the a ref in the corresponding html
def login():
    return render_template('login.html')

@app.route('/signup')       #only renders the signup page, links to userSignup that does all the actual work in db
def singup():
    return render_template('signup.html')

@app.route('/userSignup', methods = ['POST', 'GET'])  #will actually put it in db
def userSignup():
    if request.method == 'POST':    #get all info to insert into table
        fsuid = request.form['username']
        password = request.form['password']
        email = request.form['email']
        fName = request.form['firstname']
        lName = request.form['lastname']
    
    createUser(fsuid,password,email,fName,lName)    #actually creates user                               


    
    return redirect(url_for('login'))

@app.route('/schedule_insert')
def schedulepage():
        return render_template('schedule_insert.html')

@app.route('/scheduleSubmit', methods = ['POST'])  #handles schedule submission, gets info from form and puts it in db, then redirects to schedule page to show it off')
def scheduleSubmit():
    return schedulesubmit() #calls function in schedule.py to handle all the work of putting it in db, then redirects to schedule page to show it off

@app.route('/viewSchedule') 
def viewSchedule():
    return viewschedule()

#event routes
#page of all ur events
@app.route('/events')
def eventsPage():
    events = getEvents()
    return render_template('events.html', events=events)
#def getEventsData():
    #events = getEvents()
    #return jsonify({'id': events[0], 'eventName': events[1], 'location': events[2], 'eventDate': events[3], 'startTime': events[4], 'endTime': events[5], 'isDiningEvent': bool(events[6])})

@app.route('/createEvent', methods = ['GET'])
def createEventPage():
    return render_template('createEvent.html')

@app.route('/createEvent', methods=['POST'])
def submitEvent():
    eventId = createAnEvent(request.form, session['username']) #know who created event
    return redirect(url_for('viewEvent', eventId=eventId)) #bring it to event virepage

@app.route('/event/<int:eventId>') #bring to specific event
def viewEvent(eventId):
    event, members = getEvent(eventId)
    return render_template('viewEvent.html', event=event, members=members)

@app.route('/joinEvent', methods=['POST'])
def joinEventRoute():
    eventId = int(request.form['eventId'])
    username = request.form['username']
    joinAnEvent(eventId, username)
    return redirect(url_for('viewEvent', eventId=eventId))



#chicken tinder routes 
@app.route('/chicken-tinder/<int:eventId>') #ct should be tied to event
def chickenTinder(eventId):
    username = session['username']
    #get remaning restaurants
    remaining = getRemainingRestaurants(eventId, username)

    if len(remaining) == 0:
        results = getResults(eventId)
        #if done show results
        return render_template('chickenTinder.html', done=True, results=results, eventId=eventId)
    
    #if not pick next rest and keep voting
    restaurant = remaining[0]
    return render_template('chickenTinder.html', done=False, restaurant=restaurant, eventId=eventId, username=username)

@app.route('/chickenTinder/vote', methods = ['POST'])
def submitVote():
    #data = request.json #get vote data 
    eventId = int(request.form['eventId'])
    username = request.form['username']
    restaurantId = int(request.form['restaurantId'])
    vote = bool(int(request.form['vote']))
    #put vote in db 
    #recordVote(int(data['eventId']), data['username'], int(data['restaurantId']), bool(int(data['vote'])))
    #return jsonify({'success': True})
    recordVote(eventId, username, restaurantId, vote)
    return redirect(url_for('chickenTinder', eventId=eventId))


if __name__=='__main__':    #main
    app.run(debug=True)