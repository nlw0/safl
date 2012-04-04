from __future__ import division
cimport cython

import numpy as np
cimport numpy as np

DTYPE = np.float
ctypedef np.float_t DTYPE_t
DTYPE2 = np.uint
ctypedef np.uint_t DTYPE2_t

###########################################################################

# Quadratic-Fit
def fit(DTYPE_t y0,DTYPE_t y1,DTYPE_t y2):
    cdef np.float A, B, C
    x0 = -1
    x1 = 0
    x2 = 1
    A = (y1-y0)*(x2-x0)+(y2-y0)*(x0-x1)
    A /= (x1*x1-x0*x0)*(x2-x0)+(x2*x2-x0*x0)*(x0-x1)

    B = ((y1-y0)/(x1-x0)) - (x1+x0)*A

    C = y2-x2*x2*A-x2*B
   
    if (A != 0):
        return -B/(2*A)
    return 0.0

###########################################################################

# Straight line parameters
def getMBH(DTYPE_t x0,DTYPE_t y0,DTYPE_t x1,DTYPE_t y1):
    if (x1==x0):
        return np.inf,np.inf
    return (y1-y0)/(x1-x0),(y1-x1*(y1-y0)/(x1-x0))    
    
def getMBV(DTYPE_t x0,DTYPE_t y0,DTYPE_t x1,DTYPE_t y1):
    if (y1==y0):
        return np.inf,np.inf
    return (x1-x0)/(y1-y0),(x1-y1*(x1-x0)/(y1-y0))  

###########################################################################
         
# Next Point in a straight line... (x,y) = (column,line)    
def nextPointH(DTYPE2_t t, DTYPE_t m, DTYPE_t b):
    # Horizontal
    if (m == 0): 
        return t,b 
    else:
        return t,t*m+b
        
def nextPointV(DTYPE2_t t, DTYPE_t m, DTYPE_t b):
    # Vertical
    if (m == 0): 
        return b, t
    else:
        return t*m+b,t
        
###########################################################################
        
# Search for Edge in Canny's output
# Search in lines, not Columns
def SearchY(DTYPE_t j, DTYPE_t k, np.ndarray[DTYPE_t, ndim=2]  edges):
    cdef unsigned int t
    t = 0
#    if ((j+1 >= edges.shape[0]) or (k+1 >= edges.shape[1]) or (j < 0) or (k < 0)):
#        return (-1,-1)
    if (edges[j,k] == 1.0):
        return (j,k)
    while (True):
        t += 1
        if (k+t < edges.shape[1]):
            if (edges[j+t,k] == 1.0):
                return (j+t,k)
        if (k-t >= 0):
            if (edges[j-t,k] == 1.0):
                return (j-t,k)
        if (t == 1):
            return (j,k)
            
# Search in Columns               
def SearchX(DTYPE_t j, DTYPE_t k, np.ndarray[DTYPE_t, ndim=2] edges):
    cdef unsigned int t
    t = 0
    if ((j+1 >= edges.shape[0]) or (k+1 >= edges.shape[1]) or (j < 0) or (k < 0)):
        return (-1,-1)
    if (edges[j,k] == 1.0):
        return (j,k)
    while (True):
        t += 1
        if (j+t < edges.shape[0]):
            if (edges[j,k+t] == 1.0):
                return (j,k+t)
        elif (j-t >= 0):
            if (edges[j,k-t] == 1.0):
                return (j,k-t)
        if (t == 1):
            return (j,k)            
        
###########################################################################        
        
# "Walk" in the Line
def walkInLine(DTYPE_t x0, DTYPE_t y0, DTYPE_t x1, DTYPE_t y1, np.ndarray[DTYPE_t, ndim=2] mag, np.ndarray[DTYPE_t, ndim=2] edges):
    cdef float m, b, fk, fj
    cdef unsigned int i, x, y, horizontal, dim
    
    horizontal = 1

    m, b = getMBH(x0,y0,x1,y1)
    dim = int(abs(x0-x1)+1)    

    if ((m == np.inf) or (m > 1) or (m < -1)):
        m, b = getMBV(x0,y0,x1,y1)
        horizontal = 0
        dim = int(abs(y0-y1)+1)
         
    cdef np.ndarray[DTYPE_t, ndim=2] points = np.zeros([dim,2], dtype=DTYPE)

    if (horizontal != 1):
        if (y0 > y1):
            if (m == 0):
                for i in xrange(dim):
                    j, k = SearchX(y0-i,x0,edges)
                    if ( (k-1 < mag.shape[1]) and (k-1 >= 0) ):
                        points[i, 0] = j
                        points[i, 1] = k + fit(mag[j,k-1],mag[j,k],mag[j,k+1])
            else:
                for i in xrange(dim):
                    j, k = nextPointH(y0-i, m, b)
                    j, k = SearchX(int(j),int(k),edges)
                    if ( (k-1 < mag.shape[1]) and (k-1 >= 0) ):
                        points[i, 0] = j
                        points[i, 1] = k + fit(mag[j,k-1],mag[j,k],mag[j,k+1])
        else:
            if (m == 0):
                for i in xrange(dim):
                    j, k = SearchX(y0+i,x0,edges)
                    if ( (k-1 < mag.shape[1]) and (k-1 >= 0) ):
                        points[i, 0] = j
                        points[i, 1] = k + fit(mag[j,k-1],mag[j,k],mag[j,k+1])
            else:
                for i in xrange(dim):
                    j, k = nextPointH(y0+i, m, b)
                    j, k = SearchX(int(j),int(k),edges)
                    if ( (k-1 < mag.shape[1]) and (k-1 >= 0) ):
                        points[i, 0] = j
                        points[i, 1] = k + fit(mag[j,k-1],mag[j,k],mag[j,k+1])
    else:
        if (x0 > x1):
            if (m == 0):
                for i in xrange(dim):
                    j, k = SearchY(y0,x0-i,edges)
                    if ( (j-1 < mag.shape[0]) and (j-1 >= 0) ):
                        points[i, 0] = j + fit(mag[j-1,k],mag[j,k],mag[j+1,k])
                        points[i, 1] = k
            else:
                for i in xrange(dim):
                    j, k = nextPointV(x0-i, m, b)
                    j, k = SearchY(int(j),int(k), edges)
                    if ( (j-1 < mag.shape[0]) and (j-1 >= 0) ):
                        points[i, 0]= j + fit(mag[j-1,k],mag[j,k],mag[j+1,k])
                        points[i, 1] = k
        else:
            if (m == 0):
                for i in xrange(dim):
                    j, k = SearchY(y0,x0+i,edges)
                    if ( (j-1 < mag.shape[0]) and (j-1 >= 0) ):
                        points[i, 0] = j + fit(mag[j-1,k],mag[j,k],mag[j+1,k])
                        points[i, 1] = k
            else:
                for i in xrange(dim):
                    j, k = nextPointV(x0+i, m, b)
                    j, k = SearchY(int(j),int(k),edges)                     
                    if ( (j-1 < mag.shape[0]) and (j-1 >= 0) ):
                        points[i, 0] = j + fit(mag[j-1,k],mag[j,k],mag[j+1,k])
                        points[i, 1] = k 
    return points

def walkInLine2(DTYPE_t x0, DTYPE_t y0, DTYPE_t x1, DTYPE_t y1, np.ndarray[DTYPE_t, ndim=2] mag, np.ndarray[DTYPE_t, ndim=2] edges):
    cdef float m, b, fk, fj
    cdef unsigned int i, x, y, horizontal, dim
    
    horizontal = 1

    m, b = getMBH(x0,y0,x1,y1)
    dim = int(abs(x0-x1)+1)    

    if ((m == np.inf) or (m > 1) or (m < -1)):
        m, b = getMBV(x0,y0,x1,y1)
        horizontal = 0
        dim = int(abs(y0-y1)+1)
         
    cdef np.ndarray[DTYPE_t, ndim=2] points = np.zeros([dim,2], dtype=DTYPE)

    if (horizontal != 1):
        if (y0 > y1):
            if (m == 0):
                for i in xrange(dim):
                    j, k = y0-i,x0
                    if ( (k-1 < mag.shape[1]) and (k-1 >= 0) ):
                        points[i, 0] = j
                        points[i, 1] = k 
            else:
                for i in xrange(dim):
                    j, k = nextPointH(y0-i, m, b)
                    if ( (k-1 < mag.shape[1]) and (k-1 >= 0) ):
                        points[i, 0] = j
                        points[i, 1] = k 
        else:
            if (m == 0):
                for i in xrange(dim):
                    j, k = y0+i,x0
                    if ( (k-1 < mag.shape[1]) and (k-1 >= 0) ):
                        points[i, 0] = j
                        points[i, 1] = k
            else:
                for i in xrange(dim):
                    j, k = nextPointH(y0+i, m, b)
                    if ( (k-1 < mag.shape[1]) and (k-1 >= 0) ):
                        points[i, 0] = j
                        points[i, 1] = k
    else:
        if (x0 > x1):
            if (m == 0):
                for i in xrange(dim):
                    j, k = y0,x0-i
                    if ( (j-1 < mag.shape[0]) and (j-1 >= 0) ):
                        points[i, 0] = j
                        points[i, 1] = k
            else:
                for i in xrange(dim):
                    j, k = nextPointV(x0-i, m, b)
                    if ( (j-1 < mag.shape[0]) and (j-1 >= 0) ):
                        points[i, 0]= j 
                        points[i, 1] = k
        else:
            if (m == 0):
                for i in xrange(dim):
                    j, k = y0,x0+i
                    if ( (j-1 < mag.shape[0]) and (j-1 >= 0) ):
                        points[i, 0] = j
                        points[i, 1] = k
            else:
                for i in xrange(dim):
                    j, k = nextPointV(x0+i, m, b)
                    if ( (j-1 < mag.shape[0]) and (j-1 >= 0) ):
                        points[i, 0] = j
                        points[i, 1] = k 
    return points
