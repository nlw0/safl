#!/usr/bin/python2.7
# coding: utf-8
import json

from pylab import *
import numpy as np
import cv2
import scipy.optimize
import camera_model

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

    # H = array(
    #     [[7.047e-01, -7.215e-02, -2.325e+03],
    #      [-4.925e-03, 3.972e-01, -6.809e+02],
    #      [0.000e+00, 0.000e+00, 1.000e+00]]
    # )


    # H = array(
    #     [[6.438e-01, -1.562e-01, -1.834e+03],
    #      [-3.629e-03, 3.956e-01, -6.864e+02],
    #      [0.000e+00, 0.000e+00, 1.000e+00]]
    # )  ## second pair

    # H = array(
    #     [[5.960e-01, -8.127e-02, -1.911e+03],
    #      [9.234e-03, 2.824e-01, -4.909e+02],
    #      [2.884e-05, -1.044e-04, 1.000e+00]]
    # )
    H = array(
        [[1.796e-01, -1.374e-01, -2.719e+02],
         [3.461e-03, 4.025e-03, 6.590e+01],
         [6.729e-06, -2.899e-04, 1.000e+00]]
    ) ## just first image
    G = inv(H)

    # rp = array(hstack((observations[1], ones((10, 1)))))
    # lp = array(hstack((observations[0], ones((len(observations[0]), 1)))))
    rp = array(hstack((observations[3], ones((len(observations[3]), 1)))))
    lp = array(hstack((observations[2], ones((len(observations[2]), 1)))))

    lprime = dot(H, rp.T).T
    lprime = lprime[:, [0, 1]] / lprime[:, [2, 2]]
    rprime = dot(G, lp.T).T
    rprime = rprime[:, [0, 1]] / rprime[:, [2, 2]]

    qq = imread(datapath + '/frames/{:08d}.png'.format(2))
    ww = imread(datapath + '/frames/{:08d}.png'.format(3))
    ion()
    subplot(2, 2, 1)
    imshow(qq)
    plot(observations[2][:, 0], observations[2][:, 1], 'o')
    plot(lprime[:, 0], lprime[:, 1], 'ro')

    subplot(2, 2, 2)
    imshow(ww)
    plot(observations[3][:, 0], observations[3][:, 1], 'o')
    plot(rprime[:, 0], rprime[:, 1], 'ro')

    outt = cv2.warpPerspective(ww, H, (qq.shape[1], qq.shape[0]))

    subplot(2, 2, 3)
    imshow(outt)
