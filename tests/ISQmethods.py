import numpy as np
import struct

"""
ISQdata methods for Scanco Medical ISQ data input
Converted from MATLAB to Python
Author: Gianluca Iori
Maintainer: Gianluca Iori
Last update: 01/02/2018 (MATLAB)
Last update: 07/03/2025 (Python)
"""

def ISQload(filename=None, x_min=1, y_min=1, z_min=1, x_size=None, y_size=None, z_size=None, interactive=True):
    """
    Load image data from ISQ file.
    """
    header = readheader(filename)
    data = readdata(filename, x_min, y_min, z_min, x_size, y_size, z_size)
    return data, header, filename

def readheader(filename):
    """
    Reads the header of a Scanco ISQ file and returns header information.

    Args:
        filename (str): The path to the ISQ file.
        
    Returns:
        dict: Header information extracted from the file.
    """

    headerinfo = {}
    fid = open(filename, 'rb')
        
    metadata = struct.unpack('32i', fid.read(32 * 4))
    headerinfo['type'] = 'int16'  # standard for ISQ
    headerinfo['x_dim'] = metadata[11]
    headerinfo['y_dim'] = metadata[12]
    headerinfo['z_dim'] = metadata[13]
    headerinfo['x_dim_um'] = metadata[14]
    headerinfo['y_dim_um'] = metadata[15]
    headerinfo['z_dim_um'] = metadata[16]
    headerinfo['slice_thickness_um'] = metadata[17]
    headerinfo['slice_increment_um'] = metadata[18]
    headerinfo['slice_1_pos_um'] = metadata[19]
    headerinfo['min_data_value'] = metadata[20]
    headerinfo['max_data_value'] = metadata[21]
    headerinfo['mu_scaling'] = metadata[22]
    headerinfo['samplename'] = fid.read(40).decode('utf-8').strip('\x00').rstrip()
    headerinfo['energy'] = struct.unpack('I', fid.read(4))[0]
    headerinfo['intensity'] = struct.unpack('I', fid.read(4))[0]

    # Data offset
    fid.seek(508, 0)  # fseek to last 4 header bytes
    offset = struct.unpack('I', fid.read(4))[0]
    headerinfo['offset'] = offset * 512 + 512

    fid.close()

    return headerinfo

def readdata(filename, x_min, y_min, z_min, x_size, y_size, z_size):
    """
    Read a portion of Scanco ISQ data.

    Args:
        filename (str): Path to the ISQ file.
        x_min, y_min, z_min (int): Starting indices (1-based) for x, y, z.
        x_size, y_size, z_size (int): Number of elements to read along x, y, z.

    Returns:
        np.ndarray: 3D numpy array with the read data.
    """
    try:
        headerinfo = readheader(filename)
    except FileNotFoundError:
        raise FileNotFoundError('Input file missing!')

    data = np.zeros((z_size, y_size, x_size), dtype=np.int16)

    with open(filename, 'rb') as fid:
        fid.seek(headerinfo['offset'], 0)

        # Seek initial frames
        fid.seek(headerinfo['x_dim'] * headerinfo['y_dim'] * (z_min) * 2, 1)

        print('Reading ISQ data...')
        for kk in range(z_size):
            fid.seek(headerinfo['x_dim'] * (y_min) * 2, 1)
            for jj in range(y_size):
                fid.seek((x_min) * 2, 1)
                data[kk, jj, :] = np.fromfile(fid, dtype=np.int16, count=x_size)
                fid.seek((headerinfo['x_dim'] - (x_min + x_size)) * 2, 1)

            fid.seek(headerinfo['x_dim'] * (headerinfo['y_dim'] - (y_min + y_size)) * 2, 1)

        print(' done!')

    return data
