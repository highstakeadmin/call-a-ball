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
## Description: Misc functions for ball detection.
#############################################################################

import cv2
import numpy as np
import scipy

from .ocvcam import cv_project, cv_view_ray


##-----------------------------------------------------------------------------
# Detect generic contours in an image.

# img_bgr: color image, array [H x W x 3]
# cfg: configuration dict
# return: (img_c, fun_c)
#   img_c: binary contour map, array [H x W]
#   fun_c: contour indicator function, defined over [0, H] x [0, W]


def canny(img_bgr, cfg):
    img_g = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    ksz = cfg["GaussianBlur"]["ksize"]
    siX = cfg["GaussianBlur"]["sigmaX"]
    img_b = cv2.GaussianBlur(img_g, ksize=(ksz, ksz), sigmaX=siX)
    th1 = cfg["Canny"]["threshold1"]
    th2 = cfg["Canny"]["threshold2"]
    img_c = cv2.Canny(img_b, threshold1=th1, threshold2=th2)
    ys = np.arange(img_c.shape[0])
    xs = np.arange(img_c.shape[1])
    fun_c = scipy.interpolate.RegularGridInterpolator(
        (ys, xs), img_c, method="nearest", bounds_error=True
    )
    return (img_c, fun_c)


##-----------------------------------------------------------------------------
# Find the first contour point on a radial ray.

# cand: candidate, array [3], (x, y, r)
# fun_c: function of 2d argument, p in [0, H] x [0, W]
# ang_deg: radial direction angle, degrees
# cfg: configuration dict
# return: contour point or None
#   contour point: array [2], (x, y)


def find_radial(cand, fun_c, ang_deg, cfg):
    min_rel_s = cfg["FindContours"]["minRelScale"]
    max_rel_s = cfg["FindContours"]["maxRelScale"]
    (x, y, r) = cand
    ang_rad = ang_deg * np.pi / 180.0

    # Origin point and radial direction vector.
    op = np.array([x, y])
    dv = np.array([np.sin(ang_rad), np.cos(ang_rad)])

    # Radial position and edge functions.
    def rp(s):
        return op + s * dv

    def ef(s):
        return fun_c(np.flip(rp(s)))[0]

    # Find the first contour point on the ray in the valid range.
    (min_s, max_s) = (min_rel_s * r, max_rel_s * r)
    for s in np.arange(min_s, max_s, 1.0):
        try:
            v = ef(s)
        except ValueError as e:
            break
        if v > 0:
            return rp(s)
    return None


##-----------------------------------------------------------------------------
# Find several points on a candidate's contour.

# cand: candidate, array [3], (x, y, r)
# fun_c: contour indicator function, defined over [0, H] x [0, W]
# cfg: configuration dict
# return: list of contour points,
#   contour point: array [2], (x, y)


def find_contour(cand, fun_c, cfg):
    num_points = cfg["FindContours"]["points"]
    angs = np.linspace(0.0, 360.0, num_points)
    cont = []
    for ang_deg in angs:
        pt = find_radial(cand, fun_c, ang_deg, cfg)
        if pt is None:
            continue
        cont.append(pt)
    return cont


##-----------------------------------------------------------------------------
# Check whether a contour is valid and can be used for fitting.

# cont: list of contour points,
#   contour point: array [2], (x, y)
# cfg: configuration dict
# return: True or False


def valid_contour(cont, cfg):
    return len(cont) > 4


##-----------------------------------------------------------------------------
# Derive 3D view rays for the contour points.

# cand: candidate, array [3], (x, y, r)
# cont: list of contour points,
#   contour point: array [2], (x, y)
# cam: dict of camera parameters
# cfg: configuration dict
# return: cone, list of view rays, 0-th: center, rest: contour points,
#   view ray: (o, r),
#     o: array [3], view ray origin point
#     r: array [3], view ray direction vector


