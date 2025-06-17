import os
import sys
import SimpleITK as sitk
import time

# import pyfabric
sys.path.append(os.path.abspath(".."))
# sys.path.append(os.path.abspath("~/myterminus/code/pyfabric/"))
sys.path.append(os.path.abspath("/home/giiori/myterminus/code/pyfabric"))

# from tests.ISQmethods import ISQload
from resources.pyfabric_image_utils import resample_img

#define files
STORAGE = "/usr/terminus/data-xrm-01/stamplab/external/tacosound/HR-pQCT_II/00_resampled_data"
# data_dir = "/usr/terminus/data-xrm-01/stamplab/users/mwahlin/2025/trab_master/CT pipeline/processed_ds_HR_images"
data_dir = "/usr/terminus/data-xrm-01/stamplab/external/tacosound/HR-pQCT_II/00_resampled_data"

target_folders = [
    # "1955_L",
    "1956_L",
    "1996_R",
    "2005_L",
    "2007_L",
    "2019_L"
]

#loop over images
for subfolder in target_folders:

    start_time = time.time()
    folder_path = os.path.join(STORAGE, subfolder)
    mhd_files = [f for f in os.listdir(folder_path) if f.lower().endswith("_processed.mhd")]
    mhd_file = mhd_files[0]
    file_path = os.path.join(folder_path, mhd_file)

    #Load image
    mhd_image = sitk.ReadImage(file_path, imageIO="MetaImageIO")

    #Downsample image
    mhd_image_res = resample_img(mhd_image, out_spacing=[242.39930556, 242.39930556, 240.0], is_label=False)

    #Save image as .mhd
    output_filename = os.path.basename(file_path).replace("_processed.mhd", "_processed.mhd")
    output_filename = os.path.join(data_dir, subfolder, output_filename)

    sitk.WriteImage(mhd_image_res, output_filename)

    # free memory from raw image
    del mhd_image

    end_time = time.time()
    print(f"Processed {subfolder} in {end_time - start_time:.2f} seconds")
    print(f"Saved as {output_filename}")

