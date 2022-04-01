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


# -----------------------------------------------------------
def main() -> None:
    obj = Scattered([[0.3, 0.3, 0.4], [0.7, 0.2, 0.1]])
    print(obj)
    return


def tri_area(xy, pair):
    return 0.5 * np.linalg.norm(np.cross(*(pair - xy)))


def xy2bc(xy, _pairs, _AREA, tol=1.e-4):
    '''Converts 2D Cartesian coordinates to barycentric.
    Arguments:
        `xy`: A length-2 sequence containing the x and y value.
    '''
    coords = np.array([tri_area(xy, p) for p in _pairs]) / _AREA
    return np.clip(coords, tol, 1.0 - tol)


class Scattered:
    def __init__(self, points, **kwargs):
        subdiv = 5
        for key, item in kwargs.items():
            if key == 'subdiv':
                subdiv = item

        self._corners = np.array([[0, 0], [1, 0], [0.5, 0.75 ** 0.5]])
        _triangle = tri.Triangulation(self._corners[:, 0], self._corners[:, 1])
        _refined = tri.UniformTriRefiner(_triangle)
        trimesh = _refined.refine_triangulation(subdiv=subdiv)
        self._trimesh = trimesh


        self.points = points
        self.pdf = []

        for xy in zip(trimesh.x, trimesh.y):
            self.pdf.append(self.get_pdf(xy))
        self.pdf = np.array(self.pdf)

    def show_distribution(self) -> None:
        # fig = plt.figure(figsize=(10.8, 4.8))
        # fig.subplots_adjust(left=0.075, right=0.85, wspace=0.3)
        # ax = fig.add_subplot(1, 2, 1, projection='ternary')
        # ax.tricontourf(self._trimesh, self.pdf, 100, cmap='jet')
        # x, y, z = xy2bc()

        plt.tricontourf(self._trimesh, self.pdf, cmap='jet')

        plt.axis('equal')
        plt.xlim(0, 1)
        plt.ylim(0, 0.75 ** 0.5)
        plt.colorbar()
        plt.show()
        return None

    def estimate_parameters(self):
        pass

    def get_pdf(self, point) -> float:
        x = point[0]
        y = point[1]
        dist_total = 0
        for points in self.points:
            the_point = np.transpose(self._corners).dot(np.array(points))
            dist_total += self.distance((the_point[0], the_point[1]), (x, y))
        return dist_total

    @staticmethod
    def distance(p0, p1) -> float:
        acc = 0
        for dimension, value in enumerate(p0):
            acc += (p1[dimension] - value)**2
        return acc**0.5

    def __repr__(self):
        __text = f'Scattered object with points:\n'
        for index, point in enumerate(self.points):
            __text = f'{__text}Point {index}: {point}\n'
        self.show_distribution()
        return __text
   
# -----------------------------------------------------------
# Main:
if __name__ == '__main__':
    main()
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
