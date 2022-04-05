# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import numpy as np
from math import gamma


# -----------------------------------------------------------
def main() -> None:
    dirx = Dirichlet([15, 5, 5])
    points = dirx.sample(30000)
    obj = Scattered(points)
    obj.show_distribution()
    dirx.draw_pdf_contours()
    dirx.plot_points(points)
    return None


class Scattered:
    def __init__(self, points, **kwargs):
        subdiv = 5
        self._corners = np.array([[0, 0], [1, 0], [0.5, 0.75 ** 0.5]])
        self._AREA = 0.5 * 1 * 0.75 ** 0.5
        self._triangle = tri.Triangulation(self._corners[:, 0], self._corners[:, 1])
        self._pairs = [self._corners[np.roll(range(3), -i)[1:]] for i in range(3)]

        for key, item in kwargs.items():
            if key == 'subdiv':
                subdiv = item

        _refined = tri.UniformTriRefiner(self._triangle)
        trimesh = _refined.refine_triangulation(subdiv=subdiv)
        self._trimesh = trimesh
        self.points = points
        self.pdf = []

        for xy in zip(trimesh.x, trimesh.y):
            self.pdf.append(self.get_pdf(self.xy2bc(xy)))
        self.pdf = 10*np.array(self.pdf)/max(self.pdf)

    def show_distribution(self) -> None:
        plt.tricontourf(self._trimesh, self.pdf, cmap='jet')
        plt.axis('equal')
        plt.xlim(0, 1)
        plt.ylim(0, 0.75 ** 0.5)
        plt.colorbar()
        plt.show()
        return None

    # def estimate_parameters(self):
    #     pass

    def get_pdf(self, point) -> float:
        dist_total = []
        for points in self.points:
            dist_total.append(self.distance(points, point))
        val = sum(dist_total)/len(dist_total)
        return 1/val

    @staticmethod
    def distance(p0, p1) -> float:
        acc = []
        for dimension, value in enumerate(p0):
            acc.append((p1[dimension] - value)**2)
        return 1 * np.multiply.reduce(acc)

    def xy2bc(self, xy, tol=1.e-4):
        coords = np.array([self.tri_area(xy, p) for p in self._pairs]) / self._AREA
        return np.clip(coords, tol, 1.0 - tol)

    @staticmethod
    def tri_area(xy, pair):
        return 0.5 * np.linalg.norm(np.cross(*(pair - xy)))

    def __repr__(self):
        __text = f'Scattered object with points:\n'
        for index, point in enumerate(self.points):
            __text = f'{__text}Point {index}: {point}\n'
        self.show_distribution()
        return __text


########################################################################################################################
class Dirichlet(object):
    def __init__(self, alpha):
        self._alpha = np.array(alpha)
        self._coef = gamma(np.sum(self._alpha)) / np.multiply.reduce([gamma(a) for a in self._alpha])

        self._corners = np.array([[0, 0], [1, 0], [0.5, 0.75 ** 0.5]])
        self._AREA = 0.5 * 1 * 0.75 ** 0.5
        self._triangle = tri.Triangulation(self._corners[:, 0], self._corners[:, 1])
        self._pairs = [self._corners[np.roll(range(3), -i)[1:]] for i in range(3)]

    def pdf(self, x):
        return self._coef * np.multiply.reduce([xx ** (aa - 1) for (xx, aa) in zip(x, self._alpha)])

    def sample(self, n):
        return np.random.dirichlet(self._alpha, n)

    def draw_pdf_contours(self, border=True, nlevels=100, subdiv=5, **kwargs):
        plt.figure(figsize=(8, 6))
        refiner = tri.UniformTriRefiner(self._triangle)
        trimesh = refiner.refine_triangulation(subdiv=subdiv)
        pvals = [self.pdf(self.xy2bc(xy)) for xy in zip(trimesh.x, trimesh.y)]

        plt.tricontourf(trimesh, pvals, nlevels, cmap='jet', **kwargs)
        plt.colorbar()
        plt.axis('equal')
        plt.xlim(0, 1)
        plt.ylim(0, 0.75**0.5)
        if border is True:
            plt.triplot(self._triangle, linewidth=1)
        plt.show()

    def xy2bc(self, xy, tol=1.e-4):
        coords = np.array([self.tri_area(xy, p) for p in self._pairs]) / self._AREA
        return np.clip(coords, tol, 1.0 - tol)

    @staticmethod
    def tri_area(xy, pair):
        return 0.5 * np.linalg.norm(np.cross(*(pair - xy)))

    def plot_points(self, x, barycentric=True, border=True, **kwargs):
        if barycentric is True:
            x = x.dot(self._corners)
        plt.plot(x[:, 0], x[:, 1], 'k.', ms=1, **kwargs)
        plt.axis('equal')
        plt.xlim(0, 1)
        plt.ylim(0, 0.75 ** 0.5)
        plt.axis('off')
        if border is True:
            plt.triplot(self._triangle, linewidth=1)
        plt.show()


# -----------------------------------------------------------
# Main:
if __name__ == '__main__':
    main()
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
