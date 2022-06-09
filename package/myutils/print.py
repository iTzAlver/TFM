# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
from .baselinecolors import Bcolors


# -----------------------------------------------------------
class LogTracker:
    def __init__(self, file):
        self.basefile = file

    def print(self, text, color='') -> None:
        try:
            with open(self.basefile, 'a', encoding='utf-8') as file:
                file.writelines(text)
                file.writelines('\n')
        except IOError as ex:
            print(f'Exception opening file {self.basefile} ocurred: {ex}')

        col = Bcolors.HEADER
        if 'b' or 'B' in color:
            col = Bcolors.OKBLUE
        elif 'c' or 'C' in color:
            col = Bcolors.OKCYAN
        elif 'r' or 'R' in color:
            col = Bcolors.FAIL
        elif 'g' or 'G' in color:
            col = Bcolors.OKGREEN
        elif 'o' or 'O' in color:
            col = Bcolors.WARNING
        elif 'u' or 'U' in color:
            col = Bcolors.UNDERLINE
        elif 'k' or 'K' in color:
            col = Bcolors.BOLD

        print(f'{col}{text}{Bcolors.ENDC}')
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
