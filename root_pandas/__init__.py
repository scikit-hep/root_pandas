
"""
A module that extends pandas to support the ROOT data format.
"""

from pandas import DataFrame
from root_numpy import root2array, list_trees
from fnmatch import fnmatch
from root_numpy import list_branches
import itertools
from math import ceil
import re
import ROOT

__all__ = ['read_root']

def expand_braces(orig):
    r = r'.*(\{.+?[^\\]\})'
    p = re.compile(r)

    s = orig[:]
    res = list()

    m = p.search(s)
    if m is not None:
        sub = m.group(1)
        open_brace = s.find(sub)
        close_brace = open_brace + len(sub) - 1
        if sub.find(',') != -1:
            for pat in sub.strip('{}').split(','):
                res.extend(expand_braces(s[:open_brace] + pat + s[close_brace+1:]))

        else:
            res.extend(expand_braces(s[:open_brace] + sub.replace('}', '\\}') + s[close_brace+1:]))

    else:
        res.append(s.replace('\\}', '}'))

    return list(set(res))

def get_matching_variables(branches, patterns):

    selected = []

    for p in patterns:
        found = False
        for b in branches:
            if fnmatch(b, p):
                found = True
            if fnmatch(b, p) and not b in selected:
                selected.append(b)
        if not found:
            raise ValueError("Pattern '{}' didn't match any branch".format(p))
    return selected

def read_root(path, tree_key=None, columns=None, ignore=None, chunksize=None, where=None, *kargs, **kwargs):
    """
    Read a ROOT file into a pandas DataFrame.
    Further *kargs and *kwargs are passed to root_numpy's root2array.
    If the root file contains a branch called index, it will become the DataFrame's index.

    Parameters
    ----------
    path: string
        The path to the root file
    tree_key: string
        The key of the tree to load.
    columns: sequence of str
        A sequence of shell-patterns (can contain *, ?, [] or {}). Matching columns are read.
    ignore: sequence of str
        A sequence of shell-patterns (can contain *, ?, [] or {}). All matching columns are ignored (overriding the columns argument)
    chunksize: int
        If this parameter is specified, an iterator is returned that yields DataFrames with `chunksize` rows

    Returns
    -------
        DataFrame created from matching data in the specified TTree

    Notes
    -----

        >>> df = read_root('test.root', 'MyTree', columns=['A{B,C}*', 'D'], where='ABB > 100')

    """
    if not tree_key:
        branches = list_trees(path)
        if len(branches) == 1:
            tree_key = branches[0]
        else:
            raise ValueError('More than one tree found in {}'.format(path))

    branches = list_branches(path, tree_key)

    if not columns:
        all_vars = None
    else:
        # index is always loaded if it exists
        if 'index' in branches:
            columns = columns[:]
            columns.append('index')
        columns = list(itertools.chain.from_iterable(map(expand_braces, columns)))
        all_vars = get_matching_variables(branches, columns)

    if ignore:
        ignored = get_matching_variables(branches, ignore)
        ignored = list(itertools.chain.from_iterable(map(expand_braces, ignored)))
        if 'index' in ignored:
            raise ValueError('index variable is being ignored!')
        for var in ignored:
            all_vars.remove(var)

    if chunksize:
        f = ROOT.TFile(path)
        n_entries = f.Get(tree_key).GetEntries()
        f.Close()
        def genchunks():
            for chunk in range(int(ceil(float(n_entries) / chunksize))):
                arr = root2array(path, tree_key, all_vars, start=chunk * chunksize, stop=(chunk+1) * chunksize, selection=where, *kargs, **kwargs)
                yield convert_to_dataframe(arr)
        return genchunks()

    arr = root2array(path, tree_key, all_vars, selection=where, *kargs, **kwargs)
    return convert_to_dataframe(arr)

def convert_to_dataframe(array):
    if 'index' in array.dtype.names:
        df = DataFrame.from_records(array, index='index')
    else:
        df = DataFrame.from_records(array)
    return df

def to_root(df, path, tree_key="default", *kargs, **kwargs):
    """
    Write DataFrame to a ROOT file.

    Parameters
    ----------
    path: string
        File path to new ROOT file (will be overwritten)
    tree_key: string
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
    array2root(arr, path, tree_key, *kargs, **kwargs)

# Patch pandas DataFrame to support to_root method
DataFrame.to_root = to_root

