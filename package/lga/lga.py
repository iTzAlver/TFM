# -------------------------------------------------------------------#
#                                                                    #
#    Author:    Alberto Palomo Alonso.                               #
#                                                                    #
#    Git user:  https://github.com/iTzAlver                          #
#    Email:     ialver.p@gmail.com                                   #
#                                                                    #
# -------------------------------------------------------------------#
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
TARGET0 = r'./db/.exported/exported_mtx0.txt'
TARGET1 = r'./db/.exported/exported_mtx1.txt'
TARGET2 = r'./db/.exported/exported_mtx2.txt'
IMAGE_PATH = r'./db/.exported/'


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
def main() -> None:
	m1 = LGA(TARGET2)
	m1.print()
	m1.threshold(0.2)
	m1.print()
	m1.lifegame()
	m1.print()
	return None


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
class LGA:
	"""
	Class LGA (Life Game Algorythm) uses a correlartion matrix and converges the matrix to blocks based on a
	lifegame policy.
	"""
	def __init__(self, path, matrix=None, th=0.0):
		if matrix is None:
			mtx = self._readmtx(path)
			self._mtx = mtx
			self.mtx = mtx
		else:
			self._mtx = matrix
			self.mtx = matrix
		self.name = path.split('/')[-1].split('.')[0]
		self.img = self._mtx2img()
		self.ispadded = False
		self.isthreshed = False
		self.figure = None
		self.th = th

	def threshold(self, th):
		"""
		This method threshold the matrix to 0 for each value lower than the parameter 'th'.
		:param th: Threshold of the matrix.
		:return: This function doesn't return anything.
		"""
		self.th = th
		self.isthreshed = True
		retmat = np.zeros((len(self.mtx), len(self._mtx)), dtype=np.float32)
		for nrow, row in enumerate(self.mtx):
			for ncol, ele in enumerate(row):
				retmat[nrow][ncol] = ele if ele >= th else 0
		self.mtx = retmat

	def reset(self):
		"""
		This method initializes the matrix from its own contruction.
		:return: This function doesn't return anything.
		"""
		self.isthreshed = False
		self.ispadded = False
		self.mtx = self._mtx

	def print(self, showup=True, size=(4.85, 4.3)):
		"""
		This method prints the correlation matrix in orange colors.
		:return: This function doesn't return anything.
		"""
		global IMAGE_PATH
		self.img = self._mtx2img()
		self.figure = plt.figure(figsize=size, dpi=75)
		plt.imshow(self.img)
		img = Image.fromarray(self.img)
		img.save(f'{IMAGE_PATH}{self.name}.png')
		if showup:
			plt.show()
		plt.close()

	def lifegame(self, params=(3, 1, 0.01), maxcount=30, dd=0.0, ss=0.0):
		"""
		This funcion runs a lifegame on the current matrix.
		:param params: Parameters of the lifegame:
			[0]: Minimum number of bounds to become true.
			[1]: Maximum number of bounds to bedome false.
			[2]: Threshold of the matrix.
		:param maxcount: Maximum iterations in steps:
			not using a maxminum count can last forever.
		:param dd: Diagonal kernel weigths.
		:param ss: Self kernel weigths.
		:return: This function doesn't return anything.
		"""
		there_was_a_change = True
		cont = 0
		if not self.isthreshed:
			self.threshold(params[2])
		while there_was_a_change and cont < maxcount:
			cont += 1
			there_was_a_change = self._grow(counter_min=params[0], th=params[2], ss=ss)
		there_was_a_change = True
		cont = 0
		while there_was_a_change:
			cont += 1
			there_was_a_change = self._extinct(counter_min=params[1], th=params[2], ss=ss)
		there_was_a_change = True
		cont = 0
		while there_was_a_change and cont < maxcount:
			cont += 1
			self._grow(params[0], th=params[2], diagonal=True, dd=dd, ss=ss)

	def collapse(self):
		"""
		This function collapses all the pseudo-squares into squares on the diagonal.
		:return: This function returns the squares bounds.
		"""
		mtx = self.mtx
		thematrix = np.zeros((len(mtx), len(mtx)), dtype=np.float32)
		last_block = 0
		bound = []
		lindex = 0
		for index, _ in enumerate(mtx):
			if index > 0:
				if mtx[index][index - 1] > self.th:
					value = 1
				else:
					value = 0
					bound.append([last_block, index - 1])
					last_block = index
				for index2 in range(index - last_block + 1):
					thematrix[index][index - index2] = value
					thematrix[index - index2][index] = value
					thematrix[index][index] = 1
			lindex = index
		thematrix[0][0] = 1
		self.mtx = thematrix
		bound.append([last_block, lindex])
		return bound

	def _mtx2img(self):
		mtx = self.mtx
		thematrix2 = np.zeros((len(mtx), len(mtx), 3), dtype=np.uint8)
		for nrow, row in enumerate(mtx):
			for ncol, element in enumerate(row):
				thematrix2[nrow][ncol][0] = [element * 255 if element > 0 else 0][0]
				thematrix2[nrow][ncol][1] = [element * 100 if element > 0 else 0][0]
				thematrix2[nrow][ncol][2] = 0
		return thematrix2

	def _grow(self, counter_min, th, diagonal=False, anchor=True, selfed=False, dd=0.25, ss=0.5) -> bool:
		changed = False
		mtx = self._pad(self.mtx)
		newmtx = np.zeros((len(mtx), len(mtx)), dtype=np.float32)
		for _nrow, row in enumerate(self.mtx):
			nrow = _nrow + 1
			for _ncol, _ in enumerate(row):
				ncol = _ncol + 1
				ele = mtx[nrow][ncol]
				counter = 0
				if mtx[nrow][ncol - 1] >= th:
					counter += 1
				if mtx[nrow][ncol + 1] >= th:
					counter += 1
				if mtx[nrow - 1][ncol] >= th:
					counter += 1
				if mtx[nrow + 1][ncol] >= th:
					counter += 1

				if diagonal:
					if mtx[nrow - 1][ncol - 1] >= th:
						counter += dd
					if mtx[nrow - 1][ncol + 1] >= th:
						counter += dd
					if mtx[nrow + 1][ncol - 1] >= th:
						counter += dd
					if mtx[nrow + 1][ncol + 1] >= th:
						counter += dd

				if selfed and mtx[nrow][ncol] >= th:
					counter += ss

				if (counter >= counter_min) and ele <= th:
					changed = True
					newmtx[ncol][nrow] = 1
				else:
					newmtx[ncol][nrow] = 1 if ele > th else 0

				if anchor and ncol == nrow:
					newmtx[ncol][nrow] = 1

		self.mtx = self._unpad(newmtx)
		return changed

	def _extinct(self, counter_min, th, diagonal=False, anchor=True, selfed=False, dd=0.25, ss=0.5) -> bool:
		changed = False
		mtx = self._pad(self.mtx)
		newmtx = self._pad(self.mtx)
		for _nrow, row in enumerate(self.mtx):
			nrow = _nrow + 1
			for _ncol, _ in enumerate(row):
				ncol = _ncol + 1
				ele = mtx[nrow][ncol]
				counter = 0
				if mtx[nrow][ncol - 1] >= th:
					counter += 1
				if mtx[nrow][ncol + 1] >= th:
					counter += 1
				if mtx[nrow - 1][ncol] >= th:
					counter += 1
				if mtx[nrow + 1][ncol] >= th:
					counter += 1

				if diagonal:
					if mtx[nrow - 1][ncol - 1] >= th:
						counter += dd
					if mtx[nrow - 1][ncol + 1] >= th:
						counter += dd
					if mtx[nrow + 1][ncol - 1] >= th:
						counter += dd
					if mtx[nrow + 1][ncol + 1] >= th:
						counter += dd

				if selfed and mtx[nrow][ncol] >= th:
					counter += ss

				if (counter <= counter_min) and ele >= th and ncol != nrow:
					newmtx[ncol][nrow] = 0
					changed = True

				if anchor and ncol == nrow:
					newmtx[ncol][nrow] = 1

		self.mtx = self._unpad(newmtx)
		return changed

	def _printo(self, showup=False, size=(4.85, 4.3)):
		global IMAGE_PATH
		mtx = self._mtx
		thematrix2 = np.zeros((len(mtx), len(mtx), 3), dtype=np.uint8)
		for nrow, row in enumerate(mtx):
			for ncol, element in enumerate(row):
				thematrix2[nrow][ncol][0] = [element * 255 if element > 0 else 0][0]
				thematrix2[nrow][ncol][1] = [element * 100 if element > 0 else 0][0]
				thematrix2[nrow][ncol][2] = 0
		img = thematrix2
		fig = plt.figure(figsize=size, dpi=75)
		plt.imshow(img)
		img = Image.fromarray(img)
		img.save(f'{IMAGE_PATH}{self.name}_original.png')
		if showup:
			plt.show()
		plt.close()
		return fig

	@staticmethod
	def _pad(mtx):
		retmat = np.zeros(((len(mtx) + 2), len(mtx) + 2), dtype=np.float32)
		for nrow, row in enumerate(mtx):
			for ncol, ele in enumerate(row):
				retmat[nrow + 1][ncol + 1] = ele
		return retmat

	@staticmethod
	def _unpad(mtx):
		_retmat = np.zeros(((len(mtx) - 2), len(mtx) - 2), dtype=np.float32)
		retmat = np.zeros(((len(mtx) - 2), len(mtx) - 2), dtype=np.float32)
		for nrow, row in enumerate(_retmat):
			for ncol, ele in enumerate(row):
				retmat[nrow][ncol] = mtx[nrow + 1][ncol + 1]
		return retmat

	@staticmethod
	def _readmtx(path):
		with open(path, 'r', encoding='utf-8') as file:
			mymtx = np.loadtxt(file)
		return mymtx
# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#


if __name__ == '__main__':
	main()
# -------------------------------------------------------------------#
#           E   N   D          O   F           F   I   L   E         #
# -------------------------------------------------------------------#
