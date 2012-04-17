from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [
    Extension("camera_model",
              ["camera_model.pyx"],
              include_dirs=['/usr/lib/python2.7/site-packages/numpy/core/include/'],
              libraries=['m'])]

setup(
  name = 'camera model functions',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
