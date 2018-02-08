from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import sys

# Or, to use plain C, use this and don't call "cythonize"
#   Extension("foo", ["foo.c"])

extensions = [
        Extension("cstate",
            ["cstate.pyx"],
            include_dirs = sys.path,
            libraries = ["gmp"])
    ]

setup(
    ext_modules = cythonize(extensions, include_path = sys.path)
)
