from pylab import *
from .quaternion import Quat
from scipy.optimize import fmin


def project_points(shape, t, psi, fd, oc, kappa, distortion_model):
    # 3D points in the camera reference frame
    rc = dot(shape - t, Quat(psi).rot())
    # Perspective projection
    q = rc[:, :2] * fd / rc[:, [2, 2]]

    if distortion_model == 0:
        p = q + oc

    elif distortion_model == 1:
        rho2 = (q[:, 0] ** 2 + q[:, 1] ** 2)
        a = np.abs(1 + (kappa[0] * 1e-9) * rho2) ** -0.5
        p = oc + q * c_[[a, a]].T

    elif distortion_model == 2:
        rd = np.array([sqrt(q[:, 0] ** 2 + q[:, 1] ** 2)]).T
        rd2 = rd ** 2
        rd4 = rd ** 4
        rd6 = rd ** 6
        rd8 = rd ** 8
        s = (size(rd), 1)
        um = np.ones(s)
        factor = (
                     kappa[0] * rd2 + kappa[1] * rd4 + (kappa[0] ** 2) * rd4 + (kappa[1] ** 2) * rd8 + 2 * kappa[0] *
                     kappa[
                         1] * rd6) / (um + 4 * kappa[0] * rd2 + 6 * kappa[1] * rd4)
        p = q - q * factor + oc
    else:
        print('Model argument must be 0 (Harris) or 1 (Brown).')
    return p


def project_all_the_points(shape, bigvec, Ncam, distortion_model):
    output = []
    vecint = bigvec[6 * Ncam:]  ## fd, oc, kappa
    for cam in range(Ncam):
        t = bigvec[cam * 6:cam * 6 + 3]
        psi = bigvec[cam * 6 + 3:cam * 6 + 6]

        if distortion_model != 0:
            qq = project_points(shape, t, psi, vecint[0], vecint[1:3],
                                vecint[3:], distortion_model)
        else:
            qq = project_points(shape, t, psi, vecint[0], vecint[1:3],
                                [], distortion_model)

        output.append(qq)
    return np.asarray(output)


def error(X, shape, pp_ref, Ncam, distortion_model):
    pp_est = project_all_the_points(shape, X, Ncam, distortion_model)

    total_error = ((pp_est - pp_ref) ** 2).sum()

    return total_error

## Local variables:
## python-indent: 2
## end:
