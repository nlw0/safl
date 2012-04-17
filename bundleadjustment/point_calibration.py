#!/usr/bin/python2.7
#coding: utf-8
from pylab import *
from scipy.optimize import *
from cammodel import *

import simplejson

if __name__ == '__main__':

  PlotStuff = True

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

  matches = np.load(job_params['root_directory']+'/points/matches.npz')['matches']

  pp_ref = []

  shape = array([
    [ 0, 0,0],[ 0,-2,0],[ 0,-4,0],
    [-2,-1,0],[-2,-3,0],[-2,-5,0],
    [-4, 0,0],[-4,-2,0],[-4,-4,0],
    [-6,-1,0],[-6,-3,0],[-6,-5,0],
    [-8, 0,0],[-8,-2,0],[-8,-4,0],
                     ])

  distortion_model=0
  fd = 800.0
  kappa = array([100.0])
  oc = array([639, 479])

  t_0 = array([0.0,0,-10])
  psi_0 = array([0.0,0,0])
  
  for framenumber in the_frames:
    subplot(3,3,1+framenumber)
    sys.stderr.write('Reading frame %d\n'%framenumber)
    pp = np.load(job_params['root_directory']+'/points/'+'%08d.npz'%framenumber)['arr_0']
    img = flipud(imread(job_params['root_directory']+'/frames/'+'%08d.bmp'%framenumber))
    mm = matches[framenumber]
    mm = mm[mm>=0]
    pp_ref.append(pp[mm])

    imshow(img, cm.bone)
    plot(pp[mm,0], pp[mm,1], 'bo')

    
    pp_opt = project_points(shape, t_0, psi_0,
                            fd, kappa, oc,
                            distortion_model)

    plot(pp_opt[:,0], pp_opt[:,1], 'go')


  pp_ref = asarray(pp_ref)







## Local variables:
## python-indent: 2
## end:
