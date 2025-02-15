
from _sso import *
import copy_reg
import struct

ComplexType = type(1j)

def assert_matrix_sizes(A, B):
        assert A.row_count == B.row_count and A.col_count == B.col_count, "Sizes of matrices not mutch"

class ComplexMatrix:

        def __init__(self, re, im=None):
                if not im:
                        im = new_nullmatrix(re.row_count, re.col_count)
                if type(re) != Matrix or type(im) != Matrix:
                        raise TypeError("Arguments must be matrices")
                assert_matrix_sizes(re, im)
                self.re = re
                self.im = im

        def get(self, row, col):
                return self.re(row, col) + self.im(row, col)*1j

        def set(self, row, col, value):
                if type(value) == ComplexType:
                        self.re(row, col, value.re)
                        self.im(row, col, value.im)
                else:
                        self.re(row, col, value)

        def __getattr__(self, key):
                if key == "__dict__":
                        return self.__dict__
                elif key == "row_count":
                        return self.re.row_count
                elif key == "col_count":
                        return self.re.col_count
                else:
                        return self.__dict__[key]

        def __setattr__(self, key, value):
                self.__dict__[key] = value

        def copy(self):
                return ComplexMatrix(self.re.copy(), self.im.copy())

        def transp(self):
                return ComplexMatrix(self.re.transp(), self.im.transp())

        def rows(self, rows):
                return ComplexMatrix(self.re.rows(rows), self.im.rows(rows))

        def cols(self, cols):
                return ComplexMatrix(self.re.cols(cols), self.im.cols(cols))

        def clear(self):
                self.re.clear()
                self.im.clear()

        def swap_rows(self, idx1, idx2):
                self.re.swap_rows(idx1, idx2)
                self.im.swap_rows(idx1, idx2)

        def swap_cols(self, idx1, idx2):
                self.re.swap_cols(idx1, idx2)
                self.im.swap_cols(idx1, idx2)

        def __add__(self, value):
                return ComplexMatrix(self.re + value.re, self.im + value.im)

        def __radd__(self, value):
                return ComplexMatrix(self.re + value.re, self.im + value.im)

        def __sub__(self, value):
                return ComplexMatrix(self.re - value.re, self.im - value.im)

        def __rsub__(self, value):
                return ComplexMatrix(value.re - self.re, value.im - self.im)

        def __mul__(self, value):
                re = self.re*value.re - self.im*value.im
                im = self.re*value.im + self.im*value.re
                return ComplexMatrix(re, im)

        def __rmul__(self, value):
                re = value.re*self.re - value.im*self.im
                im = value.im*self.re + value.re*self.im
                return ComplexMatrix(re, im)

        def __coerce__(self, value):
                if type(value) == Matrix:
                        return self, ComplexMatrix(value, new_nullmatrix(value.row_count, value.col_count))

                


        



def _get_matrix_data(matrix):
    return matrix._get_data(), matrix.__dict__


def _set_matrix_data(matrix, value):
    data, dict = value
    matrix._set_data(data)
    for key, value in dict.items():
        setattr(matrix, key, value)


def _get_intarray_data(ia):
    Data = ()
    SZ = len(ia)
    Structure = "i"*SZ
    for i in xrange(SZ):
        Data += (ia[i], )
    return struct.pack(Structure, *Data), ia.__dict__

def _set_intarray_data(ia, value):
    Data, dict = value
    Structure = "i"*len(ia)
    Data = struct.unpack(Structure, Data)
    k = 0
    for i in Data:
        ia[k] = i
        k += 1
    for key, value in dict.items():
        setattr(ia, key, value)


def _matrix_constructor(RowCount, ColCount, Data):
    R = new_matrix(RowCount, ColCount)
    _set_matrix_data(R, Data)
    return R

def _intarray_constructor(sz, data):
    R = new_intarray(sz)
    _set_intarray_data(R, data)
    return R

def _slicer_constructor(constructor, args, buf, inital):
    R = constructor(*args)
    if not inital:
        R.next()
        for i in xrange(len(buf)):
            R.buffer[i] = buf[i]    
    return R

def _cmi_constructor(constructor, args, buf, inital):
    R = constructor(*args)
    if not inital:
        R.next()
        R.indexes = buf
    return R


 
def _pickle_matrix(Matrix):
    return _matrix_constructor, (Matrix.row_count, Matrix.col_count, _get_matrix_data(Matrix))

def _pickle_intarray(ia):
    return _intarray_constructor, (ia.size, _get_intarray_data(ia))

def _pickle_slicer(s):
    return _slicer_constructor, (s._constructor, s._args, s.buffer, s.isinital)

def _pickle_cmi(x):
    return _cmi_constructor, (x._constructor, x._args, x.indexes, x.isinital)


copy_reg.pickle(Matrix,
                _pickle_matrix,
                _matrix_constructor)
copy_reg.pickle(IntArray,
                _pickle_intarray,
                _intarray_constructor)
copy_reg.pickle(Slicer,
                _pickle_slicer,
                _slicer_constructor)
copy_reg.pickle(MatrixCIterator,
                _pickle_cmi,
                _cmi_constructor)


