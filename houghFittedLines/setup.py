from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
 
setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("fitTools",["fitTools.pyx"],include_dirs=['/usr/lib/python2.7/site-packages/numpy/core/include/'])]
)
