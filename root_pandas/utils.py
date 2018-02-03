# Copyright (c) 2012 rootpy developers and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#
# Code temporarily copied from the root_numpy package
#

import numpy as np
VLEN = np.vectorize(len)


def stretch(arr, fields=None, return_indices=False):
    """Stretch an array.
    Stretch an array by ``hstack()``-ing  multiple array fields while
    preserving column names and record array structure. If a scalar field is
    specified, it will be stretched along with array fields.
    Parameters
    ----------
    arr : NumPy structured or record array
        The array to be stretched.
    fields : list of strings, optional (default=None)
        A list of column names to stretch. If None, then stretch all fields.
    return_indices : bool, optional (default=False)
        If True, the array index of each stretched array entry will be
        returned in addition to the stretched array.
        This changes the return type of this function to a tuple consisting
        of a structured array and a numpy int64 array.
    Returns
    -------
    ret : A NumPy structured array
        The stretched array.
    Examples
    --------
    >>> import numpy as np
    >>> from root_numpy import stretch
    >>> arr = np.empty(2, dtype=[('scalar', np.int), ('array', 'O')])
    >>> arr[0] = (0, np.array([1, 2, 3], dtype=np.float))
    >>> arr[1] = (1, np.array([4, 5, 6], dtype=np.float))
    >>> stretch(arr, ['scalar', 'array'])
    array([(0, 1.0), (0, 2.0), (0, 3.0), (1, 4.0), (1, 5.0), (1, 6.0)],
        dtype=[('scalar', '<i8'), ('array', '<f8')])
    """
    dtype = []
    len_array = None

    if fields is None:
        fields = arr.dtype.names

    # Construct dtype and check consistency
    for field in fields:
        dt = arr.dtype[field]
        if dt == 'O' or len(dt.shape):
            if dt == 'O':
                # Variable-length array field
                lengths = VLEN(arr[field])
            else:
                lengths = np.repeat(dt.shape[0], arr.shape[0])
            # Fixed-length array field
            if len_array is None:
                len_array = lengths
            elif not np.array_equal(lengths, len_array):
                raise ValueError(
                    "inconsistent lengths of array columns in input")
            if dt == 'O':
                dtype.append((field, arr[field][0].dtype))
            else:
                dtype.append((field, arr[field].dtype, dt.shape[1:]))
        else:
            # Scalar field
            dtype.append((field, dt))

    if len_array is None:
        raise RuntimeError("no array column in input")

    # Build stretched output
    ret = np.empty(np.sum(len_array), dtype=dtype)
    for field in fields:
        dt = arr.dtype[field]
        if dt == 'O' or len(dt.shape) == 1:
            # Variable-length or 1D fixed-length array field
            ret[field] = np.hstack(arr[field])
        elif len(dt.shape):
            # Multidimensional fixed-length array field
            ret[field] = np.vstack(arr[field])
        else:
            # Scalar field
            ret[field] = np.repeat(arr[field], len_array)

    if return_indices:
        idx = np.concatenate(list(map(np.arange, len_array)))
        return ret, idx

    return ret
