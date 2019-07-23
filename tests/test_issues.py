import os

import pandas as pd
import root_pandas


def test_issue_60():
    df = pd.DataFrame({'a': list(range(10)), 'b': list(range(10))})
    root_pandas.to_root(df, 'tmp_1.root', 'my_tree_1')
    root_pandas.to_root(df, 'tmp_2.root', 'my_tree')
    result = root_pandas.read_root(['tmp_1.root', 'tmp_2.root'], 'my_tree', warn_missing_tree=True)
    assert len(result) == 10
    os.remove('tmp_1.root')
    os.remove('tmp_2.root')


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


def test_issue_80():
    df = pd.DataFrame({'a': [1, 2], 'b': [4, 5]})
    df.columns = ['a', 'a']
    try:
        root_pandas.to_root(df, '/tmp/example.root')
    except ValueError as e:
        assert 'DataFrame contains duplicated column names' in e.args[0]
    else:
        raise Exception('ValueError is expected')


def test_issue_82():
    variables = ['MET_px', 'MET_py', 'EventWeight']
    df = root_pandas.read_root('http://scikit-hep.org/uproot/examples/HZZ.root', 'events', columns=variables)
    assert list(df.columns) == variables
