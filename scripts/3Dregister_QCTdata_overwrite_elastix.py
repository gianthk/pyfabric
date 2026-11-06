# Script derived from 3Dregister_QCTdata.py: overwrite the QCT moving image with the elastix registration result

import os
import SimpleITK as sitk

data_dir = "/usr/terminus/data-xrm-01/stamplab/external/tacosound/"

target_folders = [
    # "1955_L",
    # "1956_L",
    # "1996_R",
    # "2005_L",
    # "2007_L",
    # "2019_L",
    # "2000_R",
    "2001_R",
]

long_QCT_names = [
    "1955_L", "1956_L", "1958_L", "1977_L", "1985_L", "1994_L", "1996_L", "2000_L",
    "2001_L", "2004_L", "2005_L", "2007_L", "2010_L", "2014_L", "2017_L", "2019_L",
    "QCT2000_R", "QCT2001_R",
]

for specimen in target_folders:

    if specimen in long_QCT_names:
        output_QCT_R_HR = os.path.join(data_dir, 'QCT', ('QCTFEMUR_' + specimen.replace("_", "")), (specimen + '_R_HR.mhd'))
        elastix_output_dir = os.path.join(data_dir, 'QCT', ('QCTFEMUR_' + specimen.replace("_", "")), ('QCTFEMUR_' + specimen.replace("_", "") + '_elastix'))

    else:
        output_QCT_R_HR = os.path.join(data_dir, 'QCT', ('QCT' + specimen.replace("_", "")), (specimen + '_R_HR.mhd'))
        elastix_output_dir = os.path.join(data_dir, 'QCT', ('QCT' + specimen.replace("_", "")), ('QCT' + specimen.replace("_", "") + '_elastix'))

    # Overwrite the moving image with the result of the registration
    img = sitk.ReadImage(f"{elastix_output_dir}/result.0.mhd")
    sitk.WriteImage(img, output_QCT_R_HR)   # overwrites the moving image
