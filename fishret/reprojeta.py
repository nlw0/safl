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

import Image

from quaternion import Quat


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
  filename = (job_params['root_directory']+'/frames/' +
              job_params['filename_format']%framenumber)
  
  img = Image.open(filename)
  #img = ascontiguousarray(flipud(img), dtype=float64)
  #img = ascontiguousarray(flipud(img), dtype=np.uint8)
  img = ascontiguousarray(img, dtype=np.uint8)




  # parsrc = array([ 195.34,  333.0,  250.0])  #fishlti
  # ori = Quat(0.97005637,  0.02279486,  0.04806207,  0.23698326)

  # parsrc = array([ 390.68,  666.  ,  500.  ])  #fishlti
  # ori = Quat(0.97403550,  0.03160926,  0.02077886,  0.22321278)

  parsrc = array([ 390.678,  617.934,  505.704 ])  #fishlti
  #ori = Quat(0.96971691,  0.04488553,  0.05750824,  0.23308198)
  #ori = Quat(0.96971691,  0,0,0.23308198)
  ori = Quat(1.0,0,0,0)



  #out = zeros((1000,1000,3), dtype=float64)
  out = zeros((1000,2000,3), dtype=uint8)

  parout = array([600, 1000, 900.0])

  reproject(out, img, 0, parout, 2, parsrc)



  out_a = zeros((1000,2000,3), dtype=uint8)
  out_b = zeros((1000,2000,3), dtype=uint8)
  out_c = zeros((1000,2000,3), dtype=uint8)
  out_d = zeros((1000,2000,3), dtype=uint8)
  out_e = zeros((1000,2000,3), dtype=uint8)


  qqa = Quat(0,0,-0.5**.5)
  qqb = Quat(-0.5**.5,0,0)
  qqc = Quat(0,0,1.0) * Quat(0.5**.5,0,0)
  qqd = Quat(0,0,-0.5**.5) * Quat(0,0.5**.5,0)
  qqe = Quat(0,0,0.5**.5) * Quat(0,-0.5**.5,0)


  rot = (qqa*ori).rot()

  parout1 = array([400, 1000, 500.0])
  reproject_rotation(out_a, img, 0, parout1, 2, parsrc, rot)

  parout2 = array([1000, 1000, 900.0])

  rot = (qqb*ori).rot()
  reproject_rotation(out_b, img, 0, parout2, 2, parsrc, rot)
  rot = (qqc*ori).rot()
  reproject_rotation(out_c, img, 0, parout2, 2, parsrc, rot)


  parout3 = array([500, 1000, 900.0])

  rot = (qqd*ori).rot()
  reproject_rotation(out_d, img, 0, parout3, 2, parsrc, rot)
  rot = (qqe*ori).rot()
  reproject_rotation(out_e, img, 0, parout3, 2, parsrc, rot)





  out_a[out_a==0] = 255
  out_b[out_b==0] = 255
  out_c[out_c==0] = 255
  out_d[out_d==0] = 255
  out_e[out_e==0] = 255


  ion()
  figure(1)

  title('Imagem obtida com uma lente olho-de-peixe')
  imshow(img)



  # figure(2)
  # imshow(out)





  figure(4, figsize=(10,11))
  subplots_adjust(left=0.05, right=.99,bottom=0.05,top=0.93,wspace=.1,hspace=.3)

  #suptitle(u'Imagens retificadas com orientação estimada')
  suptitle(u'Imagens retificadas sem orientação estimada')

  subplot(2,1,2)
  title('z direction, f=400')
  imshow(out_a)
  aa=axis()
  plot([parout1[1]], [parout1[2]], 'bs')
  axis(aa)

  subplot(4,2,1)
  title('y direction, f=1000')
  imshow(out_b)
  aa=axis()
  plot([parout2[1]], [parout2[2]], 'bs')
  axis(aa)

  subplot(4,2,2)
  title('x direction, f=500')
  imshow(out_d)
  aa=axis()
  plot([parout3[1]], [parout3[2]], 'bs')
  axis(aa)

  subplot(4,2,3)
  title('-x direction, f=500')
  imshow(out_e)
  aa=axis()
  plot([parout3[1]], [parout3[2]], 'bs')
  axis(aa)

  subplot(4,2,4)
  title('-y direction, f=1000')
  imshow(out_c)
  aa=axis()
  plot([parout2[1]], [parout2[2]], 'bs')
  axis(aa)


  
## Local variables:
## python-indent: 2
## end:
