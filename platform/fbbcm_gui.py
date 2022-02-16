import csv
from tkinter import Tk, Label, Text, ttk, END, LabelFrame, filedialog, PhotoImage, Checkbutton, Entry, BooleanVar, \
    DISABLED, NORMAL
from tkinter.font import Font, BOLD

import matplotlib.pyplot as plt
import numpy as np
import spacy
from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

import pbmm
from styles import HoverButton, ColorStyles

MODEL_LIST_LOCATION = r'transformers_models.txt'
# BERT MODEL ----------------------------------------------------
spanish_model1 = 'hiiamsid/sentence_similarity_spanish_es'
model_bert = SentenceTransformer(spanish_model1)
# USE MODEL -----------------------------------------------------
model_use = spacy.load('es_core_news_lg')

def get_code(sentence, model):
    retval = []
    if model == 'BERT':
        retval = model_bert.encode(sentence)
    elif model == 'USE':
        retval = model_use(sentence)
    return retval

def get_text_models():
    file = open(MODEL_LIST_LOCATION, 'r')
    list_of_models = []
    for line in file:
        list_of_models.append(line.rstrip('\n'))
    file.close()
    return list_of_models


def GPA(g_size, sigma, mtx_size):
    """This function creates the Gaussian Proximity Adapter based on 3 parameters:
            sigma = Sigma parameter of the Normal Distribution (zero mean).
            mtx_size = Size of the GPA.
            g_size = Number of elements taken."""
    x = np.linspace(0, g_size-1, g_size)
    g = np.exp(-1*(x**2)/(2*(sigma**2)))
    GPA = np.zeros((mtx_size, mtx_size))
    for index1 in range(mtx_size):
        for index2 in range(g_size):
            append_index = (index1 + index2) % mtx_size
            if (index1 + index2) < mtx_size:
                GPA[index1][append_index] = g[index2]
        for index3 in range(g_size):
            append_index = (index1 - index3) % mtx_size
            if (index1 - index3) >= 0:
                GPA[index1][append_index] = g[index3]
    return GPA

def modify_matrix(m0, GPA, alpha) -> []:
    m1 = []
    for index1 in range(len(m0)):
        m1_row = []
        for index2 in range(len(m0)):
            m1_row.append(alpha*GPA[index1][index2] + (1-alpha)*m0[index1][index2])
        m1.append(m1_row)
    return m1
#   -------------------------------------------------------------


