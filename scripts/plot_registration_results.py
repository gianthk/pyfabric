# Script derived from pyfabric example 04: 3D register QCT to HR-pQCT dataset
import os
import sys
import numpy as np
import pandas as pd
import SimpleITK as sitk
from skimage.filters import threshold_multiotsu
from skimage import morphology
import time

import numpy as np
import matplotlib.pyplot as plt
import os
import cv2

def export_overlap_planes(planes, output_dir="orthogonal_planes", cmap2="hot", alpha2=0.5, background=""):
    """
    Export images showing overlap of two 3D arrays.

    Parameters:
        planes:     list of tuples containing 2D numpy arrays (background, overlay)
        output_dir: folder to save images
        cmap2:      colormap for array2
        alpha2:     transparency for array2 overlay
    """

    os.makedirs(output_dir, exist_ok=True)

    index = 0
    for (slice1, slice2) in planes:
        fig, ax = plt.subplots(figsize=(10, 10))

        ax.imshow(slice1, cmap="gray", vmin=0, vmax=1, interpolation="nearest")
        ax.imshow(slice2, cmap=cmap2, alpha=alpha2, vmin=0, vmax=1, interpolation="nearest")

        ax.axis("off")

        filepath = os.path.join(output_dir, f"{background}plane_{index}.png")
        fig.savefig(filepath, bbox_inches="tight", dpi=1000)
        plt.close(fig)
        print(f"Saved: {filepath}")
        index = index + 1

sys.path.append('/usr/terminus/data-xrm-01/stamplab/users/giiori/code/pyfabric')
sys.path.append('/usr/terminus/data-xrm-01/stamplab/users/giiori/code/ORMIR_XCT')
sys.path.append('/usr/terminus/data-xrm-01/stamplab/users/giiori/code/recon_utils')

from ISQmethods import ISQload, readheader
from recon_utils import to01

data_dir = "/usr/terminus/data-xrm-01/stamplab/external/tacosound/"
STORAGE = "/usr/terminus/data-xrm-01/stamplab/external/tacosound/HR-pQCT_II"
work_dir = '/usr/terminus/data-xrm-01/stamplab/users/giiori/2025/2025-06_supertrab_registration/'

target_folders = [
    # "1955_L", # OK
    # "1956_L", # OK
    # "1996_R", # OK
    # "2005_L", # OK
    # "2007_L", # OK
    # "2019_L",   # OK
    "2000_R",   # OK
    "2001_R",   # OK
]

isqnames = [
    # "C0001577",
    # "C0001464",
    # "C0001808",
    # "C0001015",
    # "C0001429",
    # "C0001524",
    "C0002013",
    "C0001863",
]

long_QCT_names = [
    "1955_L", "1956_L", "1958_L", "1977_L", "1985_L", "1994_L", "1996_L", "2000_L",
    "2001_L", "2004_L", "2005_L", "2007_L", "2010_L", "2014_L", "2017_L", "2019_L",
    "QCT2000_R", "QCT2001_R", "QCT1996_R",
]

bg = "QCT"
bg = "HR-pQCT"

