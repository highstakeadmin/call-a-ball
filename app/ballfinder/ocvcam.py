#!/usr/bin/env python3

# -*- coding: utf-8 -*-
#############################################################################
## Call-A-Ball: an open-source demonstrator of 3D object localization
## based on camera images and the geometric camera calibration,
## completed with the help of the Radiant Metrics cloud service.
##
## Copyright (C) 2024 HS High Stake GmbH
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
## See the GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <https://www.gnu.org/licenses/>.
##
## Contact: call-a-ball@high-stake.de
##
## Description: Camera model, implemented in OpenCV.
#############################################################################

import numpy as np
import scipy


##-----------------------------------------------------------------------------
# Core OpenCV projection model.

# Model from: https://docs.opencv.org/3.4/d9/d0c/group__calib3d.html

# p: array [3], (x, y, z), a 3D point in the camera's coordinates
# ipar: array [18], intrinsic camera parameters
# eps: a sufficiently small number, threshold for inverses
# return: q: array [2], projection on the camera sensor


def cvcore(p, ipar, eps=1.0e-8):
    # Extract 3D point components.
    (x, y, z) = (p[0], p[1], p[2])

    # Extract intrinsic parameters.
    (fx, fy, cx, cy, k1, k2, p1, p2, k3, k4, k5, k6, s1, s2, s3, s4, tx, ty) = (
        ipar[0],
        ipar[1],
        ipar[2],
        ipar[3],
        ipar[4],
        ipar[5],
        ipar[6],
        ipar[7],
        ipar[8],
        ipar[9],
        ipar[10],
        ipar[11],
        ipar[12],
        ipar[13],
        ipar[14],
        ipar[15],
        ipar[16],
        ipar[17],
    )

    # Step 1: calculate x prime (x') and y prime (y').
    # Factors (-1) account for the difference in notation:
    # the y-axis is directed downwards in images, and
    # upwards - in the canonical camera's coordinates.
    (xp, yp) = (-1.0 * x / z, -1.0 * y / z)

    # Step 2: calculate squared radius r^2.
    r2 = xp**2 + yp**2

    # Step 3: apply radial and tangential distortions.
    ffn = 1 + k1 * r2 + k2 * r2**2 + k3 * r2**3  # nominator
    ffd = 1 + k4 * r2 + k5 * r2**2 + k6 * r2**3  # denominator
    assert np.fabs(ffd) > eps  # sanity check
    xpp = (
        xp * ffn / ffd + 2 * p1 * xp * yp + p2 * (r2 + 2 * xp**2) + s1 * r2 + s2 * r2**2
    )
    ypp = (
        yp * ffn / ffd + p1 * (r2 + 2 * yp**2) + 2 * p2 * xp * yp + s3 * r2 + s4 * r2**2
    )
    vpp = np.array([[xpp], [ypp], [1.0]])  # vector (x'', y'', 1)

    # Step 4: tilt the image.
    (sin_tx, sin_ty) = (np.sin(tx), np.sin(ty))
    (cos_tx, cos_ty) = (np.cos(tx), np.cos(ty))
    tm = np.array(
        [
            [cos_ty * cos_tx, 0, sin_ty * cos_tx],
            [0, cos_ty * cos_tx, -sin_tx],
            [0, 0, 1],
        ]
    )
    rm = np.array(
        [
            [cos_ty, sin_ty * sin_tx, -sin_ty * cos_tx],
            [0, cos_tx, sin_tx],
            [sin_ty, -cos_ty * sin_tx, cos_ty * cos_tx],
        ]
    )
    mm = np.matmul(tm, rm)
    vppp = np.matmul(mm, vpp)
    (xu, yu, zu) = (vppp[0, 0], vppp[1, 0], vppp[2, 0])

    # Step 5: (xu, yu, zu) = s * (x''', y''', 1), recover x''' and y'''.
    (xppp, yppp) = (xu / zu, yu / zu)

    # Step 6: transform distorted point into u,v image chip coordinates.
    (u, v) = (fx * xppp + cx, fy * yppp + cy)

    # Pack into the output 2D vector.
    q = np.array([u, v])
    return q


##-----------------------------------------------------------------------------
# Convert intrinsic parameters from OpenCV format to a flat vector.

# imtx: array [3x3], intrinsic projection matrix
# dist: array [1xN], distortion coefficients, N = 4, 5, 8, 12, or 14
# return: ipar, array [18], all intrinsic parameters in a vector


