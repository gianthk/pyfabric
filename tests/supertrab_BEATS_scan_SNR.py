# check the SNR of a BEATS trabecular bone scan
import dxchange
import tomopy
import numpy as np
import matplotlib.pyplot as plt
import tifffile
from PIL import Image

h5file = './IH_supertrab_A_macro1_mono35_6pt5um_100mm-20250421T220015.h5'
projs, flats, darks, theta = dxchange.read_aps_32id(h5file, exchange_rank=0, proj=(1000, 1020, 1))

print(projs.shape)

projs = tomopy.normalize(projs, flats, darks, ncore=1, averaging='median')
plt.imshow(projs[10, :, :])
plt.show()

print(np.std(projs[10,0:100,0:100])/np.mean(projs[10,0:100,0:100]))

tifffile.imwrite('/home/giiori/myterminus/code/pyfabric/tests/supertrab_proj_norm.tiff', projs[10,:,:])
Image.fromarray(projs[10,:,:], mode='L').save('/home/giiori/myterminus/code/pyfabric/tests/supertrab_proj_norm.png')