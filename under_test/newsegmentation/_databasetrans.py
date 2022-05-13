# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
import os
import shutil

import googletrans

NEWS_PATH = f'{os.getcwd()}/db/vtt_files/'
WRITE_PATH = f'./.internal/'
DEEPL_AUTH_KEY = 'XXXXXXX'
# -----------------------------------------------------------


def get_diff(tstamps):
    spt0 = tstamps[0].split(':')
    spt1 = tstamps[1].split(':')
    diff = 0
    for i, diffed in enumerate(spt0):
        diff += (60**(2-i))*(int(spt1[i]) - int(diffed))
    return diff


def get_diff_f(tstamps):
    st0 = tstamps[0].split('.')[0]
    st1 = tstamps[1].split('.')[0]
    dec0 = int(tstamps[0].split('.')[1])
    dec1 = int(tstamps[1].split('.')[1])
    decimal = get_diff([st0, st1])
    ret = round(decimal + (dec1-dec0)/1000, 2)
    return ret


def capital_replace(_text, cnt=0):
    unchain_words = []
    ret_phrase = []
    counter = cnt
    iterator_text = _text.split('. ')
    for _text_m in iterator_text:
        chain_words = []
        segmented_text = _text_m.split(' ')
        for idx, word in enumerate(segmented_text):
            if word != '':
                if word[0].isupper() and idx != 0:
                    chain_words.append(f'__{counter}__')
                    counter += 1
                    unchain_words.append(word)
                else:
                    chain_words.append(word)
        ret_phrase.append(' '.join(chain_words))
    ret_phrase = '. '.join(ret_phrase)
    return [ret_phrase, unchain_words, counter]


def capital_restore(_text, dkt):
    _text_p = _text
    for idx, word in enumerate(dkt):
        _text_p = _text_p.replace(f'__{idx}__', word)
    return _text_p


class VttReading:
    def __init__(self, **kwargs):
        search_case = None
        time_limit = '00:05:00'
        translate_model = False
        tmodel = 'google'
        for key, value in kwargs.items():
            if key == 'search_case':
                search_case = value
            elif key == 'time_limit':
                time_limit = value
            elif key == 'translate_model':
                translate_model = value
            elif key == 'tmodel':
                if value == 'GoogleTranslate - Online traduction.':
                    tmodel = 'google'
                elif value == 'DeepL - Online traduction.':
                    tmodel = 'deepl'
                else:
                    print('Invalid model for translation...')

        global NEWS_PATH
        self.time_limit = time_limit
        self.total = {}
        self.result = None
        self.diffs = {}

        if search_case is not None:
            if search_case[0] != '!':
                [self.result, self.result_eng] = self.__read_case(search_case, translate=translate_model, tmodel=tmodel)
                self.total[search_case] = self.result
                self.total[f'{search_case}_eng'] = self.result_eng
        else:
            for dir_case in os.listdir(NEWS_PATH):
                if dir_case[0] != '!':
                    [self.total[dir_case], self.total[f'{dir_case}_eng']] = self.__read_case(dir_case,
                                                                                             translate=translate_model,
                                                                                             tmodel=tmodel)
                print(f'Case: {dir_case} done with translation model {translate_model}')

        self.__print_news(self.total)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __read_case(self, search_case, translate=False, tmodel='google'):
        global NEWS_PATH
        sentences = {}
        sentences_eng = {}
        dir_path = f'{NEWS_PATH}{search_case}/'
        for idx, _ in enumerate(os.listdir(dir_path)):
            route = f'{dir_path}{idx+1}.vtt'
            [sentences[str(idx+1)], sentences_eng[str(idx+1)], diffcase] = self.__get_text(route, translate=translate,
                                                                                           tmodel=tmodel)
            self.diffs[f'{search_case}_{idx+1}'] = diffcase
        return [sentences, sentences_eng]

    def __get_text(self, route, translate=False, tmodel='google'):
        some_text = '!'
        timestamps = ['00:00:00', '00:00:00']
        hover_sliced = ['$ $ $']
        diffs_ = []
        diffs = []
        splitted = ['$$$']
        with open(route, 'r', encoding='utf-8') as file:
            for line in file:
                if line[0:4] == 'NOTE':
                    line = next(file)
                    if line[0] != '\n':
                        return None, None, None
                else:
                    if '00:00:00' < line[:] < self.time_limit:
                        timestamps.append([line.split(' --> ')[0][:-4], line.split(' --> ')[1][:8]])
                        # diffs_.append(get_diff([line.split(' --> ')[0][:-4], line.split(' --> ')[1][:8]]))
                        diffs_.append(get_diff_f([line.split(' --> ')[0], line.split(' --> ')[1][:12]]))
                        if timestamps[-1][0] > timestamps[-2][1] and (len(diffs_) == 1 or some_text[-1] == '!'):
                            sliced = f'${next(file)}'
                        else:
                            sliced = next(file)
                        while sliced != "\n":
                            if self.__eliminate_buffer(hover_sliced, sliced):
                                some_text = f'{some_text} {sliced[:-1]}'
                                hover_sliced.append(sliced)
                                if '.\n' in hover_sliced[-1]:
                                    diffs.append(sum(diffs_))
                                    splitted.append(some_text)
                                    some_text = ' '
                                    diffs_ = []
                            sliced = next(file)


        splitted = [self.__eliminate_doubles(mutable[2:-1]) for mutable in splitted][1:]

        if translate:
            traduction_splt = self.__translate(splitted, model=tmodel)
        else:
            traduction_splt = ['No translated.']

        if not len(splitted) == len(traduction_splt):
            print(f'Length of traduction is not the same as original: {len(splitted)} != {len(traduction_splt)} '
                  f'for route: {route}')

        return [splitted, traduction_splt, diffs]

    def __print_news(self, text_dict) -> None:
        global WRITE_PATH
        for case, dicti in text_dict.items():
            if 'eng' in case:
                dirr = r'eng/'
            else:
                dirr = r'esp/'
            try:
                shutil.rmtree(f'{WRITE_PATH}{dirr}{case}')
            except Exception as reason:
                os.mkdir(f'{WRITE_PATH}{dirr}{case}/')
                print(f'Traceback: VttReading/__print_news/shutil.rmtree: Cannot remove directory {WRITE_PATH}{case}.'
                      f'\n Reason: {reason}.')

            for key, value in dicti.items():
                if value is not None:
                    try:
                        with open(f'{WRITE_PATH}{dirr}{case}/{key}.txt', 'w', encoding='utf-8') as file:
                            for sentences in value:
                                file.writelines(f'{sentences}\n')
                            casex = case.split('_')[0]
                            file.writelines(f'%{self.diffs[f"{casex}_{key}"]}')
                    except IOError:
                        try:
                            os.mkdir(f'{WRITE_PATH}{dirr}{case}/')
                            with open(f'{WRITE_PATH}{dirr}{case}/{key}.txt', 'w', encoding='utf-8') as file:
                                for sentences in value:
                                    file.writelines(f'{sentences}\n')
                                casex = case.split('_')[0]
                                file.writelines(f'%{self.diffs[f"{casex}_{key}"]}')
                        except OSError:
                            print('Traceback: VttReading/__print_news/os.makedir'
                                  '(f\'{WRITE_PATH}{case})\'cannot be created.')

    @staticmethod
    def __eliminate_doubles(text):
        return text.replace('  ', ' ')

    #   Hard feature to include: For not repeating words or blocks in the text.
    @staticmethod
    def __eliminate_buffer(hover_sliced, sliced):
        add_permission = True
        for hover in hover_sliced:
            if sliced == hover:
                add_permission = False
        return add_permission

    @staticmethod
    def __translate(_texts_original, model='google'):
        retext_ = ''
        try:
            _text = []
            DKT = []
            cnt = 0
            for _text_original in _texts_original:
                [_text_, DKT_, cnt] = capital_replace(_text_original, cnt)
                DKT.extend(DKT_)
                _text.append(_text_)
        except Exception as exc:
            print(f'{exc}')
            raise

        if model == 'google':
            g_translator = googletrans.Translator(service_urls=['translate.google.com'])
            if _text is None:
                print('Oops, there was an error translating...')
            else:
                try:
                    txt = '\n'.join(_text)
                    retext_ = g_translator.translate(txt, src='es', dest='en').text
                    retext_ = retext_.replace('​​', '')
                except BaseException:
                    print(f'Traceback: VttReading/__translate: Cannot translate \'{_text}\' '
                          f'from model {model}; maybe too many requests.')
        else:
            print(f'Traceback: VttReading/__translate: No translator model called {model}.')
        _retext = capital_restore(retext_, DKT)
        return _retext.split('\n')
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
