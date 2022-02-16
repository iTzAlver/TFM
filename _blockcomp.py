import re
from statistics import mean

import matplotlib.pyplot as matplot
import numpy as np
import spacy
from scipy.spatial.distance import hamming

import _errorclc as ec

COMPUTE_FLAG_PATH = r'.\.multimedia\cflag'
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @fill_diagonalOne()
#
#   This function writes ones in the diagonal.
#
#       @inputs:
#           allMatchOfPiece_Original:
#           Matrix NxN to write ones.
#
#       @outputs:
#           Matrix with ones in the diagonal.
# - - - - - - - - - - - - - - - - - - - - - - - - #


def fill_diagonalOne(allMatchOfPiece_Original):
    xInd = 0
    yInd = 0
    for itetDiagX in range(len(allMatchOfPiece_Original)):
        allMatchOfPiece_Original[xInd][yInd] = 1
        xInd = xInd + 1
        yInd = yInd + 1
    return allMatchOfPiece_Original
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @Hamming_distance()
#
#   This function calculates the Hamming
#   distance. Ahmad method.
#
#       @inputs:
#           R:
#               Original stream ready to
#               be compared.
#           case:
#               String name of the case.
#               (Ground truth)
#
#       @output:
#           Average distance in the day.
# - - - - - - - - - - - - - - - - - - - - - - - - #


def Hamming_distance(R, case, day):
    y = 0
    itmx_ = 1
    for itmx_ in range(len(R)):
        strr = str(day + 1)
        data_array = np.loadtxt("./data/" + case + "/day_" + strr + ".txt")

        if len(R[itmx_]) != 0:
            x = hamming(data_array[itmx_], R[itmx_]) * len(data_array[itmx_])
            y = y + x

        else:
            continue
    average = y / len(R[itmx_])
    return average
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @compare_blocks_ahm()
#
#   This function gets the autocorrelation MTX.
#   Ahmad method.
#
#       @inputs:
#           R:
#               Original stream ready to
#               be compared.
#           case:
#               String name of the case.
#               (Ground truth)
#
#       @output:
#           Autocorrelation matrix.
# - - - - - - - - - - - - - - - - - - - - - - - - #


def compare_blocks_ahm(word_list, word_type, news_name):
    matchOfPiece = []
    listOfMatchOfPiece = []
    resultOfAllDays = []
    for itemNoP in range(0, 2):
        print()
        for itemNoN in range(0, 5):

            for item in range(0, len(word_list)):

                SlicesOfDay = word_list[item]
                indexOfType = word_type[item]

                aggreg_all_number_match_word = []
                secondOne = []
                allMatchOfPiece_Original = []
                # allMatchOfPiece_oneInMiddle = []
                allMatchOfPiece_Original_Back = []
                allMatchOfPiece_Concated = []
                allMatchOfPiece_One_dir = []
                listOfMatchOfPiece.clear()
                full_percentOfMatch = []
                tempOfMatch_listZeroOneBack = []
                averageAllDays = 0

                # comparing between blocks of same day
                for itm_1 in range(0, len(SlicesOfDay)):

                    wordOfMatch = []
                    typeOfWord = []
                    count_common = []
                    matchOfPiece.clear()

                    tempOfMatch_listZeroOne = []
                    listOFType = indexOfType[itm_1]

                    for itm_2 in range(0, len(SlicesOfDay)):

                        wordOfMatch.clear()
                        typeOfWord.clear()
                        matchOfPiece.clear()

                        list1 = SlicesOfDay[itm_1]
                        list2 = SlicesOfDay[itm_2]

                        list1 = list1.split(' ')
                        list2 = list2.split(' ')

                        list1 = list(filter(None, list1))
                        list2 = list(filter(None, list2))

                        wordOfMatch.clear()
                        typeOfWord.clear()
                        count_PROPN = 0
                        count_NOUN = 0

                        for listX in range(len(list1)):

                            for listY in range(len(list2)):
                                resultOfTwoWords = re.search(list1[listX], list2[listY])
                                if resultOfTwoWords is not None:
                                    # get the index of this word and find its type from the same index
                                    wordOfMatch.append(list1[listX])
                                    typeOfWord.append(listOFType[listX])

                        count_PROPN = typeOfWord.count('PROPN')
                        count_NOUN = typeOfWord.count('NOUN')

                        if count_PROPN > itemNoP or count_NOUN > itemNoN:

                            tempOfMatch_listZeroOne.append(1)
                            matchOfPiece.append(itm_1)
                            matchOfPiece.append(itm_2)
                            temp = matchOfPiece[:]
                            listOfMatchOfPiece.append(temp)
                        else:
                            tempOfMatch_listZeroOne.append(0)

                    allMatchOfPiece_Original.append(tempOfMatch_listZeroOne)
                    #print(tempOfMatch_listZeroOne)

                allMatchOfPiece_oneInMiddle = allMatchOfPiece_Original[:]

                ###[Original]###########################################################################

                resultOfAllDays.append(Hamming_distance(allMatchOfPiece_Original, news_name, item))
                if not np.allclose(allMatchOfPiece_Original, np.transpose(allMatchOfPiece_Original)):
                    print('Item:', item, 'is not symethric.')

            averageOfCase = mean(resultOfAllDays)
            print(averageOfCase)
            ##############################################################################
    return resultOfAllDays
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################


