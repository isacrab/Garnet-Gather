from db import getConnection
from flask import request, render_template

def schedulesubmit():
    username = request.form['username']
    event = request.form.getlist('event[]')
    day = request.form.getlist('dayofweek[]')
    start = request.form.getlist('startTime[]')
    end = request.form.getlist('endTime[]')
    
    for i in range(len(event)):
        createSchedules(username, event[i], day[i], start[i], end[i]) 
    return render_template('schedule_insert.html')

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
