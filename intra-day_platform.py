# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
import os
import time
from threading import Thread
from tkinter import END, NORMAL, DISABLED
from tkinter import Tk, LabelFrame, Text, Label, ttk, PhotoImage, Entry, Checkbutton, BooleanVar, filedialog, Toplevel

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from sentence_transformers import SentenceTransformer

import package.dserial as ds
import package.model_correlate as fbbcm
import package.news_reading as nr
import package.token_processing as tp
from package.pm import Pbmm
from package.styles import ColorStyles, HoverButton

MODEL_LIST_LOCATION = r'./db/models/models.txt'
ICO_LOCATION = r'./.multimedia/rocketico.ico'
MULTIMEDIA_ROCKET_LOCATION = r'./.multimedia/rocketico.png'
MULTIMEDIA_EYE_LOCATION = r'./.multimedia/watch.png'
MAIN_DATABASE_LOCATION = r'./db/vtt_files/'
MAIN_TEXTBASE_LOCATION = r'./db/news_text/'
LOG_FILE_PATH = r'./logfile.txt'
IMAGE_PATH = r'./.multimedia/'
TREES_DIR = r'./db/trees/'

CStyles = ColorStyles
cat2color = {'Info': CStyles.pink, 'Warning': CStyles.orange, 'Error': CStyles.red, 'Note': CStyles.blue}
# -----------------------------------------------------------

#   S   T   A   T   I   C   -   -   -   -   -   -   -   -   -


def main() -> None:
    root_node = Tk()
    MainWindow(root_node)
    root_node.iconbitmap(ICO_LOCATION)
    root_node.configure()
    root_node.mainloop()
    return


def tree_tracer(*args):
    filename = args[0].split('/')[-1]
    do = args[1]
    mytrees = ds.read_tree(filename.split('.')[-2])
    fig = go.Figure()
    slack_unique = 0
    totaltime = 0
    xholders = []
    for tree in mytrees:
        slack_div = 0
        xholders.append(slack_unique)
        zipped = zip(tree.idv, tree.payload_div)
        for idvec, payl in zipped:
            fig.add_trace(go.Scatter(x=[slack_unique, slack_div+slack_unique],
                                     y=[2, 0],
                                     mode='lines',
                                     line=dict(color='rgb(50,50,50)', width=2),
                                     showlegend=False
                                     ))
            fig.add_trace(go.Scatter(x=[slack_div+slack_unique],
                                     y=[0],
                                     mode='markers',
                                     name=f'Division {idvec}',
                                     marker=dict(symbol='circle-dot',
                                                 size=18,
                                                 color='#6175c1',
                                                 line=dict(color='rgb(90,90,90)', width=1)
                                                 ),
                                     text=payl,
                                     hoverinfo='text',
                                     opacity=0.8
                                     ))
            slack_div += 1
        # Second stage of tree:
        fig.add_trace(go.Scatter(x=[slack_unique],
                                 y=[2],
                                 mode='markers',
                                 name=f'Tree {tree.nTree}',
                                 marker=dict(symbol='circle-dot',
                                             size=20,
                                             color='#DB4551',
                                             line=dict(color='rgb(50,50,50)', width=1)
                                             ),
                                 text=f'Tree {tree.nTree}: {tree.timing} [s]',
                                 hoverinfo='text',
                                 opacity=[10*tree.pt if 10*tree.pt < 1 else 1][0]
                                 ))
        totaltime += tree.timing
        slack_unique += slack_div

    # Top of the tree:
    for holder in xholders:
        fig.add_trace(go.Scatter(x=[holder, (max(xholders)+min(xholders))/2],
                                 y=[2, 4],
                                 mode='lines',
                                 line=dict(color='rgb(90,90,90)', width=2),
                                 showlegend=False,
                                 opacity=0.8
                                 ))
    fig.add_trace(go.Scatter(x=[(max(xholders)+min(xholders))/2],
                             y=[4],
                             mode='markers',
                             name=f'Total for the day.',
                             marker=dict(symbol='circle-dot',
                                         size=20,
                                         color='#DBDB00',
                                         line=dict(color='rgb(50,50,50)', width=1)
                                         ),
                             text=f'Total time {totaltime} [s]',
                             hoverinfo='text',
                             opacity=1
                             ))
    if do:
        fig.show()


def _read_model_list() -> []:
    model_list = []
    with open(MODEL_LIST_LOCATION) as file:
        for line in file:
            model_list.append(line.rstrip('\n'))
    return model_list


def traduction_thread(**kwargs):
    nr.VttReading_(**kwargs)


def launching_thread(*args, **kwargs) -> []:
    parent = args[0]
    nt = args[1]
    # Preprocessing the $ token:
    token_processor = tp.TokenProcessing(**kwargs)
    sentence_streams = token_processor.preprocessing()
    parent.lowrite(f'Thread {nt+1} ended preprocessing.', cat='Info')

    # Correlation matrix por each day:
    xmodel = fbbcm.LoadModel(kwargs['correlation_model'])
    parent.lowrite(f'Thread {nt + 1} loaded the correlation model sucesfully.', cat='Info')
    writein = kwargs['target'].split('/')[-1]
    for day_, sentence_stream in enumerate(sentence_streams):
        day = day_ + 1
        untokenized_mtx = fbbcm.correlate(sentence_stream, xmodel=xmodel.model)
        parent.lowrite(f'Thread {nt + 1} correlated day {day} sucessfully.', cat='Info')

        if kwargs['tokens']:
            tokenized_mtx = token_processor.posprocessing(untokenized_mtx, day_)
        else:
            tokenized_mtx = untokenized_mtx
        parent.lowrite(f'Thread {nt + 1} posprocessed day {day} sucessfully.', cat='Info')

        stream_merged_pm = Pbmm(tokenized_mtx, th=kwargs['pm-th'],
                                oim=kwargs['oim']).merge_segmentation(sentence_stream)
        parent.lowrite(f'Thread {nt + 1} launched PM on day {day}.', cat='Info')

        trees_list = fbbcm.fbbcm(stream_merged_pm, kwargs['fbbcm-th'], day, 'bert', False, xmodel=xmodel.model)
        parent.lowrite(f'Thread {nt + 1} launched FBBCM on day {day}.', cat='Info')

        ds.write_tree(trees_list, f'{writein}_{day}')
        parent.lowrite(f'Thread {nt + 1} Tree {writein}_{day}.3s written.', cat='Info')

    parent.lowrite(f'Thread {nt + 1} finished computation.', cat='Info')


