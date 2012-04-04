#!/usr/bin/python
#coding:utf-8

# Copyright (c) 2012   Universidade de São Paulo et alii. See AUTHORS
# file for details.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

###############################################################################
## This script uses OpenCV point feature extractor to analyze one
## input image, and save the coordinates to an output file.

import cv
import sys

if __name__ == '__main__':
    if sys.argv[0][-7:] == '-nop.py':
        PlotStuff=False
    else:
        PlotStuff=True
        import matplotlib
        if sys.argv[0][-7:] == '-nox.py':
            matplotlib.use('Agg') 

from pylab import *

import simplejson

if __name__ == '__main__':

    ## Sets filename from input argument
    if len(sys.argv) < 3:
        print sys.argv[0], '<job_file.json> <frame_number>'
        raise Exception('Insufficient number of parameters')

    finput = open(sys.argv[1])
    job_params = simplejson.load(finput)
    finput.close()

    fileroot = job_params['root_directory']

    framenum = int(sys.argv[2])
    filename = fileroot+'/frames/'+job_params['filename_format']%framenum
    output_file = fileroot+'/points/'+'%08d'%framenum

    #Load source image and convert it to gray
    src = cv.LoadImageM(filename, cv.CV_LOAD_IMAGE_GRAYSCALE)

    Np = 1000

    #Apply corner detection
    criteria = (cv.CV_TERMCRIT_ITER|cv.CV_TERMCRIT_EPS, 10, 0.03)
    eig = cv.CreateImage(cv.GetSize(src), 32, 1)
    temp = cv.CreateImage(cv.GetSize(src), 32, 1)
    points = cv.GoodFeaturesToTrack(src, eig, temp, Np, 0.01, 10, None, 3, 0, 0.04)
    points = cv.FindCornerSubPix(src, points, (11,11), (-1, -1), criteria)

    points = array(points)

    #Save the points
    savez(output_file, points)


    if PlotStuff:
        ion()
        imshow(src, cmap=cm.bone)
        for pp in points:
            plot(points[:,0], points[:,1], 'ro')

