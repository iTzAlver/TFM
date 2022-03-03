# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
import csv
from random import choice
from tkinter import filedialog

import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


# -----------------------------------------------------------


def main_validation() -> None:
    mtz = [[1.0, 0.1, 0.7, 0.4, 0.1, 0.1],
           [0.1, 1.0, 0.8, 0.4, 0.1, 0.1],
           [0.7, 0.8, 1.0, 0.2, 0.1, 0.1],
           [0.4, 0.4, 0.2, 1.0, 0.1, 0.1],
           [0.1, 0.1, 0.1, 0.1, 1.0, 0.6],
           [0.1, 0.1, 0.1, 0.1, 0.6, 1.0]]
    kms = CalculateKmeans(mtz)
    print(kms.rbi)
    print(kms.derivative)
    plt.plot(kms.rbi, label='Parecido')
    plt.plot(kms.derivative, label='Derivada')
    plt.plot(-0.5*np.ones(len(kms.derivative)), label='Umbral para derivada')
    plt.legend(loc='upper right')
    print(kms)
    return


def bd_validation() -> None:
    mtz = []
    with open(filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')]), 'r') as f:
        reader = csv.reader(f)
        mtz_aux = list(reader)
        for i in range(len(mtz_aux)):
            if (i % 2) == 0:
                mtz.append(mtz_aux[i])
    kms = CalculateKmeans(mtz, epoch=20000)
    print(kms.rbi)
    print(kms.derivative)
    plt.plot(kms.rbi, label='Parecido')
    plt.plot(kms.derivative, label='Derivada')
    plt.plot(-0.5*np.ones(len(kms.derivative)), label='Umbral para derivada')
    plt.legend(loc='upper right')
    print(kms)
    return

def vector_validation() -> None:
    mtx = []
    the_max = 0
    the_min = 0
    with open(filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')]), 'r') as f:
        reader = csv.reader(f)
        mtz_aux = list(reader)
        for i in range(len(mtz_aux)):
            if (i % 2) == 0:
                for j in range(len(mtz_aux[i])):
                    mtz_aux[i][j] = float(mtz_aux[i][j])
                    if mtz_aux[i][j] > the_max:
                        the_max = mtz_aux[i][j]
                    if mtz_aux[i][j] < the_min:
                        the_min = mtz_aux[i][j]
                mtx.append(mtz_aux[i])

    for index1 in range(len(mtx)):
        for index2 in range(len(mtx[index1])):
            mtx[index1][index2] = (mtx[index1][index2] - the_min)/(the_max - the_min)

    kms = CalculateKmeans(mtx, epoch=2000, krange=10)
    print(kms.rbi)
    print(kms.derivative)
    plt.plot(kms.rbi, label='Parecido')
    plt.plot(kms.derivative, label='Derivada')
    plt.plot(-0.5*np.ones(len(kms.derivative)), label='Umbral para derivada')
    plt.legend(loc='upper right')
    print(kms)
    return

    
class CalculateKmeans:
    def __init__(self, mtx, epoch=300, krange=None):
        if krange is None:
            krange = len(mtx)
        self.mtx = mtx
        self.kmeans = []
        self.rbi = []
        for index in range(krange+1):
            if index > 0:
                kms_priv = KMeans(n_clusters=index, max_iter=epoch)
                kms_priv.fit(mtx)
                self.kmeans.append(kms_priv)
                self.rbi.append(kms_priv.inertia_)

        self.derivative = self.__derivative(self.rbi)
        self.jambu_elbow = self.__jambu(self.derivative, 0.5)

        self.kms = self.kmeans[self.jambu_elbow]

    def __repr__(self):
        __text = ''
        for kmeans_instance in self.kmeans:
            __text += 'Instance ' + str(max(kmeans_instance.labels_) + 1) + ': ' + str(kmeans_instance.labels_) + '\n'
        __text.join('Jambu: ' + str(self.jambu_elbow) + '\n')
        __text.join('In Jambu clustering: ' + str(self.kms.labels_) + '\n')
        try:
            self.__display_graphics()
        except:
            print('Error displaying graphics.')
        return __text

    def __derivative(self, vector) -> []:
        derivative = [-1]
        for i in range(len(vector)-1):
            derivative.append(vector[i+1] - vector[i])
        derivative[0] = derivative[1] - 1
        return derivative

    def __jambu(self, derivative, threshold=0.5) -> int:
        for index in range(len(derivative)):
            if -derivative[index] < threshold:
                return index-1
        return 0

    def __display_graphics(self) -> None:
        pca = PCA(n_components=2)
        pca_kms = pca.fit_transform(self.mtx)

        fig = plt.figure(figsize=(6, 6))
        axis = fig.add_subplot(1, 1, 1)
        axis.set_xlabel('X space', fontsize=20)
        axis.set_ylabel('Y space', fontsize=20)
        axis.set_title('Mapa KMeans', fontsize=25)
        colores = []
        for index in range(len(self.kms.labels_)):
            thecolor = "#"+''.join([choice('ABCDEF0123456789') for _ in range(3)]*2)
            colores.append(thecolor)
        colores_array = np.array(colores)
        axis.scatter(x=pca.components_[0],
                     y=pca.components_[1],
                     c=colores_array[self.kms.labels_],
                     s=50)
        plt.show()

   
# -----------------------------------------------------------
# Main:


if __name__ == '__main__':
    #main_validation()
    #bd_validation()
    vector_validation()
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
