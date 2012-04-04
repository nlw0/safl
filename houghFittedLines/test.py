import Image
from pylab import *
import scipy.ndimage
import fitTools as n
import skimage.filter
import skimage.transform

im = asarray(Image.open("/home/ftruzzi/ciencia/DADOS/yorkurban/frames/00000001.png").convert("L"), dtype=np.float)
dx = scipy.ndimage.sobel(im,0)
dy = scipy.ndimage.sobel(im,1)
mag = np.hypot(dx,dy)
theta = arctan2(dy,dx)+np.pi
theta = theta*180/np.pi
edges = skimage.filter.canny(im,1,150,80)
lines = skimage.transform.probabilistic_hough(edges,10,50,5)

#linha,coluna = nonzero(edges==True)


       

#p0,pl = lines[0]
#linhas = n.walkInLine(p0[0],p0[1],pl[0],pl[1],mag.astype("float"),edges.astype("float"))



ion()
imshow(edges, cm.bone, interpolation='nearest')
for p0,pl in lines:
    linhas = n.walkInLine(p0[0],p0[1],pl[0],pl[1],mag.astype("float"),edges.astype("float"))
#    linhas2 = n.walkInLine2(p0[0],p0[1],pl[0],pl[1],mag.astype("float"),edges.astype("float"))
    if len(linhas) != 0:
        plot(linhas[:,1],linhas[:,0],'-+')
#        plot(linhas2[:,1],linhas2[:,0],'-d')


def compareFittingV(houghLine):
    p0, pl =  houghLine
    linhas = n.walkInLine(p0[0],p0[1],pl[0],pl[1],mag.astype("float"),edges.astype("float"))
    linhas2 = n.walkInLine2(p0[0],p0[1],pl[0],pl[1],mag.astype("float"),edges.astype("float"))
    plot(linhas[:,1]-linhas2[:,1])
    grid()

def compareFittingH(houghLine):
    p0, pl =  houghLine
    linhas = n.walkInLine(p0[0],p0[1],pl[0],pl[1],mag.astype("float"),edges.astype("float"))
    linhas2 = n.walkInLine2(p0[0],p0[1],pl[0],pl[1],mag.astype("float"),edges.astype("float"))
    plot(linhas[:,0]-linhas2[:,0])
    grid()

    
    
