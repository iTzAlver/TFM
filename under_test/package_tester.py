# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
import numpy as np

import newsegmentation as ns


# -----------------------------------------------------------
def validation() -> None:
    l0 = (1, 'Hola.')
    l1 = (2, 'Se ha caido un jarrón.')
    l2 = (3, 'En la habitación de al lado.')
    tr = ns.TreeStructure(l0, l1, l2, ID=10, time=30.2)
    print(tr.isValid)
    print(tr.isComplete)
    tr.add(CP=0.6, embedding=[0.38420, 0.32294852985, 0.348902034], ref=0)
    print(tr.isComplete)
    print(tr)
    for leaf in tr:
        for idx, pl in leaf:
            print(f'{idx}: {pl}')

    mns = NS()
    print(mns)
    return


# -----------------------------------------------------------
# Main:
class NS(ns.NewsSegmentation):
    @staticmethod
    def _spatial_manager(r, s, t) -> tuple:
        return r, s, t

    @staticmethod
    def _specific_language_model(s) -> np.array:
        return ns.default_slm(s)

    def _later_correlation_manager(self, s, t) -> tuple:
        # ns.NewsSegmentation.specific_language_model(self, s)
        return s, t


if __name__ == '__main__':
    validation()
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
