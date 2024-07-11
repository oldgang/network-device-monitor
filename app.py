from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
import time
import json
from communication import ping, ping_multiple


app = Flask(__name__)
socketio = SocketIO(app, logger=True, engineio_logger=True)
activeRooms = {}

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
    if hosts is None or hosts == ['']:
        devices = {}
        emit('statusUpdate', json.dumps(devices), to=room)
        activeRooms.pop(room, None)
        leave_room(room)
        return
    print(f'pinging {hosts} for {room}')
    pingCount = 1
    devices = {}
    while room in list(activeRooms):
        if (time.time() - activeRooms[room] > 1 or activeRooms[room] == 0):
            for host in hosts:
                pingResult = ping(host, pingCount)
                output = pingResult[0]
                status = pingResult[1]
                if ': [0], 64 bytes,' in output:
                    output = ': '.join(output.split(': [0], 64 bytes,'))
                else:
                    output = f'{host}: unreachable'
                    
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
    # ping_multiple(['10.1.0.1', '10.1.0.2'], 5)



# Apps purpose:
# Show network devices and their status on a web page 
