#!/usr/bin/python2.7
#coding: utf-8

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


import sys

if __name__ == '__main__':
    
    import matplotlib
    if sys.argv[0][-7:] == '-nop.py':
        PlotStuff=False
    else:
        PlotStuff=True
        from pylab import *
        if sys.argv[0][-7:] == '-nox.py':
            matplotlib.use('Agg') 

from pylab import *

from camera_model import *

import simplejson


if __name__ == '__main__':
  ## Avoid zero divide warnings...
  np.seterr(divide='ignore')

  if PlotStuff:
    ## Plot stuff immediately
    ion()

  ##################################################################
  ## Read all the job parameters
  if len(sys.argv) != 3 and len(sys.argv) != 4:
    print sys.argv[0], '<job_file.json> <frame number>'
    raise Exception('Insufficient number of parameters')

  finput = open(sys.argv[1])
  job_params = simplejson.load(finput)
  finput.close()

  framenumber = int(sys.argv[2])

  img = imread(job_params['root_directory']+'/frames/'+
               job_params['filename_format']%framenumber)
  #img = ascontiguousarray(flipud(img), dtype=float64)
  img = ascontiguousarray(flipud(img), dtype=np.uint8)

  # parout = array([100, 500, 500.0])
  # parout = array([1000/(2*pi), 600, 800.0]) # cyl (7)
  parout = array([600, 600, 400.0]) # stereográfica

  #parsrc = array([300, 650,500,3000e-9])
  #parsrc = array([300, 639,479,3000e-9])
  #parsrc = array([ 390.678, 617.934, 505.704]) #polar equidi (2)
  parsrc = array([ 390.678, 639.0, 479.0]) #polar equidi (2)

  #out = zeros((1000,1000,3), dtype=float64)
  out = zeros((800,1200,3), dtype=uint8)
  reproject(out, img, 8, parout, 2, parsrc)

  ion()
  figure(1)
  imshow(img)
  aa=axis()
  plot([parsrc[1]], [parsrc[2]], 'bs')
  axis(aa)

  figure(2)
  imshow(out)
  aa=axis()
  plot([parout[1]], [parout[2]], 'bs')
  axis(aa)
  
## Local variables:
## python-indent: 2
## end:
