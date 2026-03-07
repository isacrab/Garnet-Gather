#all things to make the app actually run
from flask import Flask,render_template, request,redirect, url_for, jsonify,flash,session
from db import *
from authen import *
from chicken_tinder import recordVote, getRemainingRestaurants, getResults

app = Flask(__name__)
app.secret_key ="23adkfn23rfnjfa98" 

@app.route('/') #home page for now, will change to login
def homepage():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])    #login page for right now, that name /... name matches the a ref in the corresponding html
def login():
    if request.method == 'POST':    #if they submit the form
        username = request.form['username']
        password = request.form['password']

        if userExist(username,password):
            session['username'] = username
            return redirect(url_for('homepage'))
        else:
            flash("Invalid username or password.", "loginerror")
    return render_template('login.html')

@app.route('/signup')       #only renders the signup page, links to /userSignup that does all the actual work in db
def singup():
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
            print("Error in creating an admin user")
    return redirect(url_for('login'))


            
#chicken tinder routes 
#THESE ARE COMMENTED OUT BC WE DONT HAVE EVENTS SET UP SO TESTING ROUTE IN IN USE
#@app.route('/chicken-tinder')
#def chickenTinder():
    #return render_template('ChickenTinder.html')

#@app.route('/chickenTinderStart', methods = ['POST'])
#def chickenTinderStart():
    #username = request.form['username'].strip()
    #event_id = int(request.form['event_id'])

    #session['username'] = username
    #return redirect(url_for('chickenTinder', event_id=event_id))

#chicken tinder api endpoints
#get remaining restaurants
@app.route('/api/chickenTinder/nextRest', methods = ['GET'])
def getNextRestaurant():
    #get user and id
    username = request.args.get('username', 'testUser')
    eventId = int(request.args.get('eventId', 1))

    #get remaning
    remaining = getRemainingRestaurants(eventId, username)

    #if none return results
    if len(remaining) == 0:
        results = getResults(eventId)
        #format the results and then resturn them
        formatted_results = [{'id': r[0], 'name': r[1], 'imageUrl': r[2], 'votes': r[3]} for r in results]
        return jsonify({'done': True, 'results': formatted_results})

    #return next rest
    restaurant = remaining[0]
    return jsonify({
        'done': False,
        'restaurant': {'id': restaurant[0], 'name': restaurant[1], 'imageUrl': restaurant[2]},
        'remaining': len(remaining)
    })

#record vote on rest (yes or no)
@app.route('/api/chickenTinder/vote', methods = ['POST'])
def submitVote():
    data = request.json     #get vote data 
    
    #put vote in db 
    recordVote(int(data['eventId']), data['username'], int(data['restaurantId']), bool(int(data['vote'])))
    return jsonify({'success': True})

#display js test page :P
@app.route('/chickenTinderTest')
def chickenTinderTest():
    return render_template('chickenTinder.html')


if __name__=='__main__':    #main
    app.run(debug=True)