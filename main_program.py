# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
#   Import zone:
#                                                                       #
#   In this zone all libraries required are imported:
#                                                                       #
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# Custom libraries:
# Main libraries:
import datetime
import errno
import glob
import os
import re
import shutil
import time
from itertools import chain
from statistics import mean

# NLP / number libraries:
import spacy

import FB_BCM as _fb
import _blockcomp as _bc
import _dserial as ds
import _errorclc as _ec


# Other libraries:
# Unused atm:
# from collections import Counter
# from nltk.corpus import stopwords
# import collections
# import stanza
# import nltk
# from scipy.spatial.distance import hamming
# import numpy as np
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
#   Initialization zone:
#                                                                       #
#   In this zone the program is loaded:
#                                                                       #
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# nltk.download('stopwords')      # Stopwords.
# stanza.download('es')           # Download English model.
# stopword_es = nltk.corpus.stopwords.words('spanish')  # Create instance.
# nlp = stanza.Pipeline('es')  # Initialize Spanish neural pipeline
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @results_initialization()
#                                                 #
#   This function initializes the results folder.
#                                                 #
#       @inputs:
#           name: Name of the results folder.     #
# - - - - - - - - - - - - - - - - - - - - - - - - #


def results_initialization(name):
    try:
        os.makedirs(name)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    folder = name
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @Convert_lower()
#                                                 #
#   This function puts a list in lower case.
#                                                 #
#       @inputs:
#           listX: List to be put in lower case.  #
#
#       @output:
#           List in lower case.
# - - - - - - - - - - - - - - - - - - - - - - - - #


def Convert_lower(listX):
    listNew = ''
    for ind in range(len(listX)):
        listNew = listNew + listX[ind].lower()
    return listNew
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @duplicates()
#                                                 #
#   This function returns the index of duplicate
#   elements.
#                                                 #
#       @inputs:
#           lst: List to be compared.
#
#           itemOfDuplicate: List to compare with.#
#
#       @output:
#           Index of duplicate elements.
# - - - - - - - - - - - - - - - - - - - - - - - - #


def duplicates(lst, itemOfDuplicate):   # Unused.
    return [i for i, x in enumerate(lst) if x == itemOfDuplicate]
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @modify_original_list()
#                                                 #
#
#                                                 #
#       @inputs:
#
#
#       @output:
#
# - - - - - - - - - - - - - - - - - - - - - - - - #


def modify_original_list(allMatchOfPiece_Original, final_secondTwo_noDuplicate):
    if len(final_secondTwo_noDuplicate) == 0:
        allMatchOfPiece_One_dir = allMatchOfPiece_Original
    else:
        TMP = []
        allMatchOfPiece_One_dir = []
        for itemOfCell in range(len(allMatchOfPiece_Original)):
            BlockOfPiece = allMatchOfPiece_Original[itemOfCell]
            BlockOfPieceOrig = allMatchOfPiece_Original[itemOfCell]
            for itemOfFinal in range(len(final_secondTwo_noDuplicate)):
                BlockOfFinal = final_secondTwo_noDuplicate[itemOfFinal]

                if BlockOfFinal[0] == itemOfCell:
                    BlockOfPiece[BlockOfFinal[1]] = 1
                    TMP = BlockOfPiece[:]
                else:
                    TMP = BlockOfPieceOrig[:]
            allMatchOfPiece_One_dir.append(TMP)

    return allMatchOfPiece_One_dir
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @merge_subs()
#                                                 #
#
#                                                 #
#       @inputs:
#
#
#       @output:
#
# - - - - - - - - - - - - - - - - - - - - - - - - #


def merge_subs(lst_of_lsts):    # Unused.
    res = []
    for row in lst_of_lsts:
        for i, resrow in enumerate(res):
            if row[0] == resrow[0]:
                res[i] += row[1:]
                break
        else:
            res.append(row)
    return res
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @delete_element()
#                                                 #
#       Deletes an element from a list.
#                                                 #
#       @inputs:
#           list_object: List.
#           pos: Position.
# - - - - - - - - - - - - - - - - - - - - - - - - #


