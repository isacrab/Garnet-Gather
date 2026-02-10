# Garnet-Gather
Capstone proj CEN 4020L

To create a virtual env:
- navigate to the folder where the project is in and run python -m venv venv.
- activate it with the command: venv\Scripts\activate. There should now be a (venv) next to the path in the terminal.
- run pip install -r requirements.txt to make sure you have everything updated (run often to keep dependencies up to date)

If you add any dependencies, please add them in there and make sure you are in the virtual enviorment before you run pip install

Download mySql:
- go to their page and download their installer (https://dev.mysql.com/downloads/installer/) 
- download the type that includes a server
- when you get to window, download the web community option
- please please write down the password you choose we need it to access the db locally

Setting up .env file
- create a file in Garnet-Gather folder in vs code call it .env
- copy and paste this into it: 

DB_host="localhost"
DB_user="root"
DB_password="xxx"  -> fill in with ur password
DB_name="Garnet_Gatherdb"
DB_port=3306


To bring everything together!
- first time you test/run the db program, you need to create a schema on your local machine
    - go to the sql workbench, go to schemas, click create new schema and name it garnet_gatherdb (keep it this for the env variables)

To run application:
- python nameOfFile.py (you need to run both the db and the app, db will print out message if it init properly)
- click the url terminal provides
    - if its not running, you will get an error when you follow link