def test_correlate(*args, **kwargs) -> []:
    parent = args[0]
    current_model = args[1]
    token_processor = tp.TokenProcessing(**kwargs)
    sentence_stream = token_processor.preprocessing()[0]
    parent.lowrite(f'Preprocessing for testing done.', cat='Info')
    # Default:
    untokenized_mtx = fbbcm.correlate(sentence_stream, xmodel=current_model)
    parent.lowrite(f'Correlation for testing done.', cat='Info')
    # Tokens:
    if kwargs['tokens']:
        tokenized_mtx = token_processor.posprocessing(untokenized_mtx, 0)
    else:
        tokenized_mtx = untokenized_mtx
    # PM:
    if kwargs['pmen']:
        pmm = Pbmm(tokenized_mtx, th=kwargs['pmth'], oim=kwargs['oim'])
        pm_segmentation = pmm.segmentation
        stream_merged_pm = pmm.merge_segmentation(sentence_stream)
        parent.lowrite(f'PM launched with th={kwargs["pmth"]} and oim={kwargs["oim"]}.', cat='Info')
    else:
        stream_merged_pm = sentence_stream
        pm_segmentation = []
    # FB_BCM:
    if kwargs['fbbcmen']:
        trees_list = fbbcm.fbbcm(stream_merged_pm, kwargs['fbbcmth'], 0, 'bert', False, xmodel=current_model)
        parent.lowrite(f'FB-BCM launched with th={kwargs["fbbcmth"]}', cat='Info')
    else:
        trees_list = []

    parent.lowrite(f'Test processing finished.', cat='Info')
    return [np.array(untokenized_mtx), tokenized_mtx, sentence_stream, stream_merged_pm, pm_segmentation, trees_list]
#   S   T   A   T   I   C   -   -   -   -   -   -   -   -   -


class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Intra-day clustering GUI.")
        self.master.geometry('1360x670')
        self.colors = ColorStyles

        self.rocketlaunch_img = PhotoImage(file=MULTIMEDIA_ROCKET_LOCATION)
        self.rocketlaunch_img = self.rocketlaunch_img.subsample(5)
        self.watch_img = PhotoImage(file=MULTIMEDIA_EYE_LOCATION)
        self.watch_img = self.watch_img.subsample(14)
        self.rocketlaunchS_img = PhotoImage(file=MULTIMEDIA_ROCKET_LOCATION)
        self.rocketlaunchS_img = self.rocketlaunchS_img.subsample(14)
        self.rocketlaunchM_img = PhotoImage(file=MULTIMEDIA_ROCKET_LOCATION)
        self.rocketlaunchM_img = self.rocketlaunchM_img.subsample(7)
        # -------------------------------------------------------------------------------------------------------------
        #                       VARIABLES
        # -------------------------------------------------------------------------------------------------------------
        self.launcher_target = []                   # Target for launch.
        self.test_target = None                     # Target for test.
        self.read_target = []                       # Target for reading.

        self.model_list = _read_model_list()        # List of models.

        self.correlation_model = SentenceTransformer(self.model_list[0])               # B.E.R.T model.

        self.correlation_model_launch = None
        self.fbbcmth = None
        self.pmth = None
        self.oim = None
        self.selectall_v = BooleanVar()
        self.launch_tokenbool = BooleanVar()
        self.decorrelation = None

        self.num_read_targets = 0                   # Number of targets for read.
        self.num_launch_targets = 0                 # Number of targets for launch.
        self.reader_all = BooleanVar()              # Read all targets.
        self.reader_notrans = BooleanVar()          # Translation disabled?

        self.test_decorrelation = 0
        self.token_bool = BooleanVar()
        self.test_tree = None
        self.tokenized_matrix = []
        self.untokenized_matrix = []
        self.target_matrix1 = []
        self.target_matrix2 = []
        self.sentence_stream = []
        self.sentence_stream_t1 = []
        self.sentence_stream_t2 = []
        self.canvas1 = None
        self.canvas2 = None
        self.toolbar1 = None
        self.toolbar2 = None
        self.fbbcmth_test = None
        self.pmth_test = None
        self.oim_test = None
        self.pmen_test = False
        self.fbbcmen_test = False
        self.sentence_stream_pm = []
        self.pm_segmentation = []
        self.watch_fbbcm = False
        self.watch_pm = False
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.launcher_corr_lock_v = BooleanVar()
        self.launcher_algo_lock_v = BooleanVar()
        self.launcher_file_lock_v = BooleanVar()
        self.trans_lock_v = BooleanVar()
        # -------------------------------------------------------------------------------------------------------------
        #                       FILE        CONTROL
        # -------------------------------------------------------------------------------------------------------------
        self.filecontrol_lf = LabelFrame(self.master, width=220, height=90, text='File control')
        self.filecontrol_lf.place(x=5, y=5)
        self.filecontrol_import = HoverButton(self.filecontrol_lf, text='Import single file', command=self.import_file,
                                              width=15, bg=self.colors.gray)
        self.filecontrol_import.place(x=90, y=5)
        self.filecontrol_export = HoverButton(self.filecontrol_lf, text='Export results', command=self.export_file,
                                              width=15, bg=self.colors.gray)
        self.filecontrol_export.place(x=90, y=35)
        self.filecontrol_trace = HoverButton(self.filecontrol_lf, text='Trace files', command=self.trace_files,
                                             width=10, heigh=3, bg=self.colors.gray)
        self.filecontrol_trace.place(x=5, y=5)
        # -------------------------------------------------------------------------------------------------------------
        #                       NLP     CORRELATION     MODEL
        # -------------------------------------------------------------------------------------------------------------
        self.nlpmodel_lf = LabelFrame(self.master, width=400, height=165, text='Model selection')
        self.nlpmodel_lf.place(x=5, y=95)
        self.nlpmodel_downloadurl = Text(self.nlpmodel_lf, height=2, width=47)
        self.nlpmodel_downloadurl.place(x=6, y=25)
        self.nlpmodel_downloadbutt = HoverButton(self.nlpmodel_lf, text='Download model', command=self.download_model,
                                                 width=25, bg=self.colors.gray).place(x=5, y=65)
        self.nlpmodel_loadbutt = HoverButton(self.nlpmodel_lf, text='Load model', command=self.load_model,
                                             width=25, bg=self.colors.gray).place(x=200, y=65)
        self.nlpmodel_info = Label(self.nlpmodel_lf, text='Place the model URL to download:').place(x=100, y=0)
        self.nlpmodel_list = ttk.Combobox(self.nlpmodel_lf, width=60, state='readonly')
        self.nlpmodel_list.pack()
        self.nlpmodel_list.place(x=5, y=99)
        self.nlpmodel_list["values"] = self.model_list
        self.nlpmodel_infoloaded = Label(self.nlpmodel_lf, text='Loaded model:').place(x=20, y=120)
        self.nlpmodel_modelloaded = Label(self.nlpmodel_lf, text='DEFAULT MODEL')
        self.nlpmodel_modelloaded.pack()
        self.nlpmodel_modelloaded.place(x=140, y=120)
        # -------------------------------------------------------------------------------------------------------------
        #                       LAUNCHER
        # -------------------------------------------------------------------------------------------------------------
        self.launcher_lf = LabelFrame(self.master, width=600, height=215, text='Launcher')
        self.launcher_lf.place(x=5, y=260+110)
        self.launcher_button = HoverButton(self.launcher_lf, command=self.launch_parameters,
                                           image=self.rocketlaunch_img, bg=self.colors.gray).place(x=480, y=0)
        self.launcher_algo_lf = LabelFrame(self.launcher_lf, width=200, height=115, text='Algorythm parameters')
        self.launcher_algo_lf.pack()
        self.launcher_algo_lf.place(x=5, y=0)
        self.launcher_algo_infothfbcm = Label(self.launcher_algo_lf, text='FB-BCM threshold:')
        self.launcher_algo_infothfbcm.pack()
        self.launcher_algo_infothfbcm.place(x=0, y=5)
        self.launcher_algo_infothpm = Label(self.launcher_algo_lf, text='PM threshold:')
        self.launcher_algo_infothpm.pack()
        self.launcher_algo_infothpm.place(x=0, y=25)
        self.launcher_algo_infooimpm = Label(self.launcher_algo_lf, text='OIM stages:')
        self.launcher_algo_infooimpm.pack()
        self.launcher_algo_infooimpm.place(x=0, y=45)
        self.launcher_algo_thfbcm = Entry(self.launcher_algo_lf, width=8)
        self.launcher_algo_thpm = Entry(self.launcher_algo_lf, width=8)
        self.launcher_algo_oimpm = Entry(self.launcher_algo_lf, width=8)
        self.launcher_algo_thfbcm.pack()
        self.launcher_algo_thpm.pack()
        self.launcher_algo_oimpm.pack()
        self.launcher_algo_thfbcm.place(x=120, y=5)
        self.launcher_algo_thpm.place(x=120, y=25)
        self.launcher_algo_oimpm.place(x=120, y=45)
        self.launcher_algo_thfbcm.insert(-1, '0.40')
        self.launcher_algo_thpm.insert(-1, '0.22')
        self.launcher_algo_oimpm.insert(-1, '1')
        self.launcher_algo_lock = Checkbutton(self.launcher_algo_lf, text='Lock this values for launch',
                                              variable=self.launcher_algo_lock_v, command=self.launch_algo_lock)
        self.launcher_algo_lock.pack()
        self.launcher_algo_lock.place(x=5, y=70)

        self.launcher_file_lf = LabelFrame(self.launcher_lf, width=260, height=115, text='Files target')
        self.launcher_file_lf.pack()
        self.launcher_file_lf.place(x=210, y=0)
        self.launcher_file_selectall = Checkbutton(self.launcher_file_lf, text='Select all files from database',
                                                   var=self.selectall_v,
                                                   command=self.launch_file_all)
        self.launcher_file_selectall.pack()
        self.launcher_file_selectall.place(x=5, y=50)
        self.launcher_file_lock = Checkbutton(self.launcher_file_lf, text='Lock this targets for launch',
                                              command=self.launch_file_lock, variable=self.launcher_file_lock_v)
        self.launcher_file_lock.pack()
        self.launcher_file_lock.place(x=5, y=70)
        self.launcher_file_addtgt = HoverButton(self.launcher_file_lf, text='Browse target', command=self.launch_add,
                                                width=11, bg=self.colors.gray)
        self.launcher_file_addtgt.place(x=5, y=5)
        self.launcher_file_rmvtgt = HoverButton(self.launcher_file_lf, text='Remove targets', command=self.launch_rmv,
                                                width=12, bg=self.colors.gray)
        self.launcher_file_rmvtgt.pack()
        self.launcher_file_rmvtgt.place(x=97, y=5)
        self.launcher_file_ntgs_info = Label(self.launcher_file_lf, text='Number of targets added:')
        self.launcher_file_ntgs_info.pack()
        self.launcher_file_ntgs_info.place(x=5, y=33)
        self.launcher_file_ntgs = Label(self.launcher_file_lf, text='0')
        self.launcher_file_ntgs.place()
        self.launcher_file_ntgs.place(x=160, y=33)
        self.launcher_file_visualize_target = HoverButton(self.launcher_file_lf, text='Check\ntargets',
                                                          command=self.launch_visualize, heigh=5,
                                                          width=6, bg=self.colors.gray)
        self.launcher_file_visualize_target.pack()
        self.launcher_file_visualize_target.place(x=195, y=5)

        self.launcher_extra_lf = LabelFrame(self.launcher_lf, width=585, height=75, text='Correlation model')
        self.launcher_extra_lf.pack()
        self.launcher_extra_lf.place(x=5, y=115)
        self.launcher_corrmodel_info = Label(self.launcher_extra_lf, text='Select a corrleation model:')
        self.launcher_corrmodel_info.pack()
        self.launcher_corrmodel_info.place(x=5, y=0)
        self.launcher_corrmodel = ttk.Combobox(self.launcher_extra_lf, width=64, state='readonly')
        self.launcher_corrmodel.pack()
        self.launcher_corrmodel.place(x=160, y=0)
        self.launcher_corrmodel["values"] = self.model_list
        self.launcher_tokenenable = Checkbutton(self.launcher_extra_lf, text='Enable token processing',
                                                variable=self.launch_tokenbool)
        self.launcher_tokenenable.pack()
        self.launcher_tokenenable.place(x=0, y=25)
        self.launcher_decorrelation = Entry(self.launcher_extra_lf, width=7)
        self.launcher_decorrelation.place(x=280, y=30)
        self.launcher_decorrelation.insert(-1, '0.00')
        self.launcher_decorrelation_info = Label(self.launcher_extra_lf, text='Decorrelation: ')
        self.launcher_decorrelation_info.pack()
        self.launcher_decorrelation_info.place(x=190, y=28)
        self.launcher_decorrelation_info2 = Label(self.launcher_extra_lf, text='%')
        self.launcher_decorrelation_info2.pack()
        self.launcher_decorrelation_info2.place(x=320, y=28)
        self.launcher_corr_lock = Checkbutton(self.launcher_extra_lf, text='Lock this correlation for launch',
                                              variable=self.launcher_corr_lock_v, command=self.launch_corr_lock)
        self.launcher_corr_lock.pack()
        self.launcher_corr_lock.place(x=380, y=28)
        # -------------------------------------------------------------------------------------------------------------
        #                       FBBCM       METHOD
        # -------------------------------------------------------------------------------------------------------------
        self.fbbcm_lf = LabelFrame(self.master, width=195, height=100, text='FB-BCM algorythm ')
        self.fbbcm_lf.place(x=410, y=5)
        self.fbbcm_infoth = Label(self.fbbcm_lf, text='Method\'s threshold:').place(x=5, y=5)
        self.fbbcm_thentry = Entry(self.fbbcm_lf, width=8)
        self.fbbcm_thentry.pack()
        self.fbbcm_thentry.place(x=125, y=5)
        self.fbbcm_thentry.insert(-1, '0.40')
        self.fbbcm_watchbutton = HoverButton(self.fbbcm_lf, command=self.fbbcm_watch, bg=self.colors.red,
                                             image=self.watch_img).place(x=4, y=30)
        self.fbbcm_launchbutton = HoverButton(self.fbbcm_lf, command=self.fbbcm_launch, bg=self.colors.red,
                                              image=self.rocketlaunchS_img).place(x=142, y=30)
        self.fbbcm_enablebutton = HoverButton(self.fbbcm_lf, command=self.fbbcm_enable, bg=self.colors.orange,
                                              text="Enable FB-BCM", heigh=2).place(x=48, y=31)
        # -------------------------------------------------------------------------------------------------------------
        #                       PM      METHOD
        # -------------------------------------------------------------------------------------------------------------
        self.pmtoken_lf = LabelFrame(self.master, width=195, height=150, text='PM algorythm')
        self.pmtoken_lf.place(x=410, y=110)
        self.pm_infoth = Label(self.pmtoken_lf, text='Method\'s threshold:').place(x=5, y=10)
        self.pm_thentry = Entry(self.pmtoken_lf, width=8)
        self.pm_thentry.pack()
        self.pm_thentry.place(x=125, y=10)
        self.pm_thentry.insert(-1, '0.22')
        self.pm_infooim = Label(self.pmtoken_lf, text='Method\'s stages:').place(x=5, y=32)
        self.pm_oimentry = Entry(self.pmtoken_lf, width=8)
        self.pm_oimentry.pack()
        self.pm_oimentry.place(x=125, y=32)
        self.pm_oimentry.insert(-1, '1')
        self.pm_watchbutton = HoverButton(self.pmtoken_lf, command=self.pm_watch, bg=self.colors.red,
                                          image=self.watch_img).place(x=4, y=80)
        self.pm_launchbutton = HoverButton(self.pmtoken_lf, command=self.pm_launch, bg=self.colors.red,
                                           image=self.rocketlaunchS_img).place(x=143, y=80)
        self.pm_enablebutton = HoverButton(self.pmtoken_lf, command=self.pm_enable, bg=self.colors.orange,
                                           text="Enable PM", width=12, heigh=2).place(x=48, y=81)
        # -------------------------------------------------------------------------------------------------------------
        #                       TOKEN   CONTROL
        # -------------------------------------------------------------------------------------------------------------
        self.tokencontrol_lf = LabelFrame(self.master, width=175, height=90, text='Token processing')
        self.tokencontrol_lf.pack()
        self.tokencontrol_lf.place(x=230, y=5)
        self.token_checkbox = Checkbutton(self.tokencontrol_lf, text='Enable token processing',
                                          variable=self.token_bool, command=self.token_enable)
        self.token_checkbox.pack()
        self.token_checkbox.place(x=0, y=0)
        self.token_info = Label(self.tokencontrol_lf, text='Decorrelation:').place(x=5, y=21)
        self.token_info2 = Label(self.tokencontrol_lf, text='%').place(x=135, y=21)
        self.token_decorrelation = Entry(self.tokencontrol_lf, width=7)
        self.token_decorrelation.place(x=90, y=21)
        self.token_decorrelation.insert(-1, '0.00')
        self.token_decorr_setup = HoverButton(self.tokencontrol_lf, text='Set up decorrelation', height=1,
                                              command=self.set_up_token, width=20, bg=self.colors.red)
        self.token_decorr_setup.pack()
        self.token_decorr_setup.place(x=5, y=42)
        # -------------------------------------------------------------------------------------------------------------
        #                       TRANSLATOR
        # -------------------------------------------------------------------------------------------------------------
        self.translator_lf = LabelFrame(self.master, width=600, height=110, text='Translation and VTT reding')
        self.translator_lf.place(x=5, y=260)
        self.tranlator_modelinfo = Label(self.translator_lf, text='Select the translator model:')
        self.tranlator_modelinfo.pack()
        self.tranlator_modelinfo.place(x=0, y=0)
        self.translator_model = ttk.Combobox(self.translator_lf, width=52, state='readonly')
        self.translator_model.pack()
        self.translator_model.place(x=160, y=0)
        self.translator_model["values"] = ["DeepL - Online traduction.", "GoogleTranslate - Online traduction."]
        self.translator_bworsetarget = HoverButton(self.translator_lf, text='Browse target', command=self.trans_add,
                                                   width=15, bg=self.colors.gray)
        self.translator_bworsetarget.place(x=5, y=25)
        self.translator_removetarget = HoverButton(self.translator_lf, text='Remove targets', command=self.trans_rmv,
                                                   width=15, bg=self.colors.gray)
        self.translator_removetarget.place(x=5, y=55)
        self.translator_viewtarget = HoverButton(self.translator_lf, text='Check\ntargets', command=self.trans_view,
                                                 width=12, heigh=3, bg=self.colors.gray)
        self.translator_viewtarget.place(x=130, y=25)
        self.translator_launcher = HoverButton(self.translator_lf, command=self.trans_launch,
                                               image=self.rocketlaunchM_img, bg=self.colors.red).place(x=510, y=0)
        self.translator_infoadd = Label(self.translator_lf, text='Number of targets\nadded:')
        self.translator_infoadd.pack()
        self.translator_infoadd.place(x=227, y=25)
        self.translator_numadd = Label(self.translator_lf, text='0')
        self.translator_numadd.pack()
        self.translator_numadd.place(x=270, y=63)
        self.reader_selectall = Checkbutton(self.translator_lf, text='Select all targets',
                                            variable=self.reader_all, command=self.trans_selectall)
        self.reader_selectall.pack()
        self.reader_selectall.place(x=350, y=25)
        self.reader_notranslate = Checkbutton(self.translator_lf, text='Disable translation',
                                              variable=self.reader_notrans, command=self.trans_notrans)
        self.reader_notranslate.pack()
        self.reader_notranslate.place(x=350, y=45)
        self.reader_lock = Checkbutton(self.translator_lf, text='Lock targets for reading',
                                       variable=self.trans_lock_v, command=self.trans_lock)
        self.reader_lock.pack()
        self.reader_lock.place(x=350, y=65)
        # -------------------------------------------------------------------------------------------------------------
        #                       LOGGING
        # -------------------------------------------------------------------------------------------------------------
        self.logtext = Text(master, height=4, width=73, bd=5)
        self.logtext.pack()
        self.logtext.place(x=7, y=590)
        self.logptr = 0
        self.lcolor = []
        self.lowrite('\n- - - - - - - - - - - - - - - Logfile init - - - - - - - - - - - - - - -\n')
        # -------------------------------------------------------------------------------------------------------------
        #                       DISPLAY ZONE
        # -------------------------------------------------------------------------------------------------------------
        self.display_lf = LabelFrame(self.master, width=744, height=660)
        self.display_lf.place(x=610, y=6)
        self.select_lf = LabelFrame(self.display_lf, width=740, height=40)
        self.select_lf.place(x=0, y=0)
        self.information = Label(self.select_lf, text='Select a matrix to plot in slot 1:').place(x=5, y=5)
        self.information_sel = ttk.Combobox(self.select_lf, width=21, state='readonly')
        self.information_sel.pack()
        self.information_sel.place(x=180, y=5)
        self.information_sel["values"] = ['Raw correlation', 'After token processing', 'After PM', 'After FB-BCM']
        self.information2 = Label(self.select_lf, text='Select a matrix to plot in slot 2:').place(x=405, y=5)
        self.information_sel2 = ttk.Combobox(self.select_lf, width=21, state='readonly')
        self.information_sel2.pack()
        self.information_sel2.place(x=580, y=5)
        self.information_sel2["values"] = ['Raw correlation', 'After token processing', 'After PM', 'After FB-BCM']
        self.update_button = HoverButton(self.select_lf, text='Update', command=self.update_image,
                                         width=7, bg=self.colors.red)
        self.update_button.pack()
        self.update_button.place(x=340, y=5)

        self.img_lf = LabelFrame(self.display_lf, width=370, height=370)
        self.img_lf.place(x=0, y=40)
        self.gt_lf = LabelFrame(self.display_lf, width=370, height=370)
        self.gt_lf.place(x=370, y=40)

# ----------------------------------
    def import_file(self):
        filename = filedialog.askopenfilename(filetypes=[('Text Files', '*.txt')], initialdir=MAIN_TEXTBASE_LOCATION)
        self.test_target = filename
        self.lowrite(f'Added {filename} to testing target.', cat='Info')

    def export_file(self):
        if self.test_tree is not None:
            ds.write_tree(self.test_tree, 'test_tree')
            self.lowrite(f'Testing tree written in ~/db/trees/test_tree.3s.', cat='Info')
        else:
            self.lowrite(f'Cannot export tree: no tree generated by FB-BCM.', cat='Error')

    def trace_files(self):
        # newwindow = Toplevel(self.master)
        # newwindow.geometry('800x30')
        # newwindow.iconbitmap(ICO_LOCATION)
        # newwindow.title('Test targets:')
        # Label(newwindow, text=self.test_target).place(x=0, y=5)
        filename = filedialog.askopenfilename(filetypes=[('Tree Files', '*.3s')], initialdir=TREES_DIR)
        self.lowrite(f'Showing up tree {filename}.', cat='Info')
        treethread = Thread(target=tree_tracer, args=(filename, True))
        treethread.start()

# ----------------------------------
    def download_model(self):
        bert_url = self.nlpmodel_downloadurl.get('1.0', END + '-1c')
        try:
            if bert_url not in self.model_list:
                self.correlation_model = SentenceTransformer(bert_url)
                with open(MODEL_LIST_LOCATION, 'a') as file:
                    file.write('\n' + bert_url)
                self.nlpmodel_downloadurl.delete('1.0', END)
                self.model_list.append(bert_url)
                self.nlpmodel_list["values"] = self.model_list
                self.launcher_corrmodel["values"] = self.model_list
            else:
                self.lowrite(f'Model: {bert_url} already downloaded.', cat='Warning')
        except Exception as ex:
            self.lowrite(f'Model: {bert_url} not found. {ex}', cat='Warning')

    def load_model(self):
        model_name = '__empty__'
        max_cap = 30
        try:
            model_name = self.nlpmodel_list.get()
            if model_name != '' and model_name != '__empty__':
                self.correlation_model = SentenceTransformer(model_name)
                if len(model_name) > max_cap:
                    model_name = model_name[:max_cap]
                self.nlpmodel_modelloaded.config(text=model_name)
                self.lowrite(f'Sucesfully loaded model: {model_name}.', cat='Info')
            else:
                self.lowrite(f'Cannot load the model, there is no selection.', cat='Warning')
        except Exception as ex:
            self.lowrite(f'Cannot load model: {model_name}. {ex}', cat='Error')

