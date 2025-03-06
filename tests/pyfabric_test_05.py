from recon_utils import read_tiff_stack
import pyfabric

input_file = '/home/gianthk/Data/StefanFly_test/test_00__rec/test_00__rec/recon_00000.tiff'

# Read 3D data
I = read_tiff_stack(input_file)

# crop
center = [649, 461, 522]
ROIsize = 50
ROIsize = int(ROIsize/2)
ROI = I[center[2]-ROIsize:center[2]+ROIsize, center[1]-ROIsize:center[1]+ROIsize,center[0]-ROIsize:center[0]+ROIsize]

# get fabric
evecs, radii, evals, fabric_comp, DA = pyfabric.fabric(ROI, zoom=True, zoom_factor=2)

# plotting
import matplotlib.pyplot as plt
import ellipsoid_fit as ef

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
# ax.scatter(coors[:,0], coors[:,1], coors[:,2], zdir='z', s=0.4, c='b',rasterized=True)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
ef.ellipsoid_plot(center, radii, evecs, ax=ax, plot_axes=True, cage_color='red')
plt.show()

print('here')