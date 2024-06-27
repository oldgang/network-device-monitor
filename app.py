from flask import Flask, url_for, render_template, request, redirect, flash, session
from re import findall
from subprocess import Popen, PIPE, run
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import time
import json
import threading


app = Flask(__name__)
socketio = SocketIO(app, logger=True, engineio_logger=True)
activeRooms = {}

def ping(host, pingCount, timeoutMiliseconds='500'):
    pingCount = str(pingCount)
    output = Popen(["fping", host, '-c', pingCount, '-t', timeoutMiliseconds], stdout=PIPE)
    output.wait()
    stdout = output.stdout.read().decode('utf-8')
    status = findall(r'64 bytes', stdout)
    if status:
        result = 'UP'
    else:
        result = 'DOWN'
    return [stdout, result]

@socketio.on('clientConnect')
def handleConnect(jsonData):
    room = request.sid
    print(f'received connect from {room} - connecting')
    activeRooms[room] = 0
    join_room(room)
    emit('serverConnectionEstablished', room, to=room)

@socketio.on('clientIsActive')
def handleClientActivity():
    room = request.sid
    if room in activeRooms:
        activeRooms[room] = time.time()

@socketio.on('clientDisconnect')
def handleDisconnect(jsonData):
    room = request.sid
    if room in activeRooms:
        print(f'received disconnect from {room} - disconnecting')
        leave_room(room)
        activeRooms.pop(room, None)

@socketio.on('hostsToPing')
def handlePing(jsonData):
    room = request.sid
    hosts = jsonData['data'].split(' ')
    print(f'pinging {hosts} for {room}')
    pingCount = 1
    devices = {}
    lastPing = time.time()
    while room in list(activeRooms):
        if (time.time() - activeRooms[room] > 1 or activeRooms[room] == 0):
            for host in hosts:
                probeHost = ping(host, pingCount)
                output = probeHost[0]
                status = probeHost[1]
                devices[host] = {
                        'output': output,
                        'status': status
                        }
            emit('statusUpdate', json.dumps(devices), to=room)
            time.sleep(1)
        if time.time() - activeRooms[room] > 2 and activeRooms[room] != 0:
            print(f'{room} is inactive - disconnecting')
            leave_room(room)
            activeRooms.pop(room, None)

@app.route('/')
def hello():
    return 'Welcome to the Network Device Status Page!'

@app.route('/status')
def status():
    return render_template('status.html')

if __name__ == '__main__':
    app.run(app)




# Apps purpose:
# Show network devices and their status on a web page 