# -----------------------------------
    def launch_algo_lock(self):
        if self.launcher_algo_lock_v.get():
            self.fbbcmth = self.launcher_algo_thpm.get()
            self.pmth = self.launcher_algo_thpm.get()
            self.oim = self.launcher_algo_oimpm.get()
            self.launcher_algo_infothfbcm['state'] = DISABLED
            self.launcher_algo_infothpm['state'] = DISABLED
            self.launcher_algo_infooimpm['state'] = DISABLED
            self.launcher_algo_oimpm['state'] = DISABLED
            self.launcher_algo_thpm['state'] = DISABLED
            self.launcher_algo_thfbcm['state'] = DISABLED
            self.lowrite(f'Algorythm settings locked.', cat='Note')
        else:
            self.launcher_algo_infothfbcm['state'] = NORMAL
            self.launcher_algo_infothpm['state'] = NORMAL
            self.launcher_algo_infooimpm['state'] = NORMAL
            self.launcher_algo_oimpm['state'] = NORMAL
            self.launcher_algo_thpm['state'] = NORMAL
            self.launcher_algo_thfbcm['state'] = NORMAL
            self.lowrite(f'Algorythm settings unlocked.', cat='Note')

    def launch_file_lock(self):
        if self.launcher_file_lock_v.get():
            self.launcher_file_selectall['state'] = DISABLED
            self.launcher_file_visualize_target['state'] = DISABLED
            self.launcher_file_addtgt['state'] = DISABLED
            self.launcher_file_ntgs_info['state'] = DISABLED
            self.launcher_file_rmvtgt['state'] = DISABLED
            self.launcher_file_ntgs['state'] = DISABLED
            self.lowrite(f'Targets for launch locked.', cat='Note')
        else:
            self.launcher_file_selectall['state'] = NORMAL
            if not self.selectall_v.get():
                self.launcher_file_visualize_target['state'] = NORMAL
                self.launcher_file_addtgt['state'] = NORMAL
                self.launcher_file_ntgs_info['state'] = NORMAL
                self.launcher_file_rmvtgt['state'] = NORMAL
                self.launcher_file_ntgs['state'] = NORMAL
            self.lowrite(f'Targets for launch unlocked.', cat='Note')

    def launch_corr_lock(self):
        if self.launcher_corr_lock_v.get():
            self.decorrelation = self.launcher_decorrelation.get()
            self.correlation_model_launch = self.launcher_corrmodel.get()
            self.launcher_corrmodel_info['state'] = DISABLED
            self.launcher_corrmodel['state'] = DISABLED
            self.launcher_decorrelation_info2['state'] = DISABLED
            self.launcher_decorrelation_info['state'] = DISABLED
            self.launcher_decorrelation['state'] = DISABLED
            self.launcher_tokenenable['state'] = DISABLED
            self.lowrite(f'Correlation settings locked.', cat='Note')
        else:
            self.launcher_corrmodel_info['state'] = NORMAL
            self.launcher_corrmodel['state'] = NORMAL
            self.launcher_decorrelation_info2['state'] = NORMAL
            self.launcher_decorrelation_info['state'] = NORMAL
            self.launcher_decorrelation['state'] = NORMAL
            self.launcher_tokenenable['state'] = NORMAL
            self.lowrite(f'Correlation settings unlocked.', cat='Note')

    def launch_parameters(self):
        if self.launcher_algo_lock_v.get() and self.launcher_corr_lock_v.get() and self.launcher_file_lock_v.get():
            threads = []
            the_args = {'correlation_model': self.correlation_model_launch,
                        'fbbcm-th': float(self.fbbcmth),
                        'pm-th': float(self.pmth),
                        'oim': int(self.oim),
                        'tokens': self.launch_tokenbool.get(),
                        'decorrelation': float(self.decorrelation)}
            if self.selectall_v.get():
                tlist = os.listdir(MAIN_DATABASE_LOCATION)
                for nt, case in enumerate(tlist):
                    if case[0] != '!':
                        the_args['target'] = f'{MAIN_DATABASE_LOCATION}/{case}'
                        threads.append(Thread(target=launching_thread,
                                              args=(self, nt),
                                              kwargs={'correlation_model': the_args['correlation_model'],
                                                      'fbbcm-th': the_args['fbbcm-th'],
                                                      'pm-th': the_args['pm-th'],
                                                      'oim': the_args['oim'],
                                                      'tokens': the_args['tokens'],
                                                      'decorrelation': the_args['decorrelation'],
                                                      'target': the_args['target']
                                                      }))
                        casex = case.split('/')[-1]
                        self.lowrite(f'Created thread {nt+1} for case {casex} in launcher.', cat='Info')
            else:
                for nt, case in enumerate(self.launcher_target):
                    the_args['target'] = case
                    threads.append(Thread(target=launching_thread,
                                          args=(self, nt),
                                          kwargs={'correlation_model': the_args['correlation_model'],
                                                  'fbbcm-th': the_args['fbbcm-th'],
                                                  'pm-th': the_args['pm-th'],
                                                  'oim': the_args['oim'],
                                                  'tokens': the_args['tokens'],
                                                  'decorrelation': the_args['decorrelation'],
                                                  'target': the_args['target']
                                                  }))
                    casex = case.split('/')[-1]
                    self.lowrite(f'Created thread {nt+1} for case {casex} in launcher.', cat='Info')
            for thread in threads:
                thread.start()
            self.lowrite(f'All threads launched.', cat='Info')
        else:
            self.lowrite(f'Launcher did not start.', cat='Warning')
            self.lowrite(f'In order to launch the targets, all features must be locked.', cat='Note')

    def launch_file_all(self):
        if self.selectall_v.get():
            self.launcher_file_ntgs.config(text='All')
            self.launcher_file_ntgs['state'] = DISABLED
            self.launcher_file_visualize_target['state'] = DISABLED
            self.launcher_file_addtgt['state'] = DISABLED
            self.launcher_file_ntgs_info['state'] = DISABLED
            self.launcher_file_rmvtgt['state'] = DISABLED
            self.lowrite(f'All targets selected.', cat='Note')
        else:
            self.launcher_file_ntgs.config(text=str(self.num_launch_targets))
            self.launcher_file_ntgs['state'] = NORMAL
            self.launcher_file_visualize_target['state'] = NORMAL
            self.launcher_file_addtgt['state'] = NORMAL
            self.launcher_file_ntgs_info['state'] = NORMAL
            self.launcher_file_rmvtgt['state'] = NORMAL
            self.lowrite(f'Selected targets in launch target scope.', cat='Note')

    def launch_add(self):
        filename = filedialog.askdirectory(initialdir=MAIN_TEXTBASE_LOCATION)
        if filename not in self.launcher_target and filename:
            self.launcher_target.append(filename)
            self.num_launch_targets += 1
            self.launcher_file_ntgs.config(text=str(self.num_launch_targets))
            self.lowrite(f'Added to launch target scope: {filename}.', cat='Note')
        else:
            self.lowrite(f'Cannot add file \'{filename}\' to launch target scope. Maybe it is already selected.',
                         cat='Warning')

    def launch_rmv(self):
        self.num_launch_targets = 0
        self.launcher_target = []
        self.launcher_file_ntgs.config(text=str(self.num_launch_targets))
        self.lowrite(f'All targets in the launch target scope removed.', cat='Note')

    def launch_visualize(self):
        newwindow = Toplevel(self.master)
        sized = 20*len(self.launcher_target) + 5
        newwindow.geometry(f'800x{sized}')
        newwindow.iconbitmap(ICO_LOCATION)
        newwindow.title('Launching targets:')
        for n, target in enumerate(self.launcher_target):
            Label(newwindow, text=target).place(x=0, y=5 + 20*n)