def print_graph(values, block_number, threshold, day, debug=False):
    matplot.figure()
    matplot.rcParams["figure.figsize"] = [7.50, 4]
    xaxis = list(range(len(values)))
    yaxis = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    matplot.stem(values, label='Correlation')
    matplot.plot([threshold]*len(values), alpha=0.3, label='Threshold', color='red', linestyle='dashed')
    matplot.xlabel('Block number')
    matplot.ylabel('Correlation')
    matplot.xticks(xaxis)
    matplot.yticks(yaxis)
    matplot.legend()
    matplot.grid()
    matplot.title('Correlation block number ' + str(block_number) + '.')
    _saveas = r'.\.multimedia\graph\Day' + str(day) + r'\\' + str(block_number) + '.png'
    matplot.savefig(_saveas)
    matplot.close()
    if debug:
        matplot.show()
    return


def use_method(word_list, day, threshold=0.5, nlp=spacy.load('es_core_news_lg'), printed=0):
    nel = len(word_list)
    r = []
    for item1 in range(nel):
        _auxr = []
        values = []
        for item2 in range(nel):
            stc1 = word_list[item1]
            stc2 = word_list[item2]
            value = 0
            if stc1 != '' and stc2 != '':
                value = nlp(stc1).similarity(nlp(stc2))
                if value >= threshold:
                    _auxr.append(1)
                else:
                    _auxr.append(0)
            else:
                _auxr.append(0)
            values.append(value)
        r.append(_auxr)
        if printed == 1:
            print_graph(values, item1, threshold, day)
    return fill_diagonalOne(r)


def sym_correction(r_in, politics=1):
    """Symmetry correction
    in the matrix."""
    r = r_in
    for item1 in range(len(r)):
        for item2 in range(len(r)):
            if r[item1][item2] == politics and item1 != item2:
                r[item2][item1] = r[item1][item2]
    return r


def create_n_pn(word_list, word_type_original, n_pn=2, n_n=0):
    """Method based on number
    of nouns and proper nouns."""

    """Fist stage: Remove 'PUNCT' and 'SPACE' in the word type list."""
    word_type = []
    for i in range(len(word_type_original)):
        word_type_aux = []
        for j in range(len(word_type_original[i])):
            if word_type_original[i][j] != "PUNCT" and word_type_original[i][j] != "SPACE":
                word_type_aux.append(word_type_original[i][j])
        word_type.append(word_type_aux)
    """Second stage: n_pn method."""
    r = []
    for item1 in range(len(word_type)):
        _efc_row = []
        word_row = word_list[item1]
        word_row.replace('.', '')
        word_row.replace(',', '')
        word_row.replace('¿', '')
        word_row.replace('?', '')
        word_row.replace(';', '')
        word_row.replace(':', '')

        for item2 in range(len(word_type)):
            word_col = word_list[item2]
            word_col = word_col.split(' ')
            word_col = list(filter(('').__ne__, word_col))
            number_nouns = 0
            number_pronouns = 0
            for idx in range(len(word_type[item2])):
                if word_type[item2][idx] == 'PROPN':
                    if re.search(word_col[idx], word_row):
                        number_pronouns = number_pronouns + 1
                else:
                    if re.search(word_col[idx], word_row):
                        number_nouns = number_nouns + 1
            if number_nouns >= n_n and number_pronouns >= n_pn:
                _efc_row.append(1)
            else:
                _efc_row.append(0)
        r.append(_efc_row)
    return fill_diagonalOne(r)