for specimen_id, specimen in enumerate(target_folders):
    isqname = isqnames[specimen_id]

    start_time = time.time()
    folder_path = os.path.join(STORAGE, specimen)
    isq_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".isq")]
    isq_file = isq_files[0]
    file_path = os.path.join(folder_path, isq_file)
    output_folder = os.path.join(work_dir, specimen)
    os.makedirs(output_folder, exist_ok=True)

    if specimen in long_QCT_names:

        elastix_output_dir = os.path.join(data_dir, 'QCT', ('QCTFEMUR_' + specimen.replace("_", "")), ('QCTFEMUR_' + specimen.replace("_", "") + '_elastix'))
        elastix_output_file = os.path.join(data_dir, 'QCT', ('QCTFEMUR_' + specimen.replace("_", "")), ('QCTFEMUR_' + specimen.replace("_", "") + '_elastix/result.0.mhd' ))
    
    else:

        elastix_output_dir = os.path.join(data_dir, 'QCT', ('QCT' + specimen.replace("_", "")), ('QCT' + specimen.replace("_", "") + '_elastix'))
        elastix_output_file = os.path.join(data_dir, 'QCT', ('QCT' + specimen.replace("_", "")), ('QCT' + specimen.replace("_", "") + '_elastix/result.0.mhd'))

    data_3D_QCT = sitk.ReadImage(elastix_output_file, imageIO="MetaImageIO")
    size_QCT = data_3D_QCT.GetSize()
    vs_QCT = data_3D_QCT.GetSpacing()
    dimension = data_3D_QCT.GetDimension()

    # read HR-pQCT data central slice from ISQ file
    header = readheader(file_path)
    x_size = header['x_dim']
    y_size = header['y_dim']
    z_size = header['z_dim']

    cz1, cy1, cx1 = z_size // 2, y_size // 2, x_size // 2

    if specimen == "2000_R":
        z_size = 5105

    if specimen == "2001_R":
        z_size = 5105

    # read QCT
    data_3D_QCT = sitk.ReadImage(elastix_output_file, imageIO="MetaImageIO")
    size_QCT = data_3D_QCT.GetSize()
    vs_QCT = data_3D_QCT.GetSpacing()
    dimension = data_3D_QCT.GetDimension()
    print(f"Loaded registered QCT for {specimen}")
    print(f"QCT image size: {size_QCT}, spacing: {vs_QCT}, dimension: {dimension}")

    # convert to numpy array
    array_QCT = sitk.GetArrayFromImage(data_3D_QCT)

    nz2, ny2, nx2 = array_QCT.shape

    print(f"nz2: {nz2}, ny2: {ny2}, nx2: {nx2}")
    cz2, cy2, cx2 = nz2 // 2, ny2 // 2, nx2 // 2
    print(f"QCT center: cz2={cz2}, cy2={cy2}, cx2={cx2}")

    # image_data_yz, _, _ = np.zeros((y_size, z_size), dtype=np.int16), None, None
    image_data_yz, _, _ = ISQload(file_path, x_min=cx1, y_min=0, z_min=0, x_size=1, y_size=y_size, z_size=z_size)
    image_data_xz, _, _ = ISQload(file_path, x_min=0, y_min=cy1, z_min=0, x_size=x_size, y_size=1, z_size=z_size)
    image_data_xy, _, _ = ISQload(file_path, x_min=0, y_min=0, z_min=cz1, x_size=x_size, y_size=y_size, z_size=1)

    print(f"Loaded ISQ slices for {specimen} in {time.time() - start_time:.2f} seconds")
    print(f"image_data_yz shape: {image_data_yz.shape}, dtype: {image_data_yz.dtype}")
    print(f"will reshape QCT image to (y_size, z_size) = ({z_size}, {y_size}) for plotting")
    # # image_data, ISQheader, filename = ISQload(file_path)

    if bg == "QCT":
        planes = [
            (cv2.resize(to01(array_QCT[:, :, cx2]), (y_size, z_size), interpolation=cv2.INTER_LINEAR), to01(image_data_yz[:, :, 0])),
            (cv2.resize(to01(array_QCT[:, cy2, :]), (x_size, z_size), interpolation=cv2.INTER_LINEAR), to01(image_data_xz[:, 0, :])),
            (cv2.resize(to01(array_QCT[cz2, :, :]), (y_size, x_size), interpolation=cv2.INTER_LINEAR), to01(image_data_xy[0, :, :])),
        ]
    else:
        planes = [
            (to01(image_data_yz[:, :, 0]), cv2.resize(to01(array_QCT[:, :, cx2]), (y_size, z_size), interpolation=cv2.INTER_LINEAR)),
            (to01(image_data_xz[:, 0, :]), cv2.resize(to01(array_QCT[:, cy2, :]), (x_size, z_size), interpolation=cv2.INTER_LINEAR)),
            (to01(image_data_xy[0, :, :]), cv2.resize(to01(array_QCT[cz2, :, :]), (y_size, x_size), interpolation=cv2.INTER_LINEAR)),
        ]

    # plot merge of the two images
    export_overlap_planes(planes, output_dir=output_folder, cmap2="hot", alpha2=0.5, background=bg)
    print(f"Exported overlap planes for {specimen} in {time.time() - start_time:.2f} seconds")