# -----------------------------------

    def fbbcm_watch(self):
        self.watch_fbbcm = True
        self.fbbcmth_test = float(self.fbbcm_thentry.get())
        self.lowrite(f'Watch for FB-BCM.', cat='Info')
        self.update_image()
        self.watch_fbbcm = False

    def fbbcm_launch(self):
        self.fbbcmth_test = float(self.fbbcm_thentry.get())
        self.lowrite(f'FB-BCM th set to {self.fbbcmth_test}.', cat='Info')
        self.launch_test()

    def fbbcm_enable(self):
        self.fbbcmth_test = float(self.fbbcm_thentry.get())
        self.pmth_test = float(self.pm_thentry.get())
        self.oim_test = int(self.pm_oimentry.get())
        if self.fbbcmen_test:
            self.fbbcmen_test = False
            self.lowrite('FB-BCM disabled for test.', cat='Info')
        else:
            self.fbbcmen_test = True
            self.lowrite('FB-BCM enabled for test.', cat='Info')

# ------------------------------------
    def pm_watch(self):
        self.watch_pm = True
        self.pmth_test = float(self.pm_thentry.get())
        self.oim_test = int(self.pm_oimentry.get())
        self.lowrite(f'Watch for PM.', cat='Info')
        self.update_image()
        self.watch_pm = False

    def pm_launch(self):
        self.pmth_test = float(self.pm_thentry.get())
        self.oim_test = int(self.pm_oimentry.get())
        self.fbbcmth_test = float(self.fbbcm_thentry.get())
        self.lowrite(f'PM th set to {self.pmth_test} and oim to {self.oim_test}.', cat='Info')
        self.launch_test()

    def pm_enable(self):
        self.pmth_test = float(self.pm_thentry.get())
        self.oim_test = int(self.pm_oimentry.get())
        if self.pmen_test:
            self.pmen_test = False
            self.lowrite('PM disabled for test.', cat='Info')
        else:
            self.pmen_test = True
            self.lowrite('PM enabled for test.', cat='Info')

