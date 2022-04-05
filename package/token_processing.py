# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
import os

import numpy as np


# -----------------------------------------------------------
def main() -> None:
    return
    
    
class TokenProcessing:
    def __init__(self, **kwargs):
        for key, item in kwargs.items():
            if key == 'target':
                self.target = item
            elif key == 'decorrelation':
                self.decorrelation = 1 - item/100
                if self.decorrelation > 1:
                    self.decorrelation = 1
                elif self.decorrelation < 0:
                    self.decorrelation = 0
            elif key == 'tokens':
                self.posprocessing_b = item

        self.placeholders = []
        self.payload = []
        self.dcr = []
        self.diffs = []

    def preprocessing(self):
        if self.target.split('.')[-1] == 'txt':
            subtargets = [self.target.split('/')[-1]]
            self.target = self.target.strip(f'/{subtargets[0]}')
        else:
            subtargets = os.listdir(self.target)
            # Sort them clearly:
            subtargets_zip = zip([int(subtarget_[:-4]) for subtarget_ in subtargets], subtargets)
            subtargets = list([thetuple[1] for thetuple in sorted(subtargets_zip)])

        indexes = list([int(subtarget_[:-4]) for subtarget_ in subtargets])
        self.placeholders = []
        self.payload = []
        defectos = 1
        for ix, subtarget in enumerate(subtargets):
            subtarget_path = f'{self.target}/{subtarget}'
            placehold = []
            lines = []

            while defectos + ix != indexes[ix]:
                self.payload.append([])
                defectos += 1

            with open(subtarget_path, 'r', encoding='utf-8') as file:
                for idx, line in enumerate(file):
                    if line[0] == '$':
                        placehold.append(idx)
                        lines.append(line[1:].strip('\n'))
                    elif line[0] == '%':
                        thelist = line.split(' ')
                        thelist[0] = thelist[0][2:]
                        thelist = [float(val[:-1]) for val in thelist]
                        self.diffs.append(thelist)
                    else:
                        lines.append(line.strip('\n'))
            self.placeholders.append(placehold)
            self.payload.append(lines)
        return self.payload

    def posprocessing(self, corrmatrix, placeholder_id, get_time=False):
        placeholder = self.placeholders[placeholder_id]
        segmentation = []
        sized = len(corrmatrix)
        self.dcr = self.decorrelation*np.ones((sized, sized))

        for idx, place in enumerate(placeholder[:-1]):
            segmentation.append([place, placeholder[idx+1] - 1])
        segmentation.append([placeholder[-1], sized - 1])

        for segment in segmentation:
            base = segment[0]
            ending = segment[1]
            for index1 in range(ending - base + 1):
                for index2 in range(ending - base + 1):
                    self.dcr[base + index2][base + index1] = 1

        r = np.array(corrmatrix)
        mtx = r*self.dcr
        mtx[mtx < 0] = 0

        if get_time:
            retval = (mtx, self.diffs[placeholder_id])
        else:
            retval = mtx

        return retval
   
# -----------------------------------------------------------
# Main:


if __name__ == '__main__':
    main()
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
