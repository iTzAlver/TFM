# -------------------------------------------------------------------#
#                                                                    #
#    Author:    Alberto Palomo Alonso.                               #
#                                                                    #
#    Git user:  https://github.com/iTzAlver                          #
#    Email:     ialver.p@gmail.com                                   #
#                                                                    #
# -------------------------------------------------------------------#
import os

from sklearn.cluster import DBSCAN, SpectralClustering, AgglomerativeClustering, MiniBatchKMeans, MeanShift

import package.newsegmentation as ns

DATABASE_PATH = r'./db/vtt_files/'
GT_PATH = r'./db/groundtruth/f1/'
PERF_PATH = r'./db/.exported/performance/performance.txt'


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
def save_performance(results, path, append=('', 0)):
    tap = '-------------------------------------------------------------------------------------'
    if not append[0]:
        with open(path, 'w', encoding='utf-8') as file:
            file.writelines(f'Performance results:\n{tap}\n| Case\t| Day\t| Algorithm\t| Precision\t| Recall\t| F1\t| '
                            f'WinDiff\t| PkScore\t|\n{tap}\n')
            for case, listdays in results.items():
                for day, resultsday in enumerate(listdays):
                    for algorithm, result in resultsday.items():
                        file.writelines(f'| {case}\t| {day}\t\t| {algorithm}\t| {round(result["Precision"], 5):.5f}\t|'
                                        f' {round(result["Recall"], 5):.5f}\t| {round(result["F1"], 3):.3f}\t|'
                                        f' {round(result["WD"], 5):.5f}\t|'
                                        f' {round(result["Pk"], 5):.5f}\t|\n')
                    file.writelines('\n')
            file.writelines(f'{tap}')
    else:
        with open(path, 'a', encoding='utf-8') as file:
            file.writelines(f'Performance results:\n{tap}\n| Case\t| Day\t| Algorithm\t| Precision\t| Recall\t| F1\t| '
                            f'WinDiff\t| PkScore\t|\n{tap}\n')
            for algorithm, result in results.items():
                file.writelines(f'| {append[0]}\t| {append[1]}\t\t| '
                                f'{algorithm}\t| {round(result["Precision"], 5):.5f}\t|'
                                f' {round(result["Recall"], 5):.5f}\t| {round(result["F1"], 3):.3f}\t|'
                                f' {round(result["WD"], 5):.5f}\t|'
                                f' {round(result["Pk"], 5):.5f}\t|\n')
            file.writelines('\n')


def get_targets(cases):
    current_dirs = [f'{DATABASE_PATH}{case}/' for case in cases]
    current_targets = []
    for directory in current_dirs:
        listofvtt_ = os.listdir(directory)
        placecam = [int(vtt.split('.')[0]) for vtt in listofvtt_]
        sorted_zip = sorted(list(zip(listofvtt_, placecam)), key=lambda x: x[1])
        listofvtt = [element[0] for element in sorted_zip]
        current_targets.extend([f'{directory}{vtt}' for vtt in listofvtt])
    return current_targets


def get_groundtruth(cases):
    direx = {}
    for case in cases:
        directory = f'{GT_PATH}{case}/'
        listofvtt_ = os.listdir(directory)
        placecam = [int(vtt.split('.')[0]) for vtt in listofvtt_]
        sorted_zip = sorted(list(zip(listofvtt_, placecam)), key=lambda x: x[1])
        listofvtt = [element[0] for element in sorted_zip]
        current_targets = [f'{directory}{vtt}' for vtt in listofvtt]
        list_trees = []
        for current_target in current_targets:
            payload_ = []
            id_ = []
            trees = []
            with open(current_target, 'r', encoding='utf-8') as file:
                for nline, line in enumerate(file):
                    if line[0] == '%':
                        pl = '. '.join(payload_)
                        leafs = [[ids, payload, []] for ids, payload in zip(id_, payload_)]
                        trees.append(ns.TreeStructure(*tuple(leafs), payload=pl, ID=len(trees)))
                        payload_ = []
                        id_ = []
                    else:
                        id_.append(nline)
                        payload_.append(line.strip('\n'))
            list_trees.append(trees)
        direx[case] = list_trees
    return direx


def result_evaluation() -> None:
    cases = ['Julen']
    dict_of_trees = get_groundtruth(cases)
    targets = get_targets(cases)
    results = {}
    mean_results = {'pbmmfbbcm': {'F1': [], 'Precision': [], 'Recall': [], 'WD': [], 'Pk': []},
                    'dbscan': {'F1': [], 'Precision': [], 'Recall': [], 'WD': [], 'Pk': []},
                    'spectral': {'F1': [], 'Precision': [], 'Recall': [], 'WD': [], 'Pk': []},
                    'agglomera': {'F1': [], 'Precision': [], 'Recall': [], 'WD': [], 'Pk': []},
                    'meanshift': {'F1': [], 'Precision': [], 'Recall': [], 'WD': [], 'Pk': []},
                    'kshiftedm': {'F1': [], 'Precision': [], 'Recall': [], 'WD': [], 'Pk': []}}
    for case in cases:
        tree_days = dict_of_trees[case]
        results_ = []
        for nday, target in enumerate(targets):
            results__ = {}
            mynews = ns.Segmentation(target)
            results__['pbmmfbbcm'] = mynews.evaluate(tree_days[nday])
            mynews = SegmentationDbscan(target)
            results__['dbscan'] = mynews.evaluate(tree_days[nday])
            mynews = SegmentationSpectral(target)
            results__['spectral'] = mynews.evaluate(tree_days[nday])
            mynews = SegmentationAgglomerative(target)
            results__['agglomera'] = mynews.evaluate(tree_days[nday])
            mynews = SegmentationMS(target)
            results__['meanshift'] = mynews.evaluate(tree_days[nday])
            mynews = SegmentationKSM(target)
            results__['kshiftedm'] = mynews.evaluate(tree_days[nday])
            print(f'Case {case} day {nday} finished.')
            for algorithm, metrics in results__.items():
                mean_results[algorithm]['F1'].append(metrics['F1'])
                mean_results[algorithm]['Recall'].append(metrics['Recall'])
                mean_results[algorithm]['Precision'].append(metrics['Precision'])
                mean_results[algorithm]['WD'].append(metrics['WD'])
                mean_results[algorithm]['Pk'].append(metrics['Pk'])
            results_.append(results__)
            save_performance(results__, PERF_PATH, append=(case, nday))
        results[case] = results_

    _mr = {'pbmmfbbcm': {'F1': 0, 'Precision': 0, 'Recall': 0, 'WD': 0, 'Pk': 0},
           'dbscan': {'F1': 0, 'Precision': 0, 'Recall': 0, 'WD': 0, 'Pk': 0},
           'spectral': {'F1': 0, 'Precision': 0, 'Recall': 0, 'WD': 0, 'Pk': 0},
           'agglomera': {'F1': 0, 'Precision': 0, 'Recall': 0, 'WD': 0, 'Pk': 0},
           'meanshift': {'F1': 0, 'Precision': 0, 'Recall': 0, 'WD': 0, 'Pk': 0},
           'kshiftedm': {'F1': 0, 'Precision': 0, 'Recall': 0, 'WD': 0, 'Pk': 0}}
    for algorithm, metrics in mean_results.items():
        for metric, value in metrics.items():
            _mr[algorithm][metric] = sum(value) / len(value)
    save_performance(_mr, PERF_PATH, append=('Mean', 0))
    return None


def re2():
    cases = ['Julen']
    dict_of_trees = get_groundtruth(cases)
    targets = get_targets(cases)
    for case in cases:
        tree_days = dict_of_trees[case]
        for nday, target in enumerate(targets):
            if nday in [0, 1, 2, 5, 6, 10]:
                mynews = ns.Segmentation(target)
                print(mynews.evaluate(tree_days[nday], show=True))


def main():
    result_evaluation()


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
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
if __name__ == '__main__':
    main()
# -------------------------------------------------------------------#
#           E   N   D          O   F           F   I   L   E         #
# -------------------------------------------------------------------#
