# -------------------------------------------------------------------#
#                                                                    #
#    Author:    Alberto Palomo Alonso.                               #
#                                                                    #
#    Git user:  https://github.com/iTzAlver                          #
#    Email:     ialver.p@gmail.com                                   #
#                                                                    #
# -------------------------------------------------------------------#
import os
import time

import numpy as np
from sentence_transformers import SentenceTransformer

import package.newsegmentation as ns

DATABASE_PATH = r'./db/vtt_files/'
GT_PATH = r'./db/groundtruth/f1/'
LOG_FILE = r'./db/.exported/performance/opt_log.txt'
CACHE_FILE = r'./experiment.json'


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
def main() -> None:
    parameters = {'tdm': 0.3, 'sdm': 0.19, 'lcm': 0.45}
    sweeps = 6
    resolution = 30
    bw = 0.2
    models = [ns.Segmentation, Segmentation2, Segmentation3]

    validation_path = f'{DATABASE_PATH}Julen/'
    gt_path = f'{GT_PATH}Julen/'
    vg_files = [(f'{validation_path}{item}', f'{gt_path}{item.split(".")[0]}.txt')
                for item in os.listdir(validation_path)]

    _print('Starting optimization process...', Bcolors.OKGREEN)

    for nmodel, Seg in enumerate(models):
        _print(f'Starting with model {nmodel},', Bcolors.OKCYAN)
        temp_init = time.perf_counter()

        this_best_tdm = 1
        this_best_sdm = 1
        this_best_lcm = 0
        tik = time.perf_counter()

        for step in range(sweeps):

            tdm_b = (parameters['tdm'] * (1 - bw), parameters['tdm'] * (1 + bw))
            tdm_b = (tdm_b[0] if tdm_b[0] > 0 else 0, tdm_b[1] if tdm_b[1] < 1 else 1)
            sdm_b = (parameters['sdm'] * (1 - bw), parameters['sdm'] * (1 + bw))
            sdm_b = (sdm_b[0] if sdm_b[0] > 0 else 0, sdm_b[1] if sdm_b[1] < 1 else 1)
            lcm_b = (parameters['lcm'] * (1 - bw), parameters['lcm'] * (1 + bw))
            lcm_b = (lcm_b[0] if lcm_b[0] > 0 else 0, lcm_b[1] if lcm_b[1] < 1 else 1)
            tdm_slices = np.arange(tdm_b[0], tdm_b[1], (tdm_b[1] - tdm_b[0]) / resolution)
            sdm_slices = np.arange(sdm_b[0], sdm_b[1], (sdm_b[1] - sdm_b[0]) / resolution)
            lcm_slices = np.arange(lcm_b[0], lcm_b[1], (lcm_b[1] - lcm_b[0]) / resolution)

            for tdm in tdm_slices:
                results = []
                _print(f'Testing TDM for {tdm} ({time.perf_counter() - tik})', Bcolors.BOLD)
                tik = time.perf_counter()
                for fil in vg_files:
                    validation = fil[0]
                    gt = fil[1]
                    mynews = Seg(validation,
                                 tdm=tdm,
                                 sdm=(parameters['sdm'], 1, parameters['sdm'] * 0.87),
                                 lcm=(parameters['lcm'],),
                                 cache_file=CACHE_FILE)
                    results.append(mynews.evaluate(ns.gtreader(gt))['WD'])
                this = sum(results) / len(results)
                if this < this_best_tdm:
                    this_best_tdm = this
                    parameters['tdm'] = tdm
                    _print(f'Best result found for tdm: ({tdm}, WD:{this})', Bcolors.OKBLUE)

            for sdm in sdm_slices:
                results = []
                _print(f'Testing SDM for {sdm} ({time.perf_counter() - tik})', Bcolors.BOLD)
                tik = time.perf_counter()
                for fil in vg_files:
                    validation = fil[0]
                    gt = fil[1]
                    mynews = Seg(validation,
                                 tdm=parameters['tdm'],
                                 sdm=(sdm, 1, sdm * 0.87),
                                 lcm=(parameters['lcm'],),
                                 cache_file=CACHE_FILE)
                    results.append(mynews.evaluate(ns.gtreader(gt))['WD'])
                this = sum(results) / len(results)
                if this < this_best_sdm:
                    this_best_sdm = this
                    parameters['sdm'] = sdm
                    _print(f'Best result found for sdm: ({sdm}, WD:{this})', Bcolors.OKBLUE)

            for lcm in lcm_slices:
                results = []
                _print(f'Testing LCM for {lcm} ({time.perf_counter() - tik})', Bcolors.BOLD)
                tik = time.perf_counter()
                for fil in vg_files:
                    validation = fil[0]
                    gt = fil[1]
                    mynews = Seg(validation,
                                 tdm=parameters['tdm'],
                                 sdm=(parameters['sdm'], 1, parameters['sdm'] * 0.87),
                                 lcm=(lcm,),
                                 cache_file=CACHE_FILE)
                    results.append(mynews.evaluate(ns.gtreader(gt))['F1'])
                this = sum(results) / len(results)
                if this > this_best_lcm:
                    this_best_lcm = this
                    parameters['lcm'] = lcm
                    _print(f'Best result found for lcm: ({lcm}, F1:{this})', Bcolors.OKBLUE)

            bw *= 0.8

        _print(f'Optimization finished in {time.perf_counter() - temp_init} seconds for model {nmodel}:',
               Bcolors.OKGREEN)
        _print(f'Parameters selected:\n{parameters}', Bcolors.OKGREEN)


def _print(text, col=''):
    with open(LOG_FILE, 'a', encoding='utf-8') as file:
        file.writelines(text)
        file.writelines('\n')
    print(f'{col}{text}{Bcolors.ENDC}')


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
model2 = SentenceTransformer('hackathon-pln-es/paraphrase-spanish-distilroberta')
model3 = SentenceTransformer('jfarray/Model_dccuchile_bert-base-spanish-wwm-uncased_100_Epochs')


class Segmentation2(ns.NewsSegmentation):
    @staticmethod
    def _spatial_manager(r, param):
        return ns.default_sdm(r, param)

    @staticmethod
    def _specific_language_model(s):
        return model2.encode(s)

    @staticmethod
    def _later_correlation_manager(lm, s, t, param):
        return ns.default_lcm(lm, s, t, param)

    @staticmethod
    def _database_transformation(path, op):
        return ns.default_dbt(path, op)


class Segmentation3(ns.NewsSegmentation):
    @staticmethod
    def _spatial_manager(r, param):
        return ns.default_sdm(r, param)

    @staticmethod
    def _specific_language_model(s):
        return model3.encode(s)

    @staticmethod
    def _later_correlation_manager(lm, s, t, param):
        return ns.default_lcm(lm, s, t, param)

    @staticmethod
    def _database_transformation(path, op):
        return ns.default_dbt(path, op)


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
if __name__ == '__main__':
    main()
# -------------------------------------------------------------------#
#           E   N   D          O   F           F   I   L   E         #
# -------------------------------------------------------------------#
