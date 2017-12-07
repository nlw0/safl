#!/usr/bin/python2.7
# coding: utf-8
import json

from pylab import *
import numpy as np
import scipy.optimize
import camera_model


def error(X, intrinsic_parameters, Ncam, point_measurements, match_list):
    myprojs = projections(X, intrinsic_parameters, Ncam, match_list)
    rez = point_measurements.reshape(-1, 2) - myprojs
    otherside = abs(rez[:, 0]) > intrinsic_parameters[0]
    rez[otherside, 0] = 2 * intrinsic_parameters[0] - rez[otherside, 0]

    middle_cam_params = 1e5 * X[6 * (Ncam // 2):6 * (Ncam // 2) + 6]

    scale_statistic = std(X[6 * Ncam:]) - 0.81

    return hstack((rez.ravel(), middle_cam_params, scale_statistic))


def print_params(X, Ncam):
    cam_pos = X[:Ncam * 6].reshape(-1, 6)
    pts = X[Ncam * 6:].reshape(-1, 3)

    print('Camera poses:\n', cam_pos)
    print('Points:\n', pts)


def save_solution(X, Ncam):
    cam_pos = X[:Ncam * 6].reshape(-1, 6)
    np.savez(datapath + '/estimated_poses', cam_pos)


def plot_solution(X, Ncam):
    cam_pos = X[:Ncam * 6].reshape(-1, 6)
    pts = X[Ncam * 6:].reshape(-1, 3)

    figure()
    axis('equal')
    grid()
    plot(-cam_pos[:, 1], cam_pos[:, 0], 'bs-', lw=2)
    plot(-pts[:, 1], pts[:, 0], 'ro')


def projections(X, intrinsic_parameters, Ncam, match_list):
    cam_pos = X[:Ncam * 6].reshape(-1, 6)
    pts = X[Ncam * 6:].reshape(-1, 3)
    return camera_model.calculate_all_projections(cam_pos, intrinsic_parameters, pts, match_list)


def homo_mat(h):
    H = eye(3)
    H[0] = h[0:3]
    H[1] = h[3:6]
    #H[2,:2] = h[6:8]
    return H

def homo_residue(h, leftpts, rightpts):
    H = homo_mat(h)
    G = inv(H)

    lprime = dot(H, rightpts.T).T
    lprime = lprime[:,[0, 1]] / lprime[:,[2, 2]]
    rprime = dot(G, leftpts.T).T
    rprime = rprime[:,[0, 1]] / rprime[:,[2, 2]]

    lrez = (leftpts[:,:2] - lprime).ravel()
    rrez = (rightpts[:, :2] - rprime).ravel()
    return hstack((lrez, rrez))


def make_homogeneous(aa):
    return hstack((aa, ones((aa.shape[0], 1))))


if __name__ == '__main__':
    set_printoptions(precision=3)

    datapath = '/home/lealwern/data/aptina/aptina'
    config = json.load(open(datapath + '.json'))

    observations = [np.load(datapath + '/points/{:08d}.npz'.format(n))['arr_0'] for n in
                    range(1 + config['last_frame'])]
    matches = np.load(datapath + '/points/matches.npz')['matches']

    Ncam = matches.shape[0]
    Npts = 1 + max(nonzero(matches.max(axis=0) > -1)[0])
    print('cameras: {} points: {}'.format(Ncam, Npts))

    match_list = array([[kc, kp] for kc, pp in enumerate(matches) for kp in nonzero(pp > -1)[0]], dtype=np.int)

    # left_points = make_homogeneous(
    #     array([observations[0][matches[0, p]] for p in range(10)] + \
    #           [observations[2][matches[2, p]] for p in range(10, 24)])
    #     )
    # right_points = make_homogeneous(
    #     array([observations[1][matches[1, p]] for p in range(10)] + \
    #           [observations[3][matches[3, p]] for p in range(10, 24)])
    #     )
    left_points = make_homogeneous(
        array([observations[2][matches[2, p]] for p in range(14)])
        )
    right_points = make_homogeneous(
        array([observations[3][matches[3, p]] for p in range(14)])
        )

    h0 = array([1, 0, 0, 0, 1, 0])
    # h0 = array([7.047e-01, -7.215e-02, -2.325e+03, -4.925e-03, 3.972e-01, -6.809e+02, 0, 0])

    print(homo_residue(h0, left_points, right_points))

    h_opt, _= scipy.optimize.leastsq(homo_residue, h0, args=(left_points, right_points))
    print(h_opt)
    H = homo_mat(h_opt)
    G = inv(H)
    print(H)
    print(G)
