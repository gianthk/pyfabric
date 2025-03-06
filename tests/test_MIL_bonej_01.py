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
evecs, radii, evals, fabric_comp, DA = pyfabric.fabric(I, zoom=True, zoom_factor=2, zoom_size=I.shape[0]/4, ACFplot=True)

##############################################################
# from bonej results
import pandas as pd
df = pd.read_csv('/home/gianthk/Data/2019.001.coop_TUberlin_simulierte_Mensch.iorig/trabecular_samples_bin/bonej_results.csv')
radii_bj = df.iloc[1,2:5].to_numpy()
evecs_bj = np.reshape(df.iloc[1,5:14].tolist(), (3,3))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
# ax.scatter(coors[:,0], coors[:,1], coors[:,2], zdir='z', s=0.4, c='b',rasterized=True)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
ef.ellipsoid_plot([0, 0, 0], radii/np.max(radii), evecs, ax=ax, plot_axes=True, cage_color='red')
ef.ellipsoid_plot([0, 0, 0], radii_bj/np.max(radii_bj), evecs_bj, ax=ax, plot_axes=True, cage_color='blue')
plt.show()