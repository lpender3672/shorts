import numpy as np
import scipy
from matplotlib import pyplot as plt

def differentiate(f, x, h = 0.001):
    return (f(x+h) - f(x)) / h

def differentiate_n_times(n, f, x, h = 0.001):
    if n == 1:
        return differentiate(f, x, h)
    else:
        return (differentiate_n_times(n - 1, f, x + h, h) - differentiate_n_times(n - 1, f, x, h)) / h

def get_boundary_function(order, f0, f1, x0, x1):

    if not isinstance(order, int):
        raise TypeError("order must be an integer")
    if order < 1:
        raise Exception(f"order must be greater than 1")

    if order % 2 == 0:
        n = order
        print(f"Warning : order is even, the {n//2 - 1} derivative will be discontinuous at second boundary")
    else:
        n = order+1

    matrix = np.zeros((n, n))
    power = np.arange(0, n, 1)[::-1]
    matrix[0] = np.power(x0, power)
    matrix[1] = np.power(x1, power)

    for i in range(2, n, 2):
        power = np.arange(0, n - i + 1, 1)[::-1]
        factor = np.zeros(n)
        for j in range(n):
            k = n - j - 1
            if k - i//2 >= 0:
                factor[j] = np.math.factorial(k) / np.math.factorial(k - i // 2)
        matrix[i,:power.size] = factor*np.power(x0, power)
        matrix[i,:factor.size] *= factor
        matrix[i + 1,:power.size] = factor * np.power(x1, power)
        matrix[i + 1,:factor.size] *= factor

    output = np.zeros(n)
    output[0] = f0(x0)
    output[1] = f1(x1)
    for i in range(2, n, 2):
        output[i] = differentiate_n_times(i // 2, f0, x0)
        output[i + 1] = differentiate_n_times(i // 2, f1, x1)

    solution = np.linalg.solve(matrix, output)

    return lambda x: np.sum([solution[i] * x ** (n-i-1) for i in range(n)], axis=0)

## cleaning up the above function
    
def f0(x):
    return - np.exp(- x)

def f1(x):
    return 2 - np.log(x)

x0 = np.linspace(-1, 1, 20)
x1 = np.linspace(2, 3, 20)

fig = plt.gca()
fig.plot(x0, f0(x0))
fig.plot(x1, f1(x1))

boundary_f = get_boundary_function(10, f0, f1, x0[-1], x1[0])

xrange = np.linspace(x0[-1], x1[0], 100)

plt.plot(xrange, boundary_f(xrange))

plt.ylim(-2,4)

plt.show()
