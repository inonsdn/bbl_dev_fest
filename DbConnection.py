import time
from uuid import uuid4

TokenPeriod_secs = 15 * 60

class Token:
    def __init__( self, token, timeout ):
        self.token = token
        self.timeout = timeout

    def isValid( self ):
        return time.time() <= self.timeout


class UserModel:
    def __init__( self, userId: bytes, username, password, isAdmin=False, token: Token = None ):
        self.userId = userId
        self.username = username
        self.password = password
        self.isAdmin = isAdmin
        self.token = token

class Appointment:
    def __init__( self, appointmentId: bytes, user: UserModel, slot: str ):
        self.appointmentId = appointmentId
        self.user = user
        self.slot = slot

class DbConnection:
    ''' this is class to mocking db connection
        that connect to storage
    '''
    def __init__( self ):
        '''
        '''
        self.userIdToUserInfoDict: dict[bytes, UserModel] = dict()
        self.tokenToUserInfoDict: dict[str, UserModel] = dict()
        self.appointmentIdToAppointmentDict: dict[bytes, Appointment] = dict()

        self.mock()

    def mock(self):
        adminId = uuid4().bytes
        user1 = uuid4().bytes
        self.userIdToUserInfoDict[ adminId ] = UserModel( adminId, 'admin', 'admin', isAdmin=True )
        self.userIdToUserInfoDict[ user1 ] = UserModel( user1, 'user1', 'test1234', isAdmin=False )

    def createUser( self, userId: bytes, username, password, isAdmin=False ):
        if userId in self.userIdToUserInfoDict:
            raise ValueError( f'User id {userId} is already exist' )

        self.userIdToUserInfoDict[ userId ] = UserModel( userId, username, password, isAdmin )

    def getUserFromUsernameAndPassword( self, username: str, password ) -> UserModel:
        user = None
        for userId, userObj in self.userIdToUserInfoDict.items():
            if userObj.username == username and userObj.password == password:
                user = userObj
                break
        return user

    def updateUserToken( self, user: UserModel, token: str ):
        tokenTimeout = time.time() + TokenPeriod_secs
        tokenObj = Token( token, tokenTimeout )

        # remove old token
        if user.token is not None and user.token.token in self.tokenToUserInfoDict:
            self.tokenToUserInfoDict.pop(user.token.token)

        user.token = tokenObj

        self.tokenToUserInfoDict[ token ] = user

    def getUserFromToken( self, token ):
        if token not in self.tokenToUserInfoDict:
            return None
        
        return self.tokenToUserInfoDict[ token ]

    def createAppointment( self, user: UserModel, slot: str ):
        appointmentId = uuid4().bytes

        self.appointmentIdToAppointmentDict[ appointmentId ] = Appointment( appointmentId, user, slot )

        return appointmentId

    def getAllAppointments( self ):
        return list( self.appointmentIdToAppointmentDict.values() )
    
    def getAppointmentOfUser( self, user ):
        appointmentList = list()
        for appointment in self.appointmentIdToAppointmentDict.values():
            if appointment.user == user:
                appointmentList.append( appointment )
        return appointmentList

    def getAppointmentById( self, appointmentId ):
        return self.appointmentIdToAppointmentDict.get( appointmentId )
    
    def deleteAppointment( self, appointment ):

        del self.appointmentIdToAppointmentDict[ appointment.appointmentId ]
