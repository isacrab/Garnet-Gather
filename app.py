#all things to make the app actually run
from flask import Flask,render_template, request
app = Flask(__name__)

@app.route('/') #home page for now
def homepage():
    return render_template('home.html')

@app.route('/login')    #login page for right now, that name /... name matches the a ref in the corresponding html
def login():
    return render_template('login.html')

if __name__=='__main__':    #main
    app.run(debug=True)

