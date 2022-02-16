import os
from tkinter import NORMAL, StringVar
from tkinter import Tk, Button, Label, Text, ttk, END, Checkbutton, BooleanVar, LabelFrame, Entry, DISABLED

from PIL import Image, ImageTk

import main_program as mp

RESULTS_PATH = r'.\Results\\'
LOG_PATH = r'.\logs\logfile.txt'
CASES_PATH = r'.\data'
VTT_PATH = r'.\Documents\\'
GRAPHICS_PATH = r'.\.multimedia\graph\Day'
COMPUTE_FLAG_PATH = r'.\.multimedia\cflag'
TREES_PATH = r'.\trees\\'
TREES_IMAGE_PATH = r'.\.multimedia\trees\Day'


def getTrees():
    lis = os.listdir(TREES_PATH)
    rmv = []
    for item in range(len(lis)):
        if lis[item].find('.3s') != -1:
            rmv.append(lis[item])
    return rmv

def getResults():
    lis = os.listdir(RESULTS_PATH)
    rmv = []
    for item in range(len(lis)):
        if lis[item].find('words') == -1 and lis[item].find('raw') == -1 and lis[item].find('block') == -1:
            rmv.append(lis[item])
    return rmv


def getVTT(vtt_path):
    lis = os.listdir(vtt_path)
    rmv = []
    for item in range(len(lis)):
        rmv.append(lis[item])
    return rmv


def getWords():
    lis = os.listdir(RESULTS_PATH)
    rmv = []
    for item in range(len(lis)):
        if lis[item].find('words') != -1:
            rmv.append(lis[item])
    return rmv


def getRaw():
    lis = os.listdir(RESULTS_PATH)
    rmv = []
    for item in range(len(lis)):
        if lis[item].find('raw') != -1:
            rmv.append(lis[item])
    return rmv


def getTiBlocks():
    lis = os.listdir(RESULTS_PATH)
    rmv = []
    for item in range(len(lis)):
        if lis[item].find('block') != -1:
            rmv.append(lis[item])
    return rmv


def getCases():
    return os.listdir(CASES_PATH)


def execution(case, method, oim, symc, hamming, unchained, pm, oimstages, th, npnn, segtype, textype):
    if method == 'null' or case == 'null':
        return ['method error', 'case error']
    npnn2 = npnn.split(',')
    np = int(round(float(npnn2[0])))
    nn = int(round(float(npnn2[1])))
    [ret1, ret2] = mp.packed(case, method, oim, symc, hamming, unchained, pm, oimstages, th, np, nn, segtype, textype)
    if not hamming:
        ret1 = 'N.A / N.A'
    else:
        ret1 = str(round(ret1, 2)) + ' %'
    if not unchained:
        ret2 = 'N.A / N.A'
    else:
        ret2 = str(round(ret2, 2)) + ' %'
    return [ret1, ret2]


class Ventana:

    def __init__(self, master):
        self.master = master
        master.title("AUTOCORRELATION GUI")
        master.geometry('1600x800')
        self.selected_now = 'null'
        self.method_selected_var = 'null'
        self.oim_var = BooleanVar()
        self.correction_var = BooleanVar()
        self.unchained_var = BooleanVar()
        self.hamming_var = BooleanVar()
        self.pm_var = 4
        self.oimstages_var = 1
        self.th_var = 0.5
        self.npnn_var = '2,1'
        self.compgrap = BooleanVar()
        self.day_selected = 0
        self.whattoprint = 'matrix'
        #---------------------------------------------------------------------------#
        #   Segentation Options:
        #---------------------------------------------------------------------------#
        self.text_options = ['Word string', 'Raw blocks']
        self.segmentation_options = ['Temporal', 'FB-BCM']
        self.segmentation_type = self.segmentation_options[0]
        self.text_type = self.text_options[0]

        self.labelframe_seg = LabelFrame(master, text="Segmentation options", width=645/2, height=70)
        self.labelframe_seg.pack()
        self.labelframe_seg.place(x=480, y=10)

        self.etiqueta_segtype = Label(self.labelframe_seg, text="Segmentation type:")
        self.etiqueta_segtype.pack()
        self.etiqueta_segtype.place(x=10, y=0)
        self.seg_type = ttk.Combobox(self.labelframe_seg, state='readonly')
        self.seg_type["values"] = self.segmentation_options
        self.seg_type.place(x=130, y=0)
        self.seg_type.bind("<<ComboboxSelected>>", self.seg_type_selected)

        self.etiqueta_textused = Label(self.labelframe_seg, text="Text type:")
        self.etiqueta_textused.pack()
        self.etiqueta_textused.place(x=10, y=25)
        self.text_used = ttk.Combobox(self.labelframe_seg, state='readonly')
        self.text_used["values"] = self.text_options
        self.text_used.place(x=130, y=25)
        self.text_used.bind("<<ComboboxSelected>>", self.text_type_selected)
        #---------------------------------------------------------------------------#
        #   Graphic Options:
        #---------------------------------------------------------------------------#
        self.labelframe_gra = LabelFrame(master, text="Graphic options", width=320, height=70)
        self.labelframe_gra.pack()
        self.labelframe_gra.place(x=815, y=10)

        self.grap_comp = Checkbutton(self.labelframe_gra, text='Compute graphics', variable=self.compgrap)
        self.grap_comp.pack()
        self.grap_comp.place(x=5, y=0)
        self.grap_comp.select()
        #---------------------------------------------------------------------------#
        #   Matrix selection:
        #---------------------------------------------------------------------------#
        self.etiqueta3 = Label(master, text="SELECT AN AUTOCORRELATION MATRIX:")
        self.etiqueta3.pack()
        self.etiqueta3.place(x=10, y=10)

        self.lista = ttk.Combobox(master, state='readonly')
        self.lista["values"] = getResults()
        self.lista.place(x=250, y=10)
        self.lista.bind("<<ComboboxSelected>>", self.results_selected)
        #---------------------------------------------------------------------------#
        #   Launched and launch parameters:
        #---------------------------------------------------------------------------#
        self.botonEjecutar = Button(master, text="LAUNCH PARAMETERS", command=self.execute)
        self.botonEjecutar.config(bg="light cyan")
        self.botonEjecutar.pack()
        self.botonEjecutar.place(x=20, y=40)

        self.labelframe0 = LabelFrame(master, text="Launched parameters", width=435, height=65)
        self.labelframe0.pack()
        self.labelframe0.place(x=10, y=75)

        self.loglaunch = Label(self.labelframe0, text="CASE\tMETHD\tOIM\tSYM\tHAMM\tUNCH\tPM\tSTG\tT/PN")
        self.loglaunch.pack()
        self.loglaunch.place(x=10, y=0)

        self._text = StringVar()
        self._text.set("------\t---------\t-----\t-----\t--------\t-------\t----\t-----\t---")
        self.loglaunch_val = Label(self.labelframe0, textvar=self._text)
        self.loglaunch_val.pack()
        self.loglaunch_val.place(x=10, y=20)
        #---------------------------------------------------------------------------#
        #   Method and case:
        #---------------------------------------------------------------------------#
        self.list_of_methods = ['npnn', 'use', 'bert']

        self.etiqueta5 = Label(master, text="SELECT A CASE TO EXECUTE:")
        self.etiqueta5.pack()
        self.etiqueta5.place(x=10, y=150)

        self.cases = ttk.Combobox(master, state='readonly')
        self.cases["values"] = getCases()
        self.cases.place(x=250, y=150)
        self.cases.bind("<<ComboboxSelected>>", self.case_selected)

        self.etiqueta5 = Label(master, text="SELECT A METHOD TO EXECUTE:")
        self.etiqueta5.pack()
        self.etiqueta5.place(x=10, y=180)

        self.method = ttk.Combobox(master, state='readonly')
        self.method["values"] = self.list_of_methods
        self.method.place(x=250, y=180)
        self.method.bind("<<ComboboxSelected>>", self.method_selected)
        #---------------------------------------------------------------------------#
        #   Log file and exit:
        #---------------------------------------------------------------------------#
        self.botonCerrar = Button(master, text="EXIT PROGRAM", command=master.quit)
        self.botonCerrar.config(bg="pink")
        self.botonCerrar.pack()
        self.botonCerrar.place(x=1160, y=10)

        self.botonPrint = Button(master, text="PRINT LOG FILE (NO LAUNCH)", command=self.print_logfile)
        self.botonPrint.config(bg="light yellow")
        self.botonPrint.pack()
        self.botonPrint.place(x=250, y=40)

        self.etiqueta4 = Label(master, text="LOG FILE CONTENT:")
        self.etiqueta4.pack()
        self.etiqueta4.place(x=1330, y=30)

        self.texto_log = Text(master, height=26, width=50)
        self.texto_log.pack()
        self.texto_log.place(x=1160, y=50)
        #---------------------------------------------------------------------------#
        #   Graphics and matrix - Centerplace:
        #---------------------------------------------------------------------------#
        self.tabctrl_mbx = ttk.Notebook(master, height=350, width=650)
        self.tab0_mbx = ttk.Frame(self.tabctrl_mbx, height=350, width=650)
        self.tab1_mbx = ttk.Frame(self.tabctrl_mbx, height=350, width=650)
        self.tab2_mbx = ttk.Frame(self.tabctrl_mbx, height=350, width=650)
        self.tab3_mbx = ttk.Frame(self.tabctrl_mbx, height=350, width=650)
        self.tab4_mbx = ttk.Frame(self.tabctrl_mbx, height=350, width=650)
        self.tab5_mbx = ttk.Frame(self.tabctrl_mbx, height=350, width=650)
        self.tabctrl_mbx.add(self.tab0_mbx, text="R(Block_x,Block_y)        -       GroundTruth(Block_x, Block_y)")
        self.tabctrl_mbx.add(self.tab1_mbx, text='Graphics 1 ')
        self.tabctrl_mbx.add(self.tab2_mbx, text='Graphics 2 ')
        self.tabctrl_mbx.add(self.tab3_mbx, text='Graphics 3 ')
        self.tabctrl_mbx.add(self.tab4_mbx, text='Graphics 4 ')
        self.tabctrl_mbx.add(self.tab5_mbx, text='Graphics 5 ')
        self.tabctrl_mbx.pack()
        self.tabctrl_mbx.place(x=480, y=90)

        self.texto_matriz = Text(self.tab0_mbx, height=22, width=81)
        self.texto_matriz.pack()
        self.texto_matriz.place(x=0, y=0)
        #---------------------------------------------------------------------------#
        #   Error correction:
        #---------------------------------------------------------------------------#
        self.labelframe = LabelFrame(master, text="Error correction methods", width=200, height=90)
        self.labelframe.pack()
        self.labelframe.place(x=10, y=210)

        self.oim = Checkbutton(self.labelframe, text='One in the middle process',
                               variable=self.oim_var, command=self.oimchange)
        self.oim.pack()
        self.oim.place(x=0, y=10)
        self.oim.select()

        self.sym = Checkbutton(self.labelframe, text='Symmetry correction process', variable=self.correction_var,
                               command=self.correctionchange)
        self.sym.pack()
        self.sym.place(x=0, y=40)
        self.sym.select()
        #---------------------------------------------------------------------------#
        #   Error calculation:
        #---------------------------------------------------------------------------#
        self.labelframe2 = LabelFrame(master, text="Error calculation methods", width=210, height=90)
        self.labelframe2.pack()
        self.labelframe2.place(x=230, y=210)

        self.unch = Checkbutton(self.labelframe2, text='Calculate unchained errors', variable=self.unchained_var,
                                command=self.symchange)
        self.unch.place(x=0, y=10)
        self.unch.select()

        self.hamm = Checkbutton(self.labelframe2, text='Calculate hamming errors', variable=self.hamming_var)
        self.hamm.place(x=0, y=40)
        self.hamm.select()
        #---------------------------------------------------------------------------#
        #   Extra parameters:
        #---------------------------------------------------------------------------#
        self.labelframe3 = LabelFrame(master, text="Extra parameters", width=240, height=150)
        self.labelframe3.pack()
        self.labelframe3.place(x=10, y=305)

        self.oimlabel = Label(self.labelframe3, text='One in the middle stages: ')
        self.oimlabel.pack()
        self.oimlabel.place(x=10, y=10)
        self.oimstages = Entry(self.labelframe3, width=8)
        self.oimstages.pack()
        self.oimstages.place(x=160, y=10)
        self.oimstages.insert(-1, '1')

        self.pmlabel = Label(self.labelframe3, text='Punish multiplier: ')
        self.pmlabel.pack()
        self.pmlabel.place(x=10, y=40)
        self.pm = Entry(self.labelframe3, width=8)
        self.pm.pack()
        self.pm.place(x=160, y=40)
        self.pm.insert(-1, '4')

        self.thlabel = Label(self.labelframe3, text='Threshold: ')
        self.thlabel.pack()
        self.thlabel.place(x=10, y=70)
        self.th = Entry(self.labelframe3, width=8)
        self.th.pack()
        self.th.place(x=160, y=70)
        self.th.insert(-1, '0.5')
        self.th['state'] = DISABLED
        self.thlabel['state'] = DISABLED

        self.npnnlabel = Label(self.labelframe3, text='ProperNouns, Nouns: ')
        self.npnnlabel.pack()
        self.npnnlabel.place(x=10, y=100)
        self.npnn = Entry(self.labelframe3, width=8)
        self.npnn.pack()
        self.npnn.place(x=160, y=100)
        self.npnn.insert(-1, '2,0')
        self.npnn['state'] = DISABLED
        self.npnnlabel['state'] = DISABLED
        #---------------------------------------------------------------------------#
        #   Box results:
        #---------------------------------------------------------------------------#
        self.labelframe4 = LabelFrame(master, text="Results", width=180, height=150)
        self.labelframe4.pack()
        self.labelframe4.place(x=260, y=305)

        self.labelR1 = Label(self.labelframe4, text="Mean hamming error:")
        self.labelR1.pack()
        self.labelR1.place(x=20, y=5)

        self.RHamming = StringVar()
        self.RHamming.set("N.A / N.A")
        self.labelR3 = Label(self.labelframe4, textvariable=self.RHamming)
        self.labelR3.pack()
        self.labelR3.place(x=55, y=30)

        self.labelR2 = Label(self.labelframe4, text="Mean unchained error:")
        self.labelR2.pack()
        self.labelR2.place(x=20, y=60)

        self.RUnchained = StringVar()
        self.RUnchained.set("N.A / N.A")
        self.labelR4 = Label(self.labelframe4, textvariable=self.RUnchained)
        self.labelR4.pack()
        self.labelR4.place(x=55, y=85)
        #---------------------------------------------------------------------------#
        #   Text book:
        #---------------------------------------------------------------------------#
        self.tabctrl = ttk.Notebook(master, height=380, width=1595)
        self.tabV = ttk.Frame(self.tabctrl, height=380, width=1595)
        self.tab0 = ttk.Frame(self.tabctrl, height=380, width=1595)
        self.tab1 = ttk.Frame(self.tabctrl, height=380, width=1595)
        self.tab2 = ttk.Frame(self.tabctrl, height=380, width=1595)
        self.tabctrl.add(self.tabV, text='VTT files')
        self.tabctrl.add(self.tab0, text='Raw text')
        self.tabctrl.add(self.tab1, text='Text in blocks')
        self.tabctrl.add(self.tab2, text='Word string')
        self.tabctrl.pack()
        self.tabctrl.place(x=0, y=465)

        self.texto_palabras = Text(self.tab2, height=19, width=200)
        self.texto_palabras.pack()
        self.texto_palabras.place(x=0, y=0)

        self.texto_crudo = Text(self.tab0, height=19, width=200)
        self.texto_crudo.pack()
        self.texto_crudo.place(x=0, y=0)

        self.texto_bloques = Text(self.tab1, height=19, width=200)
        self.texto_bloques.pack()
        self.texto_bloques.place(x=0, y=0)

        self.text_vtt = Text(self.tabV, height=19, width=200)
        self.text_vtt.pack()
        self.text_vtt.place(x=0, y=0)
    #---------------------------------------------------------------------------#
    #   After - Selecting results:
    #---------------------------------------------------------------------------#
    def results_selected(self, event):
        self.texto_matriz.delete('1.0', END)
        self.texto_palabras.delete('1.0', END)
        self.texto_crudo.delete('1.0', END)
        self.texto_bloques.delete('1.0', END)
        self.text_vtt.delete('1.0', END)

        second_string = self.lista.get()
        MTX_PATH = RESULTS_PATH + second_string
        fil = open(MTX_PATH)
        for line in fil:
            self.texto_matriz.insert(END, line)

        mtx_words = getResults()
        idx = mtx_words.index(second_string)

        list_words = getWords()
        WDS_PATH = RESULTS_PATH + list_words[idx]
        fil = open(WDS_PATH)
        for line in fil:
            self.texto_palabras.insert(END, line)

        list_raw = getRaw()
        RAW_PATH = RESULTS_PATH + list_raw[idx]
        fil = open(RAW_PATH)
        for line in fil:
            self.texto_crudo.insert(END, line)

        list_blocks = getTiBlocks()
        BKS_PATH = RESULTS_PATH + list_blocks[idx]
        fil = open(BKS_PATH)
        for line in fil:
            self.texto_bloques.insert(END, line + '\n')

        selected_m = second_string.split('_')
        selected = selected_m[0]
        self.day_selected = selected_m[2]
        num_sel = str(int(self.day_selected) + 1)
        VTTs_PATH = VTT_PATH + selected + r'\\'
        list_vtt = getVTT(VTTs_PATH)
        selected_idx = 0
        for i in range(len(list_vtt)):
            stringsk = list_vtt[i]
            stringsk = stringsk[0:len(stringsk)-4]
            debg = (stringsk == num_sel)
            if debg:
                selected_idx = i
        VTTs_PATH = VTT_PATH + selected + r'\\' + list_vtt[selected_idx]
        fil = open(VTTs_PATH, encoding="utf-8")
        for line in fil:
            self.text_vtt.insert(END, line)


        GRAPHICS_PATH_CURRENT = GRAPHICS_PATH + self.day_selected + r'\\'
        indir = os.listdir(GRAPHICS_PATH_CURRENT)

        self.myLabels = []
        self.myGraphs = []
        self.myExtraLabel = []
        cnt = 0
        ffile = open(COMPUTE_FLAG_PATH)
        fact = int(ffile.readline())

        for object in indir:
            index = int(object[0:len(object)-4])
            index2 = index % 4
            index3 = index / 4

            if index3 < 1:
                current_tab = self.tab1_mbx
            elif index3 < 2:
                current_tab = self.tab2_mbx
            elif index3 < 3:
                current_tab = self.tab3_mbx
            elif index3 < 4:
                current_tab = self.tab4_mbx
            elif index3 < 5:
                current_tab = self.tab5_mbx
            else:
                print('Error in tab selection for graphics: raise')
                raise

            if index2 == 0 or index2 == 2:
                currentx = 5
            else:
                currentx = 330
            if index2 == 0 or index2 == 1:
                currenty = 5
            else:
                currenty = 180

            size = 300, 300
            img = Image.open(GRAPHICS_PATH_CURRENT + object)
            img.thumbnail(size, Image.ANTIALIAS)
            self.myGraphs.append(ImageTk.PhotoImage(img))
            self.myLabels.append(Label(current_tab, image=self.myGraphs[cnt]))
            self.myLabels[cnt].pack()
            self.myLabels[cnt].place(x=currentx, y=currenty)
            if fact == 0:
                self.myExtraLabel.append(Label(current_tab, text='OUT OF DATE'))
                self.myExtraLabel[cnt].pack()
                self.myExtraLabel[cnt].place(x=currentx+120, y=currenty+75)

            cnt = cnt + 1


    def trees_selected(self, event):
        self.texto_matriz.delete('1.0', END)
        self.texto_palabras.delete('1.0', END)
        self.texto_crudo.delete('1.0', END)
        self.texto_bloques.delete('1.0', END)
        self.text_vtt.delete('1.0', END)

        second_string = self.lista.get()
        MTX_PATH = TREES_PATH + second_string
        fil = open(MTX_PATH)
        for line in fil:
            self.texto_matriz.insert(END, line)

        mtx_words = getTrees()
        idx = mtx_words.index(second_string)

        list_words = getWords()
        WDS_PATH = RESULTS_PATH + list_words[idx]
        fil = open(WDS_PATH)
        for line in fil:
            self.texto_palabras.insert(END, line)

        list_raw = getRaw()
        RAW_PATH = RESULTS_PATH + list_raw[idx]
        fil = open(RAW_PATH)
        for line in fil:
            self.texto_crudo.insert(END, line)

        list_blocks = getTiBlocks()
        BKS_PATH = RESULTS_PATH + list_blocks[idx]
        fil = open(BKS_PATH)
        for line in fil:
            self.texto_bloques.insert(END, line + '\n')

        selected_m = second_string.split('_')
        selected = selected_m[0]
        day_selected_extension = selected_m[2].split('.')
        self.day_selected = day_selected_extension[0]
        num_sel = str(int(self.day_selected) + 1)
        VTTs_PATH = VTT_PATH + selected + r'\\'
        list_vtt = getVTT(VTTs_PATH)
        selected_idx = 0
        for i in range(len(list_vtt)):
            stringsk = list_vtt[i]
            stringsk = stringsk[0:len(stringsk)-4]
            debg = (stringsk == num_sel)
            if debg:
                selected_idx = i
        VTTs_PATH = VTT_PATH + selected + r'\\' + list_vtt[selected_idx]
        fil = open(VTTs_PATH, encoding="utf-8")
        for line in fil:
            self.text_vtt.insert(END, line)


        GRAPHICS_PATH_CURRENT = TREES_IMAGE_PATH + self.day_selected + r'\\'
        indir = os.listdir(GRAPHICS_PATH_CURRENT)

        self.myLabels = []
        self.myGraphs = []
        self.myExtraLabel = []
        cnt = 0
        ffile = open(COMPUTE_FLAG_PATH)
        fact = int(ffile.readline())

        for object in indir:
            aux_index = object.split('_')
            aux_index = aux_index[2]
            aux_index = aux_index.split('.')
            index = int(aux_index[0])
            index2 = index % 4
            index3 = index / 4

            if index3 < 1:
                current_tab = self.tab1_mbx
            elif index3 < 2:
                current_tab = self.tab2_mbx
            elif index3 < 3:
                current_tab = self.tab3_mbx
            elif index3 < 4:
                current_tab = self.tab4_mbx
            elif index3 < 5:
                current_tab = self.tab5_mbx
            else:
                print('Error in tab selection for graphics: raise')
                raise

            if index2 == 0 or index2 == 2:
                currentx = 5
            else:
                currentx = 330
            if index2 == 0 or index2 == 1:
                currenty = 5
            else:
                currenty = 180

            size = 300, 300
            img = Image.open(GRAPHICS_PATH_CURRENT + object)
            img.thumbnail(size, Image.ANTIALIAS)
            self.myGraphs.append(ImageTk.PhotoImage(img))
            self.myLabels.append(Label(current_tab, image=self.myGraphs[cnt]))
            self.myLabels[cnt].pack()
            self.myLabels[cnt].place(x=currentx, y=currenty)
            if fact == 0:
                self.myExtraLabel.append(Label(current_tab, text='OUT OF DATE'))
                self.myExtraLabel[cnt].pack()
                self.myExtraLabel[cnt].place(x=currentx+120, y=currenty+75)

            cnt = cnt + 1
    #---------------------------------------------------------------------------#
    #   After - Selecting execution launch:
    #---------------------------------------------------------------------------#
    def execute(self):
        self.pm_var = float(self.pm.get())
        self.oimstages_var = int(round(float(self.oimstages.get())))
        self.th_var = float(self.th.get())
        self.npnn_var = self.npnn.get()

        if self.method_selected_var == 'use':
            self._text.set(str(self.case_selected_var) + '\t' + str(self.method_selected_var) + '\t' + str(self.oim_var.get()) + '\t' + \
                str(self.correction_var.get()) + '\t' + str(self.hamming_var.get()) + '\t' + str(self.unchained_var.get()) + '\t' + \
                str(self.pm_var) + '\t' + str(self.oimstages_var) + '\t' + str(self.th_var))

        else:
            self._text.set(str(self.case_selected_var) + '\t' + str(self.method_selected_var) + '\t' + str(self.oim_var.get()) + '\t' + \
                str(self.correction_var.get()) + '\t' + str(self.hamming_var.get()) + '\t' + str(self.unchained_var.get()) + '\t' + \
                str(self.pm_var) + '\t' + str(self.oimstages_var) + '\t' + self.npnn_var)

        [ret1, ret2] = execution(self.case_selected_var,
                                 self.method_selected_var,
                                 self.oim_var.get(),
                                 self.correction_var.get(),
                                 self.hamming_var.get(),
                                 self.unchained_var.get(),
                                 self.pm_var,
                                 self.oimstages_var,
                                 self.th_var,
                                 self.npnn_var,
                                 self.segmentation_type,
                                 self.text_type)

        self.RHamming.set(ret1)
        self.RUnchained.set(ret2)

        ffile = open(COMPUTE_FLAG_PATH, 'w')
        ffile.truncate(0)
        if self.compgrap.get():
            ffile.write('1')
        else:
            ffile.write('0')
        ffile.close()

        if self.whattoprint == 'matrix':
            self.lista["values"] = getResults()
        elif self.whattoprint == 'trees':
            self.lista["values"] = getTrees()
        self.print_logfile()
    #---------------------------------------------------------------------------#
    #   After - Printing logile:
    #---------------------------------------------------------------------------#
    def print_logfile(self):
        self.texto_log.delete('1.0', END)
        fil = open(LOG_PATH)
        for line in fil:
            self.texto_log.insert(END, line)
    #---------------------------------------------------------------------------#
    #   After - Selecting case:
    #---------------------------------------------------------------------------#
    def case_selected(self, event):
        self.case_selected_var = self.cases.get()
    #---------------------------------------------------------------------------#
    #   After - Selecting method:
    #---------------------------------------------------------------------------#
    def method_selected(self, event):
        self.method_selected_var = self.method.get()
        if self.method_selected_var == 'use':
            self.npnn['state'] = DISABLED
            self.npnnlabel['state'] = DISABLED
            self.th['state'] = NORMAL
            self.thlabel['state'] = NORMAL
            self.seg_type["values"] = ['Temporal', 'FB-BCM']
        elif self.method_selected_var == 'npnn':
            self.th['state'] = DISABLED
            self.thlabel['state'] = DISABLED
            self.npnn['state'] = NORMAL
            self.npnnlabel['state'] = NORMAL
            self.seg_type["values"] = ['Temporal', 'FB-BCM']
        elif self.method_selected_var == 'bert':
            self.th['state'] = NORMAL
            self.thlabel['state'] = NORMAL
            self.npnn['state'] = DISABLED
            self.npnnlabel['state'] = DISABLED
            self.seg_type["values"] = ['FB-BCM']
    #---------------------------------------------------------------------------#
    #   After - Symethry correction:
    #---------------------------------------------------------------------------#
    def symchange(self):
        if self.unchained_var.get() == False:
            self.pm['state'] = DISABLED
            self.pmlabel['state'] = DISABLED
        else:
            self.pm['state'] = NORMAL
            self.pmlabel['state'] = NORMAL

    def correctionchange(self):
        self.oim.deselect()
    #---------------------------------------------------------------------------#
    #   After - One in the middle correction:
    #---------------------------------------------------------------------------#
    def oimchange(self):
        if self.oim_var.get() == False:
            self.oimlabel['state'] = DISABLED
            self.oimstages['state'] = DISABLED
        else:
            self.oimlabel['state'] = NORMAL
            self.oimstages['state'] = NORMAL
            self.sym.select()
    #---------------------------------------------------------------------------#
    #   After - Segmentation and text type:
    #---------------------------------------------------------------------------#
    def seg_type_selected(self, event):
        self.segmentation_type = self.seg_type.get()
        if self.segmentation_type == 'FB-BCM':
            self.oim['state'] = DISABLED
            self.sym['state'] = DISABLED
            self.oimlabel['state'] = DISABLED
            self.oimstages['state'] = DISABLED
            self.text_used['state'] = DISABLED
            self.etiqueta_textused['state'] = DISABLED
            self.method["values"] = ['use', 'bert']
            self.whattoprint = 'trees'
            self.tabctrl_mbx.tab(self.tab0_mbx, text='Merging result')
            self.etiqueta3 = Label(self.master, text="SELECT A DAY:")
            self.lista["values"] = getTrees()
            self.lista.bind("<<ComboboxSelected>>", self.trees_selected)
            self.text_type = 'Phrases'

        elif self.segmentation_type == 'Temporal':
            self.oim['state'] = NORMAL
            self.sym['state'] = NORMAL
            self.oimlabel['state'] = NORMAL
            self.oimstages['state'] = NORMAL
            self.text_used['state'] = NORMAL
            self.etiqueta_textused['state'] = NORMAL
            self.method["values"] = ['npnn', 'use', 'bert']
            self.whattoprint = 'matrix'
            self.tabctrl_mbx.tab(self.tab0_mbx, text="R(Block_x,Block_y)        -       GroundTruth(Block_x, Block_y)")
            self.etiqueta3 = Label(self.master, text="SELECT AN AUTOCORRELATION MATRIX:")
            self.lista["values"] = getResults()
            self.lista.bind("<<ComboboxSelected>>", self.results_selected)

    def text_type_selected(self, event):
        self.text_type = self.text_used.get()
#---------------------------------------------------------------------------#
#   MAIN PROGRAM
#---------------------------------------------------------------------------#
if __name__ == '__main__':
    root_node = Tk()
    window = Ventana(root_node)
    root_node.iconbitmap('./.multimedia/matrix.ico')
    root_node.mainloop()
#---------------------------------------------------------------------------#
#   eof
#---------------------------------------------------------------------------#
