import eventlet
import socketio
import json

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

@sio.event
def connect(sid, environ):
    print('connect ', sid)

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
    print('disconnect ', sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)