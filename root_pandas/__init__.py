
"""
A module that extends pandas to support the ROOT data format.
"""

from pandas import DataFrame
from root_numpy import root2array, list_trees
from fnmatch import fnmatch
from root_numpy import list_branches
from math import ceil
import ROOT

__all__ = ['read_root']

def get_matching_variables(fname, tree, patterns):
    branches = list_branches(fname, tree)

    selected = []

    for p in patterns:
        for b in branches:
            if fnmatch(b, p) and not b in selected:
                selected.append(b)
    return selected

def read_root(fname, tree_name=None, variables=None, ignore=None, chunksize=None, *kargs, **kwargs):
    """
    Read a ROOT file into a pandas DataFrame.
    Further *kargs and *kwargs are passed to root_numpy's root2array.
    If the root file contains a branch called index, it will become the DataFrame's index.

    Parameters
    ----------
    fname: string
        The filename of the root file
    tree_name: string
        The name of the tree to load
    variables: sequence
        A sequence of shell-patterns. Matching variables are read.
    ignore: sequence
        A sequence of shell-patterns. All matching variables are ignored (overriding the variables argument)

    Returns
    -------
        DataFrame from the ROOT file

    Notes
    -----

        >>> df = read_root('test.root', 'MyTree', variables=['x_*', 'y_*'], selection='x_1 > 100')

    """
    if not tree_name:
        branches = list_trees(fname)
        if len(branches) == 1:
            tree_name = branches[0]
        else:
            raise ValueError('More than one tree found in {}'.format(fname))

    if not variables:
        all_vars = None
    else:
        # index is always loaded if it exists
        variables.append('index')
        all_vars = get_matching_variables(fname, tree_name, variables)

    if ignore:
        if not all_vars:
            all_vars = get_matching_variables(fname, tree_name, ['*'])

        ignored = get_matching_variables(fname, tree_name, ignore)
        if 'index' in ignored:
            raise ValueError('index variable is being ignored!')
        for var in ignored:
            all_vars.remove(var)

    if chunksize:
        f = ROOT.TFile(fname)
        n_entries = f.Get(tree_name).GetEntries()
        f.Close()
        def genchunks():
            for chunk in range(int(ceil(float(n_entries) / chunksize))):
                arr = root2array(fname, tree_name, all_vars, start=chunk * chunksize, stop=(chunk+1) * chunksize, *kargs, **kwargs)
                yield convert_to_dataframe(arr)
        return genchunks()

    arr = root2array(fname, tree_name, all_vars, *kargs, **kwargs)
    return convert_to_dataframe(arr)

def convert_to_dataframe(array):
    if 'index' in array.dtype.names:
        df = DataFrame.from_records(array, index='index')
    else:
        df = DataFrame.from_records(array)
    return df

def to_root(df, fname, tree_name="default", *kargs, **kwargs):
    """
    Write DataFrame to a ROOT file.

    Parameters
    ----------
    fname: string
        File path to new ROOT file (will be overwritten)
    tree_name: string
        Name of tree that the DataFrame will be saved as
    
    Notes
    -----

    Further *kargs and *kwargs are passed to root_numpy's array2root.

    >>> df = DataFrame({'x': [1,2,3], 'y': [4,5,6]})
    >>> df.to_root('test.root')
    
    The DataFrame index will be saved as a branch called 'index'.
    """
    from root_numpy import array2root
    arr = df.to_records()
    array2root(arr, fname, tree_name, *kargs, **kwargs)

# Patch pandas DataFrame to support to_root method
DataFrame.to_root = to_root