def get_matrix(word_list, word_type, news_name, day, mode='npnn', threshold=0.5, pronouns=2, nouns=0, nlp=spacy.load('es_core_news_lg')):
    """Creates the autocorrelation
    matrix depending the mode."""
    GT = []
    if mode == 'npnn':
        R = create_n_pn(word_list[day], word_type[day], n_pn=pronouns, n_n=nouns)
    elif mode == 'use':
        ffile = open(COMPUTE_FLAG_PATH)
        R = use_method(word_list[day], day, threshold=threshold, nlp=nlp, printed=int(ffile.readline()))
    else:
        print('Traceback: _blockcomp: get_matrix(): Wrong mode parameter.')
        R = []
    # Ground Truth:
    for itmx_ in range(len(R)):
        strr = str(day + 1)
        GT = np.loadtxt("./data/" + news_name + "/day_" + strr + ".txt")
    return [GT, R]


def compare_single_block(gt, r, modifiers=2, mode='hamming'):
    """Compares a single block with its ground truth
    and determines the error."""
    average_error = 0
    nerrors = 0
    if mode == 'hamming':
        errors = 0
        for row in range(len(gt)):
            errors = hamming(r[row], gt[row])*len(gt[row]) + errors
        average_error = errors/len(gt)
        nerrors = errors
    elif mode == 'unchained':
        errors = ec.CalculateError(gt, r, modifiers)
        average_error = errors.eavg
        nerrors = errors.nerr
    else:
        print('Traceback _blockcomp: compare_blocks(): Wrong parameter: mode')
    return [average_error, nerrors]


def one_in_middle(r, stages, switch=1):
    ret = r
    for i in range(stages):
        for item1 in range(len(r)):
            for item2 in range(1, len(r)-1):
                if r[item1][item2-1] == switch and r[item1][item2+1] == switch:
                    ret[item1][item2] = switch
    return sym_correction(ret)


def compare_blocks(word_list, word_type, news_name, create_mode='npnn', compare_mode='hamming', nouns=0, pronouns=2,
                   threshold=0.5, punisher_multiplier=4, debug=False,
                   saveas='null', saveas_path=r'.\Results', numerrors=False, nlp=spacy.load('es_core_news_lg'),
                   correction_level=0, lvoim=1):

    """Compares the blocks."""

    if debug:
        print('News: ', news_name)
    avg = []
    avg_idem = []
    for i in range(len(word_type)):
        # Get r and gt matrix:
        [gt, r] = get_matrix(word_list, word_type, news_name, i, mode=create_mode, threshold=threshold,
                             pronouns=pronouns, nouns=nouns, nlp=nlp)

        # Symmetry correction or one in middle:
        if correction_level == 1:
            r = sym_correction(r, politics=1)
        elif correction_level == 2:
            r = one_in_middle(r, lvoim)
        # I:
        idem = fill_diagonalOne([[0 for x in range(len(r))] for y in range(len(r))])
        # Get the number of errors in every day or the average of the day:
        __auxitm = compare_single_block(gt, r, modifiers=punisher_multiplier, mode=compare_mode)
        __auxitm2 = compare_single_block(gt, idem, modifiers=punisher_multiplier, mode=compare_mode)
        if numerrors:
            avg.append(__auxitm[1])
            avg_idem.append(__auxitm2[1])
        else:
            avg.append(__auxitm[0])
            avg_idem.append(__auxitm2[0])
        if debug:
            print('Error in day ', i+1, ': ', avg[i], '/', avg_idem[i])

        # Save the matrix as a .txt file:
        if saveas != 'null':
            mtx_file = open(saveas_path + '\\' + news_name + '_day_' + str(i) + '_' + saveas, 'w')
            word_file = open(saveas_path + '\\' + news_name + '_day_' + str(i) + '_words_' + saveas, 'w')
            for itm1 in range(len(r)):
                for itm2 in range(len(r[0])):
                    mtx_file.write(str(r[itm1][itm2]) + ' ')
                mtx_file.write('    ')
                for itm3 in range(len(gt[0])):
                    mtx_file.write(str(round(gt[itm1][itm3])) + ' ')
                mtx_file.write('\n')
            for itm4 in range(len(word_list[i])):
                word_file.write(word_list[i][itm4])
                word_file.write('\n')
        # - - - - - - - - - - - - - - - - -
    if debug:
        avgt = mean(avg)
        print('\nTotal error: ', avgt, '/', mean(avg_idem))

    return [avg, avg_idem]


if __name__ == '__main__':
    print_graph([1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1], 1, 0.7, 0)
