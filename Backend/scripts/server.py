import eventlet
import socketio
import json
import logging
import db

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

logger = logging.getLogger('CC')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch.setFormatter(formatter)
logger.addHandler(ch)

# Saves all Connections as a Key Value Pair
# Where sid is the Key and the Value is:
# - None for non authenticated Clients
# - User ID for an authenticated Client
connections: dict[str, int | None] = {}
# Not sure if this is the Best way to handle that
# Where sid is the Key and the Value is the DB Instance
dbInstance: dict[str, db.Database] = {}

def getDB_Instance(sid) -> db.Database:
    if (sid in dbInstance):
        return dbInstance[sid]
    else:
        dbInstance[sid] = db.Database()
        return dbInstance[sid]

def closeDB_Instance(sid):
    instance = dbInstance.pop(sid)
    instance.DeInit()


def getUserID(sid) -> int | None:
    return connections[sid]

def isAuthenticatedUser(sid) -> bool:
    return getUserID(sid) is not None

def ValidateToken(token) -> str | None:
    userInfoDomain = "https://keycloak.dk4max.com/realms/CommunityGroups/protocol/openid-connect/userinfo"
    # TODO Make Request and retun
    # sub if it is Valid
    # None if it is Invalid
    return "sub"

@sio.event
def connect(sid, environ):
    connections[sid] = None
    print('connect ', sid)

@sio.event
def Auth(sid, msg):
    # TODO Check how the token will be sent & then get the token
    token = msg
    sub = ValidateToken(token)
    if(sub in None):
        # Invalid Token
        # Maybe let them know
        sio.emit("status", "Token Error",to=sid)
        # Disconnect
        # TODO Check if the Disconnect event will be called
        sio.disconnect(sid)
    else:
        # Valid Token
        # Get the User ID
        # This needs a Database Connection
        id = getDB_Instance(sid).getUserIDbySUB(sub=sub)
        connections[sid] = id
        sio.emit("status", "Auth Success",to=sid)

@sio.event
def my_message(sid, data):
    print('message ', data)

@sio.on("new chat message 1")
def myMessage(sid, data):
    message = data["message"]
    print(message)
    sio.emit("message chat 2", data)

@sio.on("new chat message 2")
def myMessage(sid, data):
    message = data["message"]
    print(message)
    sio.emit("message chat 1", data)

@sio.event
def disconnect(sid):
    connections.pop(sid,None)
    closeDB_Instance(sid)
    print('disconnect ', sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)