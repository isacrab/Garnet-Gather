#all things to make the app actually run
from flask import Flask,render_template, request,redirect, url_for
from db import *
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
            



if __name__=='__main__':    #main
    app.run(debug=True)