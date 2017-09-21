from setuptools import setup

setup(name='root_pandas',
      version='0.2.0',
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
