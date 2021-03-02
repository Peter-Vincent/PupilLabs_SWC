# PupilLabs_SWC
Documentation and example codes for using the Pupil Labs glasses

To get pupil labs eye glasses working: 
Go to docs.pupil-labs.com/core and download 
Go to Pupil Core
Download Pupil Core Software
Follow instructions on this pages to use glasses. You will have downloaded 3 pieces of software of which Pupil Capture allows recording of data, Pupil Player allows analysis of data in post and exporting to csv etc. 

To use time sync (draft): 
With the pupil capturre open (does not need to be recording) run PupilLabs_TimeSync.py. It should print out the PupilLabs timestamp and the (rught) eye pupil diameter. In future this will be changed to allowed it to recieve a signal sent from Bonsai and then it will write both the bonsai timestamp and the pupil labs time stamp to a csv for later syncing. 