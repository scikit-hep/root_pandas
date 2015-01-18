
# root\_pandas

A convenience wrapper around the `root_numpy` library that allows you to load and save pandas DataFrames in the ROOT format used in high energy phyics.

```python
from pandas import DataFrame
from root_pandas import read_root

df = DataFrame({'x1': [1, 2, 3], 'x2': [4, 5, 6]})

df.to_root('test.root', 'tree')

df_new = read_root('test.root', 'tree', ignore=['*1'])

# DataFrames are extremely convenient
df_new['answer'] = 42

df_new.to_root('new.root')
# The file contains a tree called 'default' with the 'x2' and 'answer' branches
```

There is also support for working with files that don't fit into memory:
If the `chunksize` parameter is specified, `read_root` returns an iterator that yields DataFrames, each containing up to `chunksize` rows.
```python
for df in read_root('bigfile.root', 'tree', chunksize=100000):
    # process df here
    df.to_root('finished.root')
```
By default, `to_root` appends to the output file.

## Installation
The package is currently not on PyPI.
To install it into your home directory with pip, run
```bash
pip install --user git+https://github.com/ibab/root_pandas
```
