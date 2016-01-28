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
    df.index.name = 'MyAwesomeName'
    df.to_root('tmp.root')
    assert('__index__MyAwesomeName' in list_branches('tmp.root'))
    df_ = read_root('tmp.root')
    assert_frame_equal(df, df_)
    os.remove('tmp.root')

    # See what happens if the index has no name
    df = pd.DataFrame({'x': [1,2,3]})
    df.to_root('tmp.root')
    df_ = read_root('tmp.root')
    assert_frame_equal(df, df_)
    os.remove('tmp.root')

def test_chunked_reading():
    df = pd.DataFrame({'x': [1,2,3,4,5,6]})
    df.to_root('tmp.root')

    count = 0
    for df_ in read_root('tmp.root', chunksize=2):
        assert(not df_.empty)
        count += 1

    assert count == 3
    os.remove('tmp.root')

