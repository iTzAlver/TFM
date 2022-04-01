# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
import os
ORIGINAL_DIR = r'../window/subtitulos_fechas/'
TARGET_DIR = f'../window/ending/'


# -----------------------------------------------------------
def main() -> None:
    ending = readwindow('1901')
    readwindow('1902', concat=ending)
    return


def readwindow(init, concat=0, typed='21h') -> int:
    items = list(filter(lambda x: init in x and typed not in x, os.listdir(ORIGINAL_DIR)))
    if not concat:
        [os.remove(f'{TARGET_DIR}{trash}') for trash in os.listdir(TARGET_DIR)]
    count = 0
    for count, item in enumerate(items):
        with open(f'{ORIGINAL_DIR}{item}', 'r', encoding='utf-8') as file_in:
            with open(f'{TARGET_DIR}{count + 1 + concat}.vtt', 'w', encoding='utf-8') as file_out:
                file_out.write(file_in.read())
    return count + 1
   
# -----------------------------------------------------------
# Main:


if __name__ == '__main__':
    main()

# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
