import eventlet
import socketio
import json
import logging
import db
import requests
from typing import Optional

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
connections: dict[str, Optional[int]] = {}
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
    instance = dbInstance.pop(sid,None)
    if (instance is not None):
        instance.DeInit()


def getUserID(sid) -> Optional[int]:
    return connections[sid]

def isAuthenticatedUser(sid) -> bool:
    return getUserID(sid) is not None

def ValidateToken(token):
    userInfoDomain = "https://keycloak.dk4max.com/realms/CommunityGroups/protocol/openid-connect/userinfo"
    headers = {'Authorization': "Bearer " + token}
    r = requests.get(url=userInfoDomain,headers=headers)
    if (r.status_code == 401):
        return None
    elif (r.status_code == 200):
        return r.json()
    else:
        logger.error(f"Unexpected Response Code: {r.status_code}")
        return None

@sio.event
def connect(sid, environ):
    connections[sid] = None
    print('connect ', sid)

@sio.event
def Auth(sid, msg):
    # TODO Check how the token will be sent & then get the token
    token = msg
    userinfo = ValidateToken(token)
    if(userinfo is None):
        # Invalid Token
        # Maybe let them know
        logger.debug(f"Authentication failed for Session {sid}")
        logger.debug(f"Using token: {token}")
        sio.emit("status", "Token Error",to=sid)
        # Disconnect
        sio.disconnect(sid)
    else:
        # Valid Token
        # Get the User ID
        # This needs a Database Connection
        logger.debug(f"Authentication succeeded for Session {sid}")
        dbInstance = getDB_Instance(sid)
        sub = userinfo['sub']
        id = dbInstance.getUserIDbySUB(sub=sub)
        if (id is None):
            id = dbInstance.CreateUser(userinfo)
        logger.debug(f"Logged in {sub} as userID {id}")
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
    logger.debug(f'disconnect {sid}')

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)