import os
import sys
sys.path.append('/usr/terminus/data-xrm-01/stamplab/users/giiori/code/pyfabric')
sys.path.append('/usr/terminus/data-xrm-01/stamplab/users/giiori/code/ORMIR_XCT')
sys.path.append('/usr/terminus/data-xrm-01/stamplab/users/giiori/code/recon_utils')
from resources.pyfabric_image_utils import resample_img
import SimpleITK as sitk
import numpy as np

 
registred_data_dir = "/usr/terminus/data-xrm-01/stamplab/external/tacosound/QCT/QCTFEMUR_2019L/2019_L_R_HR_elastix_01/2019_L_R_HR_elastix.mhd"
output_dir = "/usr/terminus/data-xrm-01/stamplab/external/tacosound/QCT/QCTFEMUR_2019L/2019_L_R_HR_elastix_01/2019_L_R_HR_elastix_resampled.mhd"

data_QCT = sitk.ReadImage(registred_data_dir, imageIO="MetaImageIO")

size_QCT = data_QCT.GetSize()
print("Image size:", size_QCT[0], size_QCT[1], size_QCT[2])
vs_QCT = data_QCT.GetSpacing() 
print("Image spacing:", vs_QCT[0], vs_QCT[1], vs_QCT[2])
dimension = data_QCT.GetDimension()
print("Dimension: ", dimension)

resample_voxel_size = 0.0303 * np.ones([3])
print("New pixelsize", resample_voxel_size)

data_QCT_res = resample_img(data_QCT, out_spacing=resample_voxel_size)

print("Saving resampled image to:", output_dir)
sitk.WriteImage(data_QCT_res, output_dir, useCompression=False)
print("Done.")