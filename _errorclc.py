# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
#   Functions zone:
#                                                                       #
#   In this zone all classes and functions are defined:
#                                                                       #
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @punish()
#                                                 #
#   This function modifies the error depending
#   on if its weak or strong.
#                                                 #
#       @inputs:
#           imp: Error in the main error matrix.  #
#
#           punish_multiplier: Weight for strong
#               errors.
#                                                 #
#       @output:
#           Returns the modified error after
#           punish
# - - - - - - - - - - - - - - - - - - - - - - - - #
def punish(imp, punish_multiplier):
    if imp == 1:
        rv = 1
    elif imp == -1:
        rv = 1/punish_multiplier
    else:
        rv = 0
    return rv


# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @calculate_error()
#                                                 #
#   This function counts the errors in the matrix
#   taking into account that is symmetric.        #
#                                                 #
#       @inputs:
#           error_mtx: Punished error matrix.     #
#                                                 #
#       @output:
#           Number of errors counted
#           in the matrix.
# - - - - - - - - - - - - - - - - - - - - - - - - #
def calculate_error(error_mtx):
    size = len(error_mtx)
    total = 0
    for i in range(0, size):
        for j in range(0, i):
            total = total + error_mtx[i][j]
    return total


# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @errors_adj()
#                                                 #
#   This function modifies the errors in order
#   to reduce the weight of all chain generated
#   errors.
#                                                 #
#       @inputs:
#           error_mtx: Punished error matrix.     #
#                                                 #
#           p: Non-punished strong error matrix.  #
#                                                 #
#           n: Non-punished weak error matrix.    #
#                                                 #
#       @output:
#           Returns the adjusted error matrix.    #
# - - - - - - - - - - - - - - - - - - - - - - - - #
def errors_adj(error_mtx, p, n):
    size = len(error_mtx)
    out_error_mtx = error_mtx

    for i in range(0, size):
        total_rowp = sum(p[i])
        total_rown = sum(n[i])
        for j in range(0, size):
            if total_rowp > 1:
                p[i][j] = round(p[i][j]/total_rowp, 3)
            if total_rown > 1:
                n[i][j] = round(n[i][j]/total_rown, 3)

    for i in range(0, size):
        for j in range(0, size):
            out_error_mtx[i][j] = out_error_mtx[i][j]*(min(p[i][j], p[j][i]) + min(n[i][j], n[j][i]))

    return out_error_mtx


# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @CalculateError
#                                                 #
#   This class works on the dataset in order
#   to calculate the error between a calculated
#   matrix and a given GroundTruth matrix.
#                                                 #
#       @inputs:
#           ground_truth: True solution of
#               the matrix.                       #
#                                                 #
#           r: Calculated matrix in previous
#               steps.
#                                                 #
#           pm: Punished multiplier, difference
#               between weak and strong errors.
#                                                 #
#       @objects:
#           size: Size of the matrix.
#                                                 #
#           errors: Error matrix calculated.
#                                                 #
#           errorsp: Strong error matrix.
#                                                 #
#           errorsn: Weak error matrix.
#                                                 #
#           nerr: Number of total errors.
#                                                 #
#           eavg: Number of errors averaged       #
#                 by number of blocks.            #
# - - - - - - - - - - - - - - - - - - - - - - - - #
class CalculateError:

    def __init__(self, ground_truth, r, pm=5):
        self.size = len(r)
        self.errors = list()
        self.errorsp = list()
        self.errorsn = list()
        for i in range(0, self.size):
            lstaux = list()
            lstauxp = list()
            lstauxn = list()
            for j in range(0, self.size):
                calc = ground_truth[i][j] - r[i][j]
                lstaux.append(punish(calc, pm))
                if calc > 0:
                    lstauxp.append(calc)
                    lstauxn.append(0)
                elif calc < 0:
                    lstauxn.append(-calc)
                    lstauxp.append(0)
                else:
                    lstauxp.append(0)
                    lstauxn.append(0)
            self.errorsp.append(lstauxp)
            self.errorsn.append(lstauxn)
            self.errors.append(lstaux)
        self.errors = errors_adj(self.errors, self.errorsp, self.errorsn)
        self.nerr = round(calculate_error(self.errors), 3)
        self.eavg = self.nerr/self.size
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
#   Tree based zone:
#                                                                       #
#   Here we have the tree extrapolation method.
#                                                                       #
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
# - - - - - - - - - - - - - - - - - - - - - - - - #
#   @tree_equivalent_matrix(trees, gt)
#                                                 #
#   This function creates a correlation matrix
#   based on the trees given.
#                                                 #
#       @inputs:
#           trees: List of trees given.           #
#                                                 #
#       @output:
#           Returns the corrleation matrix.       #
# - - - - - - - - - - - - - - - - - - - - - - - - #


