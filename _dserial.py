DATA_PATH =  r'./trees/'


class EmptyTree:
    def __init__(self):
        self.nTree = -1
        self.idv = []
        self.pt = -1
        self.payload = ''
        self.day = -1
        self.payload_div = []


def write_tree(object_array, name):
    global DATA_PATH
    myfile = open(DATA_PATH + name + '.3s', "w")
    for tree in object_array:
        myfile.writelines('{' + '\n')
        myfile.writelines('\tday:' + str(tree.day) + '\n')
        myfile.writelines('\tntree:' + str(tree.nTree) + '\n')
        myfile.writelines('\tpt:' + str(tree.pt) + '\n')
        myfile.writelines('\tpayload:' + str(tree.payload) + '\n')
        myfile.writelines('\tvek:' + '\n')
        for item in range(len(tree.idv)):
            myfile.writelines('\t\t' + str(tree.idv[item]) + '\n')
            myfile.writelines('\t\t\t' + str(tree.payload_div[item]) + '\n')
        myfile.writelines('}' + '\n')
        myfile.writelines('\n')
    return myfile


def read_tree(name):
    global DATA_PATH
    the_trees = []
    myfile = open(DATA_PATH + name + '.3s', "r")
    a_tree = EmptyTree()
    for line in myfile:
        if line[0] == '{':
            a_tree = EmptyTree()
        elif line[0] == '\t':
            if line[1] == '\t':
                if line[2] == '\t':
                    a_tree.payload_div.append(line[3:len(line)-1])
                else:
                    a_tree.idv.append(int(line[2:len(line)-1]))
            elif line[1:5] == 'day:':
                rest = int(line[5:])
                a_tree.day = int(rest)
            elif line[1:7] == 'ntree:':
                rest = int(line[7:])
                a_tree.nTree = int(rest)
            elif line[1:4] == 'pt:':
                rest = float(line[4:])
                a_tree.pt = float(rest)
            elif line[1:9] == 'payload:':
                rest = line[9:]
                a_tree.payload = rest


        elif line[0] == '}':
            the_trees.append(a_tree)
    return the_trees

