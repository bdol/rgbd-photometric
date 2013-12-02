from primesense import openni2
import os
import sys
import numpy
import cv2

if len(sys.argv)<3:
    print "Usage: python oni_to_frames.py <path to .oni> <out_dir>"
    sys.exit(1)

outDir = os.path.abspath(sys.argv[2])
rgbDir = os.path.join(outDir, "rgb")
depthDir = os.path.join(outDir, "depth")
if not os.path.isdir(outDir):
    os.mkdir(outDir)
    os.mkdir(rgbDir)
    os.mkdir(depthDir)

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

c = 0
for i in range(0, n_color_frames):
     frame = color_stream.read_frame()
     frame_data = frame.get_buffer_as_triplet()
     color = numpy.ndarray((rows, cols, 3), numpy.dtype('uint8'), frame_data)
     fName = os.path.join(rgbDir, "rgb_"+str(c).zfill(5)+".png")
     cv2.imwrite(fName, color)
     cv2.imshow('test', color)
     cv2.waitKey(1)
     c += 1
print "Saved color frames."

rows = 240
cols = 320
depth = numpy.zeros((rows, cols))

for i in range(0, n_depth_frames):
    frame = depth_stream.read_frame()
    frame_data = frame.get_buffer_as_uint16()
    for j in range(rows):
        for k in range(cols):
            depth[j,k] = frame_data[j*cols+k]
    cv2.imshow('test', depth/numpy.max(depth))
    cv2.waitKey(1)
print "Saved depth frames."


depth_stream.stop()
color_stream.stop()

openni2.unload()

print "Done!"
