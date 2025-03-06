#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Compute fabric tensor by the 3D Auto Correlation Function (ACF) of images.
For more information, call this script with the help option:
    pyfabric.py -h

"""

__author__ = ['Gianluca Iori']
__date_created__ = '2024-04-26'
__date__ = '2024-04-26'
__copyright__ = 'Copyright (c) 2024, ORMIR'
__docformat__ = 'restructuredtext en'
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = 'Gianluca Iori'
__email__ = "gianthk.iori@gmail.com"

import numpy as np
import pandas as pd
import heapq
import SimpleITK as sitk
from skimage.measure import label, regionprops, regionprops_table

#################################################################################

def dist_table(coors):
    n_points = coors.shape[0]
    disttab = np.zeros([n_points, n_points])
    for i in range(n_points):
        for j in range(n_points):
            disttab[i,j] = np.linalg.norm(coors[i,:]-coors[j,:])
    return disttab

def markers_coors(BWimage):
    # get coordinates of 5 cement markers from binary image

    label_img = label(BWimage)

    props = regionprops_table(label_img, properties=('centroid', 'area'))

    props_df = pd.DataFrame(props)

    props_df.sort_values('area', ascending=False, inplace=True)
    props_df.reset_index(drop=True, inplace=True)

    markers_df = props_df[1:6]
    centroids = markers_df[['centroid-0', 'centroid-1', 'centroid-2']].to_numpy()

    distances = dist_table(centroids)

    for row in distances:
        row.sort()

    sum2dist = np.sum(distances[:, 0:3], axis=1).tolist()
    min_3_dists = heapq.nsmallest(3, sum2dist)

    count = 0
    marker_id = np.zeros(3)
    for dist in min_3_dists:
        marker_id[count] = sum2dist.index(dist)
        count = count + 1

    M5_id = int(marker_id[0])
    M1_id = int(marker_id[1])
    M2_id = int(marker_id[2])

    sum3dist = np.sum(distances[:, 0:4], axis=1).tolist()
    max_2_dists = heapq.nlargest(2, sum3dist)

    count = 0
    marker_id = np.zeros(2)
    for dist in max_2_dists:
        marker_id[count] = sum3dist.index(dist)
        count = count + 1

    M3_id = int(marker_id[0])
    M4_id = int(marker_id[1])

    marker_coors = np.zeros([5, 3])
    marker_coors[0, :] = centroids[M1_id, :]
    marker_coors[1, :] = centroids[M2_id, :]
    marker_coors[2, :] = centroids[M3_id, :]
    marker_coors[3, :] = centroids[M4_id, :]
    marker_coors[4, :] = centroids[M5_id, :]

    return marker_coors

def resample_img(itk_image, out_spacing=[2.0, 2.0, 2.0], is_label=False):
    # Source: https://gist.github.com/mrajchl/ccbd5ed12eb68e0c1afc5da116af614a

    # Resample images to 2mm spacing with SimpleITK
    original_spacing = itk_image.GetSpacing()
    original_size = itk_image.GetSize()

    out_size = [
        int(np.round(original_size[0] * (original_spacing[0] / out_spacing[0]))),
        int(np.round(original_size[1] * (original_spacing[1] / out_spacing[1]))),
        int(np.round(original_size[2] * (original_spacing[2] / out_spacing[2])))]

    resample = sitk.ResampleImageFilter()
    resample.SetOutputSpacing(out_spacing)
    resample.SetSize(out_size)
    resample.SetOutputDirection(itk_image.GetDirection())
    resample.SetOutputOrigin(itk_image.GetOrigin())
    resample.SetTransform(sitk.Transform())
    resample.SetDefaultPixelValue(itk_image.GetPixelIDValue())

    if is_label:
        resample.SetInterpolator(sitk.sitkNearestNeighbor)
    else:
        resample.SetInterpolator(sitk.sitkBSpline)

    return resample.Execute(itk_image)

def vectors2rotation3Dmatrix(a,b):
    # VECTORS2ROTATION3DMATRIX rotation matrix R that rotates vector a onto vector b
    #    R = vectors2rotation3Dmatrix(a, b)
    #    Returns 3x3 rotation matrix that transforms vector a into vector b.

    #  Example: rotate (clockwise) vector of 90deg around Z-axis.
    #    R = vectors2rotation3Dmatrix([0 1 0], [1 0 0]);
    #    R*[1; 0; 4]
    #    ans =
    #            0
    #            -1
    #            4

    #    See: http://math.stackexchange.com/questions/180418/calculate-rotation-matrix-to-align-vector-a-to-vector-b-in-3d
    #    ______________________________________________________

    #    Author:         Gianluca Iori (gianthk.iori@gmail.com)
    #    BSRT - Charite Berlin
    #    Created on:   01/01/2016
    #    Last update:  19/04/2016

    #    See also CROSS, DOT, NORM, EYE.

    #    this class is part of the synchro toolbox
    #    ______________________________________________________

    a = a/np.linalg.norm(a);
    b = b/np.linalg.norm(b);

    v = np.cross(a,b);
    s = np.linalg.norm(v);
    c = np.dot(a,b);
    skewv = [[0, -v[2], v[1]],
             [v[2], 0, -v[0]],
             [-v[1], v[0], 0]]

    R = np.eye(3) + skewv + np.matmul(skewv, skewv)*((1 - c)/(s**2));
#     return skewv
    return R

def align_with_XYplane(n12, n14):
    # return affine rotation matrix aligning the plane defined by vectors n12 and n14 with the X-Y plane
    angle_n12_n14 = np.arctan2(np.linalg.norm(np.cross(n12, n14)), np.dot(n12, n14))
    print('Angle between n12 and n14:', abs(angle_n12_n14 / np.pi * 180), 'deg')

    # Allign n12 with -X versor and n14 with +Y versor
    R_n12_x = vectors2rotation3Dmatrix(n12, [-1, 0, 0])
    n12_1 = np.matmul(R_n12_x, n12)
    n14_1 = np.matmul(R_n12_x, n14)

    R_n14_1_y = vectors2rotation3Dmatrix(n14_1, [0, 1, 0])
    n12_2 = np.matmul(R_n14_1_y, n12_1)
    n14_2 = np.matmul(R_n14_1_y, n14_1)

    return np.matmul(R_n14_1_y, R_n12_x)

def align_with_vectors(n12, n14, v12, v14):
    # return affine rotation matrix aligning the plane defined by vectors n12 and n14 with the plane defined by vectors v12 and v14
    angle_n12_n14 = np.arctan2(np.linalg.norm(np.cross(n12, n14)), np.dot(n12, n14))
    print('Angle between n12 and n14:', abs(angle_n12_n14 / np.pi * 180), 'deg')

    angle_v12_v14 = np.arctan2(np.linalg.norm(np.cross(v12, v14)), np.dot(v12, v14))
    print('Angle between v12 and v14:', abs(angle_v12_v14 / np.pi * 180), 'deg')

    # Allign n12 with v12 versor and n14 with v14 versor
    R_n12_v12 = vectors2rotation3Dmatrix(n12, v12)
    n12_1 = np.matmul(R_n12_v12, n12)
    n14_1 = np.matmul(R_n12_v12, n14)

    R_n14_1_v14 = vectors2rotation3Dmatrix(n14_1, v14)
    n12_2 = np.matmul(R_n14_1_v14, n12_1)
    n14_2 = np.matmul(R_n14_1_v14, n14_1)

    return np.matmul(R_n14_1_v14, R_n12_v12)

def resample(image, transform):
    # Output image Origin, Spacing, Size, Direction are taken from the reference
    # image in this call to Resample
    reference_image = image
    interpolator = sitk.sitkCosineWindowedSinc
    default_value = 100.0

    return sitk.Resample(image, reference_image, transform, interpolator, default_value)

def affine_trans(image, tmatrix, verbose=False):
    # the transformation is applied around the center of the image not around its origin

    transform = sitk.AffineTransform(image.GetDimension())
    if verbose:
        print(tmatrix)
    transform.SetMatrix(tmatrix.ravel())
    transform.SetInverse()
    transform.SetCenter(np.array(image.GetSize()) / 2 * image.GetSpacing() + image.GetOrigin())
    resampled = resample(image, transform)

    return resampled
