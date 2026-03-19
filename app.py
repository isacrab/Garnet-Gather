#all things to make the app actually run
from flask import Flask,render_template, request,redirect, url_for, jsonify,flash,session
from db import *
from chicken_tinder import recordVote, getRemainingRestaurants, getResults
from datetime import timedelta
from events import createAnEvent, getEvent, getEvents, joinAnEvent
from schedule import *
from authen import *
from friends_routes import friends_bp

app = Flask(__name__)
app.register_blueprint(friends_bp)
app.secret_key ="23adkfn23rfnjfa98" 
app.permanent_session_lifetime = timedelta(hours=5)

@app.before_request
def refresh_session():
    if 'username' in session:
        session.modified = True


@app.route('/') #home page for now, will change to login
def homepage():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])    #login page for right now, that name /... name matches the a ref in the corresponding html
def login():
    if request.method == 'POST':    #if they submit the form
        username = request.form['username']
        password = request.form['password']

        if userExist(username,password):
            conn = getConnection()
            cursor= conn.cursor()
            cursor.execute("SELECT role FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()

           

            if result:
                role = result[0]
                session['username'] = username
                session['role']= role

                session.permanent= True 
                return redirect(url_for('homepage'))
        else:
            flash("Invalid username or password.", "loginerror") 

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/signup')       #only renders the signup page, links to /userSignup that does all the actual work in db
def signup():
    return render_template('signup.html')

#THIS IS FOR USERS ONLY
@app.route('/userSignup', methods = ['POST', 'GET'])  #will actually put it in db, links to @app.route('/signup')
def userSignup():
    if request.method == 'POST':    #get all info to insert into table
        fsuid = request.form['username']
        password = request.form['password']
        email = request.form['email']
        fName = request.form['firstname']
        lName = request.form['lastname']
    
        if not realEmail(email):    #check if email is valid
            print("invalid email")
            flash("Please enter a valid @fsu.edu email address.", "emailerror")
            return render_template('signup.html')

        if not validUser(fsuid):    #check if already signed up
            print("Account already exists")
            flash("An account with that username already exists.", "usererror")
            return render_template('signup.html')

        if not validEmail(email):    #check if email already in use
            print("Email already in use")
            flash("An account with that email already exists.", "emailerror")
            return render_template('signup.html')

        if not validPassword(password):
            print("invalid password")
            flash("Please enter a valid password (8-25 characters, with at least one number and one uppercase letter).", "passworderror")
            return render_template('signup.html')
       
        password = hashPassword(password)    #hash password before putting in db

        flash("Account created successfully! Please log in.", "success")
        createUser(fsuid,password,email,fName,lName, 0)    #actually creates user, in db.py                              

    return redirect(url_for('login'))

#ONE FOR THE RSOS ONLY
@app.route('/rsoSignup')
def rsoSignup():
    return render_template('rsoSignup.html')    #links with orgSignup

@app.route('/orgSignup', methods = ['POST', 'GET']) #for orgSignup, gets everything and makes RSO
def orgSignup():
    if request.method == 'POST':
        fsuid = request.form['username']
        password = request.form['password']
        email = request.form['email']
        fName = request.form['firstname']
        #lastname is being nulled out
        code = int(request.form['adminCode'])
    
        if not realEmail(email):    #check if email is valid
            print("invalid email")
            flash("Please enter a valid @fsu.edu email address.", "emailerror")
            return render_template('rsoSignup.html')

        if not validUser(fsuid):    #check if already signed up
            print("Account already exists")
            flash("An account with that username already exists.", "usererror")
            return render_template('rsoSignup.html')

        if not validEmail(email):    #check if email already in use
            print("Email already in use")
            flash("An account with that email already exists.", "emailerror")
            return render_template('rsoSignup.html')

        if not validPassword(password):
            print("invalid password")
            flash("Please enter a valid password (8-25 characters, with at least one number and one uppercase letter).", "passworderror")
            return render_template('rsoSignup.html')
       
        password = hashPassword(password)    #hash password before putting in db

        if(code==8008135):
            createUser(fsuid,password,email,fName, 0, code)    #actually creates user, in db.py 
        else:
            flash("Please enter a valid code.", "codeerror")
            return render_template('rsoSignup.html')
    return redirect(url_for('login'))

@app.route('/schedule_insert') #CHANGED HERE
def schedulepage():
    schedules=getEvents();#have to call the getevent func in here bc the html now need to show the events, pass into return bc it needs those values also
    return render_template('schedule_insert.html',schedules=schedules)#send to the schedule page, where they can submit their schedule info


            
#chicken tinder routes 
#THESE ARE COMMENTED OUT BC WE DONT HAVE EVENTS SET UP SO TESTING ROUTE IN IN USE
#@app.route('/chicken-tinder')
#def chickenTinder():
    #return render_template('ChickenTinder.html')

@app.route('/scheduleSubmit', methods = ['POST'])  #handles schedule submission, gets info from form and puts it in db, then redirects to schedule page to show it off')
def scheduleSubmit():
    return schedulesubmit() #calls function in schedule.py to handle all the work of putting it in db, then redirects to schedule page to show it off

@app.route('/viewSchedule') 
def viewSchedule():
    return viewschedule()

#added this
@app.route('/deleteschedule', methods = ['POST'])
def deleteSchedule():
        return deleteschedule() 

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

@app.route('/friendsTest')  
def friendsTest():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('friendFrontEnd.html')

if __name__=='__main__':    #main
    app.run(debug=True)
