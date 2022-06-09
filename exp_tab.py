# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
import os
import time

import numpy as np

import package.newsegmentation as ns

DATABASE_PATH = r'./db/vtt_files/'
GT_PATH = r'./db/groundtruth/f1/'
LOG_FILE = r'./db/.exported/performance/tab_log.txt'
VAR_FILE = r'db/.exported/performance/tab_var.txt'
IMG_PATH = r'./db/.exported/performance/'
CACHE_DIR = r'./cache/'


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
def main() -> None:
    parameterx = [{'tdm': 0, 'sdm': 1, 'lcm': 1},
                  {'tdm': 0.24512, 'sdm': 1, 'lcm': 1},
                  {'tdm': 0, 'sdm': 0.17733333333333345, 'lcm': 1},
                  {'tdm': 0.24512, 'sdm': 0.17733333333333345, 'lcm': 1},
                  {'tdm': 0, 'sdm': 1, 'lcm': 0.613744},
                  {'tdm': 0.24512, 'sdm': 1, 'lcm': 0.613744},
                  {'tdm': 0, 'sdm': 0.17733333333333345, 'lcm': 0.613744},
                  {'tdm': 0.24512, 'sdm': 0.17733333333333345, 'lcm': 0.613744}]
    cases = ['Julen', 'NotreDame', 'Singapur', 'Estrasburgo']
    vg_files = {}

    for case in cases:
        validation_path = f'{DATABASE_PATH}{case}/'
        gt_path = f'{GT_PATH}{case}/'
        vg_files[case] = [(f'{validation_path}{item}', f'{gt_path}{item.split(".")[0]}.txt')
                          for item in os.listdir(validation_path)]

    _print('Starting comparison process...', Bcolors.OKGREEN)
    temp_init = time.perf_counter()
    results = {}

    for case in cases:
        _print(f'Starting case {case}.', Bcolors.OKCYAN)
        results[case] = []
        cache_file = f'{CACHE_DIR}{case}.json'

        results__ = []
        for parameters in parameterx:
            results_ = []
            for fil in vg_files[case]:
                validation = fil[0]
                gt = fil[1]
                mynews = ns.Segmentation(validation,
                                         tdm=parameters['tdm'],
                                         sdm=(parameters['sdm'], 1, parameters['sdm'] * 0.87),
                                         lcm=(parameters['lcm'],),
                                         cache_file=cache_file)
                results_.append(mynews.evaluate(ns.gtreader(gt)))
            results__.append(results_)
        results[case] = results__
    _print(f'Comparison finished in {time.perf_counter() - temp_init} seconds.', Bcolors.OKGREEN)
    # -------------------------------------------------------------------#
    #   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
    #   G   R   A   P   H   I   C   S       W   D       F   1            #
    #   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
    # -------------------------------------------------------------------#
    res = []
    for case, resx in results.items():
        wd = []
        pk = []
        f1 = []
        pr = []
        re = []

        for dblaunch in resx:
            wd.append(round(sum([day['WD'] for day in dblaunch]) / len(dblaunch), 3))
            pk.append(round(sum([day['Pk'] for day in dblaunch]) / len(dblaunch), 3))
            f1.append(round(sum([day['F1'] for day in dblaunch]) / len(dblaunch), 3))
            re.append(round(sum([day['Recall'] for day in dblaunch]) / len(dblaunch), 3))
            pr.append(round(sum([day['Precision'] for day in dblaunch]) / len(dblaunch), 3))

        res.append((pr, re, f1, wd))

    res = np.array(res)
    with open(VAR_FILE, 'w', encoding='utf-8') as file:
        for npc, pcomb in enumerate(parameterx):
            file.write(f'Combination: {npc}\n')
            for ncase, case in enumerate(cases):
                file.write(f'{case}:\n')
                aka = str(res[ncase, :, npc]).replace(' ', ' & ').replace('[', '').replace(']', '')
                file.write(f'{aka}\n')
    _print(f'Written results in {VAR_FILE}.', Bcolors.WARNING)


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
def _print(text, col=''):
    with open(LOG_FILE, 'a', encoding='utf-8') as file:
        file.writelines(text)
        file.writelines('\n')
    print(f'{col}{text}{Bcolors.ENDC}')


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
