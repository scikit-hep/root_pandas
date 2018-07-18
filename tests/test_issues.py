import os

import pandas as pd
import root_pandas


def test_issue_63():
    df = pd.DataFrame({'a': [], 'b': []})
    root_pandas.to_root(df, 'tmp_1.root', 'my_tree')
    df = pd.DataFrame({'a': list(range(10)), 'b': list(range(10))})
    root_pandas.to_root(df, 'tmp_2.root', 'my_tree')
    result = list(root_pandas.read_root(['tmp_1.root', 'tmp_2.root'], 'my_tree', where='a > 2', chunksize=1))
    assert len(result) == 7
    assert all(len(df) == 1 for df in result)
    os.remove('tmp_1.root')
    os.remove('tmp_2.root')
