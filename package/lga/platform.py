# -------------------------------------------------------------------#
#                                                                    #
#    Author:    Alberto Palomo Alonso.                               #
#                                                                    #
#    Git user:  https://github.com/iTzAlver                          #
#    Email:     ialver.p@gmail.com                                   #
#                                                                    #
# -------------------------------------------------------------------#
from tkinter import END, NORMAL, DISABLED
from tkinter import Tk, LabelFrame, Text, Label, Checkbutton, BooleanVar, filedialog
from package.styles import ColorStyles, HoverButton
from package.lga.lga import LGA
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
ICO_LOCATION = r'./.multimedia/isdefeico.ico'
NAME_LOCATION = r'./db/.exported/'


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
def main() -> None:
	root_node = Tk()
	MainWindow(root_node)
	root_node.iconbitmap(ICO_LOCATION)
	root_node.configure()
	root_node.mainloop()


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
class MainWindow:
	def __init__(self, master):
		self.master = master
		self.master.title("Intra-day clustering GUI.")
		self.master.geometry('910x1025')
		self.colors = ColorStyles
		self.bounds = []
		# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		self._framed = LabelFrame(self.master, width=900, height=110, text='Matrix import:')
		self._framed.pack()
		self._framed.place(x=5, y=5)
		self._labelimport = HoverButton(self._framed, text='Import matrix', bg=ColorStyles.red, width=20, heigh=4,
		                                command=self._lookformatrix)
		self._labelimport.pack()
		self._labelimport.place(x=10, y=5)
		self._currentlabel = Label(self._framed, text='No matrix available...')
		self._currentlabel.pack()
		self._currentlabel.place(x=170, y=5)
		self._currentlabel_info = Label(self._framed, text='')
		self._currentlabel_info.pack()
		self._currentlabel_info.place(x=190, y=25)
		self._currentlabel_info2 = Label(self._framed, text='')
		self._currentlabel_info2.pack()
		self._currentlabel_info2.place(x=190, y=55)
		# - - - - - - - - - - - - - - - - - - - - -
		self.canvas = None
		self._canvasframe = LabelFrame(self.master, width=900, height=900)
		self._canvasframe.pack()
		self._canvasframe.place(x=5, y=120)
		# - - - - - - - - - - - - - - - - - - - - -
		self._frameact = LabelFrame(self._framed, width=490, height=90)
		self._frameact.pack()
		self._frameact.place(x=400, y=-4)
		self._thresh = HoverButton(self._frameact, text='Thresh:', bg=ColorStyles.orange, width=10, heigh=2,
		                           command=self._threshmat)
		self._thresh.pack()
		self._thresh.place(x=5, y=0)
		self._threshinfo = Text(self._frameact, height=1, width=8)
		self._threshinfo.pack()
		self._threshinfo.place(x=100, y=10)
		self._threshinfo.insert(END, '0.18')
		self._resetb = HoverButton(self._frameact, text='Reset matrix', bg=ColorStyles.red, width=24, heigh=1,
		                           command=self._reset)
		self._resetb.pack()
		self._resetb.place(x=5, y=50)
		self._growb = HoverButton(self._frameact, text='Grow:', bg=ColorStyles.blue, width=10, heigh=1,
		                          command=self._grow)
		self._growb.pack()
		self._growb.place(x=200, y=10)

		self._extinctb = HoverButton(self._frameact, text='Extinct:', bg=ColorStyles.blue, width=10, heigh=1,
		                             command=self._extinct)
		self._extinctb.pack()
		self._extinctb.place(x=200, y=50)

		self._growinfo = Text(self._frameact, height=1, width=5)
		self._growinfo.pack()
		self._growinfo.place(x=300, y=12)
		self._growinfo.insert(END, '2.75')

		self._extictinfo = Text(self._frameact, height=1, width=5)
		self._extictinfo.pack()
		self._extictinfo.place(x=300, y=52)
		self._extictinfo.insert(END, '1')

		self._useselfv = BooleanVar()
		self._useself = Checkbutton(self._frameact, text='Use state value?', variable=self._useselfv)
		self._useself.pack()
		self._useself.place(x=360, y=5)

		self._usediagv = BooleanVar()
		self._usediag = Checkbutton(self._frameact, text='Use diagonals?', variable=self._usediagv)
		self._usediag.pack()
		self._usediag.place(x=360, y=25)

		self._diagpon = Text(self._frameact, height=1, width=5)
		self._diagpon.pack()
		self._diagpon.place(x=375, y=55)
		self._diagpon.insert(END, '0.25')

		self._selfpon = Text(self._frameact, height=1, width=5)
		self._selfpon.pack()
		self._selfpon.place(x=430, y=55)
		self._selfpon.insert(END, '0.5')

		self._labeliff = Label(self._frameact, text='D')
		self._labeliff.pack()
		self._labeliff.place(x=360, y=55)
		self._labelifi = Label(self._frameact, text='S')
		self._labelifi.pack()
		self._labelifi.place(x=416, y=55)

		# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		self._watchb = HoverButton(self._framed, text='Watch', bg=ColorStyles.blue, width=5, heigh=1,
		                           command=self._watch)
		self._watchb.pack()
		self._watchb.place(x=350, y=55)
		self._wflag = False

		self._zipb = HoverButton(self._framed, text='Zip', bg=ColorStyles.blue, width=5, heigh=1,
		                         command=self._zip)
		self._zipb.pack()
		self._zipb.place(x=350, y=27)

		self._dob = HoverButton(self._framed, text='Run', bg=ColorStyles.blue, width=5, heigh=1,
		                        command=self._do)
		self._dob.pack()
		self._dob.place(x=350, y=0)

		self._resetb['state'] = DISABLED
		self._threshinfo['state'] = DISABLED
		self._thresh['state'] = DISABLED
		self._growb['state'] = DISABLED
		self._extinctb['state'] = DISABLED
		self._useself['state'] = DISABLED
		self._usediag['state'] = DISABLED
		self._extictinfo['state'] = DISABLED
		self._growinfo['state'] = DISABLED
		self._diagpon['state'] = DISABLED
		self._selfpon['state'] = DISABLED
		self._labelifi['state'] = DISABLED
		self._labeliff['state'] = DISABLED
		self._watchb['state'] = DISABLED
		self._zipb['state'] = DISABLED
		self._dob['state'] = DISABLED

	def _lookformatrix(self):
		filename = filedialog.askopenfilename(filetypes=[('C. Matrix', '*.txt')], initialdir=NAME_LOCATION)
		self.matmat = LGA(filename)
		self._resetb['state'] = NORMAL
		self._threshinfo['state'] = NORMAL
		self._thresh['state'] = NORMAL
		self._growb['state'] = NORMAL
		self._extinctb['state'] = NORMAL
		self._useself['state'] = NORMAL
		self._usediag['state'] = NORMAL
		self._extictinfo['state'] = NORMAL
		self._growinfo['state'] = NORMAL
		self._diagpon['state'] = NORMAL
		self._selfpon['state'] = NORMAL
		self._labelifi['state'] = NORMAL
		self._labeliff['state'] = NORMAL
		self._watchb['state'] = NORMAL
		self._zipb['state'] = NORMAL
		self._dob['state'] = NORMAL
		self._setinfo()

	def _setinfo(self):
		self._currentlabel.config(text=f'Current matrix: {self.matmat.name}')
		self._currentlabel_info.config(text=f'Matrix size: ({len(self.matmat.mtx)}x{len(self.matmat.mtx)})\n'
		                                    f'Is threshed: ({self.matmat.isthreshed})\n')
		__text = '['
		for cont, bound in enumerate(self.bounds):
			__text = f'{__text}{bound[1]}, '
			if cont % 5 == 4:
				__text = f'{__text}\n'
		if len(__text) > 1:
			__text = f'{__text[:-2]}]'
		else:
			__text = '[]'
		self._currentlabel_info2.config(text=f'Bounds: {__text}')
		self._updateimg()

	def _updateimg(self):
		if self.canvas is not None:
			self.canvas.get_tk_widget().pack_forget()
		self.matmat.print(showup=False, size=(12, 12))
		self.canvas = FigureCanvasTkAgg(self.matmat.figure, master=self._canvasframe)
		self.canvas.draw()
		self.canvas.get_tk_widget().pack()

	def _threshmat(self):
		th = float(self._threshinfo.get('1.0', END + '-1c').strip('\n'))
		if th < 0:
			th *= -1
		if th > 1:
			th /= 100
		self.matmat.threshold(th)
		self._setinfo()

	def _reset(self):
		self.matmat.reset()
		self._setinfo()

	def _grow(self):
		cnt_min = float(self._growinfo.get('1.0', END + '-1c').strip('\n'))
		th = float(self._threshinfo.get('1.0', END + '-1c').strip('\n'))
		selfpon = float(self._selfpon.get('1.0', END + '-1c').strip('\n'))
		diagpon = float(self._diagpon.get('1.0', END + '-1c').strip('\n'))
		if th < 0:
			th *= -1
		if th > 1:
			th /= 100
		self.matmat._grow(cnt_min, th=th, diagonal=self._usediagv.get(), selfed=self._useselfv.get(), ss=selfpon,
		                  dd=diagpon)
		self._setinfo()

	def _extinct(self):
		cnt_min = float(self._extictinfo.get('1.0', END + '-1c').strip('\n'))
		th = float(self._threshinfo.get('1.0', END + '-1c').strip('\n'))
		selfpon = float(self._selfpon.get('1.0', END + '-1c').strip('\n'))
		diagpon = float(self._diagpon.get('1.0', END + '-1c').strip('\n'))
		if th < 0:
			th *= -1
		if th > 1:
			th /= 100
		self.matmat._extinct(cnt_min, th=th, diagonal=self._usediagv.get(), selfed=self._useselfv.get(), ss=selfpon,
		                     dd=diagpon)
		self._setinfo()

	def _watch(self):
		if self._wflag:
			self._wflag = False
			self._setinfo()
		else:
			self._wflag = True
			if self.canvas is not None:
				self.canvas.get_tk_widget().pack_forget()
			self.matmat.print(showup=False, size=(12, 12))
			self.canvas = FigureCanvasTkAgg(self.matmat._printo(size=(12, 12)), master=self._canvasframe)
			self.canvas.draw()
			self.canvas.get_tk_widget().pack()

	def _zip(self):
		self.bounds = self.matmat.collapse()
		self._setinfo()

	def _do(self):
		cnt_min = float(self._extictinfo.get('1.0', END + '-1c').strip('\n'))
		cnt_max = float(self._growinfo.get('1.0', END + '-1c').strip('\n'))
		th = float(self._threshinfo.get('1.0', END + '-1c').strip('\n'))
		selfpon = float(self._selfpon.get('1.0', END + '-1c').strip('\n'))
		diagpon = float(self._diagpon.get('1.0', END + '-1c').strip('\n'))
		if th < 0:
			th *= -1
		if th > 1:
			th /= 100
		self.matmat.lifegame(params=(cnt_max, cnt_min, th), ss=selfpon, dd=diagpon)
		self._setinfo()


# -------------------------------------------------------------------#
#   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x   x    #
# -------------------------------------------------------------------#
if __name__ == '__main__':
	main()
# -------------------------------------------------------------------#
#           E   N   D          O   F           F   I   L   E         #
# -------------------------------------------------------------------#
