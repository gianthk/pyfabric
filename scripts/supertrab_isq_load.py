import os
import sys
import SimpleITK as sitk

# import pyfabric
sys.path.append(os.path.abspath(".."))
# sys.path.append(os.path.abspath("~/myterminus/code/pyfabric/"))
sys.path.append(os.path.abspath("/home/giiori/myterminus/code/pyfabric"))

from tests.ISQmethods import ISQload

#filtering and image processing
import numpy as np
from scipy.ndimage import gaussian_filter, zoom

#constants
sigma = 1.3
scale_factor = (1/2, 1/2, 1/2)

#define files
STORAGE = "/usr/terminus/data-xrm-01/stamplab/external/tacosound/HR-pQCT_II"
# data_dir = "/usr/terminus/data-xrm-01/stamplab/users/mwahlin/2025/trab_master/CT pipeline/processed_ds_HR_images"
data_dir = "/usr/terminus/data-xrm-01/stamplab/external/tacosound/HR-pQCT_II/00_resampled_data"

target_folders = [
    "1955_L",
    # "1956_L",
    # "1996_R",
    # "2005_L",
    # "2007_L",
    # "2019_L"
]

#TODO create loop
#loop over images

for subfolder in target_folders:

    folder_path = os.path.join(STORAGE, subfolder)
    isq_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".isq")]
    isq_file = isq_files[0]
    file_path = os.path.join(folder_path, isq_file)

    #TODO change to all slices
    #Load image
    image_data, ISQheader, filename = ISQload(file_path, x_min=0, y_min=0, z_min=0, x_size=4608, y_size=4608, z_size=5921)

    #Process image
    image_data[:] = gaussian_filter(image_data, sigma=sigma)
    np.putmask(image_data, image_data < 1000, 2000)
    #create an empty array to store results of downsampling
    new_shape = tuple(round(s * 0.5) for s in image_data.shape)
    downsampled_image = np.empty(new_shape, dtype=np.int16)
    zoom(image_data, scale_factor, order=1, output=downsampled_image).astype(np.int16)


    #Save image as .mha
    sitk_image = sitk.GetImageFromArray(downsampled_image)
    # Extract & Adjust Metadata from ISQheader
    original_spacing = np.array([ISQheader["x_dim_um"] / ISQheader["x_dim"],
        ISQheader["y_dim_um"] / ISQheader["y_dim"],
        ISQheader["slice_thickness_um"]])
    # Adjust spacing due to downsampling (factor 2)
    new_spacing = original_spacing * 2  
    sitk_image.SetSpacing(new_spacing.tolist())  # Convert to list for ITK compatibility
    # Set Origin (Z position from ISQheader)
    sitk_image.SetOrigin([0, 0, ISQheader["slice_1_pos_um"]])
    # Add metadata from ISQheader
    metadata_keys = ["samplename", "mu_scaling", "energy", "intensity", "offset"]
    for key in metadata_keys:
        sitk_image.SetMetaData(key, str(ISQheader[key]))
    # Save the processed image
    output_filename = os.path.basename(filename).replace(".ISQ", "_processed.mhd")
    output_filename = os.path.join(data_dir, subfolder, output_filename)
    sitk.WriteImage(sitk_image, output_filename)


