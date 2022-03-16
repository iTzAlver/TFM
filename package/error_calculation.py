# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
import numpy as np

from package import dserial


# -----------------------------------------------------------


def main() -> None:
    groups = [['Hola', 'Te saludo mi amigo', 'Eres lo mejor del mundo'],
              ['Adiós', 'Me despido mi enemigo', 'Eres lo peor del mundo'],
              ['La samba mola'],
              ['Mi pistola dispara balas', 'Balas dispara mi psitola'],
              ['Tres tristes tigres tragan trigo en', 'en donde', 'en un', 'trigal', 'viva el trigo']]
    payloads = ['Hola. Te saludo mi amigo. Eres lo mejor del mundo',
                'Adiós. Me despido mi enemigo. Eres lo peor del mundo',
                'La samba mola',
                'Mi pistola dispara balas. Balas dispara mi psitola. Tres tristes tigres tragan trigo en. en donde. '
                'en un. trigal. viva el trigo']
    e = get_error_matrix(groups, payloads)
    a = sum([max(row) for row in e])
    wl = sum([sum(row) - max(row) for row in e])
    ul = sum([sum(col) - max(col) for col in np.transpose(e)])
    print(f'Correct words: {a}, Wrong labeled: {wl}, Unlabeled: {ul}.')

    filename_tree = r'test_tree'
    filename_groups = r'../db/groundtruth/f1/Julen/1.txt'
    ce = CalculateError(filename_groups, filename_tree)
    print(ce)
    return None


def read_groups(path) -> [[""]]:
    groups = []
    sentences_list = []
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            if '%' in line:
                groups.append(sentences_list)
                sentences_list = []
            else:
                if line != '\n':
                    sentences_list.append(line.strip('\n'))
            if '$' in line:
                vectors = line[1:].split(';')

    vekpop = []
    for vector in vectors:
        tv = vector.split(',')
        groups[int(tv[0])].extend(groups[int(tv[1])])
        vekpop.append(int(tv[1]))

    for idx, popping in enumerate(vekpop):
        groups.pop(popping - idx)

    return groups


def get_error_matrix(groups, payloads):
    e = np.zeros([len(payloads), len(groups)])
    for ng, group in enumerate(groups):
        for sentence in group:
            for nt, payload in enumerate(payloads):
                if sentence.strip('.') in payload.strip('.'):
                    e[nt][ng] += len(sentence.split(' '))
    return e


class CalculateError:
    def __init__(self, *args, **kwargs):  # (path for groups, path for trees)
        groups = read_groups(args[0])
        trees = dserial.read_tree(args[1])
        self.results = {}

        do_f1, do_f, do_recall, do_windiff = True, True, True, False
        for key, item in kwargs.items():
            if key == 'f1' and isinstance(item, bool):
                do_f1 = item
            if key == 'f' and isinstance(item, bool):
                do_f = item
            if key == 'recall' and isinstance(item, bool):
                do_recall = item
            if key == 'windiff' and isinstance(item, bool):
                do_windiff = item

        self.E = get_error_matrix(groups, [tree.payload for tree in trees])
        self.A = sum([max(row) for row in self.E])
        self.WL = sum([sum(row) - max(row) for row in self.E])
        self.UL = sum([sum(col) - max(col) for col in np.transpose(self.E)])

        if do_f1:
            self.results['f1'] = self.f1()
        if do_f:
            self.results['f'] = self.f()
        if do_recall:
            self.results['recall'] = self.recall()
        if do_windiff:
            self.results['windiff'] = self.windiff()

    def f1(self):
        term = (self.WL + self.UL)/(2*self.A)
        return 1/(term + 1)

    def f(self):
        return self.A/(self.A + self.WL)

    def recall(self):
        return self.A/(self.A + self.UL)

    def windiff(self):
        return -1

    def get_results(self):
        return tuple(self.results.items())

    def __repr__(self):
        __text = f'Results of the error calculation:\n'
        for key, item in self.results.items():
            __text = f'{__text}{key} \t= {item}\n'
        return __text
# -----------------------------------------------------------
# Main:


if __name__ == '__main__':
    main()

# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
