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
    mns = NS(r'../db/news_text/esp/Julen/1.txt', gpa=(15, 1))
    print(mns)
    return


# -----------------------------------------------------------
# Main:
class NS(ns.NewsSegmentation):
    @staticmethod
    def _spatial_manager(r) -> tuple:
        return ns.default_sdm(r)

    @staticmethod
    def _specific_language_model(s) -> np.array:
        return ns.default_slm(s)

    @staticmethod
    def _later_correlation_manager(lm, s, t) -> tuple:
        return ns.default_lcm(lm, s, t)


if __name__ == '__main__':
    validation()
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
