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

import matplotlib.pyplot as plt
import numpy as np

import package.newsegmentation as ns

DATABASE_PATH = r'./db/vtt_files/'
GT_PATH = r'./db/groundtruth/f1/'
LOG_FILE = r'./db/.exported/performance/umb_log.txt'
VAR_FILE = r'db/.exported/performance/umb_var.txt'
IMG_PATH = r'./db/.exported/performance/'
CACHE_DIR = r'./cache/'


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
def main() -> None:
    parameters = {'tdm': 0.24512, 'sdm': 0.17733333333333345, 'lcm': 0.613744}
    cases = ['Julen', 'NotreDame', 'Estrasburgo', 'Singapur']
    sliced = 0.01
    sdi_ranges = np.arange(0, 1 + sliced, sliced)
    _print(f'Ranges: {sdi_ranges}', Bcolors.HEADER)

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
        for tdm in sdi_ranges:
            results_ = []
            for fil in vg_files[case]:
                validation = fil[0]
                gt = fil[1]
                mynews = ns.Segmentation(validation,
                                         tdm=tdm,
                                         sdm=(parameters['sdm'], 1, parameters['sdm'] * 0.87),
                                         lcm=(parameters['lcm'],),
                                         cache_file=cache_file)
                results_.append(mynews.evaluate(ns.gtreader(gt)))
            results__.append(results_)
        results[case].append(results__)

        _print(f'TDM finished computing.', Bcolors.OKBLUE)
        results__ = []
        for sdm in sdi_ranges:
            results_ = []
            for fil in vg_files[case]:
                validation = fil[0]
                gt = fil[1]
                mynews = ns.Segmentation(validation,
                                         tdm=parameters['tdm'],
                                         sdm=(sdm, 1, sdm * 0.87),
                                         lcm=(parameters['lcm'],),
                                         cache_file=cache_file)
                results_.append(mynews.evaluate(ns.gtreader(gt)))
            results__.append(results_)
        results[case].append(results__)

        _print(f'SDM finished computing.', Bcolors.OKBLUE)
        results__ = []
        for lcm in sdi_ranges:
            results_ = []
            for fil in vg_files[case]:
                validation = fil[0]
                gt = fil[1]
                mynews = ns.Segmentation(validation,
                                         tdm=parameters['tdm'],
                                         sdm=(parameters['sdm'], 1, parameters['sdm'] * 0.87),
                                         lcm=(lcm,),
                                         cache_file=cache_file)
                results_.append(mynews.evaluate(ns.gtreader(gt)))
            results__.append(results_)
        results[case].append(results__)
        _print(f'LCM finished computing.', Bcolors.OKBLUE)
    _print(f'Comparison finished in {time.perf_counter() - temp_init} seconds.', Bcolors.OKGREEN)
    # -------------------------------------------------------------------#
    #   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
    #   G   R   A   P   H   I   C   S       W   D       F   1            #
    #   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
    # -------------------------------------------------------------------#
    _sdm = []
    _tdm = []
    _lcm = []
    for case, thes in results.items():
        tdm = thes[0]
        sdm = thes[1]
        lcm = thes[2]

        wd_tdm = []
        pk_tdm = []
        for slices in tdm:
            wd_tdm.append(sum([element['WD'] for element in slices]) / len(slices))
            pk_tdm.append(sum([element['Pk'] for element in slices]) / len(slices))
        _tdm.append((wd_tdm, pk_tdm))

        wd_sdm = []
        pk_sdm = []
        for slices in sdm:
            wd_sdm.append(sum([element['WD'] for element in slices]) / len(slices))
            pk_sdm.append(sum([element['Pk'] for element in slices]) / len(slices))
        _sdm.append((wd_sdm, pk_sdm))

        r_lcm = []
        p_lcm = []
        f1_lcm = []
        for slices in lcm:
            p_lcm.append(sum([element['Precision'] for element in slices]) / len(slices))
            r_lcm.append(sum([element['Recall'] for element in slices]) / len(slices))
            f1_lcm.append(sum([element['F1'] for element in slices]) / len(slices))
        _lcm.append((p_lcm, r_lcm, f1_lcm))

    with open(VAR_FILE, 'w', encoding='utf-8') as file:
        for ncase, case in enumerate(cases):
            file.write(f'{case}:\n')
            file.write(f'TDM WD: {_tdm[ncase][0]}\n')
            file.write(f'TDM PK: {_tdm[ncase][1]}\n')
            file.write(f'SDM WD: {_sdm[ncase][0]}\n')
            file.write(f'SDM PK: {_sdm[ncase][1]}\n')
            file.write(f'LCM PR: {_lcm[ncase][0]}\n')
            file.write(f'LCM RC: {_lcm[ncase][1]}\n')
            file.write(f'LCM F1: {_lcm[ncase][2]}\n')
    _print(f'Written results in {VAR_FILE}.', Bcolors.WARNING)

    plt.figure()
    sdi_t = np.zeros(len(sdi_ranges))
    for case in _tdm:
        sdi_t += case[0]
        plt.plot(sdi_ranges, case[0], '--k', lw=0.2)
    sdi_t /= len(cases)
    plt.plot(sdi_ranges, sdi_t, 'k', lw=1)
    plt.title('WindowDiff score for each database in TDM.')
    plt.xlabel('Betta')
    plt.ylabel('WindownDiff')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.grid()
    plt.savefig(f'{IMG_PATH}tdm_wd.eps', format='eps')

    plt.figure()
    sdi_t = np.zeros(len(sdi_ranges))
    for case in _tdm:
        sdi_t += case[1]
        plt.plot(sdi_ranges, case[1], '--k', lw=0.2)
    sdi_t /= len(cases)
    plt.plot(sdi_ranges, sdi_t, 'k', lw=1)
    plt.title('Pk score for each database in TDM.')
    plt.xlabel('Betta')
    plt.ylabel('Pk score')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.grid()
    plt.savefig(f'{IMG_PATH}tdm_pk.eps', format='eps')

    plt.figure()
    sdi_t = np.zeros(len(sdi_ranges))
    for case in _sdm:
        sdi_t += case[0]
        plt.plot(sdi_ranges, case[0], '--k', lw=0.2)
    sdi_t /= len(cases)
    plt.plot(sdi_ranges, sdi_t, 'k', lw=1)
    plt.title('WindowDiff score for each database in SDM.')
    plt.xlabel('PBMM threshold')
    plt.ylabel('WindownDiff')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.grid()
    plt.savefig(f'{IMG_PATH}sdm_wd.eps', format='eps')

    plt.figure()
    sdi_t = np.zeros(len(sdi_ranges))
    for case in _sdm:
        sdi_t += case[1]
        plt.plot(sdi_ranges, case[1], '--k', lw=0.2)
    sdi_t /= len(cases)
    plt.plot(sdi_ranges, sdi_t, 'k', lw=1)
    plt.title('Pk score for each database in SDM.')
    plt.xlabel('PBMM threshold')
    plt.ylabel('Pk score')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.grid()
    plt.savefig(f'{IMG_PATH}sdm_pk.eps', format='eps')

    plt.figure()
    sdi_t = np.zeros(len(sdi_ranges))
    for case in _lcm:
        sdi_t += case[0]
        plt.plot(sdi_ranges, case[0], '--k', lw=0.2)
    sdi_t /= len(cases)
    plt.plot(sdi_ranges, sdi_t, 'k', lw=1)
    plt.title('Precision for each database in LCM.')
    plt.xlabel('FB-BCM threshold')
    plt.ylabel('Precision')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.grid()
    plt.savefig(f'{IMG_PATH}lcm_p.eps', format='eps')

    plt.figure()
    sdi_t = np.zeros(len(sdi_ranges))
    for case in _lcm:
        sdi_t += case[1]
        plt.plot(sdi_ranges, case[1], '--k', lw=0.2)
    sdi_t /= len(cases)
    plt.plot(sdi_ranges, sdi_t, 'k', lw=1)
    plt.title('Recall for each database in LCM.')
    plt.xlabel('FB-BCM threshold')
    plt.ylabel('Recall')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.grid()
    plt.savefig(f'{IMG_PATH}lcm_r.eps', format='eps')

    plt.figure()
    sdi_t = np.zeros(len(sdi_ranges))
    for case in _lcm:
        sdi_t += case[2]
        plt.plot(sdi_ranges, case[2], '--k', lw=0.2)
    sdi_t /= len(cases)
    plt.plot(sdi_ranges, sdi_t, 'k', lw=1)
    plt.title('F1 score for each database in LCM.')
    plt.xlabel('FB-BCM threshold')
    plt.ylabel('F1 score')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.grid()
    plt.savefig(f'{IMG_PATH}lcm_f1.eps', format='eps')


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
