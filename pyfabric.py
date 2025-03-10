#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Compute fabric tensor by the 3D Auto Correlation Function (ACF) of images.
For more information, call this script with the help option:
    pyfabric.py -h

"""

__author__ = ["Gianluca Iori"]
__date_created__ = "2021-10-22"
__date__ = "2024-04-27"
__copyright__ = "Copyright (c) 2024, ORMIR"
__docformat__ = "restructuredtext en"
__license__ = "GPL"
__version__ = "1.4"
__maintainer__ = "Gianluca Iori"
__email__ = "gianthk.iori@gmail.com"

import numpy as np
import numexpr as ne
import ellipsoid_fit as ef
from tqdm import tqdm
from tqdm.contrib import itertools
from scipy import ndimage
import matplotlib.pyplot as plt
import importlib

#################################################################################


def ACF(I):
    """Calculate 3D Auto Correlation Function (ACF) of given image.
    Taking advantage of the Wiener–Khintchine theorem (https://mathworld.wolfram.com/Wiener-KhinchinTheorem.html)
    the ACF is computed in the Fourier domain as:
    ACF = |ffti(fft(I) conj (fft(I)))|
    with fft() and ffti() being the discrete Fourier and discrete inverse Fourier transforms of the image I, respectively [1].

    [1] P. Varga et al., “Investigation of the three-dimensional orientation of mineralized collagen fibrils in human lamellar bone using synchrotron X-ray phase nano-tomography,” Acta Biomaterialia, vol. 9, no. 9, pp. 8118–8127, Sep. 2013, doi: 10.1016/j.actbio.2013.05.015.

    Parameters
    ----------
    I
        3D image.

    Returns
    -------
    ACF
        3D Auto Correlation Function.
    """

    Ev = np.fft.fftshift(np.fft.fftn(I))
    return np.abs(np.fft.ifftshift(np.fft.ifftn(Ev * np.conj(Ev))))


def zoom_center(ACF, size=None, zoom_factor=None):
    """Crop and zoom center of the ACF.

    Parameters
    ----------
    ACF : ndarray
        ACF data.
    size : int
        Size of the zoomed center.
    zoom_factor
        Zoom factor for imresize.


    Returns
    -------
    ACF_center: ndarray
        Zoomed center of the ACF.
    """

    if zoom_factor is None:
        zoom_factor = 2

    center = ACF.shape

    if size is None:
        size = min(center) / 2

    size = round(size / 2)

    center = [int(center[0] / 2), int(center[1] / 2), int(center[2] / 2)]

    # resize the 3D data using spline interpolation of order 2
    return ndimage.zoom(
        ACF[
            center[0] - size : center[0] + size,
            center[1] - size : center[1] + size,
            center[2] - size : center[2] + size,
        ],
        zoom_factor,
        output=None,
        order=2,
    )


def envelope(bw, method="marching_cubes"):
    """Envelope of Trues from binary image.

    Parameters
    ----------
    bw : ndarray
        Binary image.
    method : str
        'pymcubes': Requires PyMCubes module.
        'marching_cubes': scikit-image's marching cube algorithm.

    Returns
    -------
    vertices: ndarray
        Coordinates [X, Y, Z] of the ACF envelope.
    """

    # if importlib.util.find_spec("mcubes") is not None:
    #     import mcubes
    # else:
    #

    if method == "pymcubes" and importlib.util.find_spec("mcubes") is None:
        import warnings

        warnings.warn(
            "mcubes module not found. Switching to skimage method marching_cubes"
        )
        method = "marching_cubes"

    if method == "pymcubes":
        import mcubes

        # (the 0-levelset of the output of mcubes.smooth is the smoothed version of the 0.5-levelset of the binary array.
        smoothed_L = mcubes.smooth(bw)
        # Extract the 0-levelset
        vertices, triangles = mcubes.marching_cubes(
            np.transpose(smoothed_L, [2, 1, 0]), 0
        )
        # vertices, triangles = mcubes.marching_cubes(smoothed_L, 0)

    elif method == "marching_cubes":
        from skimage.measure import marching_cubes

        vertices, triangles, tmp, tmp2 = marching_cubes(
            np.transpose(bw, [2, 1, 0]), level=None, step_size=1
        )
        # vertices, triangles, tmp, tmp2 = marching_cubes(bw, level=None, step_size=1)

    else:
        raise IOError("{0} method unknown.", format(method))

    return vertices


def set_axes_equal(ax):
    """Make axes of 3D plot have equal scale so that spheres appear as spheres,
    cubes as cubes, etc..  This is one possible solution to Matplotlib's
    ax.set_aspect('equal') and ax.axis('equal') not working for 3D.
    Source
        https://stackoverflow.com/questions/13685386/matplotlib-equal-unit-length-with-equal-aspect-ratio-z-axis-is-not-equal-to

    Input
      ax: a matplotlib axis, e.g., as output from plt.gca().
    """

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    # The plot bounding box is a sphere in the sense of the infinity
    # norm, hence I call half the max range the plot radius.
    plot_radius = 0.5 * max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])


def scatter_plot(coors):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(
        coors[:, 0], coors[:, 1], coors[:, 2], zdir="z", s=20, c="b", rasterized=True
    )
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    set_axes_equal(ax)
    # plt.show()

    return ax


def to01(I):
    """Normalize data to 0-1 range.

    Parameters
    ----------
    I
        Input data.

    Returns
    -------
    I : float32
        Normalized data.
    """

    I = I.astype(np.float32, copy=False)
    data_min = np.nanmin(I)
    data_max = np.nanmax(I)
    df = np.float32(data_max - data_min)
    mn = np.float32(data_min)
    scl = ne.evaluate("(I-mn)/df", truediv=True)
    return scl.astype(np.float32)


def to01andbinary(I, t):
    """Normalize data to 0-1 range and segment with given threshold.

    Parameters
    ----------
    I
        Input data.
    t : float
        Threshold in the 0-1 range.

    Returns
    -------
    I_binary : bool
        Data after normalization and thresholding.
    """

    I = I.astype(np.float32, copy=False)
    data_min = np.nanmin(I)
    data_max = np.nanmax(I)
    df = np.float32(data_max - data_min)
    mn = np.float32(data_min)
    scl = ne.evaluate("(I-mn)/df > t", truediv=True)
    return scl.astype(np.bool)


def fabric_snake(
    I,
    ROIspacing,
    ROIsize,
    I_mask=None,
    ACF_threshold=0.5,
    ROIzoom=False,
    zoom_size=None,
    zoom_factor=None,
):
    """Compute fabric tensor of an image using a snake method.

    Parameters
    ----------
    I
        3D image data.
    ROIspacing
        Spacing of the Region Of Interest for the analysis.
        Based on the image size and on ROIspacing the analysis is performed on a structured grif of size (N_slices x N_cols x N_rows).
    ROIsize
        Size of the Region Of Interest for the analysis.
    I_mask
        3D binary mask with the same size as image data.
    ACF_threshold : int
        ACF threshold value (0-1 range).
    ROIzoom : bool
        Zoom center of ACF before ellipsoid fit.
    zoom_size : int
        Size of the zoomed center.
    zoom_factor
        Zoom factor for imresize.

    Returns
    -------
    evecs : float
        (N_slices x N_cols x N_rows x 3 x 3) Fabric tensor eigenvectors as the columns of a 3x3 matrix for each point in pointset.
    radii : float
        (N_slices x N_cols x N_rows x 3) Ellipsoid radii.
    evals : float
        (N_slices x N_cols x N_rows x 3) Ellipsoid eigenvalues.
    fabric_comp : float
        (N_slices x N_cols x N_rows x 6) Ellipsoid tensor components with order: XX, YY, ZZ, XY, YZ, XZ
    Danis : float
        (N_slices x N_cols x N_rows) Degree of Anisotropy (ratio between major and minor fabric ellipsoid axes)
    """

    if ROIsize > ROIspacing:
        raise ValueError()

    # parameters
    halfROIsize = ROIsize / 2
    # I_size = [I.shape[0] - 1, I.shape[1] - 1, I.shape[2] - 1]
    I_size = [I.shape[0], I.shape[1], I.shape[2]]
    # point_count = 0

    id2 = range(ROIspacing, I_size[2] - ROIspacing, ROIspacing)
    id1 = range(ROIspacing, I_size[1] - ROIspacing, ROIspacing)
    id0 = range(ROIspacing, I_size[0] - ROIspacing, ROIspacing)
    # n_points = len(id2) * len(id1) * len(id0)
    print(len(id0), len(id1), len(id2))

    # initialize output variables
    Danis = np.zeros([len(id0), len(id1), len(id2)])
    evecs = np.zeros([len(id0), len(id1), len(id2), 3, 3])
    radii = np.zeros([len(id0), len(id1), len(id2), 3])
    fabric_tens = np.ndarray(evecs.shape)
    fabric_comp = np.ndarray([evecs.shape[0], evecs.shape[1], evecs.shape[2], 6])

    if ROIzoom:
        # loop all points in the set
        for id0i, id1i, id2i in itertools.product(id0, id1, id2):
            # for id0i in tqdm(id0):
            #     for id1i in tqdm(id1):
            #         for id2i in tqdm(id2):
            # ROI extreemes
            x0 = round(id2i - halfROIsize)
            y0 = round(id1i - halfROIsize)
            z0 = round(id0i - halfROIsize)

            x1 = x0 + ROIsize
            y1 = y0 + ROIsize
            z1 = z0 + ROIsize

            # check if ROI exceeds image limits
            if x0 < 0:
                x0 = 0
            if y0 < 0:
                y0 = 0
            if z0 < 0:
                z0 = 0
            if x1 > I_size[2]:
                x1 = I_size[2]
            if y1 > I_size[1]:
                y1 = I_size[1]
            if z1 > I_size[0]:
                z1 = I_size[0]

            # # skip ROIs touching the masked part
            # if np.any(I_mask[z0:z1, y0:y1, x0:x1] == 0):
            #     continue

            # extract ROI around point p
            ROI = I[z0:z1, y0:y1, x0:x1]

            # calculate ACF
            ROIACF = ACF(ROI)

            # # zoom ACF center
            # ROIACF = zoom_center(
            #     ROIACF, size=zoom_size, zoom_factor=zoom_factor
            # )  # check if size of the zoom can be reduced

            # envelope of normalized ACF center
            # env_points = envelope(to01(ROIACF)>ACF_threshold)
            env_points = envelope(to01andbinary(ROIACF, ACF_threshold))

            # ellipsoid fit
            (
                center,
                evecs[id0i, id1i, id2i, :, :],
                radii[id0i, id1i, id2i, :],
                v,
            ) = ef.ellipsoid_fit(env_points)
            # center, evecs[point_count, :, :], radii[point_count, :], v = ef.ellipsoid_fit(env_points*[1,-1,1])

            # point_count = point_count + 1

            # take abs value of the radii vector
            radii[id0i, id1i, id2i, :] = np.abs(radii[id0i, id1i, id2i, :])

            # compute Degree of Anisotropy
            Danis[id0i, id1i, id2i] = np.max(radii[id0i, id1i, id2i, :], 1) / np.min(
                radii[id0i, id1i, id2i, :], 1
            )

            # Remove potential outliers based on the ellipsoid radii:
            # any ellipsoid with a radius > ROIsize/2 is removed
            if np.any(radii[id0i, id1i, id2i, :] > ROIsize * zoom_factor / 2, axis=3):
                radii[id0i, id1i, id2i, :] = np.nan
                Danis[id0i, id1i, id2i] = np.nan

            # ellipsoid radii < 1 voxel are meaningless
            if np.any(radii[id0i, id1i, id2i, :] < 1, axis=3):
                radii[id0i, id1i, id2i, :] = np.nan
                Danis[id0i, id1i, id2i] = np.nan

            # Ellipsoid eigenvalues
            evals = 1 / (radii[id0i, id1i, id2i, :] ** 2)

            # Symmetric ellipsoid tensor components
            # for cell in range(0, evecs.shape[0]):
            fabric_tens[id0i, id1i, id2i, :, :] = np.matmul(
                evecs[id0i, id1i, id2i, :, :],
                np.matmul(
                    (evals * np.identity(3)),
                    np.transpose(evecs[id0i, id1i, id2i, :, :]),
                ),
            )
            fabric_comp[id0i, id1i, id2i, :] = fabric_tens[
                id0i, id1i, id2i, [0, 1, 2, 0, 1, 0], [0, 1, 2, 1, 2, 2]
            ]

    else:
        print("here")


def fabric_pointset(
    I,
    pointset,
    ROIsize,
    ACF_threshold=0.5,
    ROIzoom=False,
    zoom_size=None,
    zoom_factor=None,
):
    """Compute fabric tensor of an image at given set of points.

    Parameters
    ----------
    I
        3D image data.
    pointset
        (Nx3) Points coordinates [x, y, z].
    ROIsize
        Size of the Region Of Interest for the analysis.
    ACF_threshold : int
        ACF threshold value (0-1 range).
    ROIzoom : bool
        Zoom center of ACF before ellipsoid fit.
    zoom_size : int
        Size of the zoomed center.
    zoom_factor
        Zoom factor for imresize.

    Returns
    -------
    evecs : float
        (Nx3x3) Fabric tensor eigenvectors as the columns of a 3x3 matrix for each point in pointset.
    radii : float
        (Nx3) Ellipsoid radii.
    evals : float
        (Nx3) Ellipsoid eigenvalues.
    fabric_comp : float
        (Nx6) Ellipsoid tensor components with order: XX, YY, ZZ, XY, YZ, XZ
    DA : float
        Degree of Anisotropy (ratio between major and minor fabric ellipsoid axes)
    """

    # parameters
    n_points = pointset.shape[0]
    halfROIsize = ROIsize / 2
    I_size = [I.shape[0] - 1, I.shape[1] - 1, I.shape[2] - 1]
    point_count = 0

    # initialize output variables
    evecs = np.zeros([n_points, 3, 3])
    radii = np.zeros([n_points, 3])
    fabric_tens = np.ndarray(evecs.shape)
    fabric_comp = np.ndarray([evecs.shape[0], 6])

    if ROIzoom:
        # loop all points in the set
        for p in tqdm(pointset):
            # ROI extreemes
            x0 = round(p[0] - halfROIsize)
            y0 = round(p[1] - halfROIsize)
            z0 = round(p[2] - halfROIsize)

            x1 = x0 + ROIsize
            y1 = y0 + ROIsize
            z1 = z0 + ROIsize

            # check if ROI exceeds image limits
            if x0 < 0:
                x0 = 0
            if y0 < 0:
                y0 = 0
            if z0 < 0:
                z0 = 0
            if x1 > I_size[2]:
                x1 = I_size[2]
            if y1 > I_size[1]:
                y1 = I_size[1]
            if z1 > I_size[0]:
                z1 = I_size[0]

            # extract ROI around point p
            ROI = I[z0:z1, y0:y1, x0:x1]

            # calculate ACF
            ROIACF = ACF(ROI)

            # zoom ACF center
            ROIACF = zoom_center(
                ROIACF, size=zoom_size, zoom_factor=zoom_factor
            )  # check if size of the zoom can be reduced

            # envelope of normalized ACF center
            # env_points = envelope(to01(ROIACF)>ACF_threshold)
            env_points = envelope(to01andbinary(ROIACF, ACF_threshold))

            # ellipsoid fit
            center, evecs[point_count, :, :], radii[point_count, :], v = (
                ef.ellipsoid_fit(env_points)
            )
            # center, evecs[point_count, :, :], radii[point_count, :], v = ef.ellipsoid_fit(env_points*[1,-1,1])

            point_count = point_count + 1

    else:
        # loop all points in the set
        for p in tqdm(pointset):
            # ROI extreemes
            x0 = round(p[0] - halfROIsize)
            y0 = round(p[1] - halfROIsize)
            z0 = round(p[2] - halfROIsize)

            x1 = x0 + ROIsize
            y1 = y0 + ROIsize
            z1 = z0 + ROIsize

            # check if ROI exceeds image limits
            if x0 < 0:
                x0 = 0
            if y0 < 0:
                y0 = 0
            if z0 < 0:
                z0 = 0
            if x1 > I_size[2]:
                x1 = I_size[2]
            if y1 > I_size[1]:
                y1 = I_size[1]
            if z1 > I_size[0]:
                z1 = I_size[0]

            # extract ROI around point p
            ROI = I[z0:z1, y0:y1, x0:x1]

            # calculate ACF
            ROIACF = ACF(ROI)

            # envelope of normalized ACF
            # the ACF intensity is normalized to the 0-1 range
            # env_points = envelope(to01(ROIACF) > ACF_threshold)
            env_points = envelope(to01andbinary(ROIACF, ACF_threshold))

            # ellipsoid fit
            # the ellipsoid envelope coordinates are scaled to 0-1
            center, evecs[point_count, :, :], radii[point_count, :], v = (
                ef.ellipsoid_fit(env_points / ROIsize)
            )
            # center, evecs[point_count, :, :], radii[point_count, :], v = ef.ellipsoid_fit((env_points*[1,-1,1])/ROIsize)

            point_count = point_count + 1

    # take abs value of the radii vector
    radii = np.abs(radii)

    # compute Degree of Anisotropy
    DA = np.max(radii, 1) / np.min(radii, 1)

    # Remove potential outliers based on the ellipsoid radii:
    # any ellipsoid with a radius > ROIsize/2 is removed
    idx = np.any(radii > ROIsize * zoom_factor / 2, axis=1)
    radii[idx, :] = np.nan
    DA[idx] = np.nan

    # ellipsoid radii < 1 voxel are meaningless
    idx = np.any(radii < 1, axis=1)
    radii[idx, :] = np.nan
    DA[idx] = np.nan

    # Ellipsoid eigenvalues
    evals = 1 / (radii**2)

    # Symmetric ellipsoid tensor components
    for cell in range(0, evecs.shape[0]):
        fabric_tens[cell, :, :] = np.matmul(
            evecs[cell, :, :],
            np.matmul(
                (evals[cell, :] * np.identity(3)), np.transpose(evecs[cell, :, :])
            ),
        )
        fabric_comp[cell, :] = fabric_tens[cell, [0, 1, 2, 0, 1, 0], [0, 1, 2, 1, 2, 2]]
        # fabric_comp[cell, :] = fabric_tens[cell, [2, 1, 0, 1, 0, 0], [2, 1, 0, 2, 1, 2]]
        # evecs[cell, :, :] = np.flipud(evecs[cell, :, :])

    return evecs, radii, evals, fabric_comp, DA
    # return evecs, np.flipud(radii), np.flipud(evals), fabric_comp, DA


def fabric(
    I, ACF_threshold=0.5, zoom=False, zoom_size=None, zoom_factor=None, ACFplot=None
):
    """Compute fabric tensor of a given image.

    Parameters
    ----------
    I
        3D image data.
    ACF_threshold : int
        ACF threshold value (0-1 range).
    zoom : bool
        Zoom center of ACF before ellipsoid fit.
    zoom_size : int
        Size of the zoomed center.
    zoom_factor
        Zoom factor for imresize.
    ACFplot
        PLot of ACF.

    Returns
    -------
    evecs : float
        (3x3) Fabric tensor eigenvectors as the columns of a 3x3 matrix.
    radii : float
        Ellipsoid radii.
    evals : float
        Ellipsoid eigenvalues.
    fabric_comp : float
        Ellipsoid tensor components with order: XX, YY, ZZ, XY, YZ, XZ
    DA : float
        Degree of Anisotropy (ratio between major and minor fabric ellipsoid axes)
    """

    # calculate ACF
    ACF_I = ACF(I)

    if zoom:
        # zoom ACF center
        ACF_I = zoom_center(
            ACF_I, size=zoom_size, zoom_factor=zoom_factor
        )  # check if size of the zoom can be reduced

    if ACFplot:
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
        ax1.imshow(ACF_I[int(ACF_I.shape[0] / 2), :, :])
        ax2.imshow(ACF_I[:, int(ACF_I.shape[1] / 2), :])
        ax3.imshow(ACF_I[:, :, int(ACF_I.shape[2] / 2)])

    # envelope of normalized ACF center
    env_points = envelope(to01andbinary(ACF_I, ACF_threshold))

    # ellipsoid fit
    center, evecs, radii, v = ef.ellipsoid_fit(env_points)

    # compute Degree of Anisotropy
    DA = np.max(radii) / np.min(radii)

    # Ellipsoid eigenvalues
    evals = 1 / (radii**2)

    # Symmetric ellipsoid tensor components
    fabric_tens = np.matmul(
        evecs, np.matmul((evals * np.identity(3)), np.transpose(evecs))
    )
    fabric_comp = fabric_tens[[0, 1, 2, 0, 1, 0], [0, 1, 2, 1, 2, 2]]

    return evecs, radii, evals, fabric_comp, DA
