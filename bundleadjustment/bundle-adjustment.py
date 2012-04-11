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

  distortion_model = 0 #0 harris e 1 brown



  ## Original intrinsic parameters of the camera.
  vecint = array([5000.0, 880.0])

  ## Original extrinsic parameters of each pose.
  vecext = array([4,0,-8.0,0,-0.2,0,
                   0,0,-8.0,0,-0.05,0,
                   0,-3,-6.0,-0.23,-0.05,0,
                   -4,0,-8.0,0,0.2,0.05])

  # oc = array([320.0,240.0])
  # kappa = array([0.0, 0.0])
  # fd = 320.0
  oc = array([500.0, 375.0])
  kappa = array([vecint[0]*1e-9, 0.0])
  fd = vecint[1]

  pp = []
  for cam in range(Ncam):
    t = vecext[cam*6:cam*6+3]
    psi = vecext[cam*6+3:cam*6+6]
    pp.append(project_points(shape, t, psi, fd, kappa, oc, distortion_model))

  vecext2 = vecext + random(vecext.shape)*0.05
  pp2 = []
  for cam in range(Ncam):
    t = vecext2[cam*6:cam*6+3]
    psi = vecext2[cam*6+3:cam*6+6]
    qq = project_points(shape, t, psi, fd, kappa, oc, distortion_model)
    pp2.append(qq + random(qq.shape)*10.0)





  ion()
  for cam in range(Ncam):
    subplot(2,2,1+cam)
    plot(pp[cam][:,0], pp[cam][:,1], 'bo')
    plot(pp2[cam][:,0], pp2[cam][:,1], 'rx')
    axis('equal')
    axis([0,1000.0,750.0,0])


## Local variables:
## python-indent: 2
## end:
