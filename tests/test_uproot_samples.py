import root_pandas
import pandas as pd
import numpy as np
from nose.tools import raises


def test_simple():
    filename = 'tests/samples/simple.root'

    reference_df = pd.DataFrame()
    reference_df['one'] = np.array([1, 2, 3, 4], dtype=np.int32)
    reference_df['two'] = np.array([1.1, 2.2, 3.3, 4.4], dtype=np.float32)
    reference_df['three'] = [b'uno', b'dos', b'tres', b'quatro']

    df = root_pandas.read_root(filename, key='tree')
    assert df.equals(reference_df)

    df = root_pandas.read_root(filename)
    assert df.equals(reference_df)


@raises(TypeError)
def test_small_evnt_tree_fullsplit():
    """ FIXME """
    filename = 'tests/samples/small-evnt-tree-fullsplit.root'
    root_pandas.read_root(filename, key='tree')


def test_small_flat_tree():
    filename = 'tests/samples/small-flat-tree.root'
    expected_columns = [
        'Int32', 'Int64', 'UInt32', 'UInt64', 'Float32', 'Float64', 'Str',
        'ArrayInt32', 'ArrayInt64', 'ArrayUInt32', 'ArrayUInt64',
        'ArrayFloat32', 'ArrayFloat64', 'N', 'SliceInt32', 'SliceInt64',
        'SliceUInt32', 'SliceUInt64', 'SliceFloat32', 'SliceFloat64'
    ]

    df = root_pandas.read_root(filename, key='tree')
    assert set(df.columns) == set(expected_columns), df.columns
