from logging import PlaceHolder
from src.db import *
from flask import request, render_template, redirect, url_for
def schedulesubmit():
    username = request.form['username']
    event = request.form.getlist('event[]')
    day = request.form.getlist('dayofweek[]')
    start = request.form.getlist('startTime[]')
    end = request.form.getlist('endTime[]')
    
    for i in range(len(event)):
        createSchedules(username, event[i], day[i], start[i], end[i]) 
    return redirect(url_for('schedulepage'))#change to redirect url bc it would not keep the event on right side filled, but call the function and now it does

def viewschedule():
    username = request.args.get('username')
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT event, dayofweek, startTime, endTime
        FROM Schedules
        WHERE username = %s
        ORDER BY dayofweek, startTime
    """, (username,))
    schedules = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('view_schedule.html', username=username, schedules=schedules)

#added this
def deleteschedule():
   username = request.form.get('username')#get hte username and the event so that we only delete the event from the username schedule, and not all events
   event = request.form.get('event')
   conn = getConnection()
   cursor = conn.cursor()

   #must be an AND bc both things need to be true
   cursor.execute("""
        DELETE FROM Schedules
        WHERE username = %s AND event = %s  
        """, (username, event))
   conn.commit()
   
   cursor.close()
   conn.close()
   return redirect(url_for('schedulepage'))
