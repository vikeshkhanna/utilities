from distutils.core import setup
import py2exe
import sys
from glob import glob
sys.path.append("C:\\bin\\")
setup(console=['janitor.py'])