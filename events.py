#Events backend
from db import createEvent, getEventById, getAllEvents, getEventMembers, joinEvent

def createAnEvent(createData, createdBy):
    eventName = createData['eventName']
    location = createData['location']
    eventDate = createData['eventDate']
    startTime = createData['startTime']
    endTime = createData['endTime']
    orgName = session.get('orgName')
    eventStatus = createData['eventStatus']
    description = createData.get('description', '')    #is optional so default is nothin
    eventType = createData['eventType']
    createdBy = createdBy
    isDiningEvent = True if createData.get('isDiningEvent') == '1' else False

    eventId = createEvent(eventName, location, eventDate, startTime, endTime, description, eventType, eventStatus, orgName, createdBy, isDiningEvent)
    return eventId

def getEvent(eventId):
    event = getEventById(eventId)
    members = getEventMembers(eventId)
    return event, members

def getEvents():
    events = getAllEvents() #from db.py
    return events

def joinAnEvent(eventId, username):
    joinEvent(eventId, username)