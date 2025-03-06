import numpy as np
import struct
import numpy as np

"""
ISQdata methods for Scanco Medical ISQ data input
Converted from MATLAB to Python
Author: Gianluca Iori
Maintainer: Gianluca Iori
Last update: 01/02/2018 (MATLAB) | Converted: Today
"""

def ISQload(filename=None, x_min=1, y_min=1, z_min=1, x_size=None, y_size=None, z_size=None, interactive=True):
    """
    Load ISQ file with optional interactive range selection.
    """
    # Placeholder for header reading and data loading logic
    header = readheader(filename)
    data = readdata(filename, x_min, y_min, z_min, x_size, y_size, z_size)
    return data, header, filename

def readheader(filename, leaveopen=False):
    """
    Reads the header of a Scanco ISQ file and returns header information.

    Args:
        filename (str): The path to the ISQ file.
        leaveopen (bool, optional): If True, leaves the file open and returns the file handle.
                                    Defaults to False.

    Returns:
        dict: Header information extracted from the file.
        Optional[file object]: The file handle if leaveopen is True.
    """
    headerinfo = {}
    try:
        fid = open(filename, 'rb')
        
        # Read header
        check = fid.read(4).decode('utf-8')  # char check[16]
        print(check)
        headerinfo['data_type_id'] = struct.unpack('I', fid.read(4))[0]  # int data_type
        headerinfo['type'] = 'int16'  # standard for ISQ
        headerinfo['nr_of_bytes'] = struct.unpack('I', fid.read(4))[0]  # int nr_of_bytes

        # Dimensions
        fid.seek(44, 1)  # skip 44 bytes to x_dim
        headerinfo['x_dim'] = struct.unpack('I', fid.read(4))[0]
        headerinfo['y_dim'] = struct.unpack('I', fid.read(4))[0]
        headerinfo['z_dim'] = struct.unpack('I', fid.read(4))[0]
        headerinfo['x_dim_um'] = struct.unpack('I', fid.read(4))[0]
        headerinfo['y_dim_um'] = struct.unpack('I', fid.read(4))[0]
        headerinfo['z_dim_um'] = struct.unpack('I', fid.read(4))[0]
        headerinfo['slice_thickness_um'] = struct.unpack('I', fid.read(4))[0]
        headerinfo['slice_increment_um'] = struct.unpack('I', fid.read(4))[0]
        headerinfo['slice_1_pos_um'] = struct.unpack('i', fid.read(4))[0]
        headerinfo['min_data_value'] = struct.unpack('i', fid.read(4))[0]
        headerinfo['max_data_value'] = struct.unpack('i', fid.read(4))[0]
        headerinfo['mu_scaling'] = struct.unpack('i', fid.read(4))[0]
        headerinfo['nr_of_samples'] = struct.unpack('I', fid.read(4))[0]
        headerinfo['nr_of_projections'] = struct.unpack('I', fid.read(4))[0]
        headerinfo['scandist_um'] = struct.unpack('I', fid.read(4))[0]
        headerinfo['scanner_type'] = struct.unpack('i', fid.read(4))[0]
        headerinfo['sampletime_us'] = struct.unpack('I', fid.read(4))[0]
        headerinfo['index_measurement'] = struct.unpack('i', fid.read(4))[0]
        headerinfo['site'] = struct.unpack('i', fid.read(4))[0]
        headerinfo['reference_line_um'] = struct.unpack('i', fid.read(4))[0]
        headerinfo['recon_alg'] = struct.unpack('i', fid.read(4))[0]
        print(headerinfo)
        headerinfo['samplename'] = fid.read(40).decode('utf-8').strip('\x00')
        headerinfo['energy'] = struct.unpack('I', fid.read(4))[0]
        headerinfo['intensity'] = struct.unpack('I', fid.read(4))[0]

        # Data offset
        fid.seek(508, 0)  # fseek to last 4 header bytes
        offset = struct.unpack('I', fid.read(4))[0]
        headerinfo['offset'] = offset * 512 + 512

        if not leaveopen:
            fid.close()
            return headerinfo
        else:
            return headerinfo, fid

    except FileNotFoundError as e:
        raise FileNotFoundError(f'Cannot open file {filename}') from e

    except Exception as e:
        if fid:
            fid.close()
        raise e

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
        headerinfo = readheader(filename, leaveopen=False)
    except FileNotFoundError:
        raise FileNotFoundError('Input file missing!')

    data = np.zeros((x_size, y_size, z_size), dtype=np.int16)

    with open(filename, 'rb') as fid:
        fid.seek(headerinfo['offset'], 0)

        # Seek initial frames
        fid.seek(headerinfo['x_dim'] * headerinfo['y_dim'] * (z_min - 1) * 2, 1)

        print('Reading ISQ data...')
        for kk in range(z_size):
            fid.seek(headerinfo['x_dim'] * (y_min - 1) * 2, 1)
            for jj in range(y_size):
                fid.seek((x_min - 1) * 2, 1)
                data[:, jj, kk] = np.fromfile(fid, dtype=np.int16, count=x_size)
                fid.seek((headerinfo['x_dim'] - (x_min + x_size - 1)) * 2, 1)

            fid.seek(headerinfo['x_dim'] * (headerinfo['y_dim'] - (y_min + y_size - 1)) * 2, 1)

        print(' done!')

    # Compensate for MATLAB row-column convention
    data = np.transpose(data, (1, 0, 2))
    return data
