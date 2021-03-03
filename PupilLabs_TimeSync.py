## pupil labs time sync
import zmq
import time 
from datetime import datetime
import csv
import sys

name = sys.argv[1]



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
subscriber.subscribe('pupil.0')  # 0 (0 = right, 1 = left) pupil  messages. Doesn't matter which if you just want timestamp 

# we need a serializer
import msgpack

timestamp = 0 



csvDirectory = "./timeSync_csvs/"
print(name)
with open(csvDirectory+name+'.csv', 'a', newline='') as csvFile: 
	print(name)
	csvWriter = csv.writer(csvFile, delimiter=',')
	csvWriter.writerow(['PupilLabsTimeStamp','TrueTime'])

	while True:
		topic, payload = subscriber.recv_multipart()
		message = msgpack.loads(payload)                                                              
		new_timestamp = message[b'timestamp']
		if new_timestamp - timestamp >= 1: 
			timestamp = new_timestamp
			now = datetime.now()
			current_time = now.strftime("%H:%M:%S.%f")
			csvWriter.writerow([current_time,timestamp])
			print("time: %s, pupil labs timestamp: %.2f, pupil diameter: %.2f" %(current_time, timestamp, message[b'diameter']))
