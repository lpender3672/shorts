import math
import material
import copy


# \
class DimensionError(Exception):
    def __init__(self, args):
        super().__init__()


# / Exceptions types


# \
def convertfraction(n, factor=""):
    if round(n, 3) == int(n):
        if int(n) == 1:
            return factor
        return str(int(n)) + factor

    for i in range(2, 1000):
        if round(n * i, 3) % 1 == 0:
            if int(n * i) == 1:
                return factor + "/" + str(i)
            return str(int(n * i)) + factor + "/" + str(i)


def simp(n):
    if convertfraction(n):
        return convertfraction(n)

    irrationals = {"pi": math.pi, "sqrt(2)": math.sqrt(2), "sqrt(3)": math.sqrt(3), "sqrt(5)": math.sqrt(5),
                   "sqrt(7)": math.sqrt(7)}
    # also need e and logs
    for name in irrationals:
        if convertfraction(n / irrationals[name]):
            return convertfraction(n / irrationals[name], name)


# / code to simplify numbers be it fractions or irrationals

class quaternion(object):  # basically a 4d vector
    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b  # x
        self.c = c  # y
        self.d = d  # z

    def conjegate(self):
        return quaternion(self.a, self.b * -1, self.c * -1, self.d * -1)

    def __mul__(a, b):
        s = a.a * b.a - a.b * b.b - a.c * b.c - a.d * b.d
        x = a.a * b.b + a.b * b.a + a.c * b.d - a.d * b.c
        y = a.a * b.c - a.b * b.d + a.c * b.a + a.d * b.b
        z = a.a * b.d + a.b * b.c - a.c * b.b + a.d * b.a

        return quaternion(s, x, y, z)


class vector3(object):
    def __init__(self, x, y, z):

        self.x, self.y, self.z = x, y, z

        self.mod = math.sqrt(x ** 2 + y ** 2 + z ** 2)

        if self.mod == 0:
            self.norm = None
        elif round(self.mod, 9) == 1:
            self.norm = self
        else:
            self.norm = vector3(x / self.mod, y / self.mod, z / self.mod)

    def zero():
        return vector3(0, 0, 0)

    def ones():
        return vector3(1, 1, 1)

    def __mul__(self, b):

        if isinstance(b, float) or isinstance(b, int):
            return vector3(self.x * b, self.y * b, self.z * b)

        if isinstance(b, vector3):
            raise TypeError("unsupported operand types")
            # dot product and vector product

    def __truediv__(self, b):

        if isinstance(b, float) or isinstance(b, int):
            if b == 0:
                raise ValueError("div by 0")
            return vector3(self.x / b, self.y / b, self.z / b)

        if isinstance(b, vector3):
            raise TypeError("unsupported operand types")

    def dot(self, b):  # the dot dot product

        return self.x * b.x + self.y * b.y + self.z * b.z

    def cross(self, b):

        # https://mathinsight.org/cross_product_formula

        x1, y1, z1 = self.x, self.y, self.z
        x2, y2, z2 = b.x, b.y, b.z

        xmat = MATRIX([[y1, z1], [y2, z2]])
        ymat = MATRIX([[x1, z1], [x2, z2]])
        zmat = MATRIX([[x1, y1], [x2, y2]])

        return vector3(xmat.determinant(), -ymat.determinant(),
                       zmat.determinant())

    def __add__(self, b):

        if isinstance(b, float) or isinstance(b, int):
            return vector3(self.x + b, self.y + b, self.z + b)

        if isinstance(b, vector3):
            return vector3(self.x + b.x, self.y + b.y, self.z + b.z)

    def __sub__(self, b):

        if isinstance(b, float) or isinstance(b, int):
            return vector3(self.x - b, self.y - b, self.z - b)

        if isinstance(b, vector3):
            return vector3(self.x - b.x, self.y - b.y, self.z - b.z)

    def toQuaternion(self):

        return quaternion(0, self.x, self.y, self.z)

    def angleBetween(self, v):
        dot = self.dot(v)

        return math.acos(dot / (self.mod * v.mod))

    def rotate(self, A, a):  # rotate

        # rotate V around axis A by angle a
        # q = (cos a/2 , A.x * sin a/2, A.y * sin a/2, A.z * sin a/2)
        # V' = q V q.conjegate

        V = self.toQuaternion()

        q = quaternion(
            math.cos(a / 2),
            A.norm.x * math.sin(a / 2),
            A.norm.y * math.sin(a / 2),
            A.norm.z * math.sin(a / 2))

        Rv = q * V * q.conjegate()

        return vector3(Rv.b, Rv.c, Rv.d)

    def toList(self):
        return [self.x, self.y, self.z]

    def __str__(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.z)


