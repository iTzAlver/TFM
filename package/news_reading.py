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
WRITE_PATH = f'{os.getcwd()}/db/news_text/'
DEEPL_AUTH_KEY = 'XXXXXXX'
# -----------------------------------------------------------


def main() -> None:
    VttReading(translate_model=True, search_case='Julen')
    return


def VttReading_(**kwargs):
    VttReading(**kwargs)


def capital_replace(_text):
    unchain_words = []
    counter = 0
    ret_phrase = []
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
    return [ret_phrase, unchain_words]


def capital_restore(_text, DKT):
    _text_p = _text
    for idx, word in enumerate(DKT):
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
            [sentences[str(idx+1)], sentences_eng[str(idx+1)]] = self.__get_text(route, translate=translate,
                                                                                 tmodel=tmodel)
        return [sentences, sentences_eng]

    def __get_text(self, route, translate=False, tmodel='google'):
        some_text = '!'
        timestamps = ['00:00:00', '00:00:00']
        hover_sliced = []
        with open(route, 'r', encoding='utf-8') as file:
            for line in file:
                if '00:00:00' < line[:] < self.time_limit:
                    timestamps.append([line.split(' --> ')[0][:-4], line.split(' --> ')[1][:-11]])
                    if timestamps[-1][0] > timestamps[-2][1] and (some_text[-1] == '.' or some_text[-1] == '!'):
                        sliced = f'${next(file)}'
                    else:
                        sliced = next(file)
                    while sliced != "\n":
                        if self.__eliminate_buffer(hover_sliced, sliced):
                            some_text = f'{some_text} {sliced[:-1]}'
                            hover_sliced.append(sliced)
                        sliced = next(file)

        some_text = self.__eliminate_doubles(self.__eliminate_hanging(some_text))
        if translate:
            traduction = self.__translate(some_text, model=tmodel)
            traduction_splt = traduction.split('. ')
            traduction_splt[0] = traduction_splt[0][2:]
        else:
            traduction_splt = ['No translated.']

        splitted = some_text.split('. ')
        splitted[0] = splitted[0][2:]

        return [splitted, traduction_splt]

    def __print_news(self, text_dict) -> None:
        global WRITE_PATH
        for case, dict in text_dict.items():
            if 'eng' in case:
                dirr = r'eng/'
            else:
                dirr = r'esp/'
            try:
                shutil.rmtree(f'{WRITE_PATH}{dirr}{case}')
            except Exception as reason:
                print(f'Traceback: VttReading/__print_news/shutil.rmtree: Cannot remove directory {WRITE_PATH}{case}.'
                      f'\n Reason: {reason}.')

            for key, value in dict.items():
                try:
                    with open(f'{WRITE_PATH}{dirr}{case}/{key}.txt', 'w', encoding='utf-8') as file:
                        for sentences in value:
                            file.writelines(f'{sentences}\n')
                except IOError:
                    try:
                        os.mkdir(f'{WRITE_PATH}{dirr}{case}/')
                        with open(f'{WRITE_PATH}{dirr}{case}/{key}.txt', 'w', encoding='utf-8') as file:
                            for sentences in value:
                                file.writelines(f'{sentences}\n')
                    except OSError:
                        print('Traceback: VttReading/__print_news/os.makedir'
                              '(f\'{WRITE_PATH}{case})\'cannot be created.')

    def __eliminate_hanging(self, text):
        if text[-1] == '.':
            return text[:-1]
        for idx, _ in enumerate(text):
            if text[-idx] == '.':
                if text[-idx+1] == ' ':
                    return text[:-idx]
        return text

    def __eliminate_doubles(self, text):
        retext = ''
        for idx, char in enumerate(text):
            if not (char == ' ' and text[idx+1] == ' '):
                retext = f'{retext}{char}'
        return retext

    #   Hard feature to include: For not repeating words or blocks in the text.
    def __eliminate_buffer(self, hover_sliced, sliced):
        add_permission = True
        for hover in hover_sliced:
            if sliced == hover:
                add_permission = False
        return add_permission

    def __translate(self, _text_original, model='google'):
        retext = ''
        try:
            [_text, DKT] = capital_replace(_text_original)
        except Exception as exc:
            print(f'{exc}')
            raise

        if model == 'google':
            g_translator = googletrans.Translator(service_urls=['translate.google.com'])
            if _text is None:
                print('Oops, there was an error translating...')
            else:
                try:
                    retext = g_translator.translate(_text).text
                except BaseException:
                    print(f'Traceback: VttReading/__translate: Cannot translate \'{_text}\' '
                          f'from model {model}; maybe too many requests.')
        else:
            print(f'Traceback: VttReading/__translate: No translator model called {model}.')
        _retext = capital_restore(retext, DKT)
        return _retext
# -----------------------------------------------------------
# Main:


if __name__ == '__main__':
    main()
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