# -------------------------------------
    def token_enable(self):
        self.test_decorrelation = float(self.token_decorrelation.get())
        self.lowrite(f'Time decorrelation enabled.', cat='Info')

    def set_up_token(self):
        self.test_decorrelation = float(self.token_decorrelation.get())
        self.lowrite(f'Decorrelation by time tokens set to {self.test_decorrelation}.', cat='Info')

# -------------------------------------
    def trans_add(self):
        filename = filedialog.askdirectory(initialdir=MAIN_DATABASE_LOCATION)
        if filename not in self.read_target and filename:
            self.read_target.append(filename)
            self.num_read_targets += 1
            self.translator_numadd.config(text=str(self.num_read_targets))
            self.lowrite(f'Added to translation target scope: {filename}.', cat='Note')
        else:
            self.lowrite(f'Cannot add file \'{filename}\' to translation target scope. Maybe it is already selected.',
                         cat='Warning')

    def trans_rmv(self):
        self.read_target = []
        self.num_read_targets = 0
        self.translator_numadd.config(text=str(self.num_read_targets))
        self.lowrite(f'All targets in the translation target scope removed.', cat='Note')

    def trans_view(self):
        newwindow = Toplevel(self.master)
        sized = 20*len(self.read_target) + 5
        newwindow.geometry(f'800x{sized}')
        newwindow.iconbitmap(ICO_LOCATION)
        newwindow.title('Reading targets:')
        for n, target in enumerate(self.read_target):
            Label(newwindow, text=target).place(x=0, y=5 + 20*n)

    def trans_launch(self):
        if self.trans_lock_v.get():
            threads = []
            bool_trans = not self.reader_notrans.get()
            tmodel = self.translator_model.get()
            if self.reader_all.get():
                threads.append(Thread(target=traduction_thread, kwargs={'translate_model': bool_trans,
                                                                        'tmodel': tmodel}))
                self.lowrite(f'Created thread for all cases in translator.', cat='Info')
            else:
                for case in self.read_target:
                    the_case = case.split('/')[-1]
                    threads.append(Thread(target=traduction_thread, kwargs={'translate_model': bool_trans,
                                                                            'search_case': the_case,
                                                                            'tmodel': tmodel}))
                    casex = case.split('/')[-1]
                    self.lowrite(f'Created thread for case {casex} in translator.', cat='Info')
            for thread in threads:
                thread.start()
        else:
            self.lowrite(f'Translator did not start.', cat='Warning')
            self.lowrite(f'In order to translate the targets, all features must be locked.', cat='Note')

    def trans_notrans(self):
        if self.reader_notrans.get():
            self.tranlator_modelinfo['state'] = DISABLED
            self.translator_model['state'] = DISABLED
            self.lowrite(f'Translation disabled for reading.', cat='Note')
        else:
            self.tranlator_modelinfo['state'] = NORMAL
            self.translator_model['state'] = NORMAL
            self.lowrite(f'Translation enabled for reading.', cat='Note')

    def trans_selectall(self):
        if self.reader_all.get():
            self.translator_numadd.config(text='All')
            self.lowrite(f'Enabled all files in translator.', cat='Note')
        else:
            self.translator_numadd.config(text=str(self.num_read_targets))
            self.lowrite(f'Disabled all files in translator.', cat='Note')

    def trans_lock(self):
        if self.trans_lock_v.get():
            self.tranlator_modelinfo['state'] = DISABLED
            self.translator_model['state'] = DISABLED
            self.translator_bworsetarget['state'] = DISABLED
            self.translator_removetarget['state'] = DISABLED
            self.translator_viewtarget['state'] = DISABLED
            self.translator_infoadd['state'] = DISABLED
            self.translator_numadd['state'] = DISABLED
            self.reader_selectall['state'] = DISABLED
            self.reader_notranslate['state'] = DISABLED
            self.lowrite(f'Locked translator and reader settings.', cat='Note')
        else:
            if not self.reader_notrans.get():
                self.tranlator_modelinfo['state'] = NORMAL
                self.translator_model['state'] = NORMAL
            self.translator_bworsetarget['state'] = NORMAL
            self.translator_removetarget['state'] = NORMAL
            self.translator_viewtarget['state'] = NORMAL
            self.translator_infoadd['state'] = NORMAL
            self.translator_numadd['state'] = NORMAL
            self.reader_selectall['state'] = NORMAL
            self.reader_notranslate['state'] = NORMAL
            self.lowrite(f'Unlocked translator and reader settings.', cat='Note')

    def lowrite(self, _text, cat=None, extra=None):
        if extra is not None:
            opening = extra
        else:
            opening = 'a'
        with open(LOG_FILE_PATH, opening, encoding='utf-8') as logfile:
            if cat is not None:
                text = f'\n<{time.ctime()}>\t[{cat}]:\t{_text}'
            else:
                text = _text
            logfile.writelines(text)
            try:
                self.lcolor.append(cat2color[cat])
            except KeyError:
                self.lcolor.append(CStyles.black)

            self.logtext.insert(END, text)
            self.logtext.tag_add(str(self.logptr), f'{len(self.lcolor)+1}.{self.logptr}', END)
            self.logtext.tag_config(str(self.logptr), foreground=self.lcolor[-1])
            self.logptr = self.logptr + len(text)
            self.logtext.see(END)