def to_ipar(imtx, dist):
    (fx, fy, cx, cy) = (imtx[0, 0], imtx[1, 1], imtx[0, 2], imtx[1, 2])
    (k1, k2, p1, p2) = (dist[0, 0], dist[0, 1], dist[0, 2], dist[0, 3])
    (k3, k4, k5, k6, s1, s2, s3, s4, tx, ty) = [0.0] * 10
    if dist.shape[1] >= 5:
        k3 = dist[0, 4]
    if dist.shape[1] >= 8:
        (k4, k5, k6) = (dist[0, 5], dist[0, 6], dist[0, 7])
    if dist.shape[1] >= 12:
        (s1, s2, s3, s4) = (dist[0, 8], dist[0, 9], dist[0, 10], dist[0, 11])
    if dist.shape[1] >= 14:
        (tx, ty) = (dist[0, 12], dist[0, 13])
    return np.array(
        [fx, fy, cx, cy, k1, k2, p1, p2, k3, k4, k5, k6, s1, s2, s3, s4, tx, ty]
    )


##-----------------------------------------------------------------------------
# Convert a flat vector of intrinsic parameters to OpenCV notation.

# ipar: array [18], intrinsic parameters in a vector
# return: (imtx, dist), OpenCV parameters
#   imtx: array [3x3], intrinsic projection matrix
#   dist: array [1x14], all distortion coefficients


def from_ipar(ipar):
    imtx = np.array([[ipar[0], 0.0, ipar[2]], [0.0, ipar[1], ipar[3]], [0.0, 0.0, 1.0]])
    dist = ipar[4:].reshape((1, 14))
    return (imtx, dist)


##-----------------------------------------------------------------------------
# Project a 3D point to a 2D image point.

# p: array [3x1], (x, y, z), a 3D point in the camera's coordinates
# imtx: array [3x3], intrinsic projection matrix
# dist: array [1xN], distortion coefficients, N = 4, 5, 8, 12, or 14
# eps: sufficiently small number, threshold for inverses
# return: q, array [2x1], (u, v), 2D sensor point


def cv_project(p, imtx, dist, eps=1.0e-8):

    # Pack parameters as a fixed-size vector.
    ipar = to_ipar(imtx, dist)

    # Main projection step.
    pv = p.reshape((3))
    qv = cvcore(pv, ipar, eps)
    q = qv.reshape((2, 1))

    return q


##-----------------------------------------------------------------------------
# Find view ray direction for a given sensor point.

# q: array [2x1], (u, v), a 2D sensor point
# imtx: array [3x3], intrinsic projection matrix
# dist: array [1xN], distortion coefficients, N = 4, 5, 8, 12, or 14
# tolerance: allowed residual re-projection error
# check_conv: whether to verify the re-projection convergence
# eps: sufficiently small number, threshold for inverses
# return: r, array [3x1], (rx, ry, rz), a view ray direction vector


def cv_view_ray(q, imtx, dist, tolerance=1.0e-3, check_conv=False, eps=1.0e-8):

    # Exract linear model parameters.
    (fx, fy, cx, cy) = (imtx[0, 0], imtx[1, 1], imtx[0, 2], imtx[1, 2])

    # Extract 2D sensor point components.
    (u, v) = (q[0, 0], q[1, 0])

    # Numerical optimization: find w = (wx, wy) such that
    # |q - cv_project(r)| -> 0, where r = (wx, wy, 1.0).

    # Initial guess acc. to linear pinhole model.
    w0 = np.array([(u - cx) / fx, (v - cy) / fy])

    # Goal function for optimization: re-projection error.
    def fit_func(w):
        r = np.array([[w[0]], [w[1]], [1.0]])  # 3D point at z = 1
        q_ = cv_project(r, imtx, dist)  # projection on sensor
        return (q_ - q).reshape((2))  # 2D discrepancy on sensor

    # Levenberg-Marquardt optimization to minimize RPE.
    fit_res = scipy.optimize.OptimizeResult(
        scipy.optimize.least_squares(fit_func, w0, method="lm")
    )

    # Recover the view ray direction.
    w = fit_res.x  # optimal (wx, wy)
    r = np.array([[w[0]], [w[1]], [1.0]])

    # Check convergence quality.
    if check_conv:
        q_ = cv_project(r, imtx, dist)
        err = np.linalg.norm(q_ - q)
        assert err < tolerance

    return r


##-----------------------------------------------------------------------------
