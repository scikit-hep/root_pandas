import os

from setuptools import setup


def get_version():
    g = {}
    exec(open(os.path.join("root_pandas", "version.py")).read(), g)
    return g["__version__"]


setup(name='root_pandas',
      version=get_version(),
      description='Read and save DataFrames from and to ROOT files',
      url='http://github.com/chrisburr/root_pandas',
      author='Chris Burr',
      author_email='c.b@cern.ch',
      license='MIT',
      install_requires=[
          'numpy',
          'pandas>=0.18.0',
          'root_numpy',
      ],
      packages=['root_pandas'],
      zip_safe=False)
