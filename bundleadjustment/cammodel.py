from pylab import *
from quaternion import Quat
from scipy.optimize import fmin



def project_points(shape, t, psi, fd, kappa, oc, distortion_method=1):

  ## 3D points in the camera reference frame
  rc = dot(shape-t, Quat(psi).rot())

  ## Perspective projection
  q = rc[:,:2] * fd / rc[:,[2,2]]

  if distortion_method == 0:
    rho2 = (q[:,0]**2 + q[:,1]**2)
    a = np.abs(1+kappa[0]*rho2)**-0.5
    p = q * c_[[a,a]].T + oc
    print a
  elif distortion_method == 1:
    rd = np.array([sqrt(q[:,0]**2+q[:,1]**2)]).T
    rd2 = rd**2
    rd4 = rd**4
    rd6 = rd**6
    rd8 = rd**8
    s = (size(rd),1)
    um = np.ones(s)
    factor = (kappa[0]*rd2+kappa[1]*rd4+(kappa[0]**2)*rd4+(kappa[1]**2)*rd8+2*kappa[0]*kappa[1]*rd6)/(um+4*kappa[0]*rd2+6*kappa[1]*rd4)  
    p = q - q*factor + oc
  else:
    print 'Model argument must be 0 (Harris) or 1 (Brown).'

  print q
  
  return p
  
def error (X, shape, qi, Ncam, distortion_method=1):
	
  ###Dados de entrada
  #recebe do ba e destrincha o vetor
  vecext = np.zeros(6*Ncam)
  vecint = np.zeros(3)
  oc = np.zeros(2)

  for i in range (6*Ncam):
    vecext[i] = X[i]

  vecint[0] = X[6*Ncam]
  vecint[1] = X[6*Ncam+1] 
  vecint[2] = X[6*Ncam+2] 
  oc[0] = X[6*Ncam+3] 
  oc[1] = X[6*Ncam+4]
 
  kappa = array([vecint[0]*1e-9, vecint[1]*1e-9])
  fd = vecint[2]
  
  q = []
  for cam in range(Ncam):
    t = vecext[cam*6:cam*6+3]
    psi = vecext[cam*6+3:cam*6+6]
    q.append(project_points(shape, t, psi, fd, kappa, oc, distortion_method))

  #Error function
  #Ja calcula para todas as imagens
  e = ((q-qi)**2).sum()

  return e


## Local variables:
## python-indent: 2
## end:
