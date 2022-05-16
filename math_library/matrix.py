import math, copy

from exceptions import DimensionError


class MATRIX(object):
    def __init__(self, arr):
        self.m = len(arr)  # vertical units
        self.n = len(arr[0])  # horizontal units

        self.arr = arr

    def __mul__(self, b):
        if isinstance(b, int) or isinstance(b, float):
            arr = []
            for r in self.arr:
                row = []
                for item in r:
                    row.append(item * b)
                arr.append(row)
            return MATRIX(arr)

        if isinstance(b, MATRIX):

            if self.n == b.m:

                list_of_tuples = zip(*b.arr)
                l = [list(elem) for elem in list_of_tuples]

                arr = []
                for row1 in self.arr:
                    row = []
                    for row2 in l:
                        v = 0
                        for x, y in zip(row1, row2):
                            v += (x * y)
                        row.append(v)
                    arr.append(row)

                return MATRIX(arr)

            else:
                raise DimensionError(
                    f"Matrix {self.n}x{self.m} cannot be multiplied by Matrix{b.n}x{b.m}"
                )


    def __add__(self, b):

        if isinstance(b, int) or isinstance(b, float):
            arr = []
            for r in self.arr:
                row = []
                for item in r:
                    row.append(item + b)
                arr.append(row)
            return MATRIX(arr)

        if isinstance(b, MATRIX):

            if self.n == b.n and self.m == b.m:
                arr = []
                for r1, r2 in zip(self.arr, b.arr):
                    row = []
                    for i1, i2 in zip(r1, r2):
                        row.append(i1 + i2)
                    arr.append(row)

                return MATRIX(arr)

            else:
                raise DimensionError(
                    f"Matrix {self.n}x{self.m} cannot be added to Matrix{b.n}x{b.m}"
                )

    def __sub__(self, b):

        if isinstance(b, int) or isinstance(b, float):
            arr = []
            for r in self.arr:
                row = []
                for item in r:
                    row.append(item - b)
                arr.append(row)
            return MATRIX(arr)

        if isinstance(b, MATRIX):

            if self.n == b.n and self.m == b.m:
                arr = []
                for r1, r2 in zip(self.arr, b.arr):
                    row = []
                    for i1, i2 in zip(r1, r2):
                        row.append(i1 - i2)
                    arr.append(row)

                return MATRIX(arr)

            else:
                raise DimensionError(
                    f"Matrix {b.n}x{b.m} cannot be subtracted from Matrix{self.n}x{self.m}"
                )

    def determinant_slow(self):
        if self.n == self.m:

            if self.n == 1:
                return self.arr[0][0]

            n = 0
            for i in range(len(self.arr)):
                l = copy.deepcopy(self.arr) # looking back at this code... I think I was doing this wrong
                for j in range(len(self.arr)): # GPT does not like this
                    l[j].pop(i)
                l.pop(0)
                n += (-1) ** i * self.arr[0][i] * MATRIX(l).determinant()
                del l

            return n
        else:
            raise DimensionError("")

    def determinant(self):  # SOMEONE ELSES CODE

        n = len(self.arr)
        AM = copy.deepcopy(self.arr)

        # Section 2: Row ops on A to get in upper triangle form
        for fd in range(n):  # A) fd stands for focus diagonal
            for i in range(fd + 1, n):  # B) only use rows below fd row
                if AM[fd][fd] == 0:  # C) if diagonal is zero ...
                    AM[fd][fd] = 1.0e-18  # change to ~zero
                # D) cr stands for "current row"
                crScaler = AM[i][fd] / AM[fd][fd]
                # E) cr - crScaler * fdRow, one element at a time
                for j in range(n):
                    AM[i][j] = AM[i][j] - crScaler * AM[fd][j]

        # Section 3: Once AM is in upper triangle form ...
        product = 1.0
        for i in range(n):
            # ... product of diagonals is determinant
            product *= AM[i][i]

        return product

    def inverse(self):

        d = self.determinant()

        if d == 0:
            raise ZeroDivisionError("Determinant is 0, cannot find inverse of matrix")

        arr = []
        for i in range(len(self.arr)):
            row = []
            for j in range(len(self.arr)):

                l = copy.deepcopy(self.arr)
                for k in range(len(self.arr)):
                    l[k].pop(j)
                l.pop(i)
                row.append((-1) ** (i + j) * MATRIX(l).determinant() / d)
            arr.append(row)

        list_of_tuples = zip(*arr)
        arr = [list(elem) for elem in list_of_tuples]

        return MATRIX(arr)

    def print(self):
        for row in self.arr:
            print(row)