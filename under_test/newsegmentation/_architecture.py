# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
from abc import abstractmethod

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from ._tdm import ftdm


# -----------------------------------------------------------
class NewsSegmentation:
    def __init__(self, tdm=0.3, sdm=((0, 0), ()), lcm=()):
        """
        Virtual class: 3 methods must be overriden.
        :param tdm: Penalty factor (betta) for Temporal Distance Manager.
        :param sdm: Spatial Distance Manager parameters:
            [0]: [0]: Variance for Gaussian.
                 [1]: Weight for GPA.
            [1]: SDM algorithm parameters.
        :param lcm: Algorithm parameters for Later Correlation Manager.
        """
        # Parameters for each module of the architecture.
        self.parameters = {"betta_tdm": tdm, "gpa": sdm[0], "sdm": sdm[1], "lcm": lcm}
        # Attribute initialization.
        self.News = []
        self.R = []
        self.s = []
        self.t = []
        self.p = []
        # Steps for in the architecture.
        p, s, t = self.reader('')
        self.p = p
        self.s.append(s)
        self.t.append(t)

        _r, r, s, t = self.temporal_manager(p, s, t)
        self.R.append(_r)
        self.R.append(r)
        self.s.append(s)
        self.t.append(t)

        r, s, t = self.spatial_manager(r, s, t)
        self.R.append(r)
        self.s.append(s)
        self.t.append(t)

        s, t = self.later_correlation_manager(s, t)
        self.R.append(self.specific_language_model(s))
        self.s.append(s)
        self.t.append(t)


        # Tree transformation:

        # Private parameters.
        self._efficientembedding = []

    def reader(self, paths):
        p = [1]
        s = ["Juan se comió un gato", "Un gato se comió a Juan", "Tigres enfadados"]
        t = [2, 4.5, 6]
        return p, s, t

    def specific_language_model(self, s) -> np.array:
        embeddings = self._specific_language_model(s)
        r = np.zeros((len(s), len(s)))
        for ne1, embedding1 in enumerate(embeddings):
            for ne2, embedding2 in enumerate(embeddings):
                value = cosine_similarity(embedding1.reshape(1, -1), embedding2.reshape(1, -1))[0][0]
                r[ne1][ne2] = value
                r[ne2][ne1] = value
        self._efficientembedding = embeddings
        return r

    def temporal_manager(self, p, s, t) -> tuple:
        r0, r1 = ftdm(p, s, self.specific_language_model, self.parameters["betta_tdm"])
        return r0, r1, s, t

    def spatial_manager(self, r, s, t):
        return self._spatial_manager(r, s, t)

    def later_correlation_manager(self, s, t):
        return self._later_correlation_manager(s, t)

    @staticmethod
    @abstractmethod
    def _spatial_manager(r, s, t) -> tuple:
        pass

    @abstractmethod
    def _later_correlation_manager(self, s, t) -> tuple:
        pass

    @staticmethod
    @abstractmethod
    def _specific_language_model(s) -> np.array:
        pass

    def __repr__(self):
        __text = f"Segmentation news object:\n{len(self.News)} news classified.\n"
        return __text

    def __iter__(self):
        self.__n = 0
        return self

    def __next__(self):
        while self.__n < len(self.News):
            yield self.News[self.__n]
            self.__n += 1
        else:
            raise StopIteration
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
