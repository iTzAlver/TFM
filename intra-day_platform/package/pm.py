# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
class Pbmm:
    def __init__(self, matrix, **kwargs):
        self.items = {"th": 0.18, "oim": 1}
        for key, value in kwargs.items():
            self.items[key] = value
        self.segmentation = self.PBMM_get_segments(matrix, self.items["oim"], self.items["th"])

    def PBMM_get_segments(self, matrix, oim_stages, th) -> []:
        """"This function uses a correlation matrix [matrix] and
        inferences through all the matrix saving the index where
        consecutive blocks have correlation. It is considered
        correlated when the value of the matrix is greater or
        equal to the threshold provided [th]. If a block is not
        correlated but next ones are, the [oim_stages] blocks
        not correlated before are now considered correlated."""
        segmentation = []
        index1 = 0
        failed_stages = 0

        while index1 < len(matrix):
            index2 = index1 + 1
            safeguard_index = index1

            while index2 < len(matrix):
                corr_vector = matrix[index2][index1:index2]
                avg = sum(corr_vector)/len(corr_vector)
                if avg >= th:
                    safeguard_index = index2
                    failed_stages = 0
                else:
                    failed_stages += 1
                    if failed_stages > oim_stages:
                        segmentation.append([index1, safeguard_index])
                        index1 = safeguard_index
                        failed_stages = 0
                        break
                index2 += 1
                if index2 == len(matrix):
                    segmentation.append([index1, safeguard_index])
                    index1 = safeguard_index + 1
                    index2 = index1 + 1
                    if index2 == len(matrix):
                        segmentation.append([index1, index1])
            index1 += 1
        return segmentation

    def merge_segmentation(self, phrases):
        intro = []
        for segz in self.segmentation:
            intro.append(segz[0])

        merged = []
        straigth = '$'
        for nphrase, phrase in enumerate(phrases):
            if nphrase in intro:
                if straigth != '$':
                    merged.append(straigth)
                straigth = ''
            if straigth != '':
                straigth = f'{straigth}. {phrase}'
            else:
                straigth = phrase
        merged.append(straigth)
        return merged
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   VALIDATION OF THE METHOD PRUPOSED - 3 MATRIX            #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #


if __name__ == '__main__':

    print('Testing method with name {x}'.format(x=__name__))
    mtx = [[1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
          [1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
          [1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
          [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
          [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
          [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
          [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]]
    seg = Pbmm(matrix=mtx, oim=1, th=0.5)
    if seg.segmentation == [[0, 2], [3, 3], [4, 4], [5, 5], [6, 6]]:
        print('Correct validarion at {result}'.format(result=seg.segmentation))
    else:
        print('Inorrect validarion at {result} vs [[0, 2], [3, 3], [4, 4], [5, 5], [6, 6]]'.format(result=seg.segmentation))

    mtx= [[1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
          [1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
          [1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
          [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
          [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0],
          [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0],
          [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0]]
    seg = Pbmm(matrix=mtx, oim=1, th=0.5)
    phr = ['Frase1', 'Frase2', 'Frase3', 'Frase4', 'Frase5', 'Frase6', 'Frase7']
    print(seg.merge_segmentation(phr))
    if seg.segmentation == [[0, 2], [3, 3], [4, 6]]:
        print('Correct validarion at {result}'.format(result=seg.segmentation))
    else:
        print('Inorrect validarion at {result} vs [[0, 2], [3, 3], [4, 6]]'.format(result=seg.segmentation))

    mtx= [[1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
          [1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
          [1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0],
          [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0],
          [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0],
          [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0],
          [0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0]]
    seg = Pbmm(matrix=mtx, oim=2, th=0.5)
    if seg.segmentation == [[0, 2], [3, 6]]:
        print('Correct validarion at {result}'.format(result=seg.segmentation))
    else:
        print('Inorrect validarion at {result} vs [[0, 2], [3, 6]]'.format(result=seg.segmentation))
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
