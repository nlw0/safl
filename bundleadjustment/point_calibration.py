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
from scipy.optimize import *
from cammodel import *

from camera_model import reprojection_error, calculate_all_projections



import simplejson


if __name__ == '__main__':

  ## Avoid zero divide warnins...
  np.seterr(divide='ignore')

  if PlotStuff:
    ## Plot stuff immediately
    ion()

  ##################################################################
  ## Read all the job parameters
  if len(sys.argv) != 2 and len(sys.argv) != 4:
    print sys.argv[0], '<job_file.json> [first frame last_frame]'
    raise Exception('Insufficient number of parameters')

  finput = open(sys.argv[1])
  job_params = simplejson.load(finput)
  finput.close()

  ## Sets filename list from input argument
  if len(sys.argv) == 4:
    frmf = int(sys.argv[2])
    frml = int(sys.argv[3])
    the_frames = range(frmf, frml+1)
  if len(sys.argv) == 2:
    the_frames = [int(x) for x in sys.stdin.read().split()]


  Ncam = len(the_frames)

  matches = np.load(job_params['root_directory']+'/points/matches.npz')['matches']

  shape = array([
    [ 0, 0,0],[ 0,-2,0],[ 0,-4,0],
    [-2,-5,0],[-2,-3,0],[-2,-1,0],
    [-4, 0,0],[-4,-2,0],[-4,-4,0],
    [-6,-5,0],[-6,-3,0],[-6,-1,0],
    [-8, 0,0],[-8,-2,0],[-8,-4,0],
                     ], dtype=np.float64)

  ## Initial estimates of intrinsic parameters.
  p_point = array(job_params['principal_point'])
  focal_distance = job_params['focal_distance']
  distortion_coefficient = job_params['distortion_coefficient']

  what_model = 1
  if what_model in [0,2]:
    vecint = array([focal_distance, 
                    p_point[0], p_point[1]])
  else:
      vecint = array([focal_distance, 
                      p_point[0], p_point[1],
                      distortion_coefficient  ])




  t_ini = array([-4,-3,-20.0])

  if what_model in [0,2]:
    x_ini = np.zeros(6*Ncam+3, dtype=np.float64)
  elif what_model == 1:
    x_ini = np.zeros(6*Ncam+4, dtype=np.float64)
  elif what_model in [3,4]:
    x_ini = np.zeros(6*Ncam+5, dtype=np.float64)

  x_ini[6*Ncam:] = vecint
  x_ini[0:6*Ncam:6] = t_ini[0]
  x_ini[1:6*Ncam:6] = t_ini[1]
  x_ini[2:6*Ncam:6] = t_ini[2]

  x_ini += random(x_ini.shape) * 0.01
  
  ## Get the observations ready, look for the approriate index for
  ## each image, using the 'matches' array.
  pp_ref = []
  for framenumber in the_frames:
    # sys.stderr.write('Reading frame %d\n'%framenumber)
    points_filename = job_params['root_directory']+'/points/'+'%08d.npz'%framenumber
    p_ref_all = np.load(points_filename)['arr_0']
    mm = matches[framenumber]
    mm = mm[mm>=0]
    pp_ref.append(p_ref_all[mm])
  pp_ref = asarray(pp_ref, dtype=np.float64)

  ## Calculate reprojections in the initial estimate.
  pp_ini = calculate_all_projections(x_ini, shape, Ncam, what_model)

  x_opt = fmin_bfgs(reprojection_error, x_ini, args=(shape, pp_ref, what_model), disp=False)
  pp_opt = calculate_all_projections(x_opt, shape, Ncam, what_model)

  ## Plota primeiras 9 imagens, e pontos extraídos, reprojeções
  ## iniciais, e reprojeções na solução encontrada.


  if PlotStuff:
    for ii in range(3):
      for kk in range(9):
        kpp = ii*9++kk
        if kpp >= Ncam:
          break

        framenumber = the_frames[kpp]
        p_ref = pp_ref[kpp]
        p_ini = pp_ini[kpp]
        p_opt = pp_opt[kpp]

        figure(ii)
        subplot(3,3,1+kk)
        img = flipud(imread(job_params['root_directory']+'/frames/'+'%08d.bmp'%framenumber))
        imshow(img, cm.bone)
        aa = axis()
        plot(p_ref[:,0], p_ref[:,1], 'bo')
        # plot(p_ini[:,0], p_ini[:,1], 'g+', mew=1, ms=7, alpha=0.4)
        plot(p_opt[:,0], p_opt[:,1], 'rx', mew=1.5)

        for n in range(p_ref.shape[0]):
          # plot([p_opt[n,0], p_ini[n,0]],
          #      [p_opt[n,1], p_ini[n,1]],
          #      'g-', alpha=0.4)
          plot([p_ref[n,0], p_opt[n,0]],
               [p_ref[n,1], p_opt[n,1]],
               'r-', alpha=0.4)
        axis(aa)







  err = reprojection_error(x_opt, shape, pp_ref, what_model)

  print x_opt[-4], x_opt[-3], x_opt[-2], x_opt[-1], err



## Local variables:
## python-indent: 2
## end:
