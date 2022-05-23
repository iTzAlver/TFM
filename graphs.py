# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
import os
import time

import numpy as np
from sentence_transformers import SentenceTransformer

import package.newsegmentation as ns

model2 = SentenceTransformer('hackathon-pln-es/paraphrase-spanish-distilroberta')
model3 = SentenceTransformer('jfarray/Model_dccuchile_bert-base-spanish-wwm-uncased_100_Epochs')
DATABASE_PATH = r'./db/vtt_files/'
GT_PATH = r'./db/groundtruth/f1/'
RES_PATH = r'./db/.exported/performance/results.txt'
NP_PATH = r'./db/.exported/performance/'
# -----------------------------------------------------------


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


def optimization(cases) -> None:
    targets = {}
    for case in cases:
        targets[case] = get_targets([case])
    references = get_groundtruth(cases)

    parameters = {'tdm': 0.3, 'sdm': 0.18, 'lcm': 0.4}
    swap = 0.2
    affinity = 0.01
    reslist = []
    parlist = [parameters]

    optimize = ['WD', 'WD', 'F1']
    paropt = ['tdm', 'sdm', 'lcm']

    _print(f'{Bcolors.OKGREEN}Optimitation initialized...{Bcolors.ENDC}')
    init_opt = time.perf_counter()
    for _ in range(24):
        # For each parameter:
        for step, ppopt in enumerate(paropt):
            # Compute all values for this parameter:
            initial = parameters[paropt[step]] - swap / 2
            ending = parameters[paropt[step]] + swap / 2
            initial = initial if initial > 0 else 0
            ending = ending if ending < 1 else 1
            param = np.arange(initial, ending, affinity)

            bres = 0
            bpar = parameters[ppopt]
            # For each parameter:
            _print(f'{Bcolors.WARNING}Launching parameter: {ppopt}.{Bcolors.ENDC}')
            for par in param:
                parameters[paropt[step]] = par
                _res = []

                # Mean score batched:
                _print(f'Launching optimization for parameter {paropt[step]}:{par}:')
                ini_timer = time.perf_counter()
                for case, _target in targets.items():
                    for nday, target in enumerate(_target):
                        myres = ns.Segmentation(target,
                                                tdm=parameters['tdm'],
                                                sdm=(parameters['sdm'], 1, parameters['sdm'] * 0.87),
                                                lcm=(parameters['lcm'],))
                        myref = references[case][nday]
                        results = myres.evaluate(myref)
                        _res.append(results[optimize[step]])

                result = sum(_res) / len(_res)
                if (result > bres and optimize[step] == 'F1') or (result < bres and optimize[step] == 'WD'):
                    bres = result
                    bpar = par
                    _print(f'{Bcolors.OKCYAN}Found best parameter: {bpar} for {paropt[step]}: {bres} '
                           f'is the best {optimize[step]}.{Bcolors.ENDC}')

                _print(f'Time ellapsed: {time.perf_counter() - ini_timer} seconds.')
            parameters[paropt[step]] = bpar
            parlist.append(parameters)
            reslist.append((bres, optimize[step]))
        swap = swap * 0.8
    ellapsed_time_optimization = time.perf_counter() - init_opt
    _print(f'Total ellapsed time: {ellapsed_time_optimization / 100} seconds per loop: {100} loops done.')
    _print(parameters)
    return


