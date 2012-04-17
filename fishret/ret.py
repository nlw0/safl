from pylab import *
import sys, os, Image, ImageFilter

if __name__ == '__main__':

  ## Sets filename from input argument
  if len(sys.argv) < 2:
    raise Exception('Insufficient number of parameters')
  else:
    filename = sys.argv[1]

  output_file = 'ret'+filename

  ##Load source image
  #src = Image.open(filename) 
  src = flipud(imread(filename))

  ret_model = 0 #0 harris, 1 odd polynomial, 2 equidistant, 3 stereographic
  interpol = 2 #0 no interpol, 1 bilinear, 2 bicubic

  ##parameters from camera calibration
  im_width = src.shape[1] #size(src)[0]
  im_height = src.shape[0] #size(src)[1]

  if ret_model == 0:
    oc = array([621.35, 505.44])
    kappa = array([3882.13e-9,0.])
    fd=365.96
  elif ret_model == 1:
    oc = array([621.35, 505.44])
    kappa = array([1e-6,0])
    fd = 365.96
  elif ret_model == 2:
    oc = array([621.35, 505.44])
    kappa = array([1e-6,0])
    fd = 365.96
  elif ret_model == 3:
    oc = array([621.35, 505.44])
    kappa = array([1e-6,0])
    fd = 365.96

  ##create output image
  out_height = 1000
  out_width = 1000
  #out = Image.new(src.mode, (out_width,out_height))	
  #pix = out.load()

  pix = zeros((out_height, out_width))
	
  ##define coordinates
  Oc_in_Of_x = im_width/2#oc[0]
  Oc_in_Of_y = im_height/2#oc[1]
  Oc_in_Or_x = out_width / 2.
  Oc_in_Or_y = out_height / 2.

  for i in range (out_height):
    for j in range (out_width): 
      #Coordenadas do "centro" do PixelCoordinates p no sistema r
      p_in_Or_x = j + 0.5
      p_in_Or_y = i + 0.5
      #Coordenadas do "centro" do PixelCoordinates p no sistema c
      escala = 5
      p_in_Oc_x = escala*(p_in_Or_x - Oc_in_Or_x)
      p_in_Oc_y = escala*(p_in_Or_y - Oc_in_Or_y)
      rp = sqrt(p_in_Oc_x**2 + p_in_Oc_y**2)
      if ret_model == 0:
        factor = 1/(sqrt(abs(1+kappa[0]*rp**2)))#mudei 1-kappa para 1+kappa
      elif ret_model == 1:
	factor = rp+kappa[0]*rp**3+kappa[1]*rp**5
      elif ret_model == 2:
	factor = fd*math.atan(rp/fd)/rp
      elif ret_model == 3:	
	factor = 2*fd*(math.tan((math.atan(rp/fd))/2))/rp

      #Coordenadas do "centro" do PixelCoordinates f no sistema c
      f_in_Oc_x = p_in_Oc_x * factor
      f_in_Oc_y = p_in_Oc_y * factor
      #Coordenadas do "centro" do PixelCoordinates f no sistema f
      f_in_Of_x = f_in_Oc_x + Oc_in_Of_x
      f_in_Of_y = f_in_Oc_y + Oc_in_Of_y
      #Coordenadas discretas do "centro" do PixelCoordinates f no sistema c
      f_in_Of_i = int(f_in_Of_y)
      f_in_Of_j = int(f_in_Of_x)
	
      if((f_in_Of_j<2) or (f_in_Of_j>(im_width-3)) or (f_in_Of_i<2) or (f_in_Of_i>(im_height-3))):
        pix[i,j] = 0
      else: 
	# pix[j,i] = src.getpixel((f_in_Of_j,f_in_Of_i))
	pix[i,j] = src[f_in_Of_i,f_in_Of_j]

  ion()
  figure(1)
  imshow(src, cm.gray)
  plot([im_width/2], [im_height/2], 'bo')

  figure(2)
  imshow(pix, cm.gray)
  plot([500],[500], 'bo')

  #if interpol == 0:	   
  #  out.show()
  #elif interpol == 1:
  #  out.resize((out_width,out_height), Image.BILINEAR)
  #  out.show()
  #elif interpol == 2:
  #  out.resize((out_width,out_height), Image.BICUBIC)
  #  out.show()
