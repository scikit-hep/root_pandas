import pandas as pd
from root_pandas import read_root
from root_numpy import list_branches
from pandas.util.testing import assert_frame_equal
import os

def test_read_write():
    df = pd.DataFrame({'x': [1,2,3]})
    df.to_root('tmp.root')
    df_ = read_root('tmp.root')
    os.remove('tmp.root')

def test_persistent_index():
    df = pd.DataFrame({'index': [42, 0, 1], 'x': [1,2,3]})
    df = df.set_index('index')
    df.to_root('tmp.root')
    print(list_branches('tmp.root'))
    assert('__index__' in list_branches('tmp.root'))
    df_ = read_root('tmp.root')
    assert_frame_equal(df, df_)
    os.remove('tmp.root')

