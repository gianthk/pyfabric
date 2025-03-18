"""
Script to load large .isq images to zarr format enabling efficent access and processing

Implementation based on supertrab_isq_load.py in this library and adapted from: 
https://github.com/dveni/pneumodomo/blob/main/scripts/prepare_dataset.py
"""

#imports
import os
import sys
import time
import numpy as np
import zarr
from pathlib import Path

#for storing metadata
def convert_header(header):
    return {key: int(value) if isinstance(value, (np.integer, np.int16, np.int32, np.int64)) else value 
            for key, value in header.items()}

# import pyfabric
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))
from tests.ISQmethods import ISQload

# Define paths
STORAGE = "/usr/terminus/data-xrm-01/stamplab/external/tacosound/HR-pQCT_II"
save_path = Path("/usr/terminus/data-xrm-01/stamplab/external/tacosound/HR-pQCT_II/zarr_data/supertrab.zarr")

# Ensure the parent directory exists before using Zarr
if not save_path.parent.exists():
    save_path.parent.mkdir(parents=True)

# Create the Zarr store
store = zarr.DirectoryStore(save_path)
root = zarr.group(store=store, overwrite=True)

target_folders = [
    "1955_L",
    "1956_L",
    "1996_R",
    "2005_L",
    "2007_L",
    "2019_L"
]

# Define chunk size
chunk_size = (1, 512, 512)

# Read the .isq (to a numpy array?)
for subfolder in target_folders:

    #define filepath
    start_time = time.time()
    folder_path = os.path.join(STORAGE, subfolder)
    isq_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".isq")]
    isq_file = isq_files[0]
    file_path = os.path.join(folder_path, isq_file)

    #Load image
    image_data, ISQheader, filename = ISQload(file_path)
    print(image_data.shape)

    #Create .zarr group
    sample_group = root.create_group(subfolder)

    #Save data to .zarr
    print(f"Saving image data for {subfolder}")
    sample_group.create_dataset("image", data=image_data, chunks=chunk_size)

    # Free memory
    del image_data
    
    print(f"{subfolder} processed in {time.time() - start_time:.2f} seconds")

# Print stored structure
print(root.tree())
print(root.info)