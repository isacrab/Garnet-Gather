#functions for everything role based/auth based 
import mysql.connector
import os
from db import *

#authentication function to check if the entered email is an @fsu.edu email
def realEmail(email):
    email=email.strip().lower() #case sensistive and remove whitespace 
    return email.endswith('@fsu.edu')