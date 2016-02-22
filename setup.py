from setuptools import setup

setup(name='root_pandas',
      version='0.1.1',
      description='Read and save DataFrames from and to ROOT files',
      url='http://github.com/ibab/root_pandas',
      author='Igor Babuschkin',
      author_email='igor@babuschk.in',
      license='MIT',
      install_requires=[
          'numpy',
          'pandas',
          'root_numpy',
      ],
      packages=['root_pandas'],
      zip_safe=False)
