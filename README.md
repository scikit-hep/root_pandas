
# root\_pandas

[![Build Status](https://travis-ci.org/scikit-hep/root_pandas.svg?branch=master)](https://travis-ci.org/scikit-hep/root_pandas)
[![Coverage Status](https://coveralls.io/repos/github/scikit-hep/root_pandas/badge.svg?branch=master)](https://coveralls.io/github/scikit-hep/root_pandas?branch=master)
[![PyPI](https://badge.fury.io/py/root_pandas.svg)](https://pypi.python.org/pypi/root_pandas/)
[![DOI](https://zenodo.org/badge/17171/scikit-hep/root_pandas.svg)](https://zenodo.org/badge/latestdoi/17171/scikit-hep/root_pandas)

`root_pandas` is a convenience package built around the `root_numpy` library.
It allows you to easily load and store pandas DataFrames using the columnar ROOT data format used in high energy physics.

It's modeled closely after the existing pandas API for reading and writing HDF5 files.
This means that in many cases, it is possible to substitute the use of HDF5 with ROOT and vice versa.

On top of that, `root_pandas` offers several features that go beyond what pandas offers with `read_hdf` and `to_hdf`.

These include

 - Specifying multiple input filenames, in which case they are read as if they were one continuous file.
 - Selecting several columns at once using `*` globbing and `{A,B}` shell patterns.
 - Flattening source files containing arrays by storing one array element each in the DataFrame, duplicating any scalar variables.

Python versions supported:

[![](https://img.shields.io/badge/python-2.7-blue.svg)](https://badge.fury.io/py/root_pandas)
[![](https://img.shields.io/badge/python-3.4-blue.svg)](https://badge.fury.io/py/root_pandas)
[![](https://img.shields.io/badge/python-3.5-blue.svg)](https://badge.fury.io/py/root_pandas)
[![](https://img.shields.io/badge/python-3.6-blue.svg)](https://badge.fury.io/py/root_pandas)


## Reading ROOT files

This is how you can read the contents of a ROOT file into a DataFrame:
```python
from root_pandas import read_root

df = read_root('myfile.root')
```

If there are several ROOT trees in the input file, you have to specify the tree key:
```python
df = read_root('myfile.root', 'mykey')
```

You can also directly read multiple ROOT files at once by passing a list of file names:
```python
df = read_root(['file1.root', 'file2.root'], 'mykey')
```
In this case, each file must have the same set of columns under the given key.

Specific columns can be selected like this:
```python
df = read_root('myfile.root', columns=['variable1', 'variable2'])
```

You can also use `*` in the column names to read in any matching branch:
```python
df = read_root('myfile.root', columns=['variable*'])
```

In addition, you can use shell brace patterns as in
```python
df = read_root('myfile.root', columns=['variable{1,2}'])
```
You can also use `*` and `{a,b}` simultaneously, and several times per string.

If you want to transform your variables using a ROOT selection string, you have
to put a `noexpand:` prefix in front of the column name that you want to use the selection string in:
```python
df = read_root('myfile.root', columns=['noexpand:sqrt(variable1)']
```

Working with stored arrays can be a bit inconventient in pandas.
`root_pandas` makes it easy to flatten your input data, providing you with a DataFrame containing only scalars:
```python
df = read_root('myfile.root', columns=['arrayvariable', 'othervariable'], flatten=True)
```

Assuming the ROOT file contains the array `[1, 2, 3]` in the first `arrayvariable` column, flattening
will expand this into three entries, where each contains one of the array elements.
All other scalar entries are duplicated.
The automatically created `__array_index` column also allows you to get the index that each array element had in its array before flattening.

There is also support for working with files that don't fit into memory:
If the `chunksize` parameter is specified, `read_root` returns an iterator that yields DataFrames, each containing up to `chunksize` rows.
```python
for df in read_root('bigfile.root', chunksize=100000):
    # process df here
```
If `bigfile.root` doesn't contain an index, the default indices of the
individual `DataFrame` chunks will still increase continuously, as if they were
parts of a single large `DataFrame`.

You can also combine any of the above options at the same time.

## Writing ROOT files

`root_pandas` patches the pandas DataFrame to have a `to_root` method that allows you to save it into a ROOT file:
```python
df.to_root('out.root', key='mytree')
```
You can also call the `to_root` function and specify the DataFrame as the first argument:
```python
to_root(df, 'out.root', key='mytree')
```

By default, `to_root` erases the existing contents of the file. Use `mode='a'` to append:
```python
for df in read_root('bigfile.root', chunksize=100000):
    df.to_root('out.root', mode='a')
```
**Warning:** When using this feature to stream data from one ROOT file into
another, you shouldn't forget to `os.remove` the output file first, otherwise
you will append more and more data to it on each run of your program.

## The DataFrame index

When reading a ROOT file, `root_pandas` will automatically add a pandas index
to the DataFrame, which starts at 1 and counts up for each entry.
When writing the DataFrame to a ROOT file, it stores the DataFrame index in a `__index__` branch.
Currently, only single-dimensional indices are supported.