def find_cone(cand, cont, cam):

    (x, y, r) = cand

    # Extract the intrinsic parameters.
    imtx = np.array(cam["intrinsics"]["camera_matrix"])
    dist = np.array(cam["intrinsics"]["distortion_coefficients"])
    dist = dist.reshape((1, -1))

    # Common origin of all view rays.
    o = np.array([0.0, 0.0, 0.0])

    # Find a view ray for the candidate's center.
    q = np.array([[x], [y]])
    r = cv_view_ray(q, imtx, dist)
    r = r.flatten()

    # Find view rays corresponding to the contour points.
    cone = [(o, r)]
    for cx, cy in cont:
        q = np.array([[cx], [cy]])
        r = cv_view_ray(q, imtx, dist)
        r = r.flatten()
        cone.append((o, r))

    return cone


##-----------------------------------------------------------------------------
# Find an approximate 3D position of the ball inside a cone.

# cone: list of view rays, 0-th ray: center, rest: contour points,
#   view ray: (o, r),
#     o: array [3], view ray origin point
#     r: array [3], view ray direction vector
# radius: float, a priori known ball radius
# return: approximate ball center in 3D, array [3], (X, Y, Z)

# The method uses two rays out of the given cone:
# - the central ray: we expect the ball center to be on it,
# - one contour ray: we expect the ball to touch it.


def fit_ball(cone, radius):

    # Unpack two useful view rays.
    (oc, rc) = cone[0]  # central ray
    (oe, re) = cone[1]  # use a single contour ray

    # Convert to NumPy.
    (oc, rc) = (np.array(oc), np.array(rc))
    (oe, re) = (np.array(oe), np.array(re))

    # vector-like distance between the ray (oc, rc) and some point pe:
    #   d = (oc - pe) + ac * rc, where
    #   ac = - [(oc - pe).rc] / [rc.rc].
    #
    # Point on the contour ray:
    #   pe = oe + ae * re
    #
    # Condition for the touching ball:
    #   d.d == R^2
    #
    # => Need to solve for the scaling factor ae.

    # Let do = oc - oe. Then:
    #   |(do - ae * re) - rc * [(do - ae * re).rc] / [rc.rc]|^2 == R^2,
    #
    # equivalent to
    #   [(do - ae * re).(do - ae * re)]
    #   + [rc.rc] * [(do - ae * re).rc]^2 / [rc.rc]^2
    #   - 2 * [rc.(do - ae * re)] * [(do - ae * re).rc] / [rc.rc]
    #   == R^2,
    #
    # equivalent to
    #   ([do.do] + ae^2 * [re.re] - 2 * ae * [do.re]) * [rc.rc]
    #   - ([do.rc] - ae * [re.rc])^2
    #   == R^2 * [rc.rc],
    #
    # equivalent to
    #   [do.do] * [rc.rc] + ae^2 * [re.re] * [rc.rc] - 2 * ae * [do.re] * [rc.rc]
    #   - [do.rc]^2 - ae^2 * [re.rc]^2 + 2 * ae * [do.rc] * [re.rc]
    #   == R^2 * [rc.rc]
    #
    # equivalent to
    #   ae^2 * ([re.re] * [rc.rc] - [re.rc]^2)
    #   + ae * 2 * ([do.rc] * [re.rc] - [do.re] * [rc.rc])
    #   + ([do.do] * [rc.rc] - [do.rc]^2 - R^2 * [rc.rc])
    #   == 0.

    # Compute useful scalar variables.
    do = oc - oe
    re_re = np.dot(re, re)
    rc_rc = np.dot(rc, rc)
    do_do = np.dot(do, do)
    re_rc = np.dot(re, rc)
    do_re = np.dot(do, re)
    do_rc = np.dot(do, rc)

    # Prepare the coefficients of a quadratic equation.
    A = re_re * rc_rc - re_rc**2
    B = 2 * (do_rc * re_rc - do_re * rc_rc)
    C = do_do * rc_rc - do_rc**2 - radius**2 * rc_rc

    # Solve the quadratic equation, take the larger root.
    ae = (-B + np.sqrt(B**2 - 4 * A * C)) / (2 * A)

    # Recover the point pc on the central ray.
    pe = oe + ae * re
    ac = -np.dot(oc - pe, rc) / rc_rc
    pc = oc + ac * rc

    return pc


