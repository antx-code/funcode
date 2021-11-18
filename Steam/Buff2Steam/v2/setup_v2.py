from distutils.core import setup
from Cython.Build import cythonize
setup(
    ext_modules = cythonize("Buff2Steam_v2.py")
)
