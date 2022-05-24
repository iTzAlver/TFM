# -------------------------------------------------------------------#
#                                                                    #
#    Author:    Alberto Palomo Alonso.                               #
#                                                                    #
#    Git user:  https://github.com/iTzAlver                          #
#    Email:     ialver.p@gmail.com                                   #
#                                                                    #
# -------------------------------------------------------------------#
import matplotlib.pyplot as plt
import numpy as np
import random


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
def main() -> None:
	fig, axs = plt.subplots(ncols=3)
	slices = np.arange(0, 1, 0.01)
	a = np.array([random.random() for _ in range(100)])
	b = np.array([random.random() for _ in range(100)])
	c = np.array([random.random() for _ in range(100)])
	d = np.array([random.random() for _ in range(100)])
	axs[0].plot(slices, a, '--k', lw=0.2)
	axs[0].plot(slices, b, '--k', lw=0.2)
	axs[0].plot(slices, c, '--k', lw=0.2)
	axs[0].plot(slices, d, 'k', lw=1)
	axs[0].set_title('WindowDiff score for each database.')
	axs[0].set_xlabel('Betta')
	axs[0].set_ylabel('WindownDiff')
	axs[0].set_xlim([0, 1])
	axs[0].set_ylim([0, 1])
	axs[0].grid()
	plt.show()
	return None


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
class Main:
	def __init__(self):
		pass


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
if __name__ == '__main__':
	main()
# -------------------------------------------------------------------#
#           E   N   D          O   F           F   I   L   E         #
# -------------------------------------------------------------------#
