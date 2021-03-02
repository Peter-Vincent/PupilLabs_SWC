## pupil labs time sync


import zmq
import time 

ctx = zmq.Context()
# The REQ talks to Pupil remote and receives the session unique IPC SUB PORT
pupil_remote = ctx.socket(zmq.REQ)

ip = 'localhost'  # If you talk to a different machine use its IP.
port = 50020  # The port defaults to 50020. Set in Pupil Capture GUI.

pupil_remote.connect(f'tcp://{ip}:{port}')
# Request 'SUB_PORT' for reading data
pupil_remote.send_string('SUB_PORT')
sub_port = pupil_remote.recv_string()

# Request 'PUB_PORT' for writing data
pupil_remote.send_string('PUB_PORT')
pub_port = pupil_remote.recv_string()
# Assumes `sub_port` to be set to the current subscription port
subscriber = ctx.socket(zmq.SUB)
subscriber.connect(f'tcp://{ip}:{sub_port}')
subscriber.subscribe('pupil.0')  # 0 (right?) pupil  messages

# we need a serializer
import msgpack

timestamp = 0 

while True:
    topic, payload = subscriber.recv_multipart()
    message = msgpack.loads(payload)
    #print(f"{topic}: {message}")
    new_timestamp = message[b'timestamp']
    if new_timestamp - timestamp >= 1: 
    	timestamp = new_timestamp
    	print("timestamp: %.2f, pupil diameter: %.2f" %(timestamp, message[b'diameter']))
