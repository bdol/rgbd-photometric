from primesense import openni2
import sys
import cv2

if len(sys.argv)<2:
    print "Usage: python oni_to_frames.py <path to .oni>"
    sys.exit(1)

niRedistPath = "openni/Redist"
openni2.initialize(niRedistPath)

fileName = sys.argv[1]
dev = openni2.Device.open_file(fileName)


depth_stream = dev.create_depth_stream()
n_depth_frames = depth_stream.get_number_of_frames()
color_stream = dev.create_color_stream()
n_color_frames = color_stream.get_number_of_frames()

print "Detected",n_depth_frames,"depth frames."
print "Detected",n_color_frames,"color frames."

depth_stream.start()
color_stream.start()

print "Saving frames..."
nx = 640
ny = 480
for i in range(0, n_color_frames):
    frame = color_stream.read_frame()
    frame_data = frame.get_buffer_as_triplet()
print "Saved color frames."

for i in range(0, n_depth_frames):
    frame = depth_stream.read_frame()
    frame_data = frame.get_buffer_as_uint16()
print "Saved depth frames."


depth_stream.stop()
color_stream.stop()

openni2.unload()

print "Done!"
