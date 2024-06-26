from flask import Flask, url_for, render_template, request, redirect, flash, session
from re import findall
from subprocess import Popen, PIPE, run
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import time
import json

app = Flask(__name__)
socketio = SocketIO(app, logger=True, engineio_logger=True)
activeRooms = []

def ping(host, pingCount, timeoutMiliseconds='250'):
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
    print('received json: ' + str(jsonData))
    room = request.sid
    activeRooms.append(room)
    join_room(room)
    emit('serverConnect', room, to=room)
    hosts = ['10.1.54.51', '10.1.54.54']
    pingCount = 1
    devices = {}
    while room in activeRooms:
        for host in hosts:
            probeHost = ping(host, pingCount)
            output = probeHost[0]
            status = probeHost[1]
            devices[host] = {
                    'output': output,
                    'status': status
                    }
        print(json.dumps(devices))
        emit('statusUpdate', json.dumps(devices), to=room)
        time.sleep(1)

@socketio.on('clientDisconnect')
def handleDisconnect(jsonData):
    print('received json: ' + str(jsonData))
    room = request.sid
    leave_room(room)
    activeRooms.remove(room)

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
