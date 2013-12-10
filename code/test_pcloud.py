import cv2
import py_normals

im = cv2.imread("/Users/bdol/code/rgbd-photometric/rgbd-util/ein_0_med_frames/depth/depth_00000.png", -1)
pcloud = py_normals.depth_to_world(im)
nRows = pcloud.shape[0]
nCols = pcloud.shape[1]

points = []
for i in range(0, nRows):
    for j in range(0, nCols):
        x = pcloud[i, j, 0]
        y = pcloud[i, j, 1]
        z = pcloud[i, j, 2]
        valid = 0
        if z>0 and z<360:
            valid = 1
        points.append([x, y, -z, valid])
        

ply = open("plytest.ply", "w")
ply.write("ply\n")
ply.write("format ascii 1.0\n")
ply.write("obj_info is_mesh 0\n")
ply.write("obj_info num_cols "+str(nCols)+"\n")
ply.write("obj_info num_rows "+str(nRows)+"\n")
ply.write("element vertex "+str(nCols*nRows)+"\n")
ply.write("property float x\n")
ply.write("property float y\n")
ply.write("property float z\n")
ply.write("property uchar diffuse_red\n")
ply.write("property uchar diffuse_green\n")
ply.write("property uchar diffuse_blue\n")
ply.write("property float intensity\n")
ply.write("element range_grid "+str(nCols*nRows)+"\n")
ply.write("property list uchar int vertex_indices\n")
ply.write("end_header\n")

# Write data
for j in range(0, len(points)):
    ply.write(str(points[j][0])+" "+str(points[j][1])+" "+str(points[j][2])+" 150 150 150 0.9\n")
# Write vertex list
for j in range(0, len(points)):
    if points[j][3] == 1:
        ply.write("1 "+str(j)+"\n")
    else:
        ply.write("0\n")

ply.close()

