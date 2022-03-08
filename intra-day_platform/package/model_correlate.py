# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
import matplotlib.pyplot as plt
import networkx as nx
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   Global models and variables.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
spanish_model1 = 'hiiamsid/sentence_similarity_spanish_es'
base_model = SentenceTransformer(spanish_model1)
model_use = spacy.load('es_core_news_lg')
thresholding = 0.2

TREE_FIG_PATH = r'./.multimedia/trees/Day'
FLAG_COMPUTE_PATH = r'.\.multimedia\cflag'


class LoadModel:
    def __init__(self, model_target):
        self.model = SentenceTransformer(model_target)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   Tree:
#
#       ITEMS:
#   nTree:          Tree identifier.
#   payload:        Text payload.
#   idv:            Vector of sentences ID.
#   pt:             Correlation power.
#   day:            Day of the tree.
#   payload_div:    Payload divided by sentences.
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class Tree:
    def __init__(self, payload='', id=-1, ntree=-1, day=-1, pt=-1, timing=0, model=None):
        self.nTree = ntree
        self.payload = payload
        self.idv = [id]
        self.pt = pt
        self.day = day
        self.payload_div = []
        self.payload_div.append(payload)
        self.code = model.encode(self.payload)
        self.timing = timing
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# FB-BCM: Favourite Based- Bidirectional Connection Merging.
#
#   fbbcm():
#
#                   INPUT:
#       sentences_vector: List of sentences to be managed.
#       threshold: Threshold of the method.
#       day: Day indexing.
#
#                   OUTPUT:
#       trees: Trees merged by the method.
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def fbbcm(sentences_vector, threshold, day, correlation_model='bert', showup=False, timing=None, xmodel=None):
    if xmodel is None:
        model = base_model
    else:
        model = xmodel
    # Step 1: Generate trees.
    trees = []

    # See if we want to compute graphics.
    ffile = open(FLAG_COMPUTE_PATH)
    savefig_int = int(ffile.readline())
    if savefig_int == 1:
        savefig = True
    else:
        savefig = False
    ffile.close()

    for _item, item in enumerate(sentences_vector):
        if timing is not None:
            trees.append(Tree(item, _item, _item, day, timing=timing[_item], model=model))
        else:
            trees.append(Tree(item, _item, _item, day, model=model))

    status = 'continue'
    it = 0

    while status == 'continue':
        con_mtx = _genconmatv2(trees, threshold, correlation_model=correlation_model, xmodel=model)

        if savefig:
            show_connections(con_mtx, it, day, showup=showup)

        there_was_merge = False
        for _row in range(len(con_mtx)):
            for _col in range(len(con_mtx[_row])):
                if con_mtx[_row][_col] >= threshold and con_mtx[_col][_row] >= threshold:
                    trees = merge_trees(trees, [trees[_row].nTree, trees[_col].nTree], xmodel=model)
                    con_mtx[_row][_col] = -1
                    con_mtx[_col][_row] = -1
                    there_was_merge = True

        acc_trees = []
        for _item in range(len(trees)):
            if trees[_item]:
                acc_trees.append(trees[_item])
        trees = acc_trees

        for _item in range(len(trees)):
            trees[_item].nTree = _item

        if not there_was_merge:
            status = 'end'

        it = it+1

    for a_tree in trees:
        a_tree.pt = corr_p(a_tree, xmodel=model)

    return trees
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   _genconmat():
#
#                   INPUT:
#       trees:      List of trees to connect.
#       threshold:  Threshold of correlation with BERT.
#
#                   OUTPUT:
#       con_mtx:    Connection matrix.
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def _genconmat(trees, threshold, correlation_model='bert', xmodel=None):
    global model_use
    model = xmodel
    sentences_vector = []
    for _item in range(len(trees)):
        sentences_vector.append(trees[_item].payload)

    code = model.encode(sentences_vector)
    mtx = []
    con_mtx = []
    cnt = 0

    for sentence1, code1 in zip(sentences_vector, code):
        mtx_row = []
        con_mtx_row = []

        if correlation_model == 'bert':
            for sentence2, code2 in zip(sentences_vector, code):
                value = cosine_similarity(code1.reshape(1, -1), code2.reshape(1, -1))[0][0]
                mtx_row.append(value)
        elif correlation_model == 'use':
            for sentence2, code2 in zip(sentences_vector, code):
                nlp_model_sentence1 = model_use(sentence1)
                nlp_model_sentence2 = model_use(sentence2)
                value = nlp_model_sentence1.similarity(nlp_model_sentence2)
                mtx_row.append(value)

        aux_row = mtx_row
        aux_row[cnt] = 0
        for _item in range(len(aux_row)):
            if aux_row[_item] == max(aux_row) and aux_row[_item] >= threshold:
                con_mtx_row.append(round(aux_row[_item], 3))
            else:
                con_mtx_row.append(0.000)

        mtx.append(mtx_row)
        con_mtx.append(con_mtx_row)
        cnt = cnt + 1

    return con_mtx
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   _genconmat():
#
#                   INPUT:
#       trees:      List of trees to connect.
#       threshold:  Threshold of correlation with BERT.
#
#                   OUTPUT:
#       con_mtx:    Connection matrix.
#
#       WHATS NEW?
#
#       v2:         Semimatrix correlation + no enconding per iteration!
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def _genconmatv2(trees, threshold, correlation_model='bert', xmodel=None):
    global model_use
    model = xmodel
    sentences_vector = []
    code = []
    for _item in range(len(trees)):
        sentences_vector.append(trees[_item].payload)
        code.append(trees[_item].code)

    mtx = []
    con_mtx = []
    cnt = 0

    sentence_matrix = []
    code_matrix = []
    for sentence1, code1 in zip(sentences_vector, code):
        sentence_matrix_row = []
        code_matrix_row = []
        for sentence2, code2 in zip(sentences_vector, code):
            sentence_matrix_row.append([sentence1, sentence2])
            code_matrix_row.append([code1, code2])
        sentence_matrix.append(sentence_matrix_row)
        code_matrix.append(code_matrix_row)

    itobj = range(len(code_matrix))

    for index1 in itobj:
        mtx_row = []
        con_mtx_row = []

        if correlation_model == 'bert':
            for index2 in itobj:
                if index1 < index2:
                    code1 = code_matrix[index1][index2][0]
                    code2 = code_matrix[index1][index2][1]
                    value = cosine_similarity(code1.reshape(1, -1), code2.reshape(1, -1))[0][0]
                    mtx_row.append(value)
                else:
                    if index1 == index2:
                        mtx_row.append(0)
                    else:
                        mtx_row.append(mtx[index2][index1])

        elif correlation_model == 'use':
            for index2 in itobj:
                if index1 < index2:
                    sentence1 = str(sentence_matrix[index1][index2][0])
                    sentence2 = str(sentence_matrix[index1][index2][1])
                    nlp_model_sentence1 = model_use(sentence1)
                    nlp_model_sentence2 = model_use(sentence2)
                    value = nlp_model_sentence1.similarity(nlp_model_sentence2)
                    mtx_row.append(value)
                else:
                    if index1 == index2:
                        mtx_row.append(0)
                    else:
                        mtx_row.append(mtx[index2][index1])

        aux_row = mtx_row
        aux_row[cnt] = 0
        for _item in range(len(aux_row)):
            if aux_row[_item] == max(aux_row) and aux_row[_item] >= threshold:
                con_mtx_row.append(round(aux_row[_item], 3))
            else:
                con_mtx_row.append(0.000)

        mtx.append(mtx_row)
        con_mtx.append(con_mtx_row)
        cnt = cnt + 1

    return con_mtx
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   merge_trees():
#
#                   INPUT:
#       trees:      List of trees to merge.
#       tree_ids:   Vector with the tree IDs to merge.
#       oim:        If one in the middle correction is set.
#
#                   OUTPUT:
#       new_:trees: List of trees merged.
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def merge_trees_v1(trees, tree_ids):
    new_trees = []
    ids = tree_ids
    ids.sort()
    target_id = ids[0]
    ids.pop(0)

    for _item in range(len(trees)):
        if _item not in ids and trees[_item] != []:
            if trees[_item].nTree == target_id:
                new_tree = trees[_item]
                for other_tree in ids:
                    new_tree = merge_payload(new_tree, trees[other_tree])

                new_trees.append(new_tree)
            else:
                new_trees.append(trees[_item])
        else:
            new_trees.append([])

    return new_trees
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   merge_trees():
#
#                   INPUT:
#       trees:      List of trees to merge.
#       tree_ids:   Vector with the tree IDs to merge.
#       oim:        If one in the middle correction is set.
#
#                   OUTPUT:
#       new_:trees: List of trees merged.
#
#       WHATS NEW?:
#
#       v2 : Now it saves the component of the code vector!
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def merge_trees(trees, tree_ids, xmodel=None):
    model = xmodel
    new_trees = []
    ids = tree_ids
    ids.sort()
    target_id = ids[0]
    ids.pop(0)

    for _item in range(len(trees)):
        if _item not in ids and trees[_item] != []:
            if trees[_item].nTree == target_id:
                new_tree = trees[_item]
                for other_tree in ids:
                    new_tree = merge_payload(new_tree, trees[other_tree])
                    new_tree.code = model.encode(new_tree.payload)

                new_trees.append(new_tree)
            else:
                new_trees.append(trees[_item])
        else:
            new_trees.append([])

    return new_trees
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   corr_p():
#
#                   INPUT:
#       tree:       Tree to calculate the correlation power.
#       mode:       Mode of calcultating the correlation power.
#
#                   OUTPUT:
#       pt:         Correlation power of the tree.
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def corr_p(tree, mode='prime', xmodel=None):
    rx = correlate(split_payload(tree.payload), xmodel=xmodel)
    T = len(rx)
    if mode == 'prime':

        if T > 1:
            acc = 0
            for x in range(0, T-1):
                for y in range(x+1, T):
                    acc = acc + rx[x][y]**2
            pt = acc * 2 / (T * (T - 1))
        else:
            pt = 1.0

    elif mode == 'sym':

        acc = 0
        for x in range(0, T-1):
            for y in range(x, T):
                acc = acc + rx[x][y]**2
        pt = acc * 2 / (T * (T + 1))

    elif mode == 'original':

        acc = 0
        for x in range(0, T-1):
            for y in range(0, T-1):
                acc = acc + rx[x][y]**2
        pt = acc * 2 / (T * T)

    else:
        print('Traceback: corr_p: Error in mode')
        return -1

    return pt
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   slplit_payload():
#
#                   INPUT:
#       payload:            Payload to be splitted by '.'.
#
#                   OUTPUT:
#       sentences_new:      List of sentences in the payload.
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def split_payload(payload):
    sentences = payload.split('.')
    sentences_new = []
    for sentence in sentences:
        if sentence != '':
            if sentence[0] == ' ':
                sentence_new = sentence[1:len(sentence)]
            else:
                sentence_new = sentence
            sentence_new = sentence_new + '.'
            sentences_new.append(sentence_new)

    return sentences_new
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   correlate():
#
#                   INPUT:
#       sentences_vector:   List of sentences to be correlated.
#
#                   OUTPUT:
#       mtx:                Correlation matrix in the sentences provided.
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def correlate(sentences_vector, xmodel=None):
    model = xmodel
    if model is None:
        print('Model is not loaded.')
        raise
    code = model.encode(sentences_vector)
    mtx = []
    for _, code1 in zip(sentences_vector, code):
        mtx_row = []
        for _, code2 in zip(sentences_vector, code):
            value = cosine_similarity(code1.reshape(1, -1), code2.reshape(1, -1))[0][0]
            mtx_row.append(value)
        mtx.append(mtx_row)
    return mtx
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   merge_payload():
#
#                   INPUT:
#       target_tree:    Main tree and target of the merge.
#       merged_tree:    Tree whose payload is going to be merged.
#
#                   OUTPUT:
#       new_tree:   Target_tree with new payload, sorted by sentences ID.
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def merge_payload(target_tree, merged_tree):
    new_tree = target_tree
    for new_payload_div in merged_tree.payload_div:
        new_tree.payload_div.append(new_payload_div)
    for id_item in merged_tree.idv:
        new_tree.idv.append(id_item)
    zipped = zip(new_tree.payload_div, new_tree.idv)
    zipped = sorted(zipped, key=lambda x: x[1])
    [new_tree.payload_div, new_tree.idv] = list(zip(*zipped))
    new_tree.idv = list(new_tree.idv)
    new_tree.payload_div = list(new_tree.payload_div)
    pyld = ''
    for division in new_tree.payload_div:
        pyld = pyld + ' ' + division
    new_tree.payload = pyld
    new_tree.timing = target_tree.timing + merged_tree.timing
    return new_tree
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   show_connections():
#
#                   INPUT:
#       connection_mtx:      Connection matrix.
#
#                   DO:
#       __do__:    Shows up a connection graph.
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def show_connections(connection_mtx, iteration, day, showup=False):
    plt.figure(figsize=(9.25, 5), dpi=80)
    plt.title('Day ' + str(day) + ', iteration ' + str(iteration))
    G = nx.DiGraph()
    lst = list(range(len(connection_mtx[0])))
    for i in range(len(lst)):
        lst[i] = str(lst[i])
    G.add_nodes_from(lst)
    for i in range(len(connection_mtx)):
        for j in range(len(connection_mtx)):
            if connection_mtx[i][j] >= 0.05:
                G.add_edge(str(i), str(j))
    nx.draw_networkx(G)
    plt.savefig(TREE_FIG_PATH + str(day) + '/tree_state_' + str(iteration) + '.png', format="PNG")
    if showup:
        plt.show(block=False)
    plt.close()
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
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   __main__():
#
#                   DO:
#       __do__:     Tests the methods and print the trees generated.
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