class vector2(vector3):
    def __init__(self, x, y):
        super().__init__(x, y, 0)


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

        if isinstance(b, vector3):
            v3MAT = MATRIX([[b.x], [b.y], [b.z]])

            return v3MAT * self

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
                l = copy.deepcopy(self.arr)
                for j in range(len(self.arr)):
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


class line(object):
    def __init__(self, direction, point):
        self.d = direction
        self.p = point

    def getpoint(self, k):
        return self.p + self.d * k

    def rotate(self, axis, angle):
        OA = self.p
        OB = self.p + self.d

        ROA = OA.rotate(axis, angle)
        ROB = OB.rotate(axis, angle)

        return line(ROB - ROA, ROA)


class plane(object):
    def __init__(self, normal, point):
        self.n = normal
        self.p = point

    def cartesian(self):
        return [self.n.x, self.n.y, self.n.z, self.n.dot(self.p)]

    def rotate(self, axis, angle):
        l = line(self.n, self.p)
        l = l.rotate(axis, angle)

        return plane(l.d, l.p)


def trace_Vector(v3, cam):  # instead of triangles

    l = line(v3 - cam.focalpos, cam.focalpos)

    a, b, c, d = cam.plane.cartesian()

    M1 = MATRIX([[a, b, c, 0],
                 [1, 0, 0, -l.d.x],
                 [0, 1, 0, -l.d.y],
                 [0, 0, 1, -l.d.z]])

    M2 = MATRIX([[d], [l.p.x], [l.p.y], [l.p.z]])

    res = M1.inverse() * M2
    k = res.arr[3][0]

    v3onPlane = l.getpoint(k) - cam.planeOrigin

    d = v3onPlane.mod
    a = v3onPlane.angleBetween(cam.left * -1)
    b = v3onPlane.angleBetween(cam.up * -1)

    if b > math.pi / 2:
        a *= -1

    if a > math.pi / 2:
        b *= -1

    x = d * math.cos(a)
    y = d * math.sin(a)

    v2 = vector2(x, y) * cam.f
    v2.k = k

    v2.ld = l.d

    return v2


"""
class triangle2(object):
    def __init__(self, verticies, normal, displayed = True, mat = None):
        self.verticies = verticies
        self.norm = normal
        self.displayed = displayed
        self.mat = mat

        # and dont inherit from triangle3


class triangle3(object):
    def __init__(self, verticies, normal=vector3.zero(), displayed = True,  mat=None):

        self.displayed = displayed
        self.verticies = verticies
        self.norm = normal
        self.mat = mat

        # if normal vector facing away from viewer, dont display
        # if normal vector is 0,0,0 or facing towards viewer, display triangle

        # all triangles of all objects are put in a big list then tested, then rendered
        # then rasturised into an image to display

class mesh(object):

"""

"""
    def convert2D(self, camera):

        # advanced...



        a, b, c, d = camera.plane.cartesian()

        # camera focalpos from origin
        p = camera.focalpos

        # find the line that goes through the vector and the focalpos

        # then find the 3d vector that this line intersects the plane using:
        # louis' Matrix

        vector2s = []

        if self.norm.dot(camera.plane.n) > 0:  # if triangle not facing the camera
            return triangle2(vector2s, camera.norm, False, self.mat)


        for v in self.verticies:
            l = line(v - p, p)

            M1 = MATRIX([[a, b, c,      0],
                         [1, 0, 0, -l.d.x],
                         [0, 1, 0, -l.d.y],
                         [0, 0, 1, -l.d.z]])

            M2 = MATRIX([[d], [l.p.x], [l.p.y], [l.p.z]])

            res = M1.inverse() * M2

            # planeVector = vector3(res.arr[0][0], res.arr[1][0], res.arr[2][0]) - camera.planeOrigin BAD METHOD?

            planeVector = l.getpoint(res.arr[3][0]) - camera.planeOrigin  # vector on plane   IF lambda MORE THAN 1 then vector is getting traced forwards

            # find the angle it makes with camera.left
            a = planeVector.angleBetween(camera.left * -1)

            # can now get x and y of the 2d vector
            x = planeVector.mod * math.cos(a)
            y = planeVector.mod * math.sin(a)

            vector2s.append(vector2(x, y))


        return triangle2(vector2s, camera.norm, True, self.mat)
"""
