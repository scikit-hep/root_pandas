from setuptools import setup

setup(name='root_pandas',
      version='0.1',
      description='Read and save DataFrames from and to ROOT files',
      url='http://github.com/ibab/root_pandas',
      author='Igor Babuschkin',
      author_email='igor@babuschk.in',
      license='MIT',
      packages=['root_pandas'],
      install_requires=[
          'pandas',
          'root_numpy',
      ],
      zip_safe=False)
