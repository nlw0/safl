#!/usr/bin/python2.7
#coding: utf-8
from pylab import *
from scipy.optimize import fmin
from scipy.optimize import fmin_powell
from cammodel import *


if __name__ == '__main__':
  #Informacoes quanto ao numero de imagens, pontos e modelo de distorcao
  Npt = 25 # Number of landmarks in the environment

  Ncam = 4

  ## The coordinates of the landmarks
  shape = zeros((Npt, 3))

  yy,xx = mgrid[-2.0:3.0,-2.0:3.0]
  shape[:,0] = xx.ravel()
  shape[:,1] = yy.ravel()

  distortion_model = 0 #0 harris e 1 odd polynomial


  ## Original intrinsic parameters of the camera.
  # oc = array([320.0,240.0])
  # kappa = array([0.0, 0.0])
  # fd = 320.0
  oc = array([500.0, 375.0])
  kappa = 5000
  fd = 880
  vecint = array([fd, kappa, oc[0], oc[1]])

  ## Original extrinsic parameters of each pose.
  vecext = array([ 4, 0,-8.0, 0,   -0.2,  0,
                   0, 0,-8.0, 0,   -0.05, 0,
                   0,-3,-6.0,-0.23,-0.05, 0,
                  -4, 0,-8.0, 0,    0.2,  0.05])

  ## Monta estimativa inicial da calibração, a partir dos valores corretos.
  x_ans = np.zeros(6*Ncam+4)
  x_ans[:6*Ncam] = vecext[:6*Ncam]
  x_ans[6*Ncam:] = vecint

  ## Calcula as coordenadas dos pontos extraídos das imagens, usando
  ## os valores corretos de todos parâmetros.
  pp_ans = project_all_the_points(shape, x_ans, Ncam, distortion_model)

  ## Monta estimativa inicial da calibração, a partir dos valores corretos.
  x_ini = np.zeros(6*Ncam+4)
  x_ini[:6*Ncam] = vecext[:6*Ncam]
  x_ini[6*Ncam:] = vecint
  for c in range(Ncam):
    # x_ini[6*c:6*c+3] += random(3) * 1e-1 ## some noise
    # x_ini[6*c+3:6*c+6] += random(3) * 1e-2 ## some noise
    x_ini[6*c:6*c+3] += random(3) * 1e-0 ## some noise
    x_ini[6*c+3:6*c+6] += random(3) * 1e-1 ## some noise
  ## Calcula todas projeções com os parâmetros estimados.
  pp_ini = project_all_the_points(shape, x_ini, Ncam, distortion_model)

  # x_opt = fmin(error, x_ini, args = (shape, pp_ans, Ncam, distortion_model),
  #              maxiter = 100000, maxfun = 100000 )
  x_opt = fmin(error, x_ini, args = (shape, pp_ans, Ncam, distortion_model),
               maxiter = 100000, maxfun = 100000 )
  pp_opt = project_all_the_points(shape, x_opt, Ncam, distortion_model)

  ion()
  for cam in range(Ncam):
    subplot(2,2,1+cam)
    la = plot(pp_ans[cam][:,0], pp_ans[cam][:,1], 'b+')[0]
    lb = plot(pp_ini[cam][:,0], pp_ini[cam][:,1], 'gx',alpha=0.5)[0]
    lc = plot(pp_opt[cam][:,0], pp_opt[cam][:,1], 'rx')[0]
    axis('equal')
    axis([0,1000.0,750.0,0])
  figlegend([la,lb,lc], ['pts','ini','ans'] )

  print "Parâmetros externos"
  for c in range(Ncam):
    print "img", c
    print x_opt[6*c:6*c+3]
    print x_ans[6*c:6*c+3]
    print x_opt[6*c+3:6*c+6]
    print x_ans[6*c+3:6*c+6]
    print 70*'='
    
  print "Parâmetros internos"
  print x_ini[-4:]
  print x_opt[-4:]
  print x_ans[-4:]

## Local variables:
## python-indent: 2
## end:
