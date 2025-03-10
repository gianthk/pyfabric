# import recon_utils as ru
import numpy as np
# import pyfabric
import os
from ISQmethods import ISQload, readheader

# STORAGE is the location of the data (on terminus, as mounted on Hari)
STORAGE = "/Volumes/stamplab_terminus/external/tacosound/HR-pQCT_II/Vincent_hand"
image = "C0001664.ISQ"

tmp = readheader(os.path.join(STORAGE, image))

print("here")