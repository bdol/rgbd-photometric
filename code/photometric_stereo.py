import numpy
import scipy.sparse
import scipy.sparse.linalg
import glob
import os
import cv2
import py_normals

def solve_for_L_and_N(M, rank=3):
    """
    Factorizes the measurement matrix M = LN (lighting direction * normals)
    returns (L, N)
    """
    U, D, V = numpy.linalg.svd(M,False, True)
    L = U[:,0:rank]
    N = V[0:rank,:]
    for i in range(rank):
        L[:,i] *= numpy.sqrt(D[i])
        N[i,:] *= numpy.sqrt(D[i])
    return (L, N)

def solve_for_A(N_ref, N):
    """
    Solves arg min A ||N_ref - A*N||_2 by solving the equivalent problem:
    N^T * A^T = N_ref^T
    """
    N_ref_t = numpy.transpose(N_ref)
    N_t = numpy.transpose(N)
    A_t, _, _, _ = numpy.linalg.lstsq(N_t, N_ref_t)
    print numpy.linalg.norm(N_ref - N)
    print numpy.linalg.norm(N_ref - numpy.dot(numpy.transpose(A_t),N))
    return numpy.transpose(A_t)

def integrate_normals(normals, mask, ref_depth, psi):
    M, N, _ = normals.shape
    pixel_to_idx = -1*numpy.ones((M, N), dtype=numpy.int32)

    # Create a mapping between pixel coordinates and indices when solving for
    # the depth map
    count = 0
    for i in range(M):
        for j in range(N):
            if mask[i,j]:
                pixel_to_idx[i,j] = count
                count += 1

    A = scipy.sparse.dok_matrix((3*count, count), dtype=numpy.float32)
    b = numpy.zeros(3*count)

    for i in range(M):
        for j in range(N):
            if mask[i,j]:
                idx = pixel_to_idx[i, j];
                row_idx1 = 2*idx;
                row_idx2 = 2*idx+1;

                # ref depth constraint
                A[2*count + idx, idx] = psi
                b[2*count + idx] = psi*ref_depth[i,j]
                #continue
                
                nx = normals[i, j, 0];
                ny = normals[i, j, 1];
                nz = normals[i, j, 2];
                # X
                if j + 1 < N and mask[i, j+1]:
                    # nz(z(i,j+1) - z(i,j) = -nx
                    idx2 = pixel_to_idx[i,j+1];
                    A[row_idx1, idx2] = nz;
                    A[row_idx1, idx]  = -nz;
                    b[row_idx1] = -nx;
                elif mask[i, j-1]:
                    # nz(z(i,j-1) - z(i,j) = nx
                    idx2 = pixel_to_idx[i,j-1];
                    A[row_idx1, idx2] = nz;
                    A[row_idx1, idx]  = -nz;
                    b[row_idx1] = nx;
                
                # Y
                if i + 1 < M and mask[i+1,j]:
                     # nz(z(i+1,j) - z(i,j) = -ny
                    idx2 = pixel_to_idx[i+1,j]
                    A[row_idx2, idx2] = nz;
                    A[row_idx2, idx]  = -nz;
                    b[row_idx2] = -ny;
                elif mask[i-1,j]:
                    # nz(z(i-1,j) - z(i,j) = ny
                    idx2 = pixel_to_idx[i-1,j];
                    A[row_idx2, idx2] = nz
                    A[row_idx2, idx] = -nz
                    b[row_idx2] = ny;

    A = scipy.sparse.csr_matrix(A)
    z, istop, itmax, r1norm = scipy.sparse.linalg.lsmr(A, b)[0:4]

    
    depth = numpy.zeros((M, N))
    for i in range(M):
        for j in range(N):
            idx = pixel_to_idx[i,j]
            if idx >= 0:
                depth[i, j] = z[idx]

    print numpy.linalg.norm(ref_depth[mask] - depth[mask])
    return depth

def make_M(image_filenames, roi):
    gamma = 1.0/2.2
    _, _, width, height = roi
    M = numpy.zeros((len(image_filenames), width*height))
    for (i, image_filename) in enumerate(image_filenames):
        image = cv2.imread(image_filename)
        image = apply_roi(image, roi)
        image = image[:,:,0].astype(numpy.float32)*1.0/255
        image = image**(gamma)
        #cv2.imshow('image', image)
        #cv2.waitKey()
        M[i, :] = image.reshape(-1)
    return M

def apply_roi(image, roi):
    x1, y1, width, height = roi
    x2 = x1 + width
    y2 = y1 + height
    return image[y1:y2, x1:x2]

def flatten_normals(normals):
    rows, cols, _ = normals.shape
    flat_normals = numpy.zeros((3, rows*cols))
    for i in range(rows):
        for j in range(cols):
            idx = i*cols+j
            flat_normals[:,idx] = normals[i,j,:]
    return flat_normals

def solve_bas_relief(ref_depth, depth, valid):
    height, width = depth.shape
    num_valid = numpy.sum(valid)

    A = numpy.ones((num_valid, 4))
    b = numpy.zeros((num_valid,))

    idx = 0
    for i in range(height):
        for j in range(width):
            if valid[i,j]:
                A[idx, 0] = j
                A[idx, 1] = i
                A[idx, 2] = depth[i,j]
                b[idx] = ref_depth[i,j]
                idx += 1

    t, _, _, _ = numpy.linalg.lstsq(A, b)
    return t

def fit_local_model(M, L, N):
    for i in range(M.shape[1]):
        errors = numpy.sqrt((M[:,i] - numpy.dot(L,N[:,i]))**2)
        max_error = numpy.max(errors)
        if max_error > 1e-5:
            rel_error = errors / max_error
            good_obs = numpy.logical_and(numpy.logical_and(rel_error < 0.1, M[:,i] > 0.25), M[:,i] < 0.8)
            if numpy.sum(good_obs) >= 5:
                N_i, _, _, _ = numpy.linalg.lstsq(L[good_obs,:], M[good_obs,i])
                N[:,i] = N_i


def main():
    video_dir = r'C:\Projects\GitHub\rgbd-photometric\rgbd-util\out'
    depth_dir = os.path.join(video_dir, 'depth')
    rgb_dir = os.path.join(video_dir, 'rgb')

    depth_image_filenames = glob.glob(os.path.join(depth_dir, '*.png'))
    rgb_image_filenames = glob.glob(os.path.join(rgb_dir, '*.png'))
    depth_image_filenames = depth_image_filenames[0:10]

    im = cv2.imread(depth_image_filenames[0], -1)
    im[im>475] = 0
    width = 80
    height = 160
    roi = [50, 20, width, height]

    im = apply_roi(im, roi)

    pcloud = py_normals.depth_to_world(im)
    ref_normals, valid = py_normals.get_normals(pcloud)
    flat_ref_normals = flatten_normals(ref_normals)

    #cv2.imshow("Normals", normals)
    #cv2.imshow("valid", valid)
    #cv2.waitKey(0)

    M = make_M(rgb_image_filenames, roi)
    L, N = solve_for_L_and_N(M,3)
    fit_local_model(M, L, N)
    # normals_image = numpy.zeros((height, width, 3))
    # for i in range(height):
    #     for j in range(width):
    #         idx = i*width+j
    #         normals_image[i, j, :] = N[:,idx]

    # cv2.imshow('normals', normals_image)
    # cv2.waitKey()
    A = solve_for_A(flat_ref_normals, N)

    N = numpy.dot(A,N)

    normals_image = numpy.zeros((height, width, 3))
    for i in range(height):
        for j in range(width):
            idx = i*width+j
            normals_image[i, j, :] = N[:,idx]

    #cv2.imshow('normals', normals_image)
    #cv2.waitKey()
    depth = integrate_normals(normals_image, pcloud[:,:,2]>0, pcloud[:,:,2], 0.3)

    t = solve_bas_relief(pcloud[:,:,2], depth, pcloud[:,:,2]>0)
    #t = [1, 1, 1, 1]
    #t = solve_bas_relief(pcloud[:,:,2], depth, valid)

    indices = -1*numpy.ones((height, width), numpy.int32)
    out = open('test.obj', 'w')
    out2 = open('depth.obj', 'w')
    count = 0
    for i in range(height):
        for j in range(width):
            x, y = pcloud[i,j,0:2]
            #valid[i,j] = numpy.linalg.norm(normals_image[i,j,:]) > 0.01
            if valid[i,j]:
                out.write('v {0} {1} {2}\n'.format(j, -i,-(t[0]*j + t[1]*i + t[2]*depth[i,j] + t[3])))
                if pcloud[i,j,2] != 0: out2.write('v {0} {1} {2}\n'.format(j, -i,-pcloud[i,j,2]))
                #out.write('v {0} {1} {2}\n'.format(pcloud[i,j,0], pcloud[i,j,1],-pcloud[i,j,2]))
                indices[i,j] = count
                count += 1


    for i in range(height):
        for j in range(width):
            if valid[i,j] and i + 1 < height and j + 1 < width:
                idx1 = indices[i,j]
                idx2 = indices[i+1,j]
                idx3 = indices[i, j+1]
                idx4 = indices[i+1,j+1]
                if idx4 >= 0:
                    if idx2 >= 0:
                        out.write('f {0} {1} {2}\n'.format(idx4+1, idx1+1, idx2+1))
                    if idx3 >= 0:
                        out.write('f {0} {1} {2}\n'.format(idx4+1, idx3+1, idx1+1))
                count += 1



if __name__ == '__main__':
    main()