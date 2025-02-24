import math
import pyfabric
# import sys
# sys.path.append('/home/gianthk/PycharmProjects/recon_utils')
import recon_utils as ru
import numpy as np
from numpy import linalg

import matplotlib.pyplot as plt
import ellipsoid_fit as ef

# I = ru.read_tiff_stack('/home/gianthk/Data/StefanFly_test/test_00__rec/test_00__rec_mini/recon_0000.tif')
I = ru.read_tiff_stack('/home/gianthk/Data/2019.001.coop_TUberlin_simulierte_Mensch.iorig/trabecular_samples/trabecular_sample_mini2/2000L_crop_imgaussfilt_60micron_uint8_0000.tif')
# I = ru.read_tiff_stack('/home/gianthk/Data/StefanFly_test/test_00__rec/test_00__rec_mini2/recon_0000.tif')
# I = ru.read_tiff_stack('/home/gianthk/Data/StefanFly_test/test_00__rec/test_00__rec/recon_00000.tiff')

# pointset = np.array([[545, 542, 507], [649, 461, 522], [530, 301, 508]])

# fabric of one image
# evecs, radii, evals, fabric_comp, DA = pyfabric.fabric(I[507 - 25:507 + 25, 542 - 25:542 + 25, 545 - 25:545 + 25])
evecs, radii, evals, fabric_comp, DA = pyfabric.fabric(I, zoom=True, zoom_factor=3, ACFplot=True)

print(evecs)
# [[ 0.2835969  -0.94720833 -0.14956327]
#  [-0.92224651 -0.22667266 -0.31317866]
#  [-0.26274354 -0.2267507   0.93784325]]

print(radii)
# [-1.8468693   1.98776173  3.0614825 ]

print(evals)
# [0.2931755  0.25308788 0.10669313]

print(fabric_comp)
# [ 0.25303729  0.27282543  0.1270938  -0.0173419   0.05271177  0.01754728]

# fabric tensor
fabric_tensor = np.array([[fabric_comp[0], fabric_comp[3], fabric_comp[5]],
                 [fabric_comp[3], fabric_comp[1], fabric_comp[4]],
                 [fabric_comp[5], fabric_comp[4], fabric_comp[2]]])

# fabric_tens = np.matmul(evecs, np.matmul((evals * np.identity(3)), np.transpose(evecs)))

# find the rotation matrix and radii of the axes
U, s, R = linalg.svd(fabric_tensor)
radii = 1.0/np.sqrt(s)

# get Euler angles
# theta_x = math.atan2(R[2,1], R[2,2])
# theta_y = math.atan2(-R[2,0], np.sqrt(R[2,1]**2+R[2,2]**2))
# theta_z = math.atan2(R[1,0], R[0,0])

theta_x = -math.asin(R[2, 0])
theta_y = math.atan2(R[2,1]/math.cos(theta_x), R[2,2]/math.cos(theta_x))
theta_z = math.atan2(R[1,0]/math.cos(theta_x), R[0,0]/math.cos(theta_x))

theta_x = np.degrees(theta_x)
theta_y = np.degrees(theta_y)
theta_z = np.degrees(theta_z)

# # angles from evecs
# theta_x1 = math.atan2(evecs[2,1], evecs[1,1])
# theta_y1 = math.atan2(evecs[0,1], evecs[2,1])
# theta_z1 = math.atan2(evecs[1,0], evecs[0,0])
#
# theta_x1 = np.degrees(theta_x1)
# theta_y1 = np.degrees(theta_y1)
# theta_z1 = np.degrees(theta_z1)
#
# theta_x2 = np.arccos(np.dot([0, evecs[1,0], evecs[2,0]], [0, 0, 1]))
# theta_y2 = np.arccos(np.dot([evecs[0,1], 0, evecs[2,1]], [1, 0, 0]))
# theta_z2 = np.arccos(np.dot([evecs[0,0], evecs[1,0], 0], [1, 0, 0]))
#
# theta_x2 = np.degrees(theta_x2)
# theta_y2 = np.degrees(theta_y2)
# theta_z2 = np.degrees(theta_z2)

##############################################################
# from bonej results
#
evals_bj = [0.004511241615908, 0.008278941187375, 0.008948688425556]
evecs_bj = [[0.395505288907472, 0.899909534220867, 0.183680147714986],
         [0.907785214070893, -0.35260316831332, -0.227149754148384],
         [0.139648027413494, -0.25658105135374, 0.956380987120577]]

fabric_tens_bj = np.matmul(evecs_bj, np.matmul((evals_bj * np.identity(3)), np.transpose(evecs_bj)))

U, s, R = linalg.svd(fabric_tens_bj)
radii_bj = 1.0/np.sqrt(s)

theta_x_bj = -math.asin(R[2, 0])
theta_y_bj = math.atan2(R[2,1]/math.cos(theta_x_bj), R[2,2]/math.cos(theta_x_bj))
theta_z_bj = math.atan2(R[1,0]/math.cos(theta_x_bj), R[0,0]/math.cos(theta_x_bj))

theta_x_bj = np.degrees(theta_x_bj)
theta_y_bj = np.degrees(theta_y_bj)
theta_z_bj = np.degrees(theta_z_bj)


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
# ax.scatter(coors[:,0], coors[:,1], coors[:,2], zdir='z', s=0.4, c='b',rasterized=True)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
ef.ellipsoid_plot([0, 0, 0], radii, evecs, ax=ax, plot_axes=True, cage_color='red')
ef.ellipsoid_plot([0, 0, 0], radii_bj*0.2, evecs_bj, ax=ax, plot_axes=True, cage_color='blue')
plt.show()