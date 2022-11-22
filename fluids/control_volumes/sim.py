import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import numba

# square fluid control volumes

# set boundary conditions

@numba.njit
def set_bnd(b, x):
    x[0, :] = x[1, :] if b == 1 else -x[1, :]
    x[-1, :] = x[-2, :] if b == 1 else -x[-2, :]
    x[:, 0] = x[:, 1] if b == 2 else -x[:, 1]
    x[:, -1] = x[:, -2] if b == 2 else -x[:, -2]

    x[0, 0] = 0.5 * (x[1, 0] + x[0, 1])
    x[0, -1] = 0.5 * (x[1, -1] + x[0, -2])
    x[-1, 0] = 0.5 * (x[-2, 0] + x[-1, 1])
    x[-1, -1] = 0.5 * (x[-2, -1] + x[-1, -2])

# linear solver
@numba.njit
def lin_solve(b, x, x0, a, c, N, iters=20):
    cRecip = 1 / c
    for k in range(0, iters):
        for j in range(1, N - 1):
            for i in range(1, N - 1):
                x[i, j] = (
                    x0[i, j]
                    + a
                    * (
                        x[i + 1, j]
                        + x[i - 1, j]
                        + x[i, j + 1]
                        + x[i, j - 1]
                    )
                ) * cRecip

        set_bnd(b, x)

# diffuse
@numba.njit
def diffuse(b, x, x0, diff, dt, N, iters):
    a = dt * diff * (N - 2) * (N - 2)
    lin_solve(b, x, x0, a, 1 + 4 * a, N, iters)

# project velocity field to make it divergence free and curl free (incompressible)
@numba.njit
def project(velocX, velocY, p, div, N):
    for j in range(1, N - 1):
        for i in range(1, N - 1):
            div[i, j] = -0.5 * (
                velocX[i + 1, j]
                - velocX[i - 1, j]
                + velocY[i, j + 1]
                - velocY[i, j - 1]
            ) / N
            p[i, j] = 0

    set_bnd(0, div)
    set_bnd(0, p)
    lin_solve(0, p, div, 1, 4, N, 20)

    for j in range(1, N - 1):
        for i in range(1, N - 1):
            velocX[i, j] -= 0.5 * (p[i + 1, j] - p[i - 1, j]) * N
            velocY[i, j] -= 0.5 * (p[i, j + 1] - p[i, j - 1]) * N

    set_bnd(1, velocX)
    set_bnd(2, velocY)

# add density to the fluid field (density is a scalar field)
@numba.njit
def advect(b, d, d0, velocX, velocY, dt, N):
    dt0 = dt * (N - 2)
    for j in range(1, N - 1):
        for i in range(1, N - 1):
            tmp1 = dt0 * velocX[i, j]
            tmp2 = dt0 * velocY[i, j]
            x = i - tmp1
            y = j - tmp2

            if x < 0.5:
                x = 0.5
            if x > N + 0.5:
                x = N + 0.5
            i0 = int(x)
            i1 = i0 + 1
            if y < 0.5:
                y = 0.5
            if y > N + 0.5:
                y = N + 0.5
            j0 = int(y)
            j1 = j0 + 1

            s1 = x - i0
            s0 = 1 - s1
            t1 = y - j0
            t0 = 1 - t1

            d[i, j] = (
                s0 * (t0 * d0[i0, j0] + t1 * d0[i0, j1])
                + s1 * (t0 * d0[i1, j0] + t1 * d0[i1, j1])
            )

    set_bnd(b, d)

class fluid():
    def __init__(self, N, visc, diff, dt):
        self.N = N
        self.visc = visc
        self.diff = diff
        self.dt = dt

        self.s = np.zeros((N, N))
        self.density = np.zeros((N, N))

        self.Vx = np.zeros((N, N))
        self.Vy = np.zeros((N, N))

        self.Vx0 = np.zeros((N, N))
        self.Vy0 = np.zeros((N, N))

    def addDensity(self, x, y, amount):
        self.density[x, y] += amount

    def addVelocity(self, x, y, amountX, amountY):
        self.Vx[x, y] += amountX
        self.Vy[x, y] += amountY

    def step(self):
        N = self.N
        visc = self.visc
        diff = self.diff
        dt = self.dt
        Vx = self.Vx
        Vy = self.Vy
        Vx0 = self.Vx0
        Vy0 = self.Vy0
        s = self.s
        density = self.density

        diffuse(1, Vx0, Vx, visc, dt, N, 4)
        diffuse(2, Vy0, Vy, visc, dt, N, 4)

        project(Vx0, Vy0, Vx, Vy, N)

        advect(1, Vx, Vx0, Vx0, Vy0, dt, N)
        advect(2, Vy, Vy0, Vx0, Vy0, dt, N)

        project(Vx, Vy, Vx0, Vy0, N)

        diffuse(0, s, density, diff, dt, N, 4)
        advect(0, density, s, Vx, Vy, dt, N)

    def render(self):
        plt.imshow(self.density, cmap="hot", interpolation="nearest")
        plt.show()

    def animate(self, T, interval):
        fig = plt.figure()
        ims = []
        for t in np.arange(0, T, self.dt):
            Nc = self.N//2
            self.addDensity(Nc, Nc, 1000)
            V = 1
            vx = V * np.sin(2 * np.pi * t / 10)
            vy = V * np.cos(2 * np.pi * t / 10)
            self.addVelocity(Nc, Nc, vx, vy)
            self.step()

            if np.isclose(t % (interval/1000), 0):
                im = plt.imshow(self.density**2, cmap="hot", interpolation="nearest")
                ims.append([im])
        
        # animation function
        ani = animation.ArtistAnimation(fig, ims, interval=interval, blit=True, repeat_delay=1000)
        plt.show()
        ani.save('fluids/control_volumes/animation.gif')
    


if __name__ == "__main__":
    mu = 0.001
    diff = 0.0001
    f = fluid(64, mu, diff, 0.01)
    f.animate(10, 20)