def threshold_evaluation(cases, **parameters) -> None:
    targets = {}
    for case in cases:
        targets[case] = get_targets([case])
    references = get_groundtruth(cases)
    parameters = {'tdm': parameters['tdm'], 'sdm': parameters['sdm'], 'lcm': parameters['lcm']}
    _print(f'{Bcolors.OKGREEN}Threshold evaluation started...{Bcolors.ENDC}')
    init_opt = time.perf_counter()
    slices = 0.02
    thsl = np.arange(0, 1 + slices, slices)

    _res_tdm = []
    _res_sdm = []
    _res_lcm = []
    _res_model0 = []
    _res_model1 = []
    _res_model2 = []

    for case, _target in targets.items():
        for value_tdm in thsl:
            _m = []
            for nday, target in enumerate(_target):
                myres = ns.Segmentation(target,
                                        tdm=value_tdm,
                                        sdm=(parameters['sdm'], 1, parameters['sdm'] * 0.87),
                                        lcm=(parameters['lcm'],))
                myref = references[case][nday]
                results = myres.evaluate(myref)
                _m.append(results['WD'])
            _res_tdm.append(sum(_m) / len(_m))

    tdm_np = np.array(_res_tdm)
    np.save(f'{NP_PATH}/tdm.npy', tdm_np)
    _print('tdm is OK...')

    for case, _target in targets.items():
        for value_sdm in thsl:
            _m = []
            for nday, target in enumerate(_target):
                myres = ns.Segmentation(target,
                                        tdm=parameters['tdm'],
                                        sdm=(value_sdm, 1, value_sdm * 0.87),
                                        lcm=(parameters['lcm'],))
                myref = references[case][nday]
                results = myres.evaluate(myref)
                _m.append(results['WD'])
            _res_sdm.append(sum(_m) / len(_m))

    sdm_np = np.array(_res_sdm)
    np.save(f'{NP_PATH}/sdm.npy', sdm_np)
    _print('sdm is OK...')

    for case, _target in targets.items():
        for value_lcm in thsl:
            _m = []
            for nday, target in enumerate(_target):
                myres = ns.Segmentation(target,
                                        tdm=parameters['tdm'],
                                        sdm=(parameters['sdm'], 1, parameters['sdm'] * 0.87),
                                        lcm=(value_lcm,))
                myref = references[case][nday]
                results = myres.evaluate(myref)
                _m.append(results['F1'])
            _res_lcm.append(sum(_m) / len(_m))

    lcm_np = np.array(_res_lcm)
    np.save(f'{NP_PATH}/lcm.npy', lcm_np)
    _print('lcm is OK...')

    for case, _target in targets.items():
        __res_model0 = []
        for nday, target in enumerate(_target):
            myres = ns.Segmentation(target,
                                    tdm=parameters['tdm'],
                                    sdm=(parameters['sdm'], 1, parameters['sdm'] * 0.87),
                                    lcm=(parameters['lcm'],))
            myref = references[case][nday]
            results = myres.evaluate(myref)
            _results = []
            for key, item in results.items():
                _results.append(item)
            __res_model0.append(results)
        _res_model0.append(__res_model0)

    md0_np = np.array(_res_model0)
    np.save(f'{NP_PATH}/md0.npy', md0_np)
    _print('mod0 is OK...')

    # parameters = {} Perfect parameters.
    for case, _target in targets.items():
        __res_model1 = []
        for nday, target in enumerate(_target):
            myres = Segmentation2(target,
                                  tdm=parameters['tdm'],
                                  sdm=(parameters['sdm'], 1, parameters['sdm'] * 0.87),
                                  lcm=(parameters['lcm'],))
            myref = references[case][nday]
            results = myres.evaluate(myref)
            _results = []
            for key, item in results.items():
                _results.append(item)
            __res_model1.append(_results)
        _res_model1.append(__res_model1)

    md1_np = np.array(_res_model1)
    np.save(f'{NP_PATH}/md1.npy', md1_np)
    _print('mod1 is OK...')

    # parameters = {} Perfect parameters.
    for case, _target in targets.items():
        __res_model2 = []
        for nday, target in enumerate(_target):
            myres = Segmentation3(target,
                                  tdm=parameters['tdm'],
                                  sdm=(parameters['sdm'], 1, parameters['sdm'] * 0.87),
                                  lcm=(parameters['lcm'],))
            myref = references[case][nday]
            results = myres.evaluate(myref)
            _results = []
            for key, item in results.items():
                _results.append(item)
            __res_model2.append(_results)
        _res_model2.append(__res_model2)
    _print('mod2 is OK...')

    md2_np = np.array(_res_model2)
    np.save(f'{NP_PATH}/md2.npy', md2_np)
    _print(f'Total ellapsed time: {time.perf_counter() - init_opt} seconds.')











def _print(text):
    with open(RES_PATH, 'a', encoding='utf-8') as file:
        file.writelines(f'{text}\n')
    print(text)


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


def main():
    cases = ['Julen']
    # optimization(cases)
    threshold_evaluation(cases, tdm=0.3, sdm=0.18, lcm=0.45)


# -----------------------------------------------------------
# Main:
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


if __name__ == '__main__':
    main()

# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
