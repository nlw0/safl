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

  print q
  
  return p
  







def cam_model (X, qi, m, n, i):
	
  ###Dados de entrada
  #recebe do ba e destrincha o vetor
  r = X[0:n][0:3]
  fd = X[n][0] 
  k1 = X[n][1]
  k2 = X[n][2]
  oc = X[(n+1)][0:2]
  t = X[(n+2):(n+i+2)][0:4]
  rot = X[(n+i+2):(n+2*i+2)][0:4]

  #Camera orientation and then rotation matrix
  #primeira imagem
  psi = Quat(rot[0][0], rot[0][1], rot[0][2])
  R = psi.rot()
  #agora as outras
  for j in range(i):
    if j != 0:
      psi = Quat(rot[j][0], rot[j][1], rot[j][2])
      R = np.append(R, psi.rot(), axis = 0) 

  R = np.reshape(R, [i,3,3]) #shape(R) = (i,3,3)

  ## Pontos no referencial da camera
  rc = np.zeros((i,n,3))
  #Pontos do objeto constantes, muda R e t de acordo com a imagem
  for j in range (i):
    rc[j] = dot(r-t[j], R[j])

  ## Apply perspective distortion
  #pontos da imagem, projetada
  q = rc[:,:,:2] * fd / rc[:,:,[2,2]]
  #shape(q) = (i,n,2)

  if m == 0:
    rho2 = (q[:,:,0]**2 + q[:,:,1]**2)
    a = c_[2*[1.0/sqrt(1+k1*rho2)]].T
    p = q / reshape(a,(i,n,2)) + oc
    k2 = 0.
    #shape(p) = (i,n,2)
  elif m == 1:
    rd = sqrt(q[:,:,0]**2+q[:,:,1]**2).T
    rd2 = rd**2
    rd4 = rd**4
    rd6 = rd**6
    rd8 = rd**8
    factor = (k1*rd2+k2*rd4+(k1**2)*rd4+(k2**2)*rd8+2*k1*k2*rd6)/(1+4*k1*rd2+6*k2*rd4)
    p = np.zeros((i,n,2))
    for j in range (i): 
      p[j] = q[j] - q[j]*(np.reshape(factor.T[j], [1,n])).T + oc
  else:
    print 'Model argument must be 0 (Harris) or 1 (Brown).'
  
  #Error function
  #Ja calcula para todas as imagens
  e = ((p-qi)**2).sum()

  return e


## Local variables:
## python-indent: 2
## end:
