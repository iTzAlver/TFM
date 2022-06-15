# -------------------------------------------------------------------#
#                                                                    #
#    Author:    Alberto Palomo Alonso.                               #
#                                                                    #
#    Git user:  https://github.com/iTzAlver                          #
#    Email:     ialver.p@gmail.com                                   #
#                                                                    #
# -------------------------------------------------------------------#
from sklearn.cluster import DBSCAN, SpectralClustering, AgglomerativeClustering, MiniBatchKMeans, MeanShift

import package.newsegmentation as ns


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
class SegmentationDbscan(ns.NewsSegmentation):
    @staticmethod
    def _spatial_manager(r, param):
        return None

    @staticmethod
    def _specific_language_model(s):
        return ns.default_slm(s)

    @staticmethod
    def _later_correlation_manager(lm, s, t, param):
        r = lm(s)
        clustering = DBSCAN(eps=1, min_samples=2).fit(r).labels_
        lbls = [label - min(clustering) for label in clustering]
        _s = ['' for _ in range(max(lbls) + 1)]
        _t = [0 for _ in range(max(lbls) + 1)]
        for index, phrase in enumerate(s):
            _s[lbls[index]] = f'{_s[lbls[index]]}. {phrase}'
            _t[lbls[index]] += t[lbls[index]]
        _s = [__s[2:] if len(__s) > 2 else '__no_payload__' for __s in _s]
        return lm(_s), _s, _t

    @staticmethod
    def _database_transformation(path, op):
        return ns.default_dbt(path, op)


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
class SegmentationSpectral(ns.NewsSegmentation):
    @staticmethod
    def _spatial_manager(r, param):
        return None

    @staticmethod
    def _specific_language_model(s):
        return ns.default_slm(s)

    @staticmethod
    def _later_correlation_manager(lm, s, t, param):
        r = lm(s)
        clustering = SpectralClustering(n_clusters=8, assign_labels='discretize', affinity='precomputed')\
            .fit(r).labels_
        lbls = [label - min(clustering) for label in clustering]
        _s = ['' for _ in range(max(lbls) + 1)]
        _t = [0 for _ in range(max(lbls) + 1)]
        for index, phrase in enumerate(s):
            _s[lbls[index]] = f'{_s[lbls[index]]}. {phrase}'
            _t[lbls[index]] += t[lbls[index]]
        _s = [__s[2:] if len(__s) > 2 else '__no_payload__' for __s in _s]
        return lm(_s), _s, _t

    @staticmethod
    def _database_transformation(path, op):
        return ns.default_dbt(path, op)


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
class SegmentationAgglomerative(ns.NewsSegmentation):
    @staticmethod
    def _spatial_manager(r, param):
        return None

    @staticmethod
    def _specific_language_model(s):
        return ns.default_slm(s)

    @staticmethod
    def _later_correlation_manager(lm, s, t, param):
        r = lm(s)
        clustering = AgglomerativeClustering(n_clusters=6).fit(r).labels_
        lbls = [label - min(clustering) for label in clustering]
        _s = ['' for _ in range(max(lbls) + 1)]
        _t = [0 for _ in range(max(lbls) + 1)]
        for index, phrase in enumerate(s):
            _s[lbls[index]] = f'{_s[lbls[index]]}. {phrase}'
            _t[lbls[index]] += t[lbls[index]]
        _s = [__s[2:] if len(__s) > 2 else '__no_payload__' for __s in _s]
        return lm(_s), _s, _t

    @staticmethod
    def _database_transformation(path, op):
        return ns.default_dbt(path, op)


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
class SegmentationKSM(ns.NewsSegmentation):
    @staticmethod
    def _spatial_manager(r, param):
        return None

    @staticmethod
    def _specific_language_model(s):
        return ns.default_slm(s)

    @staticmethod
    def _later_correlation_manager(lm, s, t, param):
        r = lm(s)
        clustering = MiniBatchKMeans(n_clusters=8, random_state=0, batch_size=6, max_iter=10).fit(r).labels_
        lbls = [label - min(clustering) for label in clustering]
        _s = ['' for _ in range(max(lbls) + 1)]
        _t = [0 for _ in range(max(lbls) + 1)]
        for index, phrase in enumerate(s):
            _s[lbls[index]] = f'{_s[lbls[index]]}. {phrase}'
            _t[lbls[index]] += t[lbls[index]]
        _s = [__s[2:] if len(__s) > 2 else '__no_payload__' for __s in _s]
        return lm(_s), _s, _t

    @staticmethod
    def _database_transformation(path, op):
        return ns.default_dbt(path, op)


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
class SegmentationMS(ns.NewsSegmentation):
    @staticmethod
    def _spatial_manager(r, param):
        return None

    @staticmethod
    def _specific_language_model(s):
        return ns.default_slm(s)

    @staticmethod
    def _later_correlation_manager(lm, s, t, param):
        r = lm(s)
        clustering = MeanShift(bandwidth=1).fit(r).labels_
        lbls = [label - min(clustering) for label in clustering]
        _s = ['' for _ in range(max(lbls) + 1)]
        _t = [0 for _ in range(max(lbls) + 1)]
        for index, phrase in enumerate(s):
            _s[lbls[index]] = f'{_s[lbls[index]]}. {phrase}'
            _t[lbls[index]] += t[lbls[index]]
        _s = [__s[2:] if len(__s) > 2 else '__no_payload__' for __s in _s]
        return lm(_s), _s, _t

    @staticmethod
    def _database_transformation(path, op):
        return ns.default_dbt(path, op)
# -------------------------------------------------------------------#
#           E   N   D          O   F           F   I   L   E         #
# -------------------------------------------------------------------#
