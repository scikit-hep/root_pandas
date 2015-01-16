
# root\_pandas

A Python module that allows you to conveniently create DataFrames from ROOT files and save them again.

```python
from pandas import DataFrame
from root_pandas import read_root

df = DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})

df.to_root('test.root', 'tree')

df_new = read_root('test.root', 'tree', ignore=['x*'])
df['extra'] = df['y']**2
```

