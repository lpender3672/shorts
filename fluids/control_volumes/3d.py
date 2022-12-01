import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numba

# set 3d boundary conditions

@numba.njit
def set_bnd_3d(b, x):
    # faces
    x[0, :, :] = x[1, :, :] if b == 1 else -x[1, :, :]
    x[-1, :, :] = x[-2, :, :] if b == 1 else -x[-2, :, :]
    x[:, 0, :] = x[:, 1, :] if b == 2 else -x[:, 1, :]
    x[:, -1, :] = x[:, -2, :] if b == 2 else -x[:, -2, :]
    x[:, :, 0] = x[:, :, 1] if b == 3 else -x[:, :, 1]
    x[:, :, -1] = x[:, :, -2] if b == 3 else -x[:, :, -2]
    # edges
    x[0, 0, :] = 0.5 * (x[1, 0, :] + x[0, 1, :])
    x[0, -1, :] = 0.5 * (x[1, -1, :] + x[0, -2, :])
    x[-1, 0, :] = 0.5 * (x[-2, 0, :] + x[-1, 1, :])
    x[-1, -1, :] = 0.5 * (x[-2, -1, :] + x[-1, -2, :])
    x[0, :, 0] = 0.5 * (x[1, :, 0] + x[0, :, 1])
    x[0, :, -1] = 0.5 * (x[1, :, -1] + x[0, :, -2])
    x[-1, :, 0] = 0.5 * (x[-2, :, 0] + x[-1, :, 1])
    x[-1, :, -1] = 0.5 * (x[-2, :, -1] + x[-1, :, -2])
    x[:, 0, 0] = 0.5 * (x[:, 1, 0] + x[:, 0, 1])
    x[:, 0, -1] = 0.5 * (x[:, 1, -1] + x[:, 0, -2])
    x[:, -1, 0] = 0.5 * (x[:, -2, 0] + x[:, -1, 1])
    x[:, -1, -1] = 0.5 * (x[:, -2, -1] + x[:, -1, -2])
    # corners
    x[0, 0, 0] = 0.333 * (x[1, 0, 0] + x[0, 1, 0] + x[0, 0, 1])
    x[0, 0, -1] = 0.333 * (x[1, 0, -1] + x[0, 1, -1] + x[0, 0, -2])
    x[0, -1, 0] = 0.333 * (x[1, -1, 0] + x[0, -2, 0] + x[0, -1, 1])
    x[0, -1, -1] = 0.333 * (x[1, -1, -1] + x[0, -2, -1] + x[0, -1, -2])
    x[-1, 0, 0] = 0.333 * (x[-2, 0, 0] + x[-1, 1, 0] + x[-1, 0, 1])
    x[-1, 0, -1] = 0.333 * (x[-2, 0, -1] + x[-1, 1, -1] + x[-1, 0, -2])
    x[-1, -1, 0] = 0.333 * (x[-2, -1, 0] + x[-1, -2, 0] + x[-1, -1, 1])
    x[-1, -1, -1] = 0.333 * (x[-2, -1, -1] + x[-1, -2, -1] + x[-1, -1, -2])

@numba.njit
def lin_solve_3d(b, x, x0, a, c):
    for k in range(20):
        for i in range(1, x.shape[0] - 1):
            for j in range(1, x.shape[1] - 1):
                for l in range(1, x.shape[2] - 1):
                    x[i, j, l] = (x0[i, j, l] + a * (x[i + 1, j, l] + x[i - 1, j, l] + x[i, j + 1, l] + x[i, j - 1, l] + x[i, j, l + 1] + x[i, j, l - 1])) / c
        set_bnd_3d(b, x)

@numba.njit
def diffuse_3d(b, x, x0, diff, dt):
    a = dt * diff * (x.shape[0] - 2) * (x.shape[1] - 2) * (x.shape[2] - 2)
    lin_solve_3d(b, x, x0, a, 1 + 6 * a)

@numba.njit
def advect_3d(b, d, d0, u, v, w, dt):
    dt0 = dt * (u.shape[0] - 2)
    for i in range(1, u.shape[0] - 1):
        for j in range(1, u.shape[1] - 1):
            for k in range(1, u.shape[2] - 1):
                x = i - dt0 * u[i, j, k]
                y = j - dt0 * v[i, j, k]
                z = k - dt0 * w[i, j, k]
                if x < 0.5:
                    x = 0.5
                if x > u.shape[0] - 1.5:
                    x = u.shape[0] - 1.5
                i0 = int(x)
                i1 = i0 + 1
                if y < 0.5:
                    y = 0.5
                if y > u.shape[1] - 1.5:
                    y = u.shape[1] - 1.5
                j0 = int(y)
                j1 = j0 + 1
                if z < 0.5:
                    z = 0.5
                if z > u.shape[2] - 1.5:
                    z = u.shape[2] - 1.5
                k0 = int(z)
                k1 = k0 + 1
                s1 = x - i0
                s0 = 1 - s1
                t1 = y - j0
                t0 = 1 - t1
                u1 = z - k0
                u0 = 1 - u1
                d[i, j, k] = s0 * (t0 * (u0 * d0[i0, j0, k0] + u1 * d0[i0, j0, k1]) + t1 * (u0 * d0[i0, j1, k0] + u1 * d0[i0, j1, k1])) + s1 * (t0 * (u0 * d0[i1, j0, k0] + u1 * d0[i1, j0, k1]) + t1 * (u0 * d0[i1, j1, k0] + u1 * d0[i1, j1, k1]))
    
    set_bnd_3d(b, d)

