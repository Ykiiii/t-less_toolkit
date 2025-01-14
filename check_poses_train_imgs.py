#!/usr/local/bin/python3
# Author: Tomas Hodan (hodantom@cmp.felk.cvut.cz)
# Center for Machine Perception, Czech Technical University in Prague

# A script to render 3D object models into the training images. The models are
# rendered at the 6D poses that are associated with the training images.
# The visualizations are saved into the folder specified by "output_dir".

from pytless import inout, renderer, misc
import os,cv2
import numpy as np
import scipy.misc
import matplotlib.pyplot as plt
import imageio

obj_ids = [5] # Choose which scene_ids to render. Eg. range(1, 31)
device = 'primesense' # options: 'primesense', 'kinect', 'canon'
model_type = 'cad' # options: 'cad', 'reconst'
im_step = 100 # Consider every im_step-th image

# Path to the T-LESS dataset
# Which you can download using the t-less_download.py script. 
data_path = 'E:/DataSets/t-less_v2'


# Path to the folder in which the images produced by this script will be saved
output_dir = os.path.join(data_path, 'output_check_poses_train_imgs')

# Paths to the elements of the T-LESS dataset
model_path_mask = os.path.join(data_path, 'models_' + model_type, 'obj_{}.ply')
obj_info_path_mask = os.path.join(data_path, 'train_{}', '{}', 'info.yml')
obj_gt_path_mask = os.path.join(data_path, 'train_{}', '{}', 'gt.yml')
rgb_path_mask = os.path.join(data_path, 'train_{}', '{}', 'rgb', '{}.{}')
depth_path_mask = os.path.join(data_path, 'train_{}', '{}', 'depth', '{}.png')
rgb_ext = {'primesense': 'png', 'kinect': 'png', 'canon': 'jpg'}
obj_colors_path = os.path.join('data', 'obj_rgb.txt')
vis_rgb_path_mask = os.path.join(output_dir, '{}_{}_{}_{}_rgb.png')
vis_depth_path_mask = os.path.join(output_dir, '{}_{}_{}_{}_depth_diff.png')

misc.ensure_dir(output_dir)
obj_colors = inout.load_colors(obj_colors_path)

plt.ioff() # Turn interactive plotting off

for obj_id in obj_ids:
    
    # Load object model
    model_path = model_path_mask.format('{:02d}'.format(obj_id))
    model = inout.load_ply(model_path)

    # Load info about the templates (including camera parameters etc.)
    obj_info_path = obj_info_path_mask.format(device, '{:02d}'.format(obj_id))
    obj_info = inout.load_info(obj_info_path)

    obj_gt_path = obj_gt_path_mask.format(device, '{:02d}'.format(obj_id))
    obj_gt = inout.load_gt(obj_gt_path)

    for im_id in obj_info.keys():
        
        if im_id % im_step != 0:
            continue
        print('obj: ' + str(obj_id) + ', device: ' + device + ', im_id: ' + str(im_id))

        
        im_info = obj_info[im_id]
        im_gt = obj_gt[im_id]

        # Get intrinsic camera parameters and object pose
        K = im_info['cam_K']
        R = im_gt[0]['cam_R_m2c']

        t = im_gt[0]['cam_t_m2c']
        # print(R)
        # print(t)

        # Visualization #1
        #-----------------------------------------------------------------------
        # Load RGB image
        rgb_path = rgb_path_mask.format(device, '{:02d}'.format(obj_id), '{:04}'.format(im_id), rgb_ext[device])
        # rgb = imageio.imread(rgb_path)
        rgb = cv2.imread(rgb_path)

        # Render RGB image of the object model at the pose associated with
        # the training image into a
        # surf_color = obj_colors[obj_id]
        surf_color = (1, 0, 0)
        im_size = (rgb.shape[1], rgb.shape[0])
        ren_rgb = renderer.render(model, im_size, K, R, t,
                                  surf_color=surf_color, mode='rgb')
        # print("ren_rgb",ren_rgb)
        # vis_rgb = 0.5 * rgb.astype(np.float) + 0.5 * ren_rgb.astype(np.float)
        # vis_rgb = vis_rgb.astype(np.uint8)

        vis_rgb = 0.5 * rgb + 0.5 * ren_rgb
        # vis_rgb = vis_rgb.astype(np.uint8)

        # Draw the bounding box of the object
        # vis_rgb = misc.draw_rect(vis_rgb, im_gt[0]['obj_bb'])

        # Save the visualization
        vis_rgb[vis_rgb > 255] = 255
        vis_rgb_path = vis_rgb_path_mask.format('{:02d}'.format(obj_id), device, model_type, '{:04}'.format(im_id))
        # imageio.imwrite(vis_rgb_path, vis_rgb.astype(np.uint8))
        cv2.imwrite(vis_rgb_path, vis_rgb.astype(np.uint8))
'''
        # Visualization #2
        #-----------------------------------------------------------------------
        if device != 'canon':
            # Load depth image
            depth_path = depth_path_mask.format(device, '{:02d}'.format(obj_id), '{:04}'.format(im_id), rgb_ext[device])
            # depth = imageio.imread(depth_path)  # Unit: 0.1 mm
            depth = cv2.imread(depth_path,cv2.IMREAD_GRAYSCALE)  # Unit: 0.1 mm

            depth = depth.astype(np.float64) * 0.1  # Convert to mm

            # Render depth image of the object model at the pose associated
            # with the training image
            im_size = (depth.shape[1], depth.shape[0])
            ren_depth = renderer.render(model, im_size, K, R, t, mode='depth')
            # print(ren_depth.shape)

            # Calculate the depth difference at pixels where both depth maps
            # are valid
            valid_mask = (depth > 0) * (ren_depth > 0)
            depth_diff = valid_mask * (depth - ren_depth.astype(np.float64))

            # Save the visualization
            vis_depth_path = vis_depth_path_mask.format('{:02d}'.format(obj_id), device,
                                                        model_type, '{:04}'.format(im_id))
            plt.matshow(depth_diff)
            plt.title('captured - rendered depth [mm]')
            plt.colorbar()
            plt.savefig(vis_depth_path)
            plt.close()
'''