'''
Python script to handle the synchronisation between Bonsai and the eyelink code.

This script also launches the eye tracker and can be used to synchronise at the 
start of the task
'''
from datetime import datetime
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pylink import *
import time
import gc
import sys
import os
import subprocess


# Functions to handle message passing
def print_handler(address, *args):
    print(f"{address}: {args}")
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f"Current time : {current_time}")


def default_handler(address, *args):
    print(f"DEFAULT {address}: {args}")
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S.%f")
    message = (args[0] + "SS" + current_time)
    getEYELINK().sendMessage(message)
    print(f"Current time : {current_time}")
    if args[0] == "END":
        getEYELINK().sendMessage("BONSAI_END")
        getEYELINK().getRecordingStatus()
        endRealTimeMode()
        gc.enable()
        getEYELINK().setOfflineMode()
        msecDelay(500)

        #Close and clean up
        getEYELINK().receiveDataFile(file_name,file_name)
        getEYELINK().close()
        print('up to line 45')
        msecDelay(500)

        # Now convert the file to asc
        subprocess.run(["edf2asc64", file_name])
        exit()




############## Eyetracker code ##############

# Eyetracking parameters
host_machine_address = '100.1.1.1'
SCREENWIDTH = 800
SCREENHEIGHT= 600
RIGHT_EYE   = 1
LEFT_EYE    = 0
def end_session():
    #ends the data recording after a buffer of 1000msec
    endRealTimeMode()
    pumpDelay(1000)
    getEYELINK().stopRecording()
    while getEYELINK().getkey():
        pass
    return 0

eyelinktracker = EyeLink(host_machine_address) # Connect with the EyeLink computer
print(sys.argv[1])
file_name = sys.argv[1] + ".edf"
getEYELINK().openDataFile(file_name)

flushGetkeyQueue()

getEYELINK().setOfflineMode()
getEYELINK().sendCommand("screen_pixel_coords =  0 0 %d %d" %(SCREENWIDTH - 1, SCREENHEIGHT - 1))
getEYELINK().sendMessage("DISPLAY_COORDS  0 0 %d %d" %(SCREENWIDTH - 1, SCREENHEIGHT - 1))

tracker_software_ver = 0
eyelink_ver = getEYELINK().getTrackerVersion()
if eyelink_ver == 3:
    tvstr = getEYELINK().getTrackerVersionString()
    vindex = tvstr.find("EYELINK CL")
    tracker_software_ver = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))

if eyelink_ver>=2:
    getEYELINK().sendCommand("select_parser_configuration 0")
    if eyelink_ver == 2: #turn off scenelink camera stuff
        getEYELINK().sendCommand("scene_camera_gazemap = NO")
else:
    getEYELINK().sendCommand("saccade_velocity_threshold = 35")
    getEYELINK().sendCommand("saccade_acceleration_threshold = 9500")

# set link data (used for gaze cursor) 
getEYELINK().sendCommand("link_event_filter = LEFT,RIGHT,FIXATION,FIXUPDATE,SACCADE,BLINK,BUTTON,INPUT")
if tracker_software_ver>=4:
    getEYELINK().sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,PUPIL,AREA,STATUS,INPUT,BUTTON")
else:
    getEYELINK().sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,PUPIL,AREA,STATUS,INPUT,BUTTON")

#setCalibrationColors( (0, 0, 0),(255, 255, 255))    #Sets the calibration target and background color
#setTargetSize(SCREENWIDTH//70, SCREENWIDTH//300)     #select best size for calibration target
setCalibrationSounds("", "", "")
setDriftCorrectSounds("", "off", "off")


if (getEYELINK().isConnected() and not getEYELINK().breakPressed()):
    # Program is ready to launch
    print(" Calibrate and verify for the participant.  Exit setup when ready. ")
    print(" DO NOT START RECORDING ")
    getEYELINK().doTrackerSetup()
    print(" Setup complete - recording")
    message = ("record_status_message 'HUMAN_DELAYED_COMPARISON_TASK'")
    getEYELINK().sendCommand(message)
    getEYELINK().sendMessage("INITIALISING RECORDING PARAMETERS")
    getEYELINK().setOfflineMode()
    msecDelay(50)
    # setup is now complete, start the recording
    error = getEYELINK().startRecording(1, 1, 1, 1)
    if error:
        sys.exit(1)
    gc.disable()

    beginRealTimeMode(100)
    now = datetime.now()
    current_time = now.strftime("%D:%H:%M:%S")
    getEYELINK().sendMessage(current_time)
    try: 
        getEYELINK().waitForBlockStart(100,1,0) 
    except RuntimeError: 
        if getLastError()[0] == 0: # wait time expired without link data 
            print("ERROR: No link samples received!") 
            sys.exit(1)
        else: # for any other status simply re-raise the exception 
            raise
    eye_used = getEYELINK().eyeAvailable() #determine which eye(s) are available 
    if eye_used == RIGHT_EYE:
        getEYELINK().sendMessage("EYE_USED 1 RIGHT")
    elif eye_used == LEFT_EYE:
        getEYELINK().sendMessage("EYE_USED 0 LEFT")
        eye_used = LEFT_EYE
    else:
        print ("Error in getting the eye information!")
        sys.exit(1)
    #reset keys and buttons on tracker
    getEYELINK().flushKeybuttons(0)
    # pole for link events and samples

    dispatcher = Dispatcher()
    dispatcher.map("/ErrorSignal*", print_handler)
    dispatcher.set_default_handler(default_handler)

    ip = "127.0.0.1" # IP address of the display machine
    port = 1337

    server = BlockingOSCUDPServer((ip,port),dispatcher)
    server.serve_forever()

else:
    raise RuntimeError(" Connection to camera can not be established " )

# Launch the callback from messages from Bonsai