@numba.njit
def project_3d(u, v, w, p, div):
    for i in range(1, u.shape[0] - 1):
        for j in range(1, u.shape[1] - 1):
            for k in range(1, u.shape[2] - 1):
                div[i, j, k] = -0.5 * (u[i + 1, j, k] - u[i - 1, j, k] + v[i, j + 1, k] - v[i, j - 1, k] + w[i, j, k + 1] - w[i, j, k - 1]) / u.shape[0]
                p[i, j, k] = 0
    set_bnd_3d(0, div)
    set_bnd_3d(0, p)
    lin_solve_3d(0, p, div, 1, 6)
    for i in range(1, u.shape[0] - 1):
        for j in range(1, u.shape[1] - 1):
            for k in range(1, u.shape[2] - 1):
                u[i, j, k] -= 0.5 * (p[i + 1, j, k] - p[i - 1, j, k]) * u.shape[0]
                v[i, j, k] -= 0.5 * (p[i, j + 1, k] - p[i, j - 1, k]) * u.shape[0]
                w[i, j, k] -= 0.5 * (p[i, j, k + 1] - p[i, j, k - 1]) * u.shape[0]
    set_bnd_3d(1, u)
    set_bnd_3d(2, v)
    set_bnd_3d(3, w)

class fluid_3D():
    def __init__(self, size, diffusion, viscosity, dt):
        self.size = size
        self.diff = diffusion
        self.visc = viscosity
        self.dt = dt
        self.s = np.zeros((size, size, size), dtype=np.float32)
        self.density = np.zeros((size, size, size), dtype=np.float32)
        self.Vx = np.zeros((size, size, size), dtype=np.float32)
        self.Vy = np.zeros((size, size, size), dtype=np.float32)
        self.Vz = np.zeros((size, size, size), dtype=np.float32)
        self.Vx0 = np.zeros((size, size, size), dtype=np.float32)
        self.Vy0 = np.zeros((size, size, size), dtype=np.float32)
        self.Vz0 = np.zeros((size, size, size), dtype=np.float32)
    
    def add_density(self, x, y, z, amount):
        self.density[x, y, z] += amount
    
    def add_velocity(self, x, y, z, amountX, amountY, amountZ):
        self.Vx[x, y, z] += amountX
        self.Vy[x, y, z] += amountY
        self.Vz[x, y, z] += amountZ
        
    def step(self):
        diffuse_3d(1, self.Vx0, self.Vx, self.visc, self.dt)
        diffuse_3d(2, self.Vy0, self.Vy, self.visc, self.dt)
        diffuse_3d(3, self.Vz0, self.Vz, self.visc, self.dt)
        project_3d(self.Vx0, self.Vy0, self.Vz0, self.Vx, self.Vy)
        advect_3d(1, self.Vx, self.Vx0, self.Vx0, self.Vy0, self.Vz0, self.dt)
        advect_3d(2, self.Vy, self.Vy0, self.Vx0, self.Vy0, self.Vz0, self.dt)
        advect_3d(3, self.Vz, self.Vz0, self.Vx0, self.Vy0, self.Vz0, self.dt)
        project_3d(self.Vx, self.Vy, self.Vz, self.Vx0, self.Vy0)
        diffuse_3d(0, self.s, self.density, self.diff, self.dt)
        advect_3d(0, self.density, self.s, self.Vx, self.Vy, self.Vz, self.dt)

    def save(self, filename):
        data = np.zeros((self.size, self.size, self.size, 4), dtype=np.float32)
        data[:, :, :, 0] = self.density
        data[:, :, :, 1] = self.Vx
        data[:, :, :, 2] = self.Vy
        data[:, :, :, 3] = self.Vz
        np.save(filename, data)
    
    def load(self, filename):
        data = np.load(filename)
        self.density = data[:, :, :, 0]
        self.Vx = data[:, :, :, 1]
        self.Vy = data[:, :, :, 2]
        self.Vz = data[:, :, :, 3]

    def render(self, T):
        # plot streamlines after time T
        x, y, z = np.mgrid[0:self.size, 0:self.size, 0:self.size]
        for t in range(T):
            self.add_density(5, 5, 5, 100)
            self.add_velocity(5, 5, 5, 1, 1, 1)
            self.step()
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.quiver(x, y, z, self.Vx, self.Vy, self.Vz, length=0.1, normalize = True)
        plt.show()


if __name__ == "__main__":
    fluid = fluid_3D(10, 0.001, 0.001, 0.1)
    fluid.add_density(5, 5, 5, 100)
    fluid.add_velocity(5, 5, 5, 1, 1, 1)
    fluid.render(2)
    fluid.save("test.npy")