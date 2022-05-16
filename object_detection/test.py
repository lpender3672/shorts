

from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime

import ctypes
import _ctypes
import numpy as np
import pygame
import sys

import cv2
import open3d.cpu.pybind as o3d


kinect = PyKinectRuntime.PyKinectRuntime( PyKinectV2.FrameSourceTypes_Color |
                                          PyKinectV2.FrameSourceTypes_Body |
                                          PyKinectV2.FrameSourceTypes_Infrared |
                                          PyKinectV2.FrameSourceTypes_Depth  )


vis = o3d.visualization.Visualizer()
vis.create_window(width=1920, height=1080)
o3d.visualization.ViewControl.set_zoom(vis.get_view_control(), 0.1)


def get_new_PointCloud(color_raw, depth_raw):
    color_as_img = o3d.geometry.Image(color_raw.astype(np.uint8))
    depth_as_img = o3d.geometry.Image(depth_raw.astype(np.uint16))

    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(color_as_img, depth_as_img,
                                                                    convert_rgb_to_intensity=False, depth_scale=1000)
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image,
                                                         o3d.camera.PinholeCameraIntrinsic(
                                                             o3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault))

    pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])

    return pcd

def get_align_color_image(kinect, color_img, color_height=1080, color_width=1920, depth_height=424, depth_width=512):
    CSP_Count = kinect._depth_frame_data_capacity
    CSP_type = _ColorSpacePoint * CSP_Count.value
    CSP = ctypes.cast(CSP_type(), ctypes.POINTER(_ColorSpacePoint))

    kinect._mapper.MapDepthFrameToColorSpace(kinect._depth_frame_data_capacity,kinect._depth_frame_data, CSP_Count, CSP)

    colorXYs = np.copy(np.ctypeslib.as_array(CSP, shape=(depth_height*depth_width,))) # Convert ctype pointer to array
    colorXYs = colorXYs.view(np.float32).reshape(colorXYs.shape + (-1,)) # Convert struct array to regular numpy array https://stackoverflow.com/questions/5957380/convert-structured-array-to-regular-numpy-array
    colorXYs += 0.5
    colorXYs = colorXYs.reshape(depth_height,depth_width,2).astype(np.int)
    colorXs = np.clip(colorXYs[:,:,0], 0, color_width-1)
    colorYs = np.clip(colorXYs[:,:,1], 0, color_height-1)

    align_color_img = np.zeros((depth_height,depth_width, 4), dtype=np.uint8)
    align_color_img[:, :] = color_img[colorYs, colorXs, :]

    return align_color_img


newC = False
newD = False

obj_pcd  = o3d.geometry.PointCloud()
first_loop = True

while True:

    if not newC: newC = kinect.has_new_color_frame()
    if not newD: newD = kinect.has_new_depth_frame()

    if newC and newD:


        color_raw = (kinect.get_last_color_frame()).reshape((1080, 1920, 4))
        depth_raw = (kinect.get_last_depth_frame()).reshape((424, 512))

        aligned_color_raw = get_align_color_image(kinect, color_raw)[:,:,0:3][:,:,::-1] # GBRD to RGB

        pcd = get_new_PointCloud(aligned_color_raw, depth_raw)
        obj_pcd.points = pcd.points
        obj_pcd.colors = pcd.colors

        if first_loop:
            vis.add_geometry(obj_pcd)
            first_loop = False

        vis.update_geometry(obj_pcd)
        events = vis.poll_events()
        vis.update_renderer()

        newC,newD = False, False

    key = cv2.waitKey(30)
    if key == 27:
        break

















o3d.visualization.ViewControl.set_zoom(vis.get_view_control(), 0.1)
vis.run()