if __name__ == '__main__':

    sentences = [
        'Juan y Luisa se van a comprar a la joyería.',                  # 00
        'Dos diamantes valen 500 dólares.',                             # 01
        'Luisa se despide de Juan tras comprar los diamantes.',         # 02
        'Bernardo se ha puesto a gritar.',                              # 03
        'Los gritos han despertado a todo el barrio de Lavapiés.',      # 04
        'Los vecinos están indignados.',                                # 05
        'Muchos de los vecinos han puesto denuncias.',                  # 06
        'Las joyas suben de precio.',                                   # 07
        'Las estrellas brillan por la noche.',                          # 08
        'El juez ha dictaminado prisión y multa para Bernardo.',        # 09
        'Las multas por escándalo público son superiores a 600 euros.'  # 10
    ]

    threshold_fine = 0.2
    n_trees = fbbcm(sentences, threshold_fine, 0, showup=False)
    print('Potencia de correlacción:')
    for tree in n_trees:
        print('Árbol ID ' + str(tree.nTree) + ':\tpt = ' + str(tree.pt))

    for tree in n_trees:
        print('Árbol ID ' + str(tree.nTree) + ':\tPayload = ' + str(tree.payload))

    threshold_wrong = 0.3
    n_trees = fbbcm(sentences, threshold_wrong, 0, showup=False)
    print('Potencia de correlacción:')
    for tree in n_trees:
        print('Árbol ID ' + str(tree.nTree) + ':\tpt = ' + str(tree.pt))

    for tree in n_trees:
        print('Árbol ID ' + str(tree.nTree) + ':\tPayload = ' + str(tree.payload))


    threshold_use = 0.6
    n_trees = fbbcm(sentences, threshold_use, 0, showup=True, correlation_model='use')
    print('Potencia de correlacción:')
    for tree in n_trees:
        print('Árbol ID ' + str(tree.nTree) + ':\tpt = ' + str(tree.pt))

    for tree in n_trees:
        print('Árbol ID ' + str(tree.nTree) + ':\tPayload = ' + str(tree.payload))

    tested = [0, 1, 2, 3, 4]
    print(tested[1:])
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
