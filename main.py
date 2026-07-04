# Python Developer Assessment (1-1.30 hrs)
# Objective:
# Create a simple web application or backend (REST APIs) that allows users to log in and perform
# appointment bookings. The application should have a frontend for login and booking, and a backend for
# authentication, authorization, and booking management.

# Requirements:
# 1. Frontend (Optional):
# o Create a login page where users can enter their username and password.
# o Create a appointment booking page where users can book a time slot (as a string/text
# for simplicity e.g. 10am-11am).
# o Use any frontend framework or library (e.g., HTML/CSS, JavaScript, React, etc.).
# 2. Backend:
# o Implement user authentication (login) and authorization.
# o Only users with admin rights can view all appointments.
# o Users without admin rights can only manage their own bookings.
# o Use Python and any web framework (e.g., Flask, Django, FastAPI, etc.).

from DbConnection import DbConnection
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4

class LoginRequest(BaseModel):
	username: str
	password: str

class AppointmentRequest(BaseModel):
	slot: str

# create app for api
app = FastAPI()

# allow the standalone login.html / booking.html pages to call this API
app.add_middleware(
	CORSMiddleware,
	allow_origins=['*'],
	allow_methods=['*'],
	allow_headers=['*'],
)

# mocking db connection object
DbConnectionObj = DbConnection()

# seed a couple of users so login works out of the box
DbConnectionObj.createUser( b'admin-id', 'admin', 'admin123', isAdmin=True )
DbConnectionObj.createUser( b'user-id', 'user', 'user123', isAdmin=False )

def getUserFromAuthorization( authorization: str = Header(None) ):
	if not authorization:
		raise HTTPException(status_code=401, detail='Missing token')

	token = authorization.replace('Bearer ', '')
	userObj = DbConnectionObj.getUserFromToken( token )
	if not userObj:
		raise HTTPException(status_code=401, detail='Invalid token')

	if not userObj.token.isValid():
		raise HTTPException(status_code=401, detail='Token is expired')

	return userObj

@app.post('/login')
def login( req: LoginRequest ):
	''' handle request of login with rest api
	'''
	# get user info of given username and password
	userObj = DbConnectionObj.getUserFromUsernameAndPassword( req.username, req.password )
	if userObj is None:
		raise HTTPException(status_code=401, detail = 'Invalid username or password'  )

	# generate token to use after login
	token = uuid4().bytes.hex()
	DbConnectionObj.updateUserToken( userObj, token )

	return {
		'token': token,
		'user_id': userObj.userId.hex(),
		'username': req.username,
		'is_admin': userObj.isAdmin,
	}

@app.post('/appointments')
def createAppointment(req: AppointmentRequest, authorization: str = Header(None)):
	userObj = getUserFromAuthorization(authorization)

	appointmentId = DbConnectionObj.createAppointment( userObj, req.slot )

	return {
		'id': appointmentId.hex(),
	}

@app.get('/appointments')
def getAppointments(authorization: str = Header(None)):
	userObj = getUserFromAuthorization(authorization)

	if userObj.isAdmin:
		appointmentList = DbConnectionObj.getAllAppointments()
	else:
		appointmentList = DbConnectionObj.getAppointmentOfUser( userObj )

	appointmentResponseDictList = list()
	for appointment in appointmentList:
		appointmentResponseDictList.append({
			'appointmentId': appointment.appointmentId.hex(),
			'user': appointment.user.username,
			'slot': appointment.slot,
		})

	return appointmentResponseDictList

@app.put('/appointments/{appointmentId}')
def updateAppointment(
	appointmentId: str,
	req: AppointmentRequest,
	authorization: str = Header(None)
):
	userObj = getUserFromAuthorization(authorization)

	appointment = DbConnectionObj.getAppointmentById( bytes.fromhex(appointmentId) )

	if not appointment:
		raise HTTPException(status_code=404, detail='Appointment not found')

	if not userObj.isAdmin and appointment.user.userId != userObj.userId:
		raise HTTPException(status_code=403, detail='Forbidden')

	appointment.slot = req.slot

	return {
		'appointmentId': appointment.appointmentId.hex(),
		'user': appointment.user.username,
		'slot': appointment.slot,
	}

@app.delete('/appointments/{appointmentId}')
def deleteAppointment(appointmentId: str, authorization: str = Header(None)):
	userObj = getUserFromAuthorization(authorization)

	appointment = DbConnectionObj.getAppointmentById( bytes.fromhex(appointmentId) )

	if not appointment:
		raise HTTPException(status_code=404, detail='Appointment not found')

	if not userObj.isAdmin and appointment.user.userId != userObj.userId:
		raise HTTPException(status_code=403, detail='Forbidden')

	DbConnectionObj.deleteAppointment( appointment )

	return {'message': 'Appointment deleted'}