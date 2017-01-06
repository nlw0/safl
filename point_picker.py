import sys

import cv2

import scipy.ndimage

from pylab import *

import numpy as np
import matplotlib.pyplot as plt

import simplejson


class Coisa:
    def __init__(self):
        ## Sets filename from input argument
        if len(sys.argv) < 3:
            print(sys.argv[0], '<job_file.json> <frame_number>')
            raise Exception('Insufficient number of parameters')

        finput = open(sys.argv[1])
        job_params = simplejson.load(finput)
        finput.close()

        fileroot = job_params['root_directory']

        framenum = int(sys.argv[2])
        filename = fileroot + '/frames/' + job_params['filename_format'] % framenum
        output_file = fileroot + '/points/' + '%08d' % framenum

        # Load source image and convert it to gray
        src = array(imread(filename)[:, :, 1], dtype=float32)
        # src = array(scipy.ndimage.gaussian_filter(isrc, 1.0) - scipy.ndimage.gaussian_filter(isrc, 100.0))[::1, ::1]

        ion()
        self.fig = figure()
        self.ax = subplot(111)
        self.ax.imshow(src)

        self.mypt, = self.ax.plot([], [], 'yo', picker=3)
        self.pointsx = []
        self.pointsy = []

        # cida = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        cidb = self.fig.canvas.mpl_connect('key_press_event', self.onpress)
        cidc = self.fig.canvas.mpl_connect('pick_event', self.onpick)

    def onpick(self, event):
        if event.mouseevent.button == 3:
            print('\n' + event.name)
            print(vars(event))
            nn = event.ind[0]
            print('ind:::', nn)
            print(self.pointsx)
            self.pointsx.pop(nn)
            self.pointsy.pop(nn)
            print(self.pointsx)
            self.mypt.set_data(self.pointsx, self.pointsy)
            self.fig.canvas.draw()

    def onpress(self, event):
        if event.key == 'q':
            print('\n' + event.name)
            x, y = event.xdata, event.ydata
            print('new point x = {}, y = {}'.format(x, y))
            print(vars(event))
            print(self.pointsx)
            self.pointsx.append(x)
            self.pointsy.append(y)
            print(self.pointsx)
            self.mypt.set_data(self.pointsx, self.pointsy)
            self.fig.canvas.draw()

        if event.key == 'd':
            print('\n' + event.name)
            x, y = event.xdata, event.ydata
            print('new point x = {}, y = {}'.format(x, y))
            print(vars(event))
            print(self.pointsx)
            self.pointsx.pop(1)
            self.pointsy.pop(1)
            print(self.pointsx)
            self.mypt.set_data(self.pointsx, self.pointsy)
            self.fig.canvas.draw()


if __name__ == '__main__':
    coisa = Coisa()
