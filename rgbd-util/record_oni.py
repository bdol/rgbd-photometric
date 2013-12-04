from primesense import openni2
import sys
import time

if len(sys.argv)<5:
    print "Usage: python record_oni.py <path of output .oni> <num frames> <delay (s)> <resolution>"
    sys.exit(1)

niRedistPath = "openni/Redist"
openni2.initialize(niRedistPath)

fileName = sys.argv[1]
dev = openni2.Device.open_any()
dev.set_depth_color_sync_enabled(True)

depth_stream = dev.create_depth_stream()
color_stream = dev.create_color_stream()

videoMode = color_stream.get_video_mode()
if int(sys.argv[4])==1:
    videoMode.resolutionX = 640
    videoMode.resolutionY = 480
elif int(sys.argv[4])==2:
    videoMode.resolutionX = 1280
    videoMode.resolutionY = 1024
else:
    videoMode.resolutionX = 320
    videoMode.resolutionY = 240
color_stream.set_video_mode(videoMode)
color_stream.camera.set_auto_exposure(False)
color_stream.camera.set_auto_white_balance(False)

videoMode = depth_stream.get_video_mode()
if int(sys.argv[4])==1:
    videoMode.resolutionX = 640
    videoMode.resolutionY = 480
elif int(sys.argv[4])==2:
    videoMode.resolutionX = 640
    videoMode.resolutionY = 480
else:
    videoMode.resolutionX = 320
    videoMode.resolutionY = 240
depth_stream.set_video_mode(videoMode)

dev.set_image_registration_mode(openni2.IMAGE_REGISTRATION_DEPTH_TO_COLOR)

depth_stream.start()
color_stream.start()
recorder = depth_stream.get_recoder(sys.argv[1]) # Note that this is mispelled in the API
recorder.attach(color_stream)

delay = int(sys.argv[3])
for i in range(0, delay):
    print "T-minus",delay-i
    time.sleep(1)

numFrames = int(sys.argv[2])
recorder.start()
for i in range(0, numFrames):
    depth_frame = depth_stream.read_frame()
    depth_frame_data = depth_frame.get_buffer_as_uint16()
    color_frame = color_stream.read_frame()
    color_frame_data = color_frame.get_buffer_as_triplet()
    print "Recorded frame",i+1,"of",numFrames
    
print "Saving",sys.argv[1]
recorder.stop()

depth_stream.stop()
color_stream.stop()

openni2.unload()

print "Done!"

