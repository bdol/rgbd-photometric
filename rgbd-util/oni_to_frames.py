from primesense import openni2
import sys
import numpy
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

rows = 240
cols = 320

for i in range(0, n_color_frames):
     frame = color_stream.read_frame()
     frame_data = frame.get_buffer_as_triplet()
     color = numpy.ndarray((rows, cols, 3), numpy.dtype('uint8'), frame_data)
     cv2.imshow('test', color)
     cv2.waitKey(1)
print "Saved color frames."

rows = 240
cols = 320
depth = numpy.zeros((rows, cols))

for i in range(0, n_depth_frames):
    frame = depth_stream.read_frame()
    frame_data = frame.get_buffer_as_uint16()
    print len(frame_data)
    for j in range(rows):
    	for k in range(cols):
    		#print j*cols+k
    		depth[j,k] = frame_data[j*cols+k]
    cv2.imshow('test', depth/numpy.max(depth))
    cv2.waitKey(1)
print "Saved depth frames."


depth_stream.stop()
color_stream.stop()

openni2.unload()

print "Done!"