def delete_element(list_object, pos):   # Unused.
    """Delete element from list at given index
     position (pos) """
    if pos < len(list_object):
        list_object.pop(pos)
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @delete_multiple_element()
#
#       Deletes elements from a list by index.
#
#       @inputs:
#           list_object: The list.
#           indices: Index of the elements
#           to be removed.
# - - - - - - - - - - - - - - - - - - - - - - - - #


def delete_multiple_element(list_object, indices):
    indices = sorted(indices, reverse=True)
    for idx in indices:
        if idx < len(list_object):
            list_object.pop(idx)
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @print_news()
#                                                 #
#       Print the news to a .txt file.
#                                                 #
#       @inputs:
#           path: The results path.
#           name: The name of the news.
#           text_list: The text to be written.
#
#       @output:
#           True if the program suceeded.
# - - - - - - - - - - - - - - - - - - - - - - - - #


def print_news(text_list, path, name, documents):
    ground_path = path + name + '_'
    for item in range(len(text_list)):
        doc = documents[item]
        doc = int(doc[0] - 1)
        total_path = ground_path + 'day_' + str(doc) + '_raw.txt'
        fil = open(total_path, 'w')
        fil.writelines(text_list[item])

        total_path = ground_path + 'day_' + str(doc) + '_block.txt'
        fil = open(total_path, 'w', encoding='utf-8')
        for item2 in text_list[item]:
            item_mod = ''
            for item3 in range(len(item2)):
                if item2[item3] != '\n':
                    item_mod = item_mod + item2[item3]
            fil.writelines(item_mod + '\n')

    return True
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @remove_duplicate()
#                                                 #
#       Removes duplicate elements in the list.
#                                                 #
#       @inputs:
#           my_list: The list.
#
#       @output:
#           List without duplicate elements.
# - - - - - - - - - - - - - - - - - - - - - - - - #


def remove_duplicate(my_list):
    temp_list = []

    for i in my_list:
        if i not in temp_list:
            temp_list.append(i)

    my_list = temp_list
    return my_list
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @add_one_in_middle_zeros()
#                                                 #
#       Corrects the array positioning '1'
#       if there is a zero between two ones.
#
#                                                 #
#       @inputs:
#           allMarchOfPiece_Original:
#               Original list.
#       @output:
#           Corrected list.
# - - - - - - - - - - - - - - - - - - - - - - - - #


def add_one_in_middle_Zeros(allMatchOfPiece_Original):
    allMatchOfPiece_oneInMiddle = []
    for oneItem in allMatchOfPiece_Original:
        for index in range(0, len(oneItem) - 2):
            if oneItem[index] == 1 and oneItem[index + 1] == 0 and oneItem[index + 2] == 1:
                oneItem[index + 1] = 1
        allMatchOfPiece_oneInMiddle.append(oneItem)
    return allMatchOfPiece_oneInMiddle
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @get_text()
#                                                 #
#       Gets the text inside the files in the
#       selected timestamp.
#                                                 #
#       @inputs:
#           all_files:
#               VTT files in the document.
#           start:
#               Beginning timestamp.
#           end:
#               Ending timestamp.
#       @output:
#           - Text from the files.
#           - Document day values.
# - - - - - - - - - - - - - - - - - - - - - - - - #


def get_text(all_files, start='00:00:00.000', end='00:05:00.000', debugging=False):
    documents = []
    all_stemmed_words = []
    textOfDoc = []
    all_newsOfDay = []
    for filename in all_files:
        textOfDoc.clear()
        all_stemmed_words.clear()

        # Reading the first 5 minutes.
        with open(filename, encoding="utf-8") as rawText:
            modifiedTstamp = []
            timeStamp = []
            newsOfDay = []
            for line in rawText:
                sentence = ''
                if start < line[:] < end:
                    timeStamp.append(line[:])
                    slice = next(rawText)
                    sentence = sentence + slice

                    while slice != "\n":
                        slice = next(rawText)
                        sentence = sentence + ' ' + slice

                    textOfDoc.append(' ' + sentence)

            # Other way of reading ... ???
            #if len(textOfDoc) < 1:
            #    with open(filename, encoding="utf-8") as rawTextSmall:
            #        lines = rawTextSmall.read()
            #        textOfDoc.append(lines)

            # Clustering if there is a time +1s and full stop '.':
            for itmX in timeStamp:
                newX = itmX.split(" --> ")
                itemY = newX[1].split(" ")

                modifiedTstamp.append(newX[0])
                modifiedTstamp.append(itemY[0])

            clearFileName = [float(s) for s in re.findall(r'-?\d+\.?\d*', filename)]
            documents.append(clearFileName)

            # Print out the text between TS and store TS of each block.
            startIndex = 0
            endIndex = 0
            lastItem = int((len(modifiedTstamp) - 1) / 2)
            timeStampOfBlocks = []

            for itmZ in range(1, (len(modifiedTstamp) - 1), 2):

                time = (datetime.datetime.strptime(modifiedTstamp[itmZ + 1], "%H:%M:%S.%f")) - datetime.datetime.strptime(
                    modifiedTstamp[itmZ], "%H:%M:%S.%f")

                counter = 0
                if time.seconds >= 1:
                    endIndex = int((itmZ + 1) / 2)

                    collect_one_news = ''
                    for TextIndex in range(startIndex, endIndex):
                        collect_one_news = collect_one_news + textOfDoc[TextIndex]

                    if len(collect_one_news) > 0:
                        if collect_one_news[len(collect_one_news) - 4] == ".":
                            collect_one_news = collect_one_news

                            if len(collect_one_news) > 0:
                                newsOfDay.append(collect_one_news)
                                timeStampOfBlocks.append(endIndex)
                            startIndex = endIndex
                        else:
                            entireX = TextIndex

                            while (collect_one_news[len(collect_one_news) - 4] != ".") and entireX < lastItem:
                                collect_one_news = collect_one_news + textOfDoc[entireX]

                                entireX = entireX + 1
                                counter = counter + 1

                            if len(collect_one_news) > 0:
                                newsOfDay.append(collect_one_news)

                            timeStampOfBlocks.append(endIndex)
                            startIndex = entireX

                    else:
                        continue
            else:
                collect_one_news = ''
                for x in range(endIndex, lastItem):
                    collect_one_news = collect_one_news + textOfDoc[x]

                if len(collect_one_news) > 0:
                    newsOfDay.append(collect_one_news)

                timeStampOfBlocks.append(lastItem)

            if debugging == True:
                print('newsOfDay', newsOfDay)

            all_newsOfDay.append(newsOfDay)

    return [all_newsOfDay, documents]
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @get_blocks()
#                                                 #
#       Gets the blocks inside the text if there
#       is a full stop + 1s.
#                                                 #
#       @inputs:
#           all_newsOfDay:
#               Text of the VTT files selected.
#
#           documents:
#               Number of day of the doc.
#
#       @output:
#           all_SlicesWithSetentencesWith_empty:
#               - Words in the blocks in
#               sentences.
#           list_all_word_type:
#               - Type of the words in the block.
# - - - - - - - - - - - - - - - - - - - - - - - - #


def get_blocks(all_newsOfDay, documents, nlp_category, path_SW, debugging=False):
    # Get the stopwords and save them in swlines.
    ####################################################################################
    swlines = []
    with open(path_SW, encoding="utf-8") as stopWordsList:
        for line in stopWordsList:
            swlines.append(line.rstrip())
    ####################################################################################
    List_all_text_slices_value = []
    list_all_word_type = []
    word_pos_inc_NOUN = []
    label_pos_inc_NOUN = []
    label_pos_inc_PROPN = []
    all_text_labels = []
    for itm in all_newsOfDay:
        all_text_slices_value = []
        wordTypeOfDay = []
        text_labels = []

        sliceOfText = itm

        if debugging == True:
            print('Slices/Blocks in this day #:  ', len(sliceOfText))

        for itm_x in range(0, len(sliceOfText)):

            doc_PROPN = nlp_category(sliceOfText[itm_x])
            doc_NOUN = nlp_category(sliceOfText[itm_x])

            # PROPN part: that find PROPN words, save it in PROPN list, and also save the type in a type list
            #################################################################################
            word_pos_PROPN = []
            label_pos_PROPN = []
            for ent in doc_PROPN:
                label_pos_inc_PROPN = []
                word_pos_PROPN.append(ent)
                label_pos_PROPN.append(ent.pos_)

            list_included_wrd_PROPN = ['PROPN']
            part_txt_PROPN = []
            text_word_pos_inc_PROPN = ''

            for entity_PROPN in range(len(label_pos_PROPN)):

                if label_pos_PROPN[entity_PROPN] in list_included_wrd_PROPN:
                    # concatenation of the text together
                    text_word_pos_inc_PROPN = text_word_pos_inc_PROPN + ' ' + str(word_pos_PROPN[entity_PROPN])

                    # removing numbers
                    result_No_Number_PROPN = re.sub(r'[0-9]+', '', text_word_pos_inc_PROPN)
                    words_PROPN = re.findall(r'\w+', result_No_Number_PROPN)

                    # word not in stopwords
                    new_important_words_PROPN = [word for word in words_PROPN if word not in swlines]
                    part_txt_PROPN = new_important_words_PROPN

            text_labels.append(label_pos_PROPN)
            # #removing duplicate words
            res = [idx for idx, item in enumerate(part_txt_PROPN) if item in part_txt_PROPN[:idx]]

            delete_multiple_element(part_txt_PROPN, res)

            for xText in range(len(part_txt_PROPN)):
                label_pos_inc_PROPN.append('PROPN')

            # NOUN part: that find NOUN words, save it in NOUN list and also save the type in type list
            #################################################################################
            word_pos_NOUN = []
            label_pos_NOUN = []

            for ent in doc_NOUN:
                word_pos_inc_NOUN = []
                label_pos_inc_NOUN = []
                word_pos_NOUN.append(ent)
                label_pos_NOUN.append(ent.pos_)

            list_included_wrd_NOUN = ['NOUN']
            part_txt_NOUN = []
            text_word_pos_inc_NOUN = ''

            for entity_NOUN in range(len(label_pos_NOUN)):

                if label_pos_NOUN[entity_NOUN] in list_included_wrd_NOUN:
                    # concatenation of the text together
                    text_word_pos_inc_NOUN = text_word_pos_inc_NOUN + ' ' + str(word_pos_NOUN[entity_NOUN])

                    # removing numbers
                    result_No_Number_NOUN = re.sub(r'[0-9]+', '', text_word_pos_inc_NOUN)
                    words_NOUN = re.findall(r'\w+', result_No_Number_NOUN)

                    # keep words not in stopwords
                    new_important_words_NOUN = [word for word in words_NOUN if word not in swlines]

                    part_txt_NOUN = new_important_words_NOUN

            word_pos_inc_NOUN.clear()

            # removing duplicate words
            res_NOUN = [idx for idx, item in enumerate(part_txt_NOUN) if item in part_txt_NOUN[:idx]]

            delete_multiple_element(part_txt_NOUN, res_NOUN)

            for xTextPropn in range(len(part_txt_NOUN)):
                label_pos_inc_NOUN.append('NOUN')

            # Create list of all noun & propn, the same for the types
            ###################################################################################################################
            merged_list_of_words = part_txt_PROPN + part_txt_NOUN
            merged_list_of_type = label_pos_inc_PROPN + label_pos_inc_NOUN

            all_text_slices_value.append(merged_list_of_words)
            wordTypeOfDay.append(merged_list_of_type)

        all_text_labels.append(text_labels)
        list_all_word_type.append(wordTypeOfDay)
        List_all_text_slices_value.append(all_text_slices_value)

    # Sort all the list by days.
    ####################################################################################
    documents_back = list(chain.from_iterable(documents))

    for i in range(0, len(documents_back)):
        documents_back[i] = int(documents_back[i])

    documents_back, List_all_text_slices_value, list_all_word_type, all_text_labels, all_newsOfDay_sorted = (list(t) for t in zip(*sorted(
        zip(documents_back, List_all_text_slices_value, list_all_word_type, all_text_labels, all_newsOfDay))))

    # Get text of slice as sentences.
    ####################################################################################

    part_txt_1 = []
    all_SliceOfSentencesWith_empty = []
    tempPart_1 = ''

    for itemOfslice_1 in List_all_text_slices_value:
        part_txt_1.clear()
        for IndexFirst_1 in range(0, len(itemOfslice_1)):
            toText = ''
            sliceItem_1 = itemOfslice_1[IndexFirst_1]

            for itmSlice_1 in range(0, len(sliceItem_1)):
                toText = toText + Convert_lower(sliceItem_1[itmSlice_1]) + ' '

            part_txt_1.append(toText)
            tempPart_1 = part_txt_1[:]

        all_SliceOfSentencesWith_empty.append(tempPart_1)

    return [all_SliceOfSentencesWith_empty, list_all_word_type, all_text_labels, all_newsOfDay_sorted]
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @phrase_segmentation()
#                                                 #
#       Splits the payload in sentences.
#
#                                                 #
#       @inputs:
#           news_day:
#               News lists in days.
#       @output:
#           Day in sentences.
# - - - - - - - - - - - - - - - - - - - - - - - - #


def phrase_segmentation(news_day):
    """"First index: Day. Second index: Sentence."""
    retmtx = []
    for day in range(len(news_day)):
        phrases = []
        workstring = ''
        last_element = ' '
        next_element = ' '
        for segment in news_day[day]:
            for char_idx in range(len(segment)):
                char = segment[char_idx]
                if last_element != ' ' or char != ' ':
                    if char != '\n':
                        if char != '.':
                            workstring = workstring + char
                        else:
                            next_element = segment[char_idx + 1]
                            if not (next_element.isdigit() and last_element.isdigit()):
                                phrases.append(workstring + '.')
                                workstring = ''
                            else:
                                workstring = workstring + char
                last_element = char

        for sentence_idx in range(len(phrases)):
            sentence = phrases[sentence_idx]
            while sentence[0] == ' ':
                sentence = sentence[1:]
                phrases[sentence_idx] = sentence

        new_sentence = ''
        for sentence_idx in range(len(phrases)):
            sentence = phrases[sentence_idx]
            last_element = ' '
            new_sentence = ''
            for char in sentence:
                if last_element != ' ' or char != ' ':
                    new_sentence = new_sentence + char
                last_element = char
            phrases[sentence_idx] = new_sentence

        retmtx.append(phrases)
    return retmtx
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
#   Main program:
#                                                                       #
#   This is the zone where the program is run:
#                                                                       #
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
########################################################################################################################
def packed(case, method, oim, symc, hamming, unchained, pm, oimstages, th, np, nn, segtype, textype):
    nlp_category = spacy.load('es_core_news_lg')  # Load spacy.
    if segtype != 'FB-BCM':
        results_initialization('Results')   # Initialize results dir.
    else:
        results_initialization('trees')
    news_name = case     # News used.

    start = '00:00:00.000'  # Start timestamp.
    end = '00:05:00.000'    # End timestamp.

    # Log file.
    ####################################################################################
    log_name = 'logfile'
    log_path = r'.\logs' + '\\' + log_name + '.txt'
    log_file = open(log_path, 'w')
    log_file_title = 'RESULTS:'
    log_file.write('----------------L O G F I L E-------------------\n' + log_file_title + '\n\n')

    # Path definition.
    ####################################################################################
    path = r'.\Documents' + '\\' + news_name
    path_SW = r'.\stopword.txt'
    all_files = glob.glob(path + "/*.vtt")

    # Importing VTT files to text. From 'start' to 'end'.
    ####################################################################################
    [all_newsOfDay, documents] = get_text(all_files, start, end)
    print_news(all_newsOfDay, r'.\Results\\', news_name, documents)

    # Create blocks depending the method, sorted by days.
    ####################################################################################
    if segtype == 'Temporal':
        [all_SliceOfSentencesWith_empty, list_all_word_type, text_labels, all_newsOfDay] = \
            get_blocks(all_newsOfDay, documents, nlp_category, path_SW)
    elif segtype == 'FB-BCM':
        [all_SliceOfSentencesWith_empty, list_all_word_type, text_labels, all_newsOfDay] = \
            get_blocks(all_newsOfDay, documents, nlp_category, path_SW)
    else:
        print('Error in segmentation type: raise')
        raise

    # Selecting the string to work with:
    ####################################################################################
    worktext = []
    worktypes = []
    if textype == 'Word string':
        worktext = all_SliceOfSentencesWith_empty
        worktypes = list_all_word_type
    elif textype == 'Raw blocks':
        worktext = []
        for i1 in range(len(all_newsOfDay)):
            mod2 = []
            for i2 in all_newsOfDay[i1]:
                mod = ''
                for i3 in range(len(i2)):
                    if i2[i3] != '\n':
                        mod = mod + i2[i3]
                mod2.append(Convert_lower(mod))
            worktext.append(mod2)
        worktypes = text_labels
    elif textype == 'Phrases':
        worktext = phrase_segmentation(all_newsOfDay)
    else:
        print('Error in text type: raise')
        worktext = []
        worktypes = []
        raise

    # Doing the comparison between the blocks. Ahmad + Alberto code.
    ####################################################################################
    launch_mode = method
    threshold_use = th
    level_oim = oimstages
    level = 0
    ret1 = 0
    ret2 = 0
    if symc:
        level = 1
    if oim:
        level = 2

    if segtype == 'Temporal':
        if launch_mode == 'npnn':
            log_file.write('Hamming distance:\n')
            if True:
                n_nouns = nn
                n_pronouns = np
                log_file.write('\n')
                if True:
                    [avg, avg_idem] = _bc.compare_blocks(worktext, worktypes, news_name,
                                                         debug=False,
                                                         nouns=n_nouns, pronouns=n_pronouns,
                                                         saveas='p' + str(n_pronouns) + '_n' + str(n_nouns) + '.txt',
                                                         numerrors=True,
                                                         compare_mode='hamming', lvoim=level_oim,
                                                         nlp=nlp_category, correction_level=level, punisher_multiplier=pm)
                    __text = '\n\tCase ' + str(n_pronouns) + ' pronouns and ' + str(n_nouns) + ' nouns:\n\n'
                    log_file.write(__text)
                    print(__text)
                    for item1 in range(len(avg)):
                        ratio = 100*avg[item1]/avg_idem[item1]
                        __text = 'Day ' + str(item1) + ': ' + str(round(avg[item1], 2)) + '/' + \
                                 str(round(avg_idem[item1], 2)) + '.   \tRatio: ' + str(round(ratio, 2)) + '%\n'
                        log_file.write(__text)
                        print(__text)

                    ratio = 100 * mean(avg) / mean(avg_idem)
                    ret1 = ratio
                    __text = '\n\tAverage: ' + str(round(mean(avg), 2)) + '/' + str(round(mean(avg_idem), 2)) + '\tRatio: ' + \
                             str(round(ratio, 2)) + '%\n\n'
                    log_file.write(__text)
                    print(__text)

            log_file.write('\n----------------------------------------\nUnchained errors:\n')
            if True:
                n_nouns = nn
                n_pronouns = np
                log_file.write('\n')
                if True:
                    [avg, avg_idem] = _bc.compare_blocks(worktext, worktypes, news_name,
                                                         debug=False,
                                                         nouns=n_nouns, pronouns=n_pronouns,
                                                         saveas='p' + str(n_pronouns) + '_n' + str(n_nouns) + '.txt',
                                                         numerrors=True, lvoim=level_oim,
                                                         compare_mode='unchained',
                                                         nlp=nlp_category, correction_level=level, punisher_multiplier=pm)
                    __text = '\n\tCase ' + str(n_pronouns) + ' pronouns and ' + str(n_nouns) + ' nouns:\n\n'
                    log_file.write(__text)
                    print(__text)
                    for item1 in range(len(avg)):
                        ratio = 100*avg[item1]/avg_idem[item1]
                        __text = 'Day ' + str(item1) + ': ' + str(round(avg[item1], 2)) + '/' + \
                                 str(round(avg_idem[item1], 2)) + '.   \tRatio: ' + str(round(ratio, 2)) + '%\n'
                        log_file.write(__text)
                        print(__text)

                    ratio = 100 * mean(avg) / mean(avg_idem)
                    ret2 = ratio
                    __text = '\n\tAverage: ' + str(round(mean(avg), 2)) + '/' + str(round(mean(avg_idem), 2)) + '\tRatio: ' + \
                             str(round(ratio, 2)) + '%\n\n'
                    log_file.write(__text)
                    print(__text)
        elif launch_mode == 'use':
            """Universal sentence encoder:"""
            if hamming:
                log_file.write('\n----------------------------------------\nHamming distance:\n')
                __text = '\n\tCase with Universal Sentence Encoder.\n'
                log_file.write(__text)
                print(__text)
                [avg, avg_idem] = _bc.compare_blocks(worktext, worktypes, news_name,
                                   debug=False,
                                   saveas='use.txt',
                                   numerrors=True,
                                   compare_mode='hamming',
                                   create_mode='use',
                                   nlp=nlp_category, lvoim=level_oim,
                                   threshold=threshold_use, correction_level=level, punisher_multiplier=pm)

                for item1 in range(len(avg)):
                    ratio = 100 * avg[item1] / avg_idem[item1]
                    __text = 'Day ' + str(item1) + ': ' + str(round(avg[item1], 2)) + '/' + \
                             str(round(avg_idem[item1], 2)) + '.   \tRatio: ' + str(round(ratio, 2)) + '%\n'
                    log_file.write(__text)
                    print(__text)
                ratio = 100 * mean(avg) / mean(avg_idem)
                ret1 = ratio
                __text = '\n\tAverage: ' + str(round(mean(avg), 2)) + '/' + str(round(mean(avg_idem), 2)) + '\tRatio: ' + \
                         str(round(ratio, 2)) + '%\n\n'
                log_file.write(__text)
                print(__text)

            if unchained:
                log_file.write('\n----------------------------------------\nUnchained:\n')
                __text = '\n\tCase with Universal Sentence Encoder.\n'
                log_file.write(__text)
                print(__text)
                [avg, avg_idem] = _bc.compare_blocks(worktext, worktypes, news_name,
                                   debug=False,
                                   saveas='use.txt',
                                   numerrors=True,
                                   compare_mode='unchained',
                                   create_mode='use',
                                   nlp=nlp_category, lvoim=level_oim,
                                   threshold=threshold_use, correction_level=level, punisher_multiplier=pm)

                for item1 in range(len(avg)):
                    ratio = 100 * avg[item1] / avg_idem[item1]
                    __text = 'Day ' + str(item1) + ': ' + str(round(avg[item1], 2)) + '/' + \
                             str(round(avg_idem[item1], 2)) + '.   \tRatio: ' + str(round(ratio, 2)) + '%\n'
                    log_file.write(__text)
                    print(__text)
                ratio = 100 * mean(avg) / mean(avg_idem)
                ret2 = ratio
                __text = '\n\tAverage: ' + str(round(mean(avg), 2)) + '/' + str(round(mean(avg_idem), 2)) + '\tRatio: ' + \
                         str(round(ratio, 2)) + '%\n\n'
                log_file.write(__text)
                print(__text)
#######################################################################################################################################################
    elif segtype == 'FB-BCM':
        mytrees = []
        rx = []
        avg_hamming = []
        avg_unchained = []
        avg_hamming_idem = []
        avg_unchained_idem = []
        ticktock_mtx = []
        log_file.write('USING FB-BCM METHOD (NO UPGRADES):\n')
        _ticktock_text = ''

        for day in range(len(worktext)):

            try:
                gt = _bc.np.loadtxt("./groundtruth/fbbcm/" + news_name + "/day_" + str(day) + ".txt")
                results_initialization(r'./.multimedia/trees/Day' + str(day))

                tick = time.time()
                this_trees = _fb.fbbcm(worktext[day], th, day, showup=False, correlation_model=launch_mode)
                tock = time.time()
                ticktock = tock - tick
                ticktock_mtx.append(ticktock)
                _ticktock_text = _ticktock_text + 'Day ' + str(day) + ':\t' + str(round(ticktock, 1)) + ' seg.\n'

                mytrees.append(this_trees)
                ds.write_tree(this_trees, case + '_day_' + str(day))
                rx.append(_ec.tree_equivalent_matrix(this_trees))
                idem = _bc.fill_diagonalOne([[0 for x in range(len(gt))] for y in range(len(gt))])

                if hamming:
                    [aux, aux2] = _bc.compare_single_block(gt, rx[day], modifiers=pm, mode='hamming')
                    [aux_idem, aux_idem2] = _bc.compare_single_block(gt, idem, modifiers=pm, mode='hamming')
                    avg_hamming.append(aux2)
                    avg_hamming_idem.append(aux_idem2)
                if unchained:
                    [aux, aux2] = _bc.compare_single_block(gt, rx[day], modifiers=pm, mode='unchained')
                    [aux_idem, aux_idem2] = _bc.compare_single_block(gt, idem, modifiers=pm, mode='unchained')
                    avg_unchained.append(aux2)
                    avg_unchained_idem.append(aux_idem2)

            except:
                if hamming:
                    avg_hamming.append(-1)
                    avg_hamming_idem.append(-1)
                if unchained:
                    avg_unchained.append(-1)
                    avg_unchained_idem.append(-1)

        if hamming:
            [avg, avg_idem] = [avg_hamming, avg_hamming_idem]
            log_file.write('\n----------------------------------------\nHamming distance:\n')
            __text = '\n\tCase with FB-BCM.\n'
            log_file.write(__text)

            for item1 in range(len(avg)):
                ratio = 100 * avg[item1] / avg_idem[item1]
                __text = 'Day ' + str(item1) + ': ' + str(round(avg[item1], 2)) + '/' + \
                         str(round(avg_idem[item1], 2)) + '.   \tRatio: ' + str(round(ratio, 2)) + '%\n'
                log_file.write(__text)

            ratio = 100 * mean(avg) / mean(avg_idem)
            ret1 = ratio
            __text = '\n\tAverage: ' + str(round(mean(avg), 2)) + '/' + str(round(mean(avg_idem), 2)) + '\tRatio: ' + \
                     str(round(ratio, 2)) + '%\n\n'
            log_file.write(__text)

        if unchained:
            [avg, avg_idem] = [avg_unchained, avg_unchained_idem]
            log_file.write('\n----------------------------------------\nUnchained:\n')
            __text = '\n\tCase with FB-BCM.\n'
            log_file.write(__text)
            print(__text)

            for item1 in range(len(avg)):
                ratio = 100 * avg[item1] / avg_idem[item1]
                __text = 'Day ' + str(item1) + ': ' + str(round(avg[item1], 2)) + '/' + \
                         str(round(avg_idem[item1], 2)) + '.   \tRatio: ' + str(round(ratio, 2)) + '%\n'
                log_file.write(__text)

            ratio = 100 * mean(avg) / mean(avg_idem)
            ret2 = ratio
            __text = '\n\tAverage: ' + str(round(mean(avg), 2)) + '/' + str(round(mean(avg_idem), 2)) + '\tRatio: ' + \
                     str(round(ratio, 2)) + '%\n\n'
            log_file.write(__text)

        log_file.write('\n----------------------------------------\nTickTock info.:\n')
        log_file.write(_ticktock_text)
        log_file.write('\n\tTotal: ' + str(round(sum(ticktock_mtx), 2)) + ' seg.\n')

    return [ret1, ret2]


if __name__ == '__main__':
    testing = [
        ['No hay descanso.\n Tres de los cuatro terroristas \n \n \n han sido abatidos. Mañana en las \n noticias más.\n Julen ha sido hallado \n.', 'Esta es la frase 1. Esta es la frase \n \n 2\n \n han sido abatidos. Mañana en las \n más,\n y mejor.\n', ],
        ['Esa imagen es lo que se ve desde la superficie  y esto es lo que no se ve.  Así es la estructura del pozo.\n', 'El objetivo rescatar al pequeño.',  'El proyecto de presupuestos lle\nga al Congreso.  Son las cuentas con más gast\no público desde 2010  Destacan más partidas para programas sociales,  contra la pobreza infantil o la dependencia,  y también el aumento de inversiones en Cataluña.  El gobierno necesita entre otros  el apoyo de los independentistas catalanes  que por ahora mantienen el NO a los presupuestos,  aunque desde el ejecutivo nacional se escuchan voces más optimistas.  '],
    ]
    file = open(r'./Results/Julen_day_0_raw.txt')
    printed = phrase_segmentation(testing)
    for text in file:
        print(text)