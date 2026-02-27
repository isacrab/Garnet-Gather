#all things to make the app actually run
from flask import Flask,render_template, request,redirect, url_for, jsonify
from db import *
from chicken_tinder import recordVote, getRemainingRestaurants, getResults

app = Flask(__name__)

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
