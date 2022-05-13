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

from ._structures import TreeStructure
from ._tdm import ftdm


# -----------------------------------------------------------
class NewsSegmentation:
    def __init__(self, news_path, tdm=0.3, gpa=(0, 0), sdm=(), lcm=(), ref=0):
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
        self.parameters = {"betta_tdm": tdm, "gpa": gpa, "sdm": sdm, "lcm": lcm}
        self.reference = ref
        # Attribute initialization.
        self.News = []
        self.R = []
        self.s = []
        self.t = []
        self.p = []
        # Private parameters.
        self._efficientembedding = []
        self._initial_efficientembedding = []
        self._directives = []
        # Steps for in the architecture.
        if '.txt' in news_path:
            news_path_txt = news_path
        else:
            news_path_txt = self.__database_transformation(news_path)

        p, s, t = self.__reader(news_path_txt)
        self.p = p
        self.s.append(s)
        self.t.append(t)

        _r, r, s, t = self.__temporal_manager(p, s, t)
        self.R.append(_r)
        self.R.append(r)
        self.s.append(s)
        self.t.append(t)
        self._initial_efficientembedding = self._efficientembedding.copy()

        r, s, t = self.__spatial_manager(r, s, t)
        self.R.append(r)
        self.s.append(s)
        self.t.append(t)

        r, s, t = self.__later_correlation_manager(s, t)
        self.R.append(r)
        self.s.append(s)
        self.t.append(t)
        # Tree transformation:
        self.__treefication()

    def __database_transformation(self, path):
        return self._database_transformation(path)

    @staticmethod
    def __reader(path):
        s = []
        p = []
        t = []
        linenumber = 0
        with open(path, 'r', encoding='utf-8') as file:
            for _line in file:
                if _line[0] == '%':
                    _str_t = _line[2:-1].split(', ')
                    t = np.array([float(str_t) for str_t in _str_t])
                else:
                    if _line[0] == '$':
                        p.append(linenumber)
                        line = _line[1:]
                    else:
                        line = _line
                    s.append(line.strip('\n'))
                linenumber += 1
        return p, s, t

    def __specific_language_model(self, s) -> np.array:
        embeddings = self._specific_language_model(s)
        r = np.zeros((len(s), len(s)))
        for ne1, embedding1 in enumerate(embeddings):
            for ne2, embedding2 in enumerate(embeddings):
                value = cosine_similarity(embedding1.reshape(1, -1), embedding2.reshape(1, -1))[0][0]
                r[ne1][ne2] = value
                r[ne2][ne1] = value
        self._efficientembedding = embeddings
        return r

    def __temporal_manager(self, p, s, t) -> tuple:
        r0, r1 = ftdm(p, s, self.__specific_language_model, self.parameters["betta_tdm"])
        return r0, r1, s, t

    def __spatial_manager(self, r, s, t):
        # GPA sub-module:
        rp = np.zeros((len(r), len(r)))
        for nr, row in enumerate(r):
            for nc, element in enumerate(row):
                # ['gpa'][0] -> Variance for Gaussian.
                # ['gpa'][1] -> w for Gaussian.
                gpa = np.exp(-((nr - nc) ** 2) / (2 * self.parameters['gpa'][0])) \
                    if self.parameters['gpa'][0] > 0 else element
                rp[nr][nc] = element + self.parameters['gpa'][1] * (gpa - element)
        # SDM algorithm:
        self._directives = self._spatial_manager(rp)
        # Merge components:
        s2 = []
        t2 = []
        _s = ''
        _t = 0
        for pos, phrase in enumerate(s):
            if pos in self._directives:
                s2.append(_s[2:])
                t2.append(_t)
                _s = ''
                _t = 0
            else:
                _s = f'{_s}. {phrase}'
                _t += t[pos]
        return rp, s2, np.array(t2)

    def __later_correlation_manager(self, s, t):
        r, s, t = self._later_correlation_manager(self.__specific_language_model, s, t)
        return np.array(r), s, np.array(t)

    def __treefication(self):
        initial_s = self.s[0]
        end_s = self.s[-1]
        tinfo = self.t[-1]
        for treeid, payload in enumerate(end_s):
            leafs = []
            cembedding = []
            for leaf_id, initial in enumerate(initial_s):
                if initial in payload:
                    leafs.append((leaf_id, initial))
                    cembedding.append(self._initial_efficientembedding[leaf_id])
            tree = TreeStructure(*tuple(leafs), ID=treeid, embedding=self._efficientembedding[treeid], payload=payload,
                                 time=tinfo[treeid], reference=self.reference, CP=self.__cpcalc(cembedding))
            self.News.append(tree)

    @staticmethod
    def __cpcalc(cembedding):
        r = np.zeros((len(cembedding), len(cembedding)))
        for ne1, emb1 in enumerate(cembedding):
            for ne2, emb2 in enumerate(cembedding):
                value = cosine_similarity(emb1.reshape(1, -1), emb2.reshape(1, -1))[0][0]
                r[ne1][ne2] = value
                r[ne2][ne1] = value
        cp = 0
        for nr, row in enumerate(r):
            for nc, element in enumerate(row):
                if nc > nr:
                    cp += element ** 2
        cp /= len(cembedding) * (len(cembedding) - 1)
        return np.float(2 * cp)

    @staticmethod
    @abstractmethod
    def _spatial_manager(r) -> tuple:
        pass

    @staticmethod
    @abstractmethod
    def _later_correlation_manager(lm, s, t) -> tuple:
        pass

    @staticmethod
    @abstractmethod
    def _specific_language_model(s) -> np.array:
        pass

    def _database_transformation(self, path):
        return path

    def __repr__(self):
        __text = f"NewsSegmentation object: {len(self.News)} news classified."
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

    def plotmtx(self, *args, color='orange', saveas=''):
        if color not in ['orange', 'black']:
            print(f'Warning: Color: {color} not defined. Orange chosen.')
            color = 'orange'
        if len(args) == 0:
            pass
        else:
            for num in args:
                pass
        return 0

    def gui(self):
        pass
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