class Ventana:
    def __init__(self, master):
        self.master = master
        self.master.title("NLP Playground.")
        self.master.geometry('1360x670')
        self.colors = ColorStyles
        self.img = PhotoImage(file='./image/bg2.png')
        self.main_bg = PhotoImage(file='./image/background.png')
        self.mybg = Label(master)
        self.mybg.pack()
        self.mybg.config(image=self.img)
        self.mybg.place(x=-5, y=-5)
        # Texto a introducir.
        self.text_in = Text(self.master, height=1, width=60)
        self.text_in.pack()
        self.text_in.place(x=10, y=50)
        # Botón de insertar palabra.
        self.go = HoverButton(master, text="INSERT", command=self.insert, bg=self.colors.blue)
        self.go.pack()
        self.go.place(x=500, y=46)
        # Botón de reset.
        self.reset_but = HoverButton(master, text="RESET ALL", command=self.reset, width=76, bg=self.colors.pink)
        self.reset_but.pack()
        self.reset_but.place(x=10, y=80)
        # Botón de salir.
        self.exit = HoverButton(master, text="EXIT", command=master.quit, width=76, bg=self.colors.red)
        self.exit.pack()
        self.exit.place(x=10, y=10)
        # Matriz:
        self.imagen = LabelFrame(self.master, width=540, height=540)
        self.imagen.pack()
        self.imagen.place(x=10, y=120)
        self.mybg_if = Label(self.imagen)
        self.mybg_if.pack()
        self.mybg_if.config(image=self.main_bg)
        self.mybg_if.place(x=-10, y=-10)

        # Sentence control: --------------------------------------------------------------------------------------------
        self.control_frame = LabelFrame(self.master, width=230, height=250)
        self.control_frame.pack()
        self.control_frame.place(x=560, y=10)
        self.mybg_cf = Label(self.control_frame)
        self.mybg_cf.pack()
        self.mybg_cf.config(image=self.img)
        self.mybg_cf.place(x=-10, y=-10)
        # Selección de frase.
        self.texto_cajeta = Label(self.control_frame, text='Select the sentence:', font=Font(self.master,
                                                                                             size=10, weight=BOLD))
        self.texto_cajeta.config(bg='black', fg='white')
        self.texto_cajeta.pack()
        self.texto_cajeta.place(x=35, y=5)
        self.cajeta = ttk.Combobox(self.control_frame, state='readonly')
        self.cajeta.place(x=30, y=30)
        self.cajeta["values"] = []
        self.cajeta.bind("<<ComboboxSelected>>", self.cajeta_accion)
        self.sentence_selected = ''
        self.index_selected = -1
        # Botón de merge.
        self.boton_merge = HoverButton(self.control_frame, text='Merge blocks', command=self.merge_sentences,
                                       width=12, bg=self.colors.orange)
        self.boton_merge.pack()
        self.boton_merge.place(x=60, y=70)
        # Botón de delete.
        self.boton_delete = HoverButton(self.control_frame, text='Delete block',
                                        command=lambda: self.deletesentence(self.index_selected),
                                        width=12, bg=self.colors.blue)
        self.boton_delete.pack()
        self.boton_delete.place(x=60, y=100)
        # Selección de merge.
        self.texto_merge = Label(self.control_frame, text='Select the sentence to merge:', font=Font(self.master,
                                                                                                     size=10,
                                                                                                     weight=BOLD))
        self.texto_merge.config(bg='black', fg='white')
        self.texto_merge.pack()
        self.texto_merge.place(x=10, y=135)
        self.merge = ttk.Combobox(self.control_frame, state='readonly')
        self.merge.place(x=30, y=160)
        self.merge["values"] = []
        self.merge.bind("<<ComboboxSelected>>", self.select_merge)
        self.sentence_merge = ''
        self.index_merge = -1
        # Modelo de correlacción.
        self.texto_corr = Label(self.control_frame, text='Select the correlation method:', font=Font(self.master,
                                                                                                     size=10,
                                                                                                     weight=BOLD))
        self.texto_corr.config(bg='black', fg='white')
        self.texto_corr.pack()
        self.texto_corr.place(x=10, y=185)
        self.model = ttk.Combobox(self.control_frame, state='readonly')
        self.model.place(x=30, y=210)
        self.model["values"] = ['BERT', 'USE']
        self.model.bind("<<ComboboxSelected>>", self.change_code)
        self.model.set('BERT')

        # Load model: --------------------------------------------------------------------------------------------------
        self.load_frame = LabelFrame(self.master, width=230, height=250)
        self.load_frame.pack()
        self.load_frame.place(x=560, y=260)
        self.mybg_lf = Label(self.load_frame)
        self.mybg_lf.pack()
        self.mybg_lf.config(image=self.img)
        self.mybg_lf.place(x=-10, y=-10)
        # Selección de modelo.
        self.texto_load = Label(self.load_frame, text='Select the BERT model:', font=Font(self.master, size=10,
                                                                                          weight=BOLD))
        self.texto_load.config(bg='black', fg='white')
        self.texto_load.pack()
        self.texto_load.place(x=35, y=5)
        self.load = ttk.Combobox(self.load_frame, state='readonly')
        self.load.place(x=30, y=30)
        self.model_list = get_text_models()
        self.load["values"] = self.model_list
        self.load.bind("<<ComboboxSelected>>", self.set_up_model)
        # Botón de carga.
        self.boton_load = HoverButton(self.load_frame, text='Load model', command=self.load_model, width=12,
                                      bg=self.colors.orange)
        self.boton_load.pack()
        self.boton_load.place(x=60, y=70)
        # Botón de descarga.
        self.boton_download = HoverButton(self.load_frame, text='Download', command=self.download_model, width=12,
                                          bg=self.colors.blue)
        self.boton_download.pack()
        self.boton_download.place(x=60, y=210)
        # URL.
        self.url_box = Text(self.load_frame, height=3, width=25)
        self.url_box.pack()
        self.url_box.place(x=10, y=140)
        # URL text.
        self.text_url = Label(self.load_frame, text='Place the URL of the model:', font=Font(self.master, size=10,
                                                                                             weight=BOLD))
        self.text_url.config(bg='black', fg='white')
        self.text_url.pack()
        self.text_url.place(x=15, y=110)

        # Load blocks: -------------------------------------------------------------------------------------------------
        self.blocks_frame = LabelFrame(self.master, width=230, heigh=70)
        self.blocks_frame.pack()
        self.blocks_frame.place(x=560, y=510)
        self.mybg_bf = Label(self.blocks_frame)
        self.mybg_bf.pack()
        self.mybg_bf.config(image=self.img)
        self.mybg_bf.place(x=-10, y=-10)
        # Botón de carga de ficheros VTT.
        self.boton_ficheros = HoverButton(self.blocks_frame, text='Browse', command=self.load_files,
                                          width=12, bg=self.colors.yellow)
        self.boton_ficheros.pack()
        self.boton_ficheros.place(x=10, y=30)
        # Botón de exportación de ficheros.
        self.boton_exportar = HoverButton(self.blocks_frame, text='Export', command=self.save_files,
                                          width=12, bg=self.colors.blue)
        self.boton_exportar.pack()
        self.boton_exportar.place(x=120, y=30)
        # Eqtiqueta de carga de ficheros.
        self.texto_ficheros = Label(self.blocks_frame, text='Import / export custom files:', font=Font(self.master, size=10,
                                                                                              weight=BOLD))
        self.texto_ficheros.config(bg='black', fg='white')
        self.texto_ficheros.pack()
        self.texto_ficheros.place(x=20, y=5)
        # GPA: --------------------------------------------------------------------------------------------------------
        self.gpa_enable_var = BooleanVar()
        self.gpa_frame = LabelFrame(self.master, width=230, heigh=80)
        self.gpa_frame.pack()
        self.gpa_frame.place(x=560, y=580)
        self.mybg_gf = Label(self.gpa_frame)
        self.mybg_gf.pack()
        self.mybg_gf.config(image=self.img)
        self.mybg_gf.place(x=-10, y=-10)
        self.gpa_enable = Checkbutton(self.gpa_frame, text='Enable GPA',
                               variable=self.gpa_enable_var, command=self.en_dis_gpa)
        self.gpa_enable.config(bg='black', fg='white', activebackground='white', activeforeground='black',
                               selectcolor="black")
        self.gpa_enable.pack()
        self.gpa_enable.place(x=130, y=5)
        self.gpa_alpha_select_label = Label(self.gpa_frame, text='Weigth')
        self.gpa_alpha_select_label.config(bg='black', fg='white')
        self.gpa_alpha_select_label.pack()
        self.gpa_alpha_select_label.place(x=5, y=10)
        self.gpa_alpha_select = Entry(self.gpa_frame, width=8)
        self.gpa_alpha_select.pack()
        self.gpa_alpha_select.place(x=60, y=10)
        self.gpa_gsize_select_label = Label(self.gpa_frame, text='Size')
        self.gpa_gsize_select_label.config(bg='black', fg='white')
        self.gpa_gsize_select_label.pack()
        self.gpa_gsize_select_label.place(x=5, y=30)
        self.gpa_gsize_select = Entry(self.gpa_frame, width=8)
        self.gpa_gsize_select.pack()
        self.gpa_gsize_select.place(x=60, y=30)
        self.gpa_sigma_select_label = Label(self.gpa_frame, text='Sigma')
        self.gpa_sigma_select_label.config(bg='black', fg='white')
        self.gpa_sigma_select_label.pack()
        self.gpa_sigma_select_label.place(x=5, y=50)
        self.gpa_sigma_select = Entry(self.gpa_frame, width=8)
        self.gpa_sigma_select.pack()
        self.gpa_sigma_select.place(x=60, y=50)

        self.gpa_button = HoverButton(self.gpa_frame, text='Set GPA', command=self.set_gpa,
                                          width=12, bg=self.colors.red)
        self.gpa_button.pack()
        self.gpa_button.place(x=130, y=40)
        self.gpa_gsize_select.insert(-1, '3')
        self.gpa_sigma_select.insert(-1, '2')
        self.gpa_alpha_select.insert(-1, '0.5')

        self.gpa_sigma_var = 2
        self.gpa_gsize_var = 3
        self.gpa_alpha_var = 0.5
        # Full payload: -----------------------------------------------------------------------------------------------
        self.payload_frame = LabelFrame(self.master, width=540, height=680)
        self.payload_frame.pack()
        self.payload_frame.place(x=810, y=-10)
        self.mybg_pyl = Label(self.payload_frame)
        self.mybg_pyl.pack()
        self.mybg_pyl.config(image=self.img)
        self.mybg_pyl.place(x=-10, y=-10)
        self.text_payload = Text(self.payload_frame, height=6, width=43)
        self.text_payload.pack()
        self.text_payload.place(x=5, y=15)
        # Methods sel.: -----------------------------------------------------------------------------------------------
        self.texto_metodo = Label(self.payload_frame, text='Select a clustering method:', font=Font(self.master,
                                                                                                    size=10,
                                                                                                    weight=BOLD))
        self.texto_metodo.config(bg='black', fg='white')
        self.texto_metodo.pack()
        self.texto_metodo.place(x=360, y=15)

        self.bool_flag_fbbcm = BooleanVar()
        self.bool_flag_pbmm = BooleanVar()
        self.cb_fbbcm = Checkbutton(self.payload_frame, text='Enable FBBCM',
                                      variable=self.bool_flag_fbbcm, command=self.method_changed)
        self.cb_fbbcm.config(bg='black', fg='white', activebackground='white', activeforeground='black',
                             selectcolor="black")
        self.cb_fbbcm.pack()
        self.cb_fbbcm.place(x=370, y=35)
        self.cb_pbmm = Checkbutton(self.payload_frame, text='Enable PBMM',
                               variable=self.bool_flag_pbmm, command=self.method_changed)
        self.cb_pbmm.config(bg='black', fg='white', activebackground='white', activeforeground='black',
                            selectcolor="black")
        self.cb_pbmm.pack()
        self.cb_pbmm.place(x=370, y=55)
        self.th_label = Label(self.payload_frame, text='Threshold')
        self.th_label.config(bg='black', fg='white')
        self.th_label.pack()
        self.th_label.place(x=370, y=80)
        self.th_selection = Entry(self.payload_frame, width=8)
        self.th_selection.pack()
        self.th_selection.place(x=460, y=80)
        self.oim_label = Label(self.payload_frame, text='OIM stages')
        self.oim_label.config(bg='black', fg='white')
        self.oim_label.pack()
        self.oim_label.place(x=370, y=100)
        self.oim_selection = Entry(self.payload_frame, width=8)
        self.oim_selection.pack()
        self.oim_selection.place(x=460, y=100)
        self.oim_selection.insert(-1, '1')
        self.th_selection.insert(-1, '0.18')
        self.setup_method = HoverButton(self.payload_frame, text="SET", command=self.method_changed, bg=self.colors.red)
        self.setup_method.pack()
        self.setup_method.place(x=505, y=45)
        # Ground truth: -----------------------------------------------------------------------------------------------
        self.gt_label = LabelFrame(self.master, width=540, height=540)
        self.gt_label.pack()
        self.gt_label.place(x=810, y=120)
        self.mybg_gt = Label(self.gt_label)
        self.mybg_gt.pack()
        self.mybg_gt.config(image=self.main_bg)
        self.mybg_gt.place(x=-10, y=-10)


# -------- Flujo de programa. ------------------------------------------------------------------------------------------
        self.sentences = []
        self.codes = []
        self.correlation_mtx = []
        self.embedding_model = 'BERT'
        self.bert_url = spanish_model1
        self.GPA = []
        self.gt_imported = False
        self.thematrix_gt = []
        self.FB_BCM_FLAG = False
        self.PBMM_FLAG = False
        self.oim_variable = 1
        self.theshold_variable = 0.18
# ----------------------------------------------------------------------------------------------------------------------
        self.en_dis_gpa()
# ----------------------------------------------------------------------------------------------------------------------
    #   Acción de unir frases (cuidado que no sean la misma)
    def merge_sentences(self):
        if self.index_merge != self.index_selected:
            self.sentences[self.index_selected] = self.sentence_selected + '. ' + self.sentence_merge
            self.codes[self.index_selected] = get_code(self.sentences[self.index_selected], self.embedding_model)
            self.deletesentence(self.index_merge)
            self.index_merge = -1
        else:
            print('WARNING: Merging same sentence to itself!')

    #   Acción tras seleccionar la frase.
    def cajeta_accion(self, event):
        self.sentence_selected = self.cajeta.get()
        self.index_selected = self.sentences.index(self.sentence_selected)
        self.text_payload.delete('1.0', END)
        self.text_payload.insert('1.0', self.sentence_selected)

    #   Acción tras seleccionar la union.
    def select_merge(self, event):
        self.sentence_merge = self.merge.get()
        self.index_merge = self.sentences.index(self.sentence_merge)

    #   Insertar una frase al algoritmo.
    def insert(self):
        new_sentence = self.text_in.get('1.0', END + '-1c')
        self.sentences.append(new_sentence)
        self.codes.append(get_code(new_sentence, self.embedding_model))
        self.text_in.delete('1.0', END)
        self.generate_matrix()
        self.generate_image()
        self.cajeta["values"] = self.sentences
        self.merge["values"] = self.sentences

    #   Borrar la frase.
    def deletesentence(self, index):
        if index != -1:
            self.sentences.pop(index)
            self.codes.pop(index)
            self.correlation_mtx.pop(index)
            self.cajeta["values"] = self.sentences
            self.merge["values"] = self.sentences
            self.sentence_selected = ''
            self.index_selected = -1
            self.generate_matrix()
            if self.gt_imported:
                self.thematrix_gt = np.delete(self.thematrix_gt, index, 1)
                self.thematrix_gt = np.delete(self.thematrix_gt, index, 0)
            try:
                self.generate_image()
            except:
                print('WARNING: Last block deleted.')

    #   Resetear las frases.
    def reset(self):
        self.sentences = []
        self.codes = []
        self.thematrix_gt = []
        self.correlation_mtx = []
        self.cajeta["values"] = self.sentences
        self.merge["values"] = self.sentences
        self.sentence_selected = ''
        self.index_selected = -1

    #   Generar la matriz de correlación.
    def generate_matrix(self):
        self.correlation_mtx = []
        for index1 in range(len(self.codes)):
            correlation_mtx_row = []
            for index2 in range(len(self.codes)):
                code1 = self.codes[index1]
                code2 = self.codes[index2]
                if self.embedding_model == 'BERT':
                    correlation_mtx_row.append(cosine_similarity(code1.reshape(1, -1), code2.reshape(1, -1))[0][0])
                elif self.embedding_model == 'USE':
                    correlation_mtx_row.append(code1.similarity(code2))

            self.correlation_mtx.append(correlation_mtx_row)

        if self.gpa_enable_var.get() == True:
            self.correlation_mtx = modify_matrix(self.correlation_mtx,
                                                 GPA(self.gpa_gsize_var, self.gpa_sigma_var, len(self.correlation_mtx)),
                                                 self.gpa_alpha_var)

    #   Generar la figura.
    def generate_image(self):
        sized = len(self.correlation_mtx)
        thematrix = np.zeros((sized, sized, 3), dtype=np.uint8)

        for index1 in range(sized):
            maximum = self.correlation_mtx[index1].copy()
            maximum.sort(reverse=True)
            for index2 in range(sized):
                if self.correlation_mtx[index1][index2] < 0:
                    self.correlation_mtx[index1][index2] = 0

                thematrix[index1][index2][0] = 255*self.correlation_mtx[index1][index2]
                thematrix[index1][index2][1] = 100*self.correlation_mtx[index1][index2]
                thematrix[index1][index2][2] = 0

                if self.FB_BCM_FLAG:
                    if self.correlation_mtx[index1][index2] == maximum[1]:
                        thematrix[index1][index2][2] += 127

        if self.PBMM_FLAG:
            segmentation = pbmm.Pbmm(self.correlation_mtx, oim=self.oim_variable, th=self.theshold_variable)
            print('Segmentation is {sem}'.format(sem=segmentation.segmentation))
            for segment in segmentation.segmentation:
                base = segment[0]
                ending = segment[1]
                for index1 in range(ending - base + 1):
                    for index2 in range(ending - base + 1):
                        thematrix[base + index2][base + index1][2] += 128


        plt.close()
        myFig = plt.figure(figsize=(5.4, 4.9), dpi=100)
        plt.imshow(thematrix)
        img = Image.fromarray(thematrix)
        img.save('./image/last_image.png')
        plt.title("Correlation matrix (" + self.embedding_model + ")")

        axis = range(sized)
        plt.xticks(axis, self.sentences, rotation='vertical')
        plt.yticks(axis, self.sentences)

        try:
            self.canvas.get_tk_widget().pack_forget()
            self.toolbar.destroy()
            self.canvas = FigureCanvasTkAgg(myFig, master=self.imagen)
            self.canvas.draw()
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.imagen)
            self.toolbar.update()
            self.canvas.get_tk_widget().pack()
        except:
            self.canvas = FigureCanvasTkAgg(myFig, master=self.imagen)
            self.canvas.draw()
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.imagen)
            self.toolbar.update()
            self.canvas.get_tk_widget().pack()

        if self.gt_imported:
            plt.close()
            myFig = plt.figure(figsize=(5.4, 4.9), dpi=100)
            plt.imshow(self.thematrix_gt, cmap='gray')
            plt.title("Ground Truth")

            axis = range(sized)
            plt.xticks(axis, self.sentences, rotation='vertical')
            plt.yticks(axis, self.sentences)

            try:
                self.canvas_gt.get_tk_widget().pack_forget()
                self.toolbar_gt.destroy()
                self.canvas_gt = FigureCanvasTkAgg(myFig, master=self.gt_label)
                self.canvas_gt.draw()
                self.toolbar_gt = NavigationToolbar2Tk(self.canvas_gt, self.gt_label)
                self.toolbar_gt.update()
                self.canvas_gt.get_tk_widget().pack()
            except:
                self.canvas_gt = FigureCanvasTkAgg(myFig, master=self.gt_label)
                self.canvas_gt.draw()
                self.toolbar_gt = NavigationToolbar2Tk(self.canvas_gt, self.gt_label)
                self.toolbar_gt.update()
                self.canvas_gt.get_tk_widget().pack()

    def change_code(self, event) -> None:
        self.embedding_model = self.model.get()
        self.reset()

    def set_up_model(self, event) -> None:
        self.bert_url = self.load.get()

    def load_model(self) -> None:
        global model_bert
        model_bert = SentenceTransformer(self.bert_url)
        self.reset()

    def download_model(self) -> None:
        global model_bert
        self.bert_url = self.url_box.get('1.0', END + '-1c')
        try:
            if self.bert_url not in self.model_list:
                model_bert = SentenceTransformer(self.bert_url)
                file = open(MODEL_LIST_LOCATION, 'a')
                file.write('\n' + self.bert_url)
                file.close()
                self.url_box.delete('1.0', END)
                self.model_list.append(self.bert_url)
                self.load["values"] = self.model_list
                self.reset()
            else:
                print('Model: ' + self.bert_url + ' already downloaded.')
        except:
            print('Model: ' + self.bert_url + ' not found')

    def load_files(self) -> None:
        try:
            self.reset()
            filename = filedialog.askopenfilename(filetypes=[('Text Files', '*.txt')])
            try:
                file = open(filename, mode='r', encoding='utf-8')
                for line in file:
                    self.sentences.append(line.rstrip('\n'))
                    self.codes.append(get_code(line, self.embedding_model))
            except:
                file = open(filename, mode='r')
                for line in file:
                    self.sentences.append(line.rstrip('\n'))
                    self.codes.append(get_code(line, self.embedding_model))
            self.generate_matrix()
            self.cajeta["values"] = self.sentences
            self.merge["values"] = self.sentences

            filename = filedialog.askopenfilename(filetypes=[('Text Files', '*.txt')])
            self.gt_imported = False
            try:
                self.thematrix_gt = np.loadtxt(filename)
                self.gt_imported = True
            except:
                print("WARNING: Invalid GT.")

            self.generate_image()
        except:
            print('WARNING: No files selected.')

    def set_gpa(self) -> None:
        self.gpa_gsize_var = int(self.gpa_gsize_select.get())
        self.gpa_sigma_var = float(self.gpa_sigma_select.get())
        self.gpa_alpha_var = float(self.gpa_alpha_select.get())
        self.generate_matrix()
        self.generate_image()

    def en_dis_gpa(self) -> None:
        settingup_state = DISABLED
        if self.gpa_enable_var.get() == True:
            settingup_state = NORMAL
        if self.codes != []:
            self.generate_matrix()
            self.generate_image()
        self.gpa_alpha_select['state'] = settingup_state
        self.gpa_sigma_select['state'] = settingup_state
        self.gpa_gsize_select['state'] = settingup_state
        self.gpa_alpha_select_label['state'] = settingup_state
        self.gpa_sigma_select_label['state'] = settingup_state
        self.gpa_gsize_select_label['state'] = settingup_state
        self.gpa_button['state'] = settingup_state

    def method_changed(self) -> None:
        self.FB_BCM_FLAG = self.bool_flag_fbbcm.get()
        self.PBMM_FLAG = self.bool_flag_pbmm.get()
        self.oim_variable = round(int(self.oim_selection.get()), 0)
        self.theshold_variable = float(self.th_selection.get())
        self.generate_image()

    def save_files(self) -> None:
        file = filedialog.asksaveasfile(parent=self.master, defaultextension=".txt",
                                        initialfile="frases.txt", title="Guardar frases")
        for sentence in self.sentences:
            file.write(sentence + '\n')

        file = filedialog.asksaveasfile(parent=self.master, defaultextension=".csv",
                                        initialfile="matriz.csv", title="Guardar matriz")

        writer = csv.writer(file)
        writer.writerows(self.correlation_mtx)
        file.close()

#---------------------------------------------------------------------------#
#   MAIN PROGRAM
#---------------------------------------------------------------------------#
if __name__ == '__main__':
    root_node = Tk()
    window = Ventana(root_node)
    root_node.iconbitmap('../.multimedia/matrix.ico')
    root_node.configure(bg='black')
    root_node.mainloop()
#---------------------------------------------------------------------------#
#   END OF FILE
#---------------------------------------------------------------------------#