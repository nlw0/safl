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
CTYPE = np.uint8
ctypedef np.uint8_t CTYPE_t

cimport cython



cdef double project_point(double *out_x, double *out_y,
                          double x, double y, double z,
                          int camera_model, double* params):

    cdef double ux, uy, factor

    cdef double r2,r4,r6,r8,k1,k2, rho

    if camera_model == 0 or camera_model == 1 or camera_model == 2:
        ux = params[0] * x/z
        uy = params[0] * y/z

    ## Simple perspective projection.
    if camera_model == 0:
        out_x[0] = params[1] + ux
        out_y[0] = params[2] + uy

    ## Harris distortion model.
    elif camera_model == 1:
        factor = 1.0/sqrt(fabs(1 + params[3] * (ux*ux+uy*uy)))
        out_x[0] = params[1] + ux * factor
        out_y[0] = params[2] + uy * factor

    ## Polar azimuhtal equidistant projection
    elif camera_model == 2:
        ux = x
        uy = y
        factor = hypot(ux,uy)
        ux = ux / factor
        uy = uy / factor
        rho = atan2(factor, z)
        out_x[0] = params[1] + params[0]*ux*rho
        out_y[0] = params[2] + params[0]*uy*rho

    ## Inverse from 5th order odd polynomial
    elif camera_model == 3:
        r2 = ux*ux + uy*uy
        r4 = r2*r2
        r6 = r4*r2
        r8 = r4*r4
        k1 = params[3]
        k2 = params[4]
        factor = (1 - ((k1*r2 + k2*r4 + (k1*k1)*r4 + (k2*k2)*r8 + 2*k1*k2*r6) /
                       (1 + 4*k1*r2 + 6*k2*r4)))
        out_x[0] = params[1] + ux * factor
        out_y[0] = params[2] + uy * factor

    ## 5th order odd polynomial
    elif camera_model == 4:
        r2 = ux*ux + uy*uy
        r4 = r2*r2
        r6 = r4*r2
        r8 = r4*r4
        k1 = params[3]
        k2 = params[4]
        factor = (1 + (k1*r2 + k2*r4))
        out_x[0] = params[1] + ux * factor
        out_y[0] = params[2] + uy * factor




cdef double point_direction(double* out_x, double* out_y,
                            double* out_z, double x, double y,
                            int camera_model, double* params):
    
    cdef double ux, uy, factor
    cdef double rx, ry, rho, the, phi
    cdef double r2, r4, r6, r8, k1, k2

    ## Simple perspective projection.
    if camera_model == 0:
        out_x[0] = x - params[1]
        out_y[0] = y - params[2]
        out_z[0] = params[0]

    ## Harris distortion model.
    elif camera_model == 1:
        ux = x - params[1]
        uy = y - params[2]
        factor = 1.0/sqrt(fabs(1 - params[3] * (ux*ux+uy*uy)))
        ux = ux * factor
        uy = uy * factor

        out_x[0] = ux
        out_y[0] = uy
        out_z[0] = params[0]

    ## Polar azimuhtal equidistant projection
    elif camera_model == 2:
        rx = (x - params[1])/params[0]
        ry = (y - params[2])/params[0]
        phi = sqrt(rx*rx+ry*ry)
        rx = rx/phi
        ry = ry/phi
        out_x[0] = cos(phi)*rx
        out_y[0] = cos(phi)*ry
        out_z[0] = sin(phi)

    ## Inverse from 5th order odd polynomial
    elif camera_model == 3:

        ux = x - params[1]
        uy = y - params[2]
        r2 = ux*ux + uy*uy
        r4 = r2*r2
        k1 = params[3]
        k2 = params[4]
        factor = (1 + (k1*r2 + k2*r4))
        out_x[0] = ux * factor
        out_y[0] = uy * factor
        out_z[0] = params[0]

    ## 5th order odd polynomial
    elif camera_model == 4:
        ux = x - params[1]
        uy = y - params[2]
        r2 = ux*ux + uy*uy
        r4 = r2*r2
        r6 = r4*r2
        r8 = r4*r4
        k1 = params[3]
        k2 = params[4]
        factor = (1 - ((k1*r2 + k2*r4 + (k1*k1)*r4 + (k2*k2)*r8 + 2*k1*k2*r6) /
                       (1 + 4*k1*r2 + 6*k2*r4)))
        out_x[0] = ux * factor
        out_y[0] = uy * factor
        out_z[0] = params[0]

    ## Equiretangular
    elif camera_model == 5:
        if params[3] == 0:
            the = (x - params[1]) / params[0]
            phi = (y - params[2]) / params[0]

            out_x[0] = cos(phi) * sin(the)
            out_y[0] = sin(phi)
            out_z[0] = cos(phi) * cos(the)

    ## Also equirectangular, but with the z-axis as the zenith.
    elif camera_model == 6:
        if params[3] == 0:
            the = (x - params[1]) / params[0]
            phi = (y - params[2]) / params[0]

            out_x[0] = cos(phi) * sin(the)
            out_y[0] = cos(phi) * cos(the)
            out_z[0] = sin(phi)

    ## Cylindrical, with the z-axis as the zenith.
    elif camera_model == 7:
        the = (x - params[1]) / params[0]
        phi = (y - params[2]) / params[0]
        
        out_x[0] = sin(the)
        out_y[0] = cos(the)
        out_z[0] = -phi

    ## stereographic projection
    elif camera_model == 8:
        ux = (x - params[1]) / params[0]
        uy = (y - params[2]) / params[0]

        factor = 1.0/(1+ux*ux+uy*uy)
        out_x[0] = 2*ux*factor
        out_y[0] = 2*uy*factor
        out_z[0] = -(-1+ux*ux+uy*uy) * factor


def reproject(np.ndarray[CTYPE_t, ndim=3, mode="c"] out not None,
              np.ndarray[CTYPE_t, ndim=3, mode="c"] src not None,
              int model_out,
              np.ndarray[DTYPE2_t, ndim=1, mode="c"] params_out not None,
              int model_src,
              np.ndarray[DTYPE2_t, ndim=1, mode="c"] params_src not None):

    cdef double rx,ry,rz

    cdef double sk, sj
    cdef int isk, isj

    cdef char* outd = <char*> out.data
    cdef char* srcd = <char*> src.data

    Ncol_out = out.shape[1]
    Ncol_src = src.shape[1]
    for j in range(out.shape[0]):
        for k in range(out.shape[1]):
            point_direction(&rx, &ry, &rz, k, j, model_out, <double *> params_out.data)
            project_point(&sk, &sj, rx, ry, rz, model_src, <double *> params_src.data)
            isk = lround(sk)
            isj = lround(sj)
            if (isj < 0 or isj >= src.shape[0] or
                isk < 0 or isk >= src.shape[1]):
                continue
            outd[j*Ncol_out*3 + k*3 + 0] = srcd[isj*Ncol_src*3 + isk*3  ]
            outd[j*Ncol_out*3 + k*3 + 1] = srcd[isj*Ncol_src*3 + isk*3 + 1]
            outd[j*Ncol_out*3 + k*3 + 2] = srcd[isj*Ncol_src*3 + isk*3 + 2]


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
    if camera_model == 0 or camera_model == 2:
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
    if camera_model == 0 or camera_model == 2:
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
cdef extern long int lround(double)
cdef extern double tan(double)
cdef extern double atan2(double,double)
cdef extern double cos(double)
cdef extern double sin(double)