##-----------------------------------------------------------------------------
# Refine ball center positions using all contour rays.

# ball: approximate center coordinates in 3D, array [3], (X, Y, Z)
# cone: list of view rays, 0-th: center, rest: contour points,
#   view ray: (o, r),
#     o: array [3], view ray origin point
#     r: array [3], view ray direction vector
# radius: float, a priori known ball radius
# cfg: configuration dict
# return: refined ball center in 3D, array [3], (X, Y, Z)


def refine_ball(ball, cone, radius, cfg):

    # We neglect the central view ray.
    num_rays = len(cone) - 1

    # Aux function: distance between a ray and a point.
    # o: array [3], ray origin point
    # r: array [3], direction vector of the ray
    # p: array [3], point in 3D
    # return: scalar distance
    def rpdist(o, r, p):
        u = o - p
        a = -np.dot(u, r) / np.dot(r, r)
        d = u + a * r
        return np.sqrt(np.dot(d, d))

    # Aux function: discrepancies between the ray-point
    # distances and the ball's radius for the cone
    # p: array [3], point in 3D
    def errf(p):
        e = [rpdist(o, r, p) - radius for (o, r) in cone[1:]]
        return np.array(e)

    # Find the point that minimizes the discrepancies.
    res = scipy.optimize.least_squares(errf, ball, method="lm")
    ball_r = res.x

    return ball_r


##-----------------------------------------------------------------------------
# Re-project the ball's center back onto the sensor.

# ball: center coordinates in 3D, array [3], (X, Y, Z)
# cand: candidate, array [3], (x, y, r)
# radius: float, a priori known ball radius
# cam: dict of camera parameters
# cfg: configuration dict
# return: projection of the ball's center, array [2], (x, y)


def project_center(ball, cand, radius, cam):

    # Extract the intrinsic parameters.
    imtx = np.array(cam["intrinsics"]["camera_matrix"])
    dist = np.array(cam["intrinsics"]["distortion_coefficients"])
    dist = dist.reshape((1, -1))

    p = ball.reshape((3, 1))
    q = cv_project(p, imtx, dist).flatten()
    return q


##-----------------------------------------------------------------------------
# Re-project a ball's contour back onto the sensor.

# ball: center coordinates in 3D, array [3], (X, Y, Z)
# cont: list of found contour points,
#   contour point: array [2], (x, y)
# radius: float, a priori known ball radius
# cam: dict of camera parameters
# cfg: configuration dict
# return: list of refined contour points,
#   contour point: array [2], (x, y)


def project_contour(ball, cont, radius, cam, cfg):

    # Number of points to project.
    num_points = cfg["ShowTargets"]["points"]

    # Extract the intrinsic parameters.
    imtx = np.array(cam["intrinsics"]["camera_matrix"])
    dist = np.array(cam["intrinsics"]["distortion_coefficients"])
    dist = dist.reshape((1, -1))

    # Pre-compute several points on a circle.
    angs = np.linspace(0.0, 2 * np.pi, num_points)
    us = radius * np.sin(angs)
    vs = radius * np.cos(angs)

    cont_r = []
    ctr = cv_project(ball, imtx, dist).flatten()
    cont_r.append(ctr)

    # Cut parallel to the x-plane.
    for u, v in zip(us, vs):
        p = (ball + np.array([0, u, v])).reshape((3, 1))
        q = cv_project(p, imtx, dist).flatten()
        cont_r.append(q)
    cont_r.append(ctr)

    # Cut parallel to the y-plane.
    for u, v in zip(us, vs):
        p = (ball + np.array([u, 0, v])).reshape((3, 1))
        q = cv_project(p, imtx, dist).flatten()
        cont_r.append(q)
    cont_r.append(ctr)

    # Cut parallel to the z-plane.
    for u, v in zip(us, vs):
        p = (ball + np.array([u, v, 0])).reshape((3, 1))
        q = cv_project(p, imtx, dist).flatten()
        cont_r.append(q)
    cont_r.append(ctr)

    return cont_r


##-----------------------------------------------------------------------------
