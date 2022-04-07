# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
from math import gamma

import matplotlib.pyplot as plt
import matplotlib.tri as tri
import numpy as np


# -----------------------------------------------------------


def main() -> None:
    original = Dirichlet([0], alphas=[12, 5, 7])
    testpoints = original.sample(1000)
    estimated = Dirichlet(testpoints)

    pars = [parameter for parameter in estimated.parameters]
    print(pars)
    f, ax = plt.subplots(nrows=2, ncols=2)

    original.draw_pdf_contours(ax=ax[0, 0])
    original.plot_points(original.sample(1000), ax=ax[0, 1])
    estimated.draw_pdf_contours(ax=ax[1, 0])
    estimated.plot_points(estimated.sample(1000), ax=ax[1, 1])
    # ax[0, 0].title(f'Original: {pars}.')
    # f.colorbar()
    plt.show()
    return

    
class Dirichlet:
    def __init__(self, points, alphas=None, steps=3):
        self.measurement = np.array(points)

        self._corners = np.array([[0, 0], [1, 0], [0.5, 0.75 ** 0.5]])
        self._AREA = 0.5 * 1 * 0.75 ** 0.5
        self._triangle = tri.Triangulation(self._corners[:, 0], self._corners[:, 1])
        self._pairs = [self._corners[np.roll(range(3), -i)[1:]] for i in range(3)]
        self._refined = tri.UniformTriRefiner(self._triangle)
        self.trimesh = self._refined.refine_triangulation(subdiv=5)

        if alphas is not None:
            self._alpha = np.array(alphas)
        else:
            self._alpha = self._estimate_parameters(steps=steps)

        self._coef = gamma(np.sum(self._alpha)) / np.multiply.reduce([gamma(a) for a in self._alpha])
        self.parameters = self._alpha

    def draw_pdf_contours(self, border=True, nlevels=100, ax=plt, **kwargs):
        # ax.figure(figsize=(8, 6))
        trimesh = self.trimesh
        pvals = [self.pdf(self._xy2bc(xy)) for xy in zip(trimesh.x, trimesh.y)]
        ax.tricontourf(trimesh, pvals, nlevels, cmap='jet', **kwargs)
        # ax.colorbar()
        ax.axis('equal')
        # ax.xlim(0, 1)
        # ax.ylim(0, 0.75**0.5)
        ax.axis('off')
        if border is True:
            ax.triplot(self._triangle, color='black', linewidth=2)
        # plt.show()

    def plot_points(self, x, barycentric=True, border=True, ax=plt, **kwargs):
        if barycentric is True:
            x = x.dot(self._corners)
        ax.plot(x[:, 0], x[:, 1], 'k.', ms=1, **kwargs)
        ax.axis('equal')
        # ax.xlim(0, 1)
        # ax.ylim(0, 0.75 ** 0.5)
        ax.axis('off')
        if border is True:
            ax.triplot(self._triangle, color='black', linewidth=1)
        # plt.show()

    def _estimate_parameters(self, steps=3):
        initialguess = [2, 2, 2]
        initialguess2 = [2.0]
        lr = [0.1**(i+1) for i in range(steps)]
        for lrn in lr:
            self._prealpha = self.minimize_gd(self._minimize_mean, np.array(initialguess, dtype=np.float_), lr=lrn)
            pars = self.minimize_gd(self._minimize_var, initialguess2, lr=lrn)
            initialguess = pars*self._prealpha
            initialguess2 = [1]

        return initialguess

    # Not that useful functions:
    #
    #   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -

    def _minimize_mean(self, initialguess, scale=1000):
        y = self.p_mean(self.measurement)
        pred = self.p_mean(Dirichlet([0], alphas=initialguess).sample(scale))
        acc = 0
        for dim, val in enumerate(y):
            acc += (val - pred[dim]) ** 2
        return 10 * acc ** 0.5

    def _minimize_var(self, initialguess, scale=1000):
        y = self.p_var(self.measurement)
        pred = self.p_var(Dirichlet([0], alphas=initialguess[0]*self._prealpha).sample(scale))
        acc = 0
        for dim, val in enumerate(y):
            acc += (val - pred[dim]) ** 2
        return 10 * acc ** 0.5

    @staticmethod
    def p_mean(dist):
        arr = np.transpose(dist)
        means = []
        for dim in arr:
            means.append(sum(dim) / len(dim))
        return np.array(means)

    def p_var(self, dist):
        arr = np.transpose(dist)
        mean = self.p_mean(dist)
        vars_ = []
        for i, dim in enumerate(arr):
            dix = []
            for value in dim:
                dix.append((value-mean[i])**2)
            vars_.append(sum(dix) / len(dix))
        return np.array(vars_)

    @staticmethod
    def minimize_gd(func, args, lr=0.1, err=0, epoch=20, max_epoch=1000):
        error = [err + 1]
        lrn = lr
        par = args.copy()
        cnt = 0
        cnt_max = 0
        best_this = sum([func(par), func(par), func(par), func(par), func(par)]) / 5
        best_par = par

        while error[-1] > err and cnt < epoch and cnt_max < max_epoch:

            for j, _ in enumerate(par):
                roam = []
                for i in range(3):
                    this_par = par.copy()
                    this_par[j] = this_par[j] * (1 + (i - 1) * lrn)
                    roam.append(this_par)
                    this_err = sum([func(roam[-1]), func(roam[-1]), func(roam[-1]), func(roam[-1]), func(roam[-1])]) / 5
                    if this_err < best_this:
                        best_this = this_err
                        best_par = this_par
                        print(f'New best:{best_par}')
                        cnt = 0

            error.append(best_this)
            par = best_par
            cnt += 1
            cnt_max += 1
        return best_par

    def pdf(self, x):
        return self._coef * np.multiply.reduce([xx ** (aa - 1) for (xx, aa) in zip(x, self._alpha)])

    def sample(self, n):
        return np.random.dirichlet(self._alpha, n)

    def _xy2bc(self, xy, tol=1.e-4):
        coords = np.array([self._tri_area(xy, p) for p in self._pairs]) / self._AREA
        return np.clip(coords, tol, 1.0 - tol)

    @staticmethod
    def _tri_area(xy, pair):
        return 0.5 * np.linalg.norm(np.cross(*(pair - xy)))
# -----------------------------------------------------------
# Main:


if __name__ == '__main__':
    main()
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
