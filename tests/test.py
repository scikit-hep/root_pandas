import pandas as pd
from root_pandas import read_root
from root_numpy import list_branches
from pandas.util.testing import assert_frame_equal
import numpy as np
import ROOT
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

def test_flatten():
    tf = ROOT.TFile('tmp.root', 'RECREATE')
    tt = ROOT.TTree("a", "a")

    length = np.array([3])
    x = np.array([0, 1, 2], dtype='float64')
    tt.Branch('length', length, 'length/I')
    tt.Branch('x', x, 'x[length]/D')

    tt.Fill()
    x[0] = 3
    x[1] = 4
    x[2] = 5
    tt.Fill()
    
    tf.Write()
    tf.Close()

    branches = list_branches('tmp.root')

    df_ = read_root('tmp.root', flatten=True)

    assert('__array_index' in df_.columns)
    assert(len(df_) == 6)
    assert(np.all(df_['__array_index'] == np.array([0, 1, 2, 0, 1, 2])))

    # Also flatten chunked data

    for df_ in read_root('tmp.root', flatten=True, chunksize=1):
        assert(len(df_) == 3)
        assert(np.all(df_['__array_index'] == np.array([0, 1, 2])))