# -------------------------------------
    def update_image(self, noexe=True) -> None:
        if not noexe:
            self.launch_test()
        wtx = 0
        type1 = self.information_sel.get()
        type2 = self.information_sel2.get()

        if len(self.untokenized_matrix) == 0:
            self.lowrite('Test has not been launched yet, no figures created.', cat='Error')
            return

        # Type selection:
        if type1 == 'Raw correlation':
            self.target_matrix1 = self.untokenized_matrix
            self.sentence_stream_t1 = self.sentence_stream
        elif type1 == 'After token processing':
            self.target_matrix1 = self.tokenized_matrix
            self.sentence_stream_t1 = self.sentence_stream
        elif type1 == 'After PM':
            self.target_matrix1 = fbbcm.correlate(self.sentence_stream_pm, self.correlation_model)
            self.sentence_stream_t1 = self.sentence_stream_pm
        elif type1 == 'After FB-BCM':
            self.target_matrix1 = fbbcm.tree_equivalent_matrix(self.test_tree)
            self.sentence_stream_t1 = range(len(self.target_matrix1))

        if type2 == 'Raw correlation':
            self.target_matrix2 = self.untokenized_matrix
            self.sentence_stream_t2 = self.sentence_stream
        elif type2 == 'After token processing':
            self.target_matrix2 = self.tokenized_matrix
            self.sentence_stream_t2 = self.sentence_stream
        elif type2 == 'After PM':
            self.target_matrix2 = fbbcm.correlate(self.sentence_stream_pm, self.correlation_model)
            self.sentence_stream_t2 = self.sentence_stream_pm
        elif type2 == 'After FB-BCM':
            self.target_matrix2 = fbbcm.tree_equivalent_matrix(self.test_tree)
            self.sentence_stream_t2 = range(len(self.target_matrix2))

        # Matrix generation:
        sized1 = len(self.target_matrix1)
        thematrix = np.zeros((sized1, sized1, 3), dtype=np.uint8)
        for nrow, row in enumerate(self.target_matrix1):
            xrow = row.copy()
            mrow = (xrow.sort(), xrow[-2])[1]
            for ncol, element in enumerate(self.target_matrix1[nrow]):
                thematrix[nrow][ncol][0] = [element * 255 if element > 0 else 0][0]
                thematrix[nrow][ncol][1] = [element * 100 if element > 0 else 0][0]
                thematrix[nrow][ncol][2] = [element * wtx if element > 0 else 0][0]
                if element == mrow and self.watch_fbbcm:
                    thematrix[nrow][ncol][2] += 100

        for row, _ in enumerate(thematrix):
            for col, __ in enumerate(thematrix):
                if thematrix[row][col][2] > self.fbbcmth_test and thematrix[col][row][2] > self.fbbcmth_test:
                    thematrix[row][col][2] += 150

        if self.watch_pm:
            thesegmentation = Pbmm(self.target_matrix1, th=self.pmth_test, oim=self.oim_test).segmentation
            for segment in thesegmentation:
                base = segment[0]
                ending = segment[1]
                for index1 in range(ending - base + 1):
                    for index2 in range(ending - base + 1):
                        thematrix[base + index2][base + index1][2] += 150

        # Matrix generation:
        sized2 = len(self.target_matrix2)
        thematrix2 = np.zeros((sized2, sized2, 3), dtype=np.uint8)
        for nrow, row in enumerate(self.target_matrix2):
            xrow = row.copy()
            mrow = (xrow.sort(), xrow[-2])[1]
            for ncol, element in enumerate(self.target_matrix2[nrow]):
                thematrix2[nrow][ncol][0] = [element * 255 if element > 0 else 0][0]
                thematrix2[nrow][ncol][1] = [element * 100 if element > 0 else 0][0]
                thematrix2[nrow][ncol][2] = [element * wtx if element > 0 else 0][0]
                if element == mrow and self.watch_fbbcm:
                    thematrix2[nrow][ncol][2] += 100

        for row, _ in enumerate(thematrix2):
            for col, __ in enumerate(thematrix2):
                if thematrix2[row][col][2] > self.fbbcmth_test and thematrix2[col][row][2] > self.fbbcmth_test:
                    thematrix2[row][col][2] += 150

        if self.watch_pm:
            thesegmentation = Pbmm(self.target_matrix2, th=self.pmth_test, oim=self.oim_test).segmentation
            for segment in thesegmentation:
                base = segment[0]
                ending = segment[1]
                for index1 in range(ending - base + 1):
                    for index2 in range(ending - base + 1):
                        thematrix2[base + index2][base + index1][2] += 150

        # Figure plotting:
        plt.close()
        plt.close()
        myfig = plt.figure(figsize=(4.8, 4.3), dpi=75)
        plt.imshow(thematrix)
        img = Image.fromarray(thematrix)
        img.save(f'{IMAGE_PATH}slot1.png')
        plt.title(f'Matrix {type1}')
        axis = range(sized1)
        plt.xticks(axis, self.sentence_stream_t1, rotation='vertical')
        plt.yticks(axis, self.sentence_stream_t1)

        if self.canvas1 is not None:
            self.canvas1.get_tk_widget().pack_forget()
            self.toolbar1.destroy()
        self.canvas1 = FigureCanvasTkAgg(myfig, master=self.img_lf)
        self.canvas1.draw()
        self.toolbar1 = NavigationToolbar2Tk(self.canvas1, self.img_lf)
        self.toolbar1.update()
        self.canvas1.get_tk_widget().pack()

        myfig2 = plt.figure(figsize=(4.8, 4.3), dpi=75)
        plt.imshow(thematrix2)
        img = Image.fromarray(thematrix)
        img.save(f'{IMAGE_PATH}slot2.png')
        plt.title(f'Matrix {type2}')
        axis = range(sized2)
        plt.xticks(axis, self.sentence_stream_t2, rotation='vertical')
        plt.yticks(axis, self.sentence_stream_t2)

        if self.canvas2 is not None:
            self.canvas2.get_tk_widget().pack_forget()
            self.toolbar2.destroy()
        self.canvas2 = FigureCanvasTkAgg(myfig2, master=self.gt_lf)
        self.canvas2.draw()
        self.toolbar2 = NavigationToolbar2Tk(self.canvas2, self.gt_lf)
        self.toolbar2.update()
        self.canvas2.get_tk_widget().pack()
        self.lowrite(f'All images updated.', cat='Info')
        return

    def launch_test(self) -> None:
        if self.test_target is not None:
            [self.untokenized_matrix, self.tokenized_matrix, self.sentence_stream, self.sentence_stream_pm,
             self.pm_segmentation, self.test_tree] = \
                test_correlate(self, self.correlation_model, target=self.test_target,
                               decorrelation=self.test_decorrelation,
                               tokens=self.token_bool.get(), fbbcmth=self.fbbcmth_test, pmth=self.pmth_test,
                               oim=self.oim_test, pmen=self.pmen_test, fbbcmen=self.fbbcmen_test)
        else:
            self.lowrite('There is no target for test.', cat='Error')
        return
# -----------------------------------------------------------
# Main:


if __name__ == '__main__':
    main()
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
