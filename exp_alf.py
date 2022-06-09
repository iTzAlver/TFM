# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
import os

import package.myutils as mu
import package.newsegmentation as ns
from exp_alg import SegmentationMS, SegmentationKSM, SegmentationSpectral, SegmentationDbscan, SegmentationAgglomerative

BASE_TEST = r'./db/vtt_files/'
BASE_GT = r'./db/groundtruth/f1/'


# -----------------------------------------------------------
def main() -> None:
    ltr = mu.LogTracker(r'./db/.exported/performance/results_algorithms.txt')
    ltr.print('Algorithm evaluation launched', 'b')
    cases = ['Julen', 'NotreDame', 'Singapur', 'Estrasburgo']
    algorithms = [ns.Segmentation, SegmentationDbscan, SegmentationKSM, SegmentationMS, SegmentationAgglomerative,
                  SegmentationSpectral]

    for case in cases:
        ltr.print('\n')
        ltr.print(f'Starting testing for case {case}', 'b')
        for algorithm in algorithms:
            ltr.print(f'Starting algorithm: {algorithm}', 'c')

            tstfiles = [f'{BASE_TEST}{case}/{xcase}' for xcase in os.listdir(f'{BASE_TEST}{case}/')]
            gtfiles = [f'{BASE_GT}{case}/{xcase}' for xcase in os.listdir(f'{BASE_GT}{case}/')]
            files = zip(tstfiles, gtfiles)

            alg_p = 0
            alg_r = 0
            alg_f1 = 0
            alg_wd = 0
            alg_pk = 0
            for tst, gt in files:
                results_day = algorithm(tst).evaluate(gt)
                alg_p += results_day['Precision']
                alg_r += results_day['Recall']
                alg_f1 += results_day['F1']
                alg_wd += results_day['WD']
                alg_pk += results_day['Pk']
            alg_p /= len(tstfiles)
            alg_r /= len(tstfiles)
            alg_f1 /= len(tstfiles)
            alg_wd /= len(tstfiles)
            alg_pk /= len(tstfiles)

            ltr.print(f'Precision: {round(alg_p, 2)}')
            ltr.print(f'Recall: {round(alg_r, 2)}')
            ltr.print(f'F1: {round(alg_f1, 2)}')
            ltr.print(f'WD: {round(alg_wd, 2)}')
            ltr.print(f'Pk: {round(alg_pk, 2)}')
            ltr.print('\n')


# -----------------------------------------------------------
# Main:
if __name__ == '__main__':
    main()

# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
