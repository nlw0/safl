# cython: boundscheck=False
# cython. wraparound=False
# cython: cdivision=True
# cython: profile=False
# file: camori_aux.pyx


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

from __future__ import division
import numpy as np
cimport numpy as np
DTYPE = np.float32
ctypedef np.float32_t DTYPE_t
DTYPE2 = np.float64
ctypedef np.float64_t DTYPE2_t

cimport cython



cdef double project_point(double *out_x, double *out_y, double x, double y, double z, int camera_model,
                         double* params):

    cdef double ux, uy, kappa, nf

    if camera_model == 0 or camera_model == 1 or camera_model == 2:
        ux = params[0] * x/z
        uy = params[0] * y/z

    ## Simple perspective projection.
    if camera_model == 0:
        out_x[0] = params[1] + ux
        out_y[0] = params[2] + uy
        
    ## Harris distortion model.
    elif camera_model == 1:
        kappa = 1e-9 * params[3]
        nf = 1.0/sqrt(fabs(1 + kappa * (ux*ux+uy*uy)))
        out_x[0] = params[1] + ux * nf
        out_y[0] = params[2] + uy * nf

    ## Polynomial distortion model.
    # elif camera_model == 2:
    #     cdef r2 = ux*ux + uy*uy
    #     cdef double k1 = params[3]
    #     cdef double k2 = params[4]
    #     out_x[0] = params[1] + ux * nf
    #     out_y[0] = params[2] + uy * nf
    #     factor = (k2*rd2+k4*rd4+(k2**2)*rd4+(k4**2)*rd8+2*k2*k4*rd6)/(1+4*k2*rd2+6*k4*rd4)
        


def calc_projection_harris(x,y,z, camera_model, fd, kappa, xc, yc):
    cdef double xd, yd
    cdef double parms[4]
    parms[0] = fd
    parms[1] = xc
    parms[2] = yc
    parms[3] = kappa
    project_point(&xd, &yd, x,y,z,1,parms)
    return xd,yd



@cython.boundscheck(False)
@cython.wraparound(False)
def calculate_all_projections(
                np.ndarray[DTYPE2_t, ndim=1, mode="c"] all_params not None,
                np.ndarray[DTYPE2_t, ndim=2, mode="c"] structure not None,
                int Ncam,
                camera_model = 0):

    cdef int Npts = structure.shape[0]

    ## Check out size of stuff
    if camera_model == 0:
        assert all_params.shape[0] == Ncam * 6 + 3
    elif camera_model == 1:
        assert all_params.shape[0] == Ncam * 6 + 4
    else:
        raise 'Invalid camera model'

    cdef double* pos = <double*> all_params.data
    cdef double* shp = <double*> structure.data

    cdef double* params = (<double*> all_params.data) + 6 * Ncam

    cdef double r00, r01, r02, r10, r11, r12, r20, r21, r22

    cdef double a,b,c,d, tx ,ty, tz

    cdef double px,py,pz, qx,qy,qz, ix,iy, ex, ey

    cdef double p_err
    cdef double total_error = 0.0
    cdef int kc, kp

    cdef np.ndarray output = np.zeros([Ncam, Npts, 2], dtype=DTYPE2)


    for kc in range(Ncam):
        tx  = pos[kc*6 + 0]
        ty  = pos[kc*6 + 1]
        tz  = pos[kc*6 + 2]

        b = pos[kc*6 + 3]
        c = pos[kc*6 + 4]
        d = pos[kc*6 + 5]
        a = sqrt(fabs(1-(b**2+c**2+d**2)))

        ## Acha parâmetros da matriz de rotação
        r00 = (a*a+b*b-c*c-d*d)
        r10 = (2*b*c-2*a*d)
        r20 = (2*b*d+2*a*c)
        r01 = (2*b*c+2*a*d)
        r11 = (a*a-b*b+c*c-d*d)
        r21 = (2*c*d-2*a*b)
        r02 = (2*b*d-2*a*c)
        r12 = (2*c*d+2*a*b)
        r22 = (a*a-b*b-c*c+d*d)

        for kp in range(Npts):
            px = shp[kp*3 + 0]
            py = shp[kp*3 + 1]
            pz = shp[kp*3 + 2]

            px = px-tx
            py = py-ty
            pz = pz-tz
            qx = r00 * px + r01 * py + r02 * pz 
            qy = r10 * px + r11 * py + r12 * pz 
            qz = r20 * px + r21 * py + r22 * pz 

            project_point(&ix, &iy, qx,qy,qz, camera_model, params)

            output[kc,kp,0] = ix
            output[kc,kp,1] = iy

    return output



###############################################################################
### Old target function for equirectangular projection. Must be
### updated to use the external M-estimator procedures. Must calculate
### the derivatives too some day so we can use FilterSQP.
@cython.boundscheck(False)
@cython.wraparound(False)
def reprojection_error(
                np.ndarray[DTYPE2_t, ndim=1, mode="c"] all_params not None,
                np.ndarray[DTYPE2_t, ndim=2, mode="c"] structure not None,
                np.ndarray[DTYPE2_t, ndim=3, mode="c"] pp_ref not None,
                camera_model):

    cdef int Ncam = pp_ref.shape[0]
    cdef int Npts = structure.shape[0]

    assert pp_ref.shape[1] == Npts

    ## Check out size of stuff
    if camera_model == 0:
        assert all_params.shape[0] == Ncam * 6 + 3
    elif camera_model == 1:
        assert all_params.shape[0] == Ncam * 6 + 4
    else:
        raise 'Invalid camera model'

    cdef double* pos = <double*> all_params.data
    cdef double* pts = <double*> pp_ref.data
    cdef double* shp = <double*> structure.data

    cdef double* params = (<double*> all_params.data) + 6 * Ncam

    cdef double r00, r01, r02, r10, r11, r12, r20, r21, r22

    cdef double a,b,c,d, tx ,ty, tz

    cdef double px,py,pz, qx,qy,qz, ix,iy, ex, ey

    cdef double p_err
    cdef double total_error = 0.0
    cdef int kc, kp

    for kc in range(Ncam):
        tx  = pos[kc*6 + 0]
        ty  = pos[kc*6 + 1]
        tz  = pos[kc*6 + 2]

        b = pos[kc*6 + 3]
        c = pos[kc*6 + 4]
        d = pos[kc*6 + 5]
        a = sqrt(fabs(1-(b**2+c**2+d**2)))

        ## Acha parâmetros da matriz de rotação
        r00 = (a*a+b*b-c*c-d*d)
        r10 = (2*b*c-2*a*d)
        r20 = (2*b*d+2*a*c)
        r01 = (2*b*c+2*a*d)
        r11 = (a*a-b*b+c*c-d*d)
        r21 = (2*c*d-2*a*b)
        r02 = (2*b*d-2*a*c)
        r12 = (2*c*d+2*a*b)
        r22 = (a*a-b*b-c*c+d*d)

        for kp in range(Npts):
            px = shp[kp*3 + 0]
            py = shp[kp*3 + 1]
            pz = shp[kp*3 + 2]

            px = px-tx
            py = py-ty
            pz = pz-tz
            qx = r00 * px + r01 * py + r02 * pz 
            qy = r10 * px + r11 * py + r12 * pz 
            qz = r20 * px + r21 * py + r22 * pz 

            project_point(&ix, &iy, qx,qy,qz, camera_model, params)

            ex = ix - pts[kc * Npts*2 + kp*2    ]
            ey = iy - pts[kc * Npts*2 + kp*2 + 1]
            # p_err = ex * ex + ey * ey
            p_err = fabs(ex) + fabs(ey)

            total_error = total_error + p_err

    return total_error


cdef extern double hypot(double,double)
cdef extern double sqrt(double)
cdef extern double fabs(double)
