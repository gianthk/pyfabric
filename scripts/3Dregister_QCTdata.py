# Script derived from pyfabric example 04: 3D register QCT to HR-pQCT dataset

import os
import sys
import numpy as np
import pandas as pd
import SimpleITK as sitk
from skimage.filters import threshold_multiotsu
from skimage import morphology

sys.path.append('/usr/terminus/data-xrm-01/stamplab/users/giiori/code/pyfabric')
sys.path.append('/usr/terminus/data-xrm-01/stamplab/users/giiori/code/ORMIR_XCT')
sys.path.append('/usr/terminus/data-xrm-01/stamplab/users/giiori/code/recon_utils')

from imaging_utils import periosteummask
# import pyfabric
from resources.pyfabric_image_utils import markers_coors, resample_img, align_with_vectors, affine_trans

data_dir = "/usr/terminus/data-xrm-01/stamplab/external/tacosound/"
work_dir = '/usr/terminus/data-xrm-01/stamplab/users/giiori/2025/2025-06_supertrab_registration/'

elastix_parameter_file = '/home/giiori/myterminus/code/pyfabric/elastix/Parameters.Par0015.expC.phantom.NC.affine2.txt'

target_folders = [
    "1955_L",
    "1956_L",
    "1996_R",
    "2005_L",
    "2007_L",
    "2019_L"
]

long_QCT_names = [
    "1955_L", "1956_L", "1958_L", "1977_L", "1985_L", "1994_L", "1996_L", "2000_L",
    "2001_L", "2004_L", "2005_L", "2007_L", "2010_L", "2014_L", "2017_L", "2019_L"
]

isqnames = [
    "C0001577",
    "C0001464",
    "C0001808",
    "C0001015",
    "C0001429",
    "C0001524"
]

master_filename = os.path.join(data_dir, 'tacosound_master_all.csv')
master = pd.read_csv(master_filename, sep=',')

for specimen_id, specimen in enumerate(target_folders):
    isqname = isqnames[specimen_id]

    input_file_HR_res = os.path.join(data_dir, 'HR-pQCT_II/00_resampled_data', specimen, (isqname + '_processed.mhd'))

    if specimen in long_QCT_names:
        # input_dir_QCT_DCM = os.path.join(data_dir, 'QCT/', ('QCTFEMUR_' + specimen.replace("_", "")), 'Q_CT_DIAGBILANZ_HR_0003') # load the original DICOM files (contain misalignmed slices)
        input_file_QCT_fixed = os.path.join(data_dir, 'QCT', ('QCTFEMUR_' + specimen.replace("_", "")), (specimen + '_3Dslicer.mhd'))
        output_QCT_R_HR = os.path.join(data_dir, 'QCT', ('QCTFEMUR_' + specimen.replace("_", "")), (specimen + '_R_HR.mhd'))
        output_QCT_R_HR_mask = os.path.join(data_dir, 'QCT', ('QCTFEMUR_' + specimen.replace("_", "")), (specimen + '_R_HR_mask.mhd'))
        output_R_HR = os.path.join(data_dir, 'QCT', ('QCTFEMUR_' + specimen.replace("_", "")), (specimen + '_R_HR.npy'))
        elastix_output_dir = os.path.join(data_dir, 'QCT', ('QCTFEMUR_' + specimen.replace("_", "")), ('QCTFEMUR_' + specimen.replace("_", "") + '_elastix'))
    
    else:
        # input_dir_QCT_DCM = os.path.join(data_dir, 'QCT/', ('QCT' + specimen.replace("_", "")), 'Q_CT_DIAGBILANZ_HR_0003')
        input_file_QCT_fixed = os.path.join(data_dir, 'QCT', ('QCT' + specimen.replace("_", "")), (specimen + '_3Dslicer.mhd'))
        output_QCT_R_HR = os.path.join(data_dir, 'QCT', ('QCT' + specimen.replace("_", "")), (specimen + '_R_HR.mhd'))
        output_QCT_R_HR_mask = os.path.join(data_dir, 'QCT', ('QCT' + specimen.replace("_", "")), (specimen + '_R_HR_mask.mhd'))
        output_R_HR = os.path.join(data_dir, 'QCT', ('QCT' + specimen.replace("_", "")), (specimen + '_R_HR.npy'))
        elastix_output_dir = os.path.join(data_dir, 'QCT', ('QCT' + specimen.replace("_", "")), ('QCT' + specimen.replace("_", "") + '_elastix'))

    # Read HR-pQCT input data
    data_3D_res = sitk.ReadImage(input_file_HR_res, imageIO="MetaImageIO")

    # Read coordinates of cement markers
    specimen_master = master[master['$specimen'].str.contains(specimen) & master['$site'].str.contains('femur_prox')]
    markers_coordinates_HR = np.array([
        [specimen_master['$M1x'].iloc[0], specimen_master['$M1y'].iloc[0], specimen_master['$M1z'].iloc[0]],
        [specimen_master['$M2x'].iloc[0], specimen_master['$M2y'].iloc[0], specimen_master['$M2z'].iloc[0]],
        [specimen_master['$M3x'].iloc[0], specimen_master['$M3y'].iloc[0], specimen_master['$M3z'].iloc[0]],
        [specimen_master['$M4x'].iloc[0], specimen_master['$M4y'].iloc[0], specimen_master['$M4z'].iloc[0]],
        [specimen_master['$M5x'].iloc[0], specimen_master['$M5y'].iloc[0], specimen_master['$M5z'].iloc[0]]
    ])

    # Read and inspect QCT input data
    # reader = sitk.ImageSeriesReader()
    # dicom_names = reader.GetGDCMSeriesFileNames(input_dir_QCT_DCM)
    # reader.SetFileNames(dicom_names)
    # data_3D_QCT = reader.Execute()

    data_3D_QCT = sitk.ReadImage(input_file_QCT_fixed, imageIO="MetaImageIO")
    size_QCT = data_3D_QCT.GetSize()
    vs_QCT = data_3D_QCT.GetSpacing()
    dimension = data_3D_QCT.GetDimension()

    # Resample dataset to isotropic voxel size
    vs_QCT_new = np.min(vs_QCT) * np.ones([3])
    data_3D_QCT_res = resample_img(data_3D_QCT, out_spacing=vs_QCT_new)

    # Median filter
    filter = sitk.MedianImageFilter()
    filter.SetRadius(1)
    data_3D_QCT_med = filter.Execute(data_3D_QCT_res)

    # Find cement markers
    ts = threshold_multiotsu(sitk.GetArrayFromImage(data_3D_QCT_med))
    data_3D_QCT_BW = morphology.binary_opening(sitk.GetArrayFromImage(data_3D_QCT_med) > ts[1])

    markers_coordinates = markers_coors(data_3D_QCT_BW[0:120,:,:]) # [z, y, x]
    markers_coordinates = np.fliplr(markers_coordinates * data_3D_QCT_med.GetSpacing()) # [x, y, z]

    # Alignment and registration rotation matrices
    n12 = markers_coordinates[1,:] - markers_coordinates[0,:]
    n14 = markers_coordinates[3,:] - markers_coordinates[0,:]
    v12 = markers_coordinates_HR[1,:] - markers_coordinates_HR[0,:]
    v14 = markers_coordinates_HR[3,:] - markers_coordinates_HR[0,:]

    R_HR = align_with_vectors(n12, n14, v12, v14)
    np.save(output_R_HR, R_HR)

    # Apply affine transformation to QCT stack
    data_3D_QCT_trans = affine_trans(data_3D_QCT, tmatrix=R_HR)
    data_3D_QCT_med = affine_trans(data_3D_QCT_med, tmatrix=R_HR)

    # Recalculate markers coordinates on transformed QCT image
    data_3D_QCT_BW_trans = morphology.binary_opening(sitk.GetArrayFromImage(data_3D_QCT_med) > ts[1])
    markers_coordinates_trans = markers_coors(data_3D_QCT_BW_trans[0:120,:,:]) # [z, y, x]
    markers_coordinates_trans = np.fliplr(markers_coordinates_trans * data_3D_QCT_med.GetSpacing()) # [x, y, z]

    # Get offset between HR-pQCT and transformed QCT images
    Offset_HR_QCTtrans = np.mean(markers_coordinates_HR - markers_coordinates_trans, axis=0)

    # Fix QCT transformed image origin to include the offset
    data_3D_QCT_trans.SetOrigin(data_3D_QCT_trans.GetOrigin() + Offset_HR_QCTtrans)
    data_3D_QCT_trans.SetOrigin(Offset_HR_QCTtrans)

    # Write transformed dataset as single MHD file
    writer = sitk.ImageFileWriter()
    writer.SetFileName(output_QCT_R_HR)
    writer.Execute(data_3D_QCT_trans)

    # Create mask for QCT transformed image
    filter = sitk.MedianImageFilter()
    filter.SetRadius(1)
    data_3D_QCT_med = filter.Execute(data_3D_QCT_trans)

    data_3D_QCT_BW_peri = periosteummask(sitk.GetArrayFromImage(data_3D_QCT_med)>(ts[1]-400),
                                         closepixels=5,
                                         closevoxels=5,
                                         remove_objects_smaller_than=1,
                                         removeunconn=True,
                                         verbose=True)
    
    data_3D_QCT_BW_peri = sitk.GetImageFromArray(data_3D_QCT_BW_peri.astype('uint8'))
    data_3D_QCT_BW_peri.CopyInformation(data_3D_QCT_trans)

    hole_filling_filter = sitk.VotingBinaryIterativeHoleFillingImageFilter()
    hole_filling_filter.SetRadius(3)
    hole_filling_filter.SetMajorityThreshold(1)
    hole_filling_filter.SetBackgroundValue(0)
    hole_filling_filter.SetForegroundValue(1)
    hole_filling_filter.Execute(data_3D_QCT_BW_peri)

    closing_filter = sitk.BinaryMorphologicalClosingImageFilter()
    closing_filter.SetKernelRadius(8)
    closing_filter.Execute(data_3D_QCT_BW_peri)

    dilate_filter = sitk.BinaryDilateImageFilter()
    dilate_filter.SetKernelRadius(20)
    data_3D_QCT_BW_peri = dilate_filter.Execute(data_3D_QCT_BW_peri)

    # Write mask for QCT transformed image
    writer.SetFileName(output_QCT_R_HR_mask)
    writer.Execute(data_3D_QCT_BW_peri)

    # Write resampled HR dataset as MHD file
    data_3D_res.SetOrigin([0.0, 0.0, 0.0])
    data_3D_res.SetSpacing(1e-3 * np.array(data_3D_res.GetSpacing()))
    output_file_HR_res = os.path.join(data_dir, 'HR-pQCT_II/00_resampled_data', specimen, (isqname + '_processed2.mhd'))
    writer = sitk.ImageFileWriter()
    writer.SetFileName(output_file_HR_res)
    writer.Execute(data_3D_res)

    # launch elastix 3D affine registration command
    # elastix_command = (f"/home/giiori/myterminus/software/elastix5.1/bin/elastix -f {output_file_HR_res} -m {output_QCT_R_HR} -fMask {output_QCT_R_HR_mask} -out {elastix_output_dir} -p {elastix_parameter_file} ")
    
    elastix_command = (
        "export LD_LIBRARY_PATH=/home/giiori/myterminus/software/elastix5.1/lib:$LD_LIBRARY_PATH && "
        f"/home/giiori/myterminus/software/elastix5.1/bin/elastix -f {output_file_HR_res} -m {output_QCT_R_HR} -fMask {output_QCT_R_HR_mask} -out {elastix_output_dir} -p {elastix_parameter_file} "
        )
    
    os.system(elastix_command)
    print(elastix_command)