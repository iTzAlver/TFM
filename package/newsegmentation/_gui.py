# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
from tkinter import Label, LabelFrame, PhotoImage, Checkbutton, BooleanVar, Entry, ttk, Text, Tk, Button

from sentence_transformers import SentenceTransformer

MULTIMEDIA_ROCKET_LOCATION = r'./.multimedia/rocketico.png'
MULTIMEDIA_EYE_LOCATION = r'./.multimedia/watch.png'
ICO_LOCATION = r'./.multimedia/rocketico.ico'
MODEL_LIST_LOCATION = r'./.multimedia/models.txt'
# -----------------------------------------------------------


def gui() -> None:
    root_node = Tk()
    MainWindow(root_node)
    root_node.iconbitmap(ICO_LOCATION)
    root_node.configure()
    root_node.mainloop()
    return


def _read_model_list() -> []:
    model_list = []
    with open(MODEL_LIST_LOCATION) as file:
        for line in file:
            model_list.append(line.rstrip('\n'))
    return model_list


class ColorStyles:
    blue = '#8685cb'
    pink = '#c539b7'
    yellow = '#c8c963'
    gray = '#BBBBBB'
    red = '#c42717'
    orange = '#cc5500'
    black = '#111111'


class HoverButton(Button):
    def __init__(self, master, **kw):
        Button.__init__(self, master=master, **kw)
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.brigth_span = 3
        self.newbg = None

    def on_enter(self, e):
        self.newbg = '#'
        for index in range(len(self["background"])):
            if index != 0:
                hex_str = str(hex(int(self["background"][index], 16) + self.brigth_span))
                self.newbg = self.newbg + hex_str[2]
        self['background'] = self.newbg
        return e

    def on_leave(self, e):
        self.newbg = '#'
        for index in range(len(self["background"])):
            if index != 0:
                hex_str = str(hex(int(self["background"][index], 16) - self.brigth_span))
                self.newbg = self.newbg + hex_str[2]
        self['background'] = self.newbg
        return e


class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Intra-day clustering GUI.")
        self.master.geometry('1360x710')
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
        self.canvas3 = None
        self.toolbar1 = None
        self.toolbar2 = None
        self.toolbar3 = None
        self.fbbcmth_test = 0.5
        self.pmth_test = 0.2
        self.oim_test = 1
        self.pmen_test = True
        self.fbbcmen_test = True
        self.sentence_stream_pm = []
        self.pm_segmentation = []
        self.watch_fbbcm = False
        self.watch_pm = False

        self.timestudy = None
        self.errors_listing = []

        self.ow = None
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
        HoverButton(self.nlpmodel_lf, text='Download model', command=self.download_model,
                    width=25, bg=self.colors.gray).place(x=5, y=65)
        HoverButton(self.nlpmodel_lf, text='Load model', command=self.load_model,
                    width=25, bg=self.colors.gray).place(x=200, y=65)
        Label(self.nlpmodel_lf, text='Place the model URL to download:').place(x=100, y=0)
        self.nlpmodel_list = ttk.Combobox(self.nlpmodel_lf, width=60, state='readonly')
        self.nlpmodel_list.pack()
        self.nlpmodel_list.place(x=5, y=99)
        self.nlpmodel_list["values"] = self.model_list
        self.nlpmodel_list.set(self.model_list[0])
        Label(self.nlpmodel_lf, text='Loaded model:').place(x=20, y=120)
        self.nlpmodel_modelloaded = Label(self.nlpmodel_lf, text='DEFAULT MODEL')
        self.nlpmodel_modelloaded.pack()
        self.nlpmodel_modelloaded.place(x=140, y=120)
        # -------------------------------------------------------------------------------------------------------------
        #                       LAUNCHER
        # -------------------------------------------------------------------------------------------------------------
        self.launcher_lf = LabelFrame(self.master, width=600, height=215, text='Launcher')
        self.launcher_lf.place(x=5, y=260+110)
        HoverButton(self.launcher_lf, command=self.launch_parameters,
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
        self.launcher_algo_thfbcm.insert(-1, '0.50')
        self.launcher_algo_thpm.insert(-1, '0.20')
        self.launcher_algo_oimpm.insert(-1, '1')
        self.launcher_algo_lock = Checkbutton(self.launcher_algo_lf, text='Lock this values for launch',
                                              variable=self.launcher_algo_lock_v, command=self.launch_algo_lock)
        self.launcher_algo_lock.pack()
        self.launcher_algo_lock.place(x=5, y=70)

        self.launcher_file_lf = LabelFrame(self.launcher_lf, width=260, height=115, text='Files target')
        self.launcher_file_lf.pack()
        self.launcher_file_lf.place(x=210, y=0)
        self.launcher_file_selectall = Checkbutton(self.launcher_file_lf, text='Select all files from database',
                                                   variable=self.selectall_v,
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
        self.launcher_corrmodel.set(self.model_list[0])
        self.launcher_tokenenable = Checkbutton(self.launcher_extra_lf, text='Enable token processing',
                                                variable=self.launch_tokenbool)
        self.launcher_tokenenable.pack()
        self.launcher_tokenenable.place(x=0, y=25)
        self.launcher_decorrelation = Entry(self.launcher_extra_lf, width=7)
        self.launcher_decorrelation.place(x=280, y=30)
        self.launcher_decorrelation.insert(-1, '20.00')
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
        Label(self.fbbcm_lf, text='Method\'s threshold:').place(x=5, y=5)
        self.fbbcm_thentry = Entry(self.fbbcm_lf, width=8)
        self.fbbcm_thentry.pack()
        self.fbbcm_thentry.place(x=125, y=5)
        self.fbbcm_thentry.insert(-1, '0.50')
        HoverButton(self.fbbcm_lf, command=self.fbbcm_watch, bg=self.colors.red,
                    image=self.watch_img).place(x=4, y=30)
        HoverButton(self.fbbcm_lf, command=self.fbbcm_launch, bg=self.colors.red,
                    image=self.rocketlaunchS_img).place(x=143, y=30)
        HoverButton(self.fbbcm_lf, command=self.fbbcm_enable, bg=self.colors.orange,
                    text="Disable FB-BCM", heigh=2).place(x=47, y=31)
        # -------------------------------------------------------------------------------------------------------------
        #                       PM      METHOD
        # -------------------------------------------------------------------------------------------------------------
        self.pmtoken_lf = LabelFrame(self.master, width=195, height=120, text='PM algorythm')
        self.pmtoken_lf.place(x=410, y=110)
        Label(self.pmtoken_lf, text='Method\'s threshold:').place(x=5, y=5)
        self.pm_thentry = Entry(self.pmtoken_lf, width=8)
        self.pm_thentry.pack()
        self.pm_thentry.place(x=125, y=5)
        self.pm_thentry.insert(-1, '0.20')
        Label(self.pmtoken_lf, text='Method\'s stages:').place(x=5, y=27)
        self.pm_oimentry = Entry(self.pmtoken_lf, width=8)
        self.pm_oimentry.pack()
        self.pm_oimentry.place(x=125, y=27)
        self.pm_oimentry.insert(-1, '1')
        HoverButton(self.pmtoken_lf, command=self.pm_watch, bg=self.colors.red,
                    image=self.watch_img).place(x=4, y=52)
        HoverButton(self.pmtoken_lf, command=self.pm_launch, bg=self.colors.red,
                    image=self.rocketlaunchS_img).place(x=143, y=52)
        HoverButton(self.pmtoken_lf, command=self.pm_enable, bg=self.colors.orange,
                    text="Disable PM", width=12, heigh=2).place(x=48, y=53)
        HoverButton(self.master, command=self.optimization_callback, bg=self.colors.blue,
                    text="Parameters optimization", width=26).place(x=410, y=233)
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
        Label(self.tokencontrol_lf, text='Decorrelation:').place(x=5, y=21)
        Label(self.tokencontrol_lf, text='%').place(x=135, y=21)
        self.token_decorrelation = Entry(self.tokencontrol_lf, width=7)
        self.token_decorrelation.place(x=90, y=21)
        self.token_decorrelation.insert(-1, '20.00')
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
        self.translator_model.set("GoogleTranslate - Online traduction.")
        self.translator_bworsetarget = HoverButton(self.translator_lf, text='Browse target', command=self.trans_add,
                                                   width=15, bg=self.colors.gray)
        self.translator_bworsetarget.place(x=5, y=25)
        self.translator_removetarget = HoverButton(self.translator_lf, text='Remove targets', command=self.trans_rmv,
                                                   width=15, bg=self.colors.gray)
        self.translator_removetarget.place(x=5, y=55)
        self.translator_viewtarget = HoverButton(self.translator_lf, text='Check\ntargets', command=self.trans_view,
                                                 width=12, heigh=3, bg=self.colors.gray)
        self.translator_viewtarget.place(x=130, y=25)
        HoverButton(self.translator_lf, command=self.trans_launch,
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
        self.logtext = Text(master, height=6, width=73, bd=5)
        self.logtext.pack()
        self.logtext.place(x=7, y=590)
        self.logptr = 0
        self.lcolor = []
        self.lowrite('- - - - - - - - - - - - - - - Logfile init - - - - - - - - - - - - - - -\n', cat='Intro')
        # -------------------------------------------------------------------------------------------------------------
        #                       DISPLAY ZONE
        # -------------------------------------------------------------------------------------------------------------
        self.display_lf = LabelFrame(self.master, width=744, height=700)
        self.display_lf.place(x=610, y=6)
        self.select_lf = LabelFrame(self.display_lf, width=740, height=40)
        self.select_lf.place(x=0, y=0)
        Label(self.select_lf, text='Select a matrix to plot in slot 1:').place(x=5, y=5)
        self.information_sel = ttk.Combobox(self.select_lf, width=21, state='readonly')
        self.information_sel.pack()
        self.information_sel.place(x=180, y=5)
        self.information_sel["values"] = ['Raw correlation', 'After token processing', 'After PM', 'After FB-BCM']
        self.information_sel.set('After token processing')
        Label(self.select_lf, text='Select a matrix to plot in slot 2:').place(x=405, y=5)
        self.information_sel2 = ttk.Combobox(self.select_lf, width=21, state='readonly')
        self.information_sel2.pack()
        self.information_sel2.place(x=580, y=5)
        self.information_sel2["values"] = ['Raw correlation', 'After token processing', 'After PM', 'After FB-BCM']
        self.information_sel2.set('After FB-BCM')
        self.update_button = HoverButton(self.select_lf, text='Update', command=self.update_image,
                                         width=7, bg=self.colors.orange)
        self.update_button.pack()
        self.update_button.place(x=340, y=5)

        self.img_lf = LabelFrame(self.display_lf, width=370, height=370)
        self.img_lf.place(x=0, y=40)
        self.gt_lf = LabelFrame(self.display_lf, width=370, height=370)
        self.gt_lf.place(x=370, y=40)
        self.pie_lf = LabelFrame(self.display_lf, width=370, height=285)
        self.pie_lf.place(x=0, y=410)
        self.moreinfo_lf = LabelFrame(self.display_lf, width=370, height=285)
        self.moreinfo_lf.place(x=370, y=410)

        self.persistance_jump = HoverButton(self.pie_lf, text='TO PERSISTANCE', command=self.persistance_jumpwin,
                                            width=16, bg=self.colors.blue)
        self.persistance_jump.pack()
        self.persistance_jump.place(x=235, y=248)

        Label(self.moreinfo_lf, text='Select a tree payload:').place(x=5, y=5)
        self.textsel = ttk.Combobox(self.moreinfo_lf, width=7, state='readonly')
        self.textsel.pack()
        self.textsel.place(x=130, y=5)
        self.textsel.bind("<<ComboboxSelected>>", self.watch_tree_callback)
        self.textsel["values"] = []
        self.textree = Text(self.moreinfo_lf, height=14, width=43, bd=3)
        self.textree.pack()
        self.textree.place(x=5, y=40)
        self.othertreebutton = HoverButton(self.moreinfo_lf, text='Select other tree', command=self.other_tree,
                                           width=18, bg=self.colors.red)
        self.othertreebutton.pack()
        self.othertreebutton.place(x=210, y=5)
   
# -----------------------------------------------------------
# Main:


if __name__ == '__main__':
    gui()

# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