def tree_equivalent_matrix(trees):
    """"Getting the size of the matrix"""
    matrix_size = 0
    for tree in trees:
        matrix_size = matrix_size + len(tree.idv)

    mtx = []
    for index in range(matrix_size):
        row = []
        for index in range(matrix_size):
            row.append(0)
        mtx.append(row)

    for tree in trees:
        for id1 in tree.idv:
            for id2 in tree.idv:
                mtx[id1][id2] = 1

    return mtx
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
#   Testbench zone:
#                                                                       #
#   Here we have the main program, testing the functions.
#                                                                       #
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #

import FB_BCM as fb
if __name__ == '__main__':
    myTrees = []
    tree0 = fb.Tree('Arbol 0', 0, 0, 0)
    tree1 = fb.Tree('Arbol 1', 1, 1, 0)
    tree2 = fb.Tree('Arbol 2', 2, 2, 0)
    tree3 = fb.Tree('Arbol 3', 3, 3, 0)
    tree4 = fb.Tree('Arbol 4', 4, 4, 0)
    tree5 = fb.Tree('Arbol 5', 5, 5, 0)
    tree6 = fb.Tree('Arbol 6', 6, 6, 0)
    myTrees = [tree0, tree1, tree2, tree3, tree4, tree5, tree6]
    myTrees = fb.merge_trees(myTrees, [1, 2])
    myTrees = fb.merge_trees(myTrees, [4, 5])
    myTrees = fb.merge_trees(myTrees, [0, 1])
    myTrees2 = []
    for tree in myTrees:
        if tree != []:
            myTrees2.append(tree)

    myMtx = tree_equivalent_matrix(myTrees2)
    print('EOT')










