
"""
A module that extends pandas to support the ROOT data format.
"""

import numpy as np
from numpy.lib.recfunctions import append_fields
from pandas import DataFrame
from root_numpy import root2array, list_trees
from fnmatch import fnmatch
from root_numpy import list_branches
from root_numpy.extern.six import string_types
import itertools
from math import ceil
import re
import ROOT

from .utils import stretch


__all__ = [
    'read_root',
    'to_root',
]


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


def get_matching_variables(branches, patterns, fail=True):
    selected = []

    for p in patterns:
        found = False
        for b in branches:
            if fnmatch(b, p):
                found = True
            if fnmatch(b, p) and b not in selected:
                selected.append(b)
        if not found and fail:
            raise ValueError("Pattern '{}' didn't match any branch".format(p))
    return selected


def read_root(paths, key=None, columns=None, ignore=None, chunksize=None, where=None, flatten=False, *args, **kwargs):
    """
    Read a ROOT file, or list of ROOT files, into a pandas DataFrame.
    Further *args and *kwargs are passed to root_numpy's root2array.
    If the root file contains a branch matching __index__*, it will become the DataFrame's index.

    Parameters
    ----------
    paths: string or list
        The path(s) to the root file(s)
    key: string
        The key of the tree to load.
    columns: str or sequence of str
        A sequence of shell-patterns (can contain *, ?, [] or {}). Matching columns are read.
    ignore: str or sequence of str
        A sequence of shell-patterns (can contain *, ?, [] or {}). All matching columns are ignored (overriding the columns argument).
    chunksize: int
        If this parameter is specified, an iterator is returned that yields DataFrames with `chunksize` rows.
    where: str
        Only rows that match the expression will be read.
    flatten: bool
        If set to True, will use root_numpy.stretch to flatten arrays in the root file into individual entries.
        All arrays specified in the columns must have the same length for this to work.
        Be careful if you combine this with chunksize, as chunksize will refer to the number of unflattened entries,
        so you will be iterating over a number of entries that is potentially larger than chunksize.
        The index of each element within its former array will be saved in the __array_index column.

    Returns
    -------
        DataFrame created from matching data in the specified TTree

    Notes
    -----

        >>> df = read_root('test.root', 'MyTree', columns=['A{B,C}*', 'D'], where='ABB > 100')

    """

    if not isinstance(paths, list):
        paths = [paths]
    # Use a single file to search for trees and branches
    seed_path = paths[0]

    if not key:
        trees = list_trees(seed_path)
        if len(trees) == 1:
            key = trees[0]
        elif len(trees) == 0:
            raise ValueError('No trees found in {}'.format(seed_path))
        else:
            raise ValueError('More than one tree found in {}'.format(seed_path))

    branches = list_branches(seed_path, key)

    if not columns:
        all_vars = branches
    else:
        if isinstance(columns, string_types):
            columns = [columns]
        # __index__* is always loaded if it exists
        # XXX Figure out what should happen with multi-dimensional indices
        index_branches = filter(lambda x: x.startswith('__index__'), branches)
        if index_branches:
            columns = columns[:]
            columns.append(index_branches[0])
        columns = list(itertools.chain.from_iterable(list(map(expand_braces, columns))))
        all_vars = get_matching_variables(branches, columns)

    if ignore:
        if isinstance(ignore, string_types):
            ignore = [ignore]
        ignored = get_matching_variables(branches, ignore, fail=False)
        ignored = list(itertools.chain.from_iterable(list(map(expand_braces, ignored))))
        if any(map(lambda x: x.startswith('__index__', ignored))):
            raise ValueError('__index__* branch is being ignored!')
        for var in ignored:
            all_vars.remove(var)

    def do_flatten(arr):
        arr_, idx = stretch(arr, return_indices=True)
        arr = append_fields(arr_, '__array_index', idx, usemask=False, asrecarray=True)
        return arr

    if chunksize:
        tchain = ROOT.TChain(key)
        for path in paths:
            tchain.Add(path)
        n_entries = tchain.GetEntries()
        # XXX could explicitly clean up the opened TFiles with TChain::Reset

        def genchunks():
            for chunk in range(int(ceil(float(n_entries) / chunksize))):
                arr = root2array(paths, key, all_vars, start=chunk * chunksize, stop=(chunk+1) * chunksize, selection=where, *args, **kwargs)
                if flatten:
                    arr = do_flatten(arr)
                yield convert_to_dataframe(arr)

        return genchunks()

    arr = root2array(paths, key, all_vars, selection=where, *args, **kwargs)
    if flatten:
        arr = do_flatten(arr)
    return convert_to_dataframe(arr)


def convert_to_dataframe(array):
    indices = list(filter(lambda x: x.startswith('__index__'), array.dtype.names))
    if len(indices) == 0:
        df = DataFrame.from_records(array)
    elif len(indices) == 1:
        # We store the index under the __index__* branch, where
        # * is the name of the index
        df = DataFrame.from_records(array, index=indices[0])
        index_name = indices[0][len('__index__'):]
        if not index_name:
            # None means the index has no name
            index_name = None
        df.index.name = index_name
    else:
        raise ValueError("More than one index found in file")
    return df


def to_root(df, path, key='default', mode='w', *args, **kwargs):
    """
    Write DataFrame to a ROOT file.

    Parameters
    ----------
    path: string
        File path to new ROOT file (will be overwritten)
    key: string
        Name of tree that the DataFrame will be saved as
    mode: string, {'w', 'a'}
        Mode that the file should be opened in (default: 'w')

    Notes
    -----

    Further *args and *kwargs are passed to root_numpy's array2root.

    >>> df = DataFrame({'x': [1,2,3], 'y': [4,5,6]})
    >>> df.to_root('test.root')

    The DataFrame index will be saved as a branch called '__index__*',
    where * is the name of the index in the original DataFrame
    """

    if mode == 'a':
        mode = 'update'
    elif mode == 'w':
        mode = 'recreate'
    else:
        raise ValueError('Unknown mode: {}. Must be "a" or "w".'.format(mode))

    from root_numpy import array2root
    # We don't want to modify the user's DataFrame here, so we make a shallow copy
    df_ = df.copy(deep=False)
    name = df_.index.name
    if name is None:
        # Handle the case where the index has no name
        name = ''
    df_['__index__' + name] = df_.index
    arr = df_.to_records(index=False)
    array2root(arr, path, key, mode=mode, *args, **kwargs)


# Patch pandas DataFrame to support to_root method
DataFrame.to_root = to_root
