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
print dev.get_sensor_info(openni2.SENSOR_DEPTH)

depth_stream = dev.create_depth_stream()
n_depth_frames = depth_stream.get_number_of_frames()
color_stream = dev.create_color_stream()
n_color_frames = color_stream.get_number_of_frames()

print "Detected",n_depth_frames,"depth frames."
print "Detected",n_color_frames,"color frames."

depth_stream.start()
color_stream.start()

print "Saving frames..."

c_rows = color_stream.get_video_mode().resolutionY
c_cols = color_stream.get_video_mode().resolutionX

c = 0
for i in range(0, n_color_frames):
     frame = color_stream.read_frame()
     frame_data = frame.get_buffer_as_triplet()
     color = numpy.ndarray((c_rows, c_cols, 3), numpy.dtype('uint8'), frame_data)
     fName = os.path.join(rgbDir, "rgb_"+str(c).zfill(5)+".png")
     cv2.imwrite(fName, color)
     cv2.imshow('test', color)
     cv2.waitKey(1)
     c += 1
print "Saved color frames."

d_rows = depth_stream.get_video_mode().resolutionY
d_cols = depth_stream.get_video_mode().resolutionX

depth = numpy.zeros((d_rows, d_cols))

c = 0
for i in range(0, n_depth_frames):

    frame = depth_stream.read_frame()
    frame_data = frame.get_buffer_as_uint16()

    points = []
    for j in range(d_rows):
        for k in range(d_cols):
            depth[j,k] = frame_data[j*d_cols+k]
            if depth[j, k]>0 and depth[j, k]<400:
                # Transform the data
                z = float(depth[j, k])/1000
                x = (float(k)-320)*z/570
                y = (float(j)-240)*z/570
                points.append([x, y, z])

    fName = os.path.join(depthDir, "depth_"+str(c).zfill(5)+".png")
    cv2.imwrite(fName, depth.astype('uint16'))
    cv2.imshow('test', depth/numpy.max(depth))
    cv2.waitKey(1)

    ply = open(os.path.join(depthDir, "ply_"+str(c).zfill(5)+".ply"), "w")
    ply.write("ply\n")
    ply.write("format ascii 1.0\n")
    ply.write("element vertex "+str(len(points))+"\n")
    ply.write("property float x\n")
    ply.write("property float y\n")
    ply.write("property float z\n")
    ply.write("end_header\n")
    for j in range(0, len(points)):
        ply.write(str(points[j][0])+" "+str(points[j][1])+" "+str(points[j][2])+"\n")
    ply.close()
    c += 1
print "Saved depth frames."


depth_stream.stop()
color_stream.stop()

openni2.unload()

print "Done!"