# if __name__ == '__main__':
#     gt = [[1, 1, 1, 1, 1, 0, 0, 0, 0],
#           [1, 1, 1, 1, 1, 0, 0, 0, 0],
#           [1, 1, 1, 1, 1, 0, 0, 0, 0],
#           [1, 1, 1, 1, 1, 0, 0, 0, 0],
#           [1, 1, 1, 1, 1, 0, 0, 0, 0],
#           [0, 0, 0, 0, 0, 1, 1, 0, 0],
#           [0, 0, 0, 0, 0, 1, 1, 0, 0],
#           [0, 0, 0, 0, 0, 0, 0, 1, 1],
#           [0, 0, 0, 0, 0, 0, 0, 1, 1]]
#     R0 = [[1, 1, 1, 1, 1, 0, 0, 0, 0],
#           [1, 1, 1, 1, 1, 0, 0, 0, 0],
#           [1, 1, 1, 1, 1, 0, 0, 0, 0],
#           [1, 1, 1, 1, 1, 0, 0, 0, 0],
#           [1, 1, 1, 1, 1, 0, 0, 0, 0],
#           [0, 0, 0, 0, 0, 1, 1, 0, 0],
#           [0, 0, 0, 0, 0, 1, 1, 0, 0],
#           [0, 0, 0, 0, 0, 0, 0, 1, 1],
#           [0, 0, 0, 0, 0, 0, 0, 1, 1]]
#     R1 = [[1, 1, 1, 1, 0, 0, 0, 0, 0],
#           [1, 1, 1, 1, 0, 0, 0, 0, 0],
#           [1, 1, 1, 1, 0, 0, 0, 0, 0],
#           [1, 1, 1, 1, 0, 0, 0, 0, 0],
#           [0, 0, 0, 0, 1, 0, 0, 0, 0],
#           [0, 0, 0, 0, 0, 1, 1, 0, 0],
#           [0, 0, 0, 0, 0, 1, 1, 0, 0],
#           [0, 0, 0, 0, 0, 0, 0, 1, 1],
#           [0, 0, 0, 0, 0, 0, 0, 1, 1]]
#     R2 = [[1, 1, 1, 1, 1, 1, 0, 0, 0],
#           [1, 1, 1, 1, 1, 1, 0, 0, 0],
#           [1, 1, 1, 1, 1, 1, 0, 0, 0],
#           [1, 1, 1, 1, 1, 1, 0, 0, 0],
#           [1, 1, 1, 1, 1, 1, 0, 0, 0],
#           [1, 1, 1, 1, 1, 1, 1, 0, 0],
#           [0, 0, 0, 0, 0, 1, 1, 0, 0],
#           [0, 0, 0, 0, 0, 0, 0, 1, 1],
#           [0, 0, 0, 0, 0, 0, 0, 1, 1]]
#     R3 = [[1, 1, 1, 1, 0, 0, 0, 0, 0],
#           [1, 1, 1, 1, 0, 0, 0, 0, 0],
#           [1, 1, 1, 1, 0, 0, 0, 0, 0],
#           [1, 1, 1, 1, 0, 0, 0, 0, 0],
#           [0, 0, 0, 0, 1, 1, 1, 0, 0],
#           [0, 0, 0, 0, 1, 1, 1, 0, 0],
#           [0, 0, 0, 0, 1, 1, 1, 0, 0],
#           [0, 0, 0, 0, 0, 0, 0, 1, 1],
#           [0, 0, 0, 0, 0, 0, 0, 1, 1]]
#
#     gt2 = [[1, 1, 1, 0, 0, 0, 1],
#            [1, 1, 1, 0, 0, 0, 1],
#            [1, 1, 1, 1, 0, 0, 1],
#            [0, 0, 1, 1, 0, 0, 0],
#            [0, 0, 0, 0, 1, 1, 0],
#            [0, 0, 0, 0, 1, 1, 0],
#            [1, 1, 1, 0, 0, 0, 1]]
#
#     R02 = [[1, 1, 0, 0, 0, 0, 0],
#            [1, 1, 0, 0, 0, 0, 0],
#            [0, 0, 1, 1, 0, 0, 0],
#            [0, 0, 1, 1, 0, 0, 0],
#            [0, 0, 0, 0, 1, 1, 0],
#            [0, 0, 0, 0, 1, 1, 1],
#            [0, 0, 0, 0, 0, 1, 1]]
#
#     gt3 = [[1, 1, 1, 0, 1, 0],
#            [1, 1, 0, 0, 1, 0],
#            [1, 0, 1, 1, 0, 1],
#            [0, 0, 1, 1, 0, 1],
#            [1, 1, 0, 0, 1, 0],
#            [0, 0, 1, 1, 0, 1]]
#
#     R03 = [[1, 1, 1, 0, 0, 1],
#            [1, 1, 1, 0, 0, 1],
#            [1, 1, 1, 1, 0, 1],
#            [0, 0, 1, 1, 0, 1],
#            [0, 0, 0, 0, 1, 0],
#            [1, 1, 1, 1, 0, 1]]
#
#     dataset = list()
#     dataset.append([gt, R0, 0])
#     dataset.append([gt, R1, 1])
#     dataset.append([gt, R2, 0.2])
#     dataset.append([gt, R3, 1.2])
#     dataset.append([gt2, R02, 2.2-0.33])
#     dataset.append([gt3, R03, 1.4-0.1])
#
#     indexing = 1
#     for dataset_line in dataset:
#         print("Dataset número: ", indexing, "\n")
#         [gtx, Rx, error_gt] = dataset_line
#         ins = CalculateError(gtx, Rx, 5)
#         print("Matriz de errores:")
#         [print(*line) for line in ins.errors]
#         print("\n", "Errores graves")
#         [print(*line) for line in ins.errorsp]
#         print("\n", "Errores leves")
#         [print(*line) for line in ins.errorsn]
#         print("\n", "Error total cometido: ", ins.nerr)
#         if ins.nerr == error_gt:
#             print("Acierto.", "\n----------------------------------------------\n\n")
#         else:
#             if ins.nerr - error_gt >= 0.1:
#                 print("Fallo, esperado: ", error_gt, "Diff: ", abs(ins.nerr - error_gt))
#                 exit(6)
#             else:
#                 print("Acierto. Diff: ", round(abs(ins.nerr - error_gt), 2),
#                       "\n----------------------------------------------\n\n")
#         indexing = indexing + 1
#     print("Todos los test exitosos. Saliendo del testbench...")
