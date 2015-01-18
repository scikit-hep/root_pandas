
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

## Installation
The package is currently not on PyPI.
To install it into your home directory with pip, run
```bash
pip install --user git+https://github.com/ibab/root_pandas
```
