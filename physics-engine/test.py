
import numpy as np
import cupy as cp

from objects.display import display

from objects.plane import plane
from objects.line import line




from functions import *





a = np.array([1,0,0])
b = np.array([0,1,0])

R = getRotationMatrix(a, np.pi/2)

print(np.matmul(R, b))

p = plane(a,b)
l = line(a,b)

print(p.intersect(p))

