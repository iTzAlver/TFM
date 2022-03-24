# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                                                           #
#   This file was created by: Alberto Palomo Alonso         #
# Universidad de Alcalá - Escuela Politécnica Superior      #
#                                                           #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
# Import statements:
import random
from collections import defaultdict
from tkinter import END
from tkinter import LabelFrame, Text, Label, ttk, filedialog, Entry, PhotoImage
from tkinter import Tk

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

import package.dserial as ds
from package.styles import ColorStyles, HoverButton

ICO_LOCATION = r'./.multimedia/isdefeico.ico'
TREES_DIR = r'./db/trees/'
LOGO_LOCATION = r'./.multimedia/isdefe.png'
UPARROW_LOCATION = r'./.multimedia/uprow.png'
DOWNARROW_LOCATION = r'./.multimedia/downrow.png'

PLOTCOLOR = {'0': '#6175c1', '1': '#dede49', '2': '#55db48', '3': '#db4064', '4': '#d18238', '5': '#cf38b8',
             '6': '#9612e3', '7': '#96e307', '8': '#1912e3', '9': '#000000', '10': '#12d5e3', '11': '#806c08'}
NUM_LABELS = 4


# -----------------------------------------------------------
def main() -> None:
    root_node = Tk()
    MainWindow(root_node)
    root_node.iconbitmap(ICO_LOCATION)
    root_node.configure()
    root_node.mainloop()
    return


def get_max_wd(string):
    temp = defaultdict(int)
    string_ = string.replace('.', '')
    string_ = string_.replace('\n', '')
    string_ = string_.replace(',', '')
    for wrd in string_.split():
        if len(wrd) > 4:
            wrd_ = f'{wrd[0].lower()}{wrd[1:]}'
            temp[wrd_] += 1
    maxarg__ = max(temp, key=temp.get)
    maxarg_ = f'{maxarg__[0].upper()}{maxarg__[1:]}'
    return maxarg_


def mat2ad(mtx0):
    ady = []
    shap = []
    treex = 0
    for day, dayO in enumerate(mtx0):
        for tree, treeO in enumerate(dayO):
            ady_ = []
            for day2, dayO2 in enumerate(treeO):
                for tree2, treeO2 in enumerate(dayO2):
                    ady_.append(treeO2)
            ady.append(ady_)
            treex = tree + 1
        shap.append(treex)
    return np.array(ady), shap


def tree_stream_tracer(thematrix, tree_stream, labels):
    fig = go.Figure()
    cnt = 0
    timer = np.zeros((NUM_LABELS, len(thematrix)))
    payload = ['' for _ in range(NUM_LABELS)]
    for thedays, daystrees in enumerate(thematrix):
        cl = [255 * random.random(), 255 * random.random(), 255 * random.random()]
        for thetrees, tree in enumerate(daystrees):
            for day2, daycos in enumerate(tree):
                for tree2, treecorr in enumerate(daycos):

                    inverse = thematrix[day2][tree2][thedays][thetrees]
                    max_inverse = max(thematrix[day2][tree2][thedays])
                    if treecorr > 0.1 and treecorr == max(daycos) and inverse > 0.1 and inverse == max_inverse:
                        fig.add_trace(go.Scatter(x=[thetrees, tree2],
                                                 y=[thedays, day2],
                                                 mode='lines',
                                                 line=dict(color=f'rgb({cl[0]},{cl[1]},{cl[2]})', width=0.5),
                                                 showlegend=False,
                                                 opacity=0.3
                                                 ))
            label = labels[cnt]
            fig.add_trace(go.Scatter(x=[thetrees],
                                     y=[thedays],
                                     mode='markers',
                                     name=f'Tree {thetrees} day {thedays}',
                                     marker=dict(symbol='circle-dot',
                                                 size=18,
                                                 color=PLOTCOLOR[str(label)],
                                                 line=dict(color='rgb(90,90,90)', width=1)
                                                 ),
                                     text=f'{tree_stream[thedays][thetrees].payload}',
                                     hoverinfo='text',
                                     opacity=0.8
                                     ))
            timer[label][thedays] += tree_stream[thedays][thetrees].timing
            payload[label] = f'{payload[label]} {tree_stream[thedays][thetrees].payload}'
            cnt += 1
    fig.show()
    return timer, payload


def get_correlation(tree_0, tree_1):
    code1 = tree_0.code
    code2 = tree_1.code
    return cosine_similarity(code1.reshape(1, -1), code2.reshape(1, -1))[0][0]


def stream_correlation(trees_stream, threshold, nwords) -> [[[[float]]]]:
    sctm = []
    for trees in trees_stream:
        uctm = []
        for tree in trees:
            ctm = []
            for trees_external in trees_stream:
                ctm_day = []
                for tree_external in trees_external:
                    if tree_external.day != tree.day and len(tree.payload.split(' ')) > nwords:
                        thecorr = get_correlation(tree, tree_external)
                        if thecorr > threshold:
                            ctm_day.append(thecorr)
                        else:
                            ctm_day.append(0)
                    else:
                        ctm_day.append(0)
                ctm.append(ctm_day)
            uctm.append(ctm)
        sctm.append(uctm)
    return sctm


class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Extra-day clustering GUI (Test).")
        self.master.geometry('875x540')
        self.colors = ColorStyles

        self.tree_streams = {}
        self.names = []
        self.mtx = []
        self.labelmtx = []

        self.ady = []
        self.shape = []
        self.kmeans = []
        self.timing = []
        self.labeltitles = []
        # -------------------------------------------------------------------------------------
        self.imglogo = PhotoImage(file=LOGO_LOCATION)
        # self.imglogo = self.imglogo.subsample(1)
        self.img_arrup = PhotoImage(file=UPARROW_LOCATION)
        self.img_arrup = self.img_arrup.subsample(20)
        self.img_arrdw = PhotoImage(file=DOWNARROW_LOCATION)
        self.img_arrdw = self.img_arrdw.subsample(20)
        # -------------------------------------------------------------------------------------
        # self.lf_logo = LabelFrame(self.master, width=395, height=100)
        # self.lf_logo.pack()
        # self.lf_logo.place(x=475, y=5)
        self.labelogo = Label(self.master)
        self.labelogo.config(image=self.imglogo)
        self.labelogo.pack()
        # self.labelogo.place(x=100, y=15)
        self.labelogo.place(x=485, y=-8)
        # -------------------------------------------------------------------------------------
        self.lf_import = LabelFrame(self.master, width=250, height=100, text='Tree importation')
        self.lf_import.pack()
        self.lf_import.place(x=5, y=5)
        self.importbutton = HoverButton(self.lf_import, text='Import tree-stream', command=self.import_trees,
                                        width=15, bg=self.colors.gray)
        self.importbutton.pack()
        self.importbutton.place(x=5, y=5)
        self.resetbutton = HoverButton(self.lf_import, text='Reset tree-streams', command=self.reset_streams,
                                       width=15, bg=self.colors.gray)
        self.resetbutton.pack()
        self.resetbutton.place(x=125, y=5)
        self.importlabel = Label(self.lf_import, text='Last imported tree days: ')
        self.importlabel.pack()
        self.importlabel.place(x=5, y=35)
        self.importlabel_d = Label(self.lf_import, text='<No import>')
        self.importlabel_d.pack()
        self.importlabel_d.place(x=145, y=35)
        self.importlabel2 = Label(self.lf_import, text='Last case imported: ')
        self.importlabel2.pack()
        self.importlabel2.place(x=5, y=55)
        self.importlabel_d2 = Label(self.lf_import, text='<No import>')
        self.importlabel_d2.pack()
        self.importlabel_d2.place(x=145, y=55)
        # -------------------------------------------------------------------------------------
        self.lf_watch = LabelFrame(self.master, width=250, height=430, text='Watch trees')
        self.lf_watch.pack()
        self.lf_watch.place(x=5, y=105)
        self.selectree_info = Label(self.lf_watch, text='Select a tree stream:')
        self.selectree_info.pack()
        self.selectree_info.place(x=5, y=5)
        self.selectree = ttk.Combobox(self.lf_watch, width=15, state='readonly')
        self.selectree.pack()
        self.selectree.place(x=125, y=5)
        self.selectree.bind("<<ComboboxSelected>>", self.watchtrees)
        self.selectree["values"] = self.names
        self.selectree_info2 = Label(self.lf_watch, text='Select a day in stream:')
        self.selectree_info2.pack()
        self.selectree_info2.place(x=5, y=35)
        self.selectree2 = ttk.Combobox(self.lf_watch, width=13, state='readonly')
        self.selectree2.pack()
        self.selectree2.place(x=135, y=35)
        self.selectree2.bind("<<ComboboxSelected>>", self.watchtrees_day)
        self.texttree = Text(self.lf_watch, height=21, width=29, bd=2)
        self.texttree.pack()
        self.texttree.place(x=4, y=65)
        # -------------------------------------------------------------------------------------
        self.lf_correlate = LabelFrame(self.master, width=210, height=100, text='Tree correlation')
        self.lf_correlate.pack()
        self.lf_correlate.place(x=260, y=5)
        self.runbutton = HoverButton(self.lf_correlate, text='Correlate stream', command=self.run_correlation,
                                     width=15, bg=self.colors.gray)
        self.runbutton.pack()
        self.runbutton.place(x=5, y=5)
        self.selectarget_info = Label(self.lf_correlate, text='Select target:')
        self.selectarget_info.pack()
        self.selectarget_info.place(x=15, y=35)
        self.selectarget = ttk.Combobox(self.lf_correlate, width=14, state='readonly')
        self.selectarget.pack()
        self.selectarget.place(x=5, y=55)

        self.th_info = Label(self.lf_correlate, text='Threshold:').place(x=130, y=35)
        self.th_entry = Entry(self.lf_correlate, width=10)
        self.th_entry.pack()
        self.th_entry.place(x=128, y=56)
        self.th_entry.insert(-1, '0.55')

        self.news_info = Label(self.lf_correlate, text='News:').place(x=140, y=-7)
        self.nw_entry = Entry(self.lf_correlate, width=5)
        self.nw_entry.pack()
        self.nw_entry.place(x=143, y=14)
        self.nw_entry.insert(-1, '4')
        # -------------------------------------------------------------------------------------
        self.lf_graph = LabelFrame(self.master, width=610, height=425)
        self.lf_graph.pack()
        self.lf_graph.place(x=260, y=110)
        self.canvas = None
        self.toolbar = None
        self.buttonup = HoverButton(self.lf_graph, text='Up', command=self.rotate_up,
                                    width=4, bg=self.colors.gray)
        self.buttondown = HoverButton(self.lf_graph, text='Down', command=self.rotate_down,
                                      width=4, bg=self.colors.gray)
        self.buttonnorm = HoverButton(self.lf_graph, text='Normalize', command=self.normalize,
                                      width=8, bg=self.colors.gray)
        # -------------------------------------------------------------------------------------

    def import_trees(self) -> None:
        filenames = filedialog.askopenfilenames(filetypes=[('Tree Files', '*.3s')],
                                                initialdir=TREES_DIR)
        stream = []
        filename = ''
        try:
            for _filename in filenames:
                filename = _filename.split('/')[-1].split('.')[0]
                stream.append(ds.read_tree(filename))
            if len(stream) > 0:
                name = f'{filename.split("_")[0]}_{len(stream)}'
                self.names.append(name)
                self.tree_streams[name] = stream
                self.importlabel_d.config(text=f'{len(stream)} days.')
                self.importlabel_d2.config(text=f'{filename.split("_")[0]}.')
                self.selectree["values"] = self.names
                self.selectarget["values"] = self.names

        except Exception as ex:
            print(f'Exception raised: {ex}')
        finally:
            return None

    def reset_streams(self) -> None:
        self.tree_streams = {}
        self.names = []
        self.selectree["values"] = []
        self.selectarget["values"] = []
        return None

    def watchtrees(self, event):
        self.selectree2["values"] = list(range(1, int(self.selectree.get().split('_')[-1])))
        return event

    def watchtrees_day(self, event):
        thetrees = self.tree_streams[self.selectree.get()][int(self.selectree2.get()) - 1]
        self.texttree.delete('1.0', END)
        totaltime = sum([t.timing for t in thetrees])
        self.texttree.insert(END, f'{len(thetrees)} trees; {totaltime} s\n\n')
        for tree in thetrees:
            _text = f'Tree: {tree.nTree}; {round(tree.timing, 2)} s\n{tree.payload}\n'
            self.texttree.insert(END, _text)
        return event

    def run_correlation(self) -> None:
        global NUM_LABELS
        NUM_LABELS = int(self.nw_entry.get())
        corr = float(self.th_entry.get())
        self.mtx = stream_correlation(self.tree_streams[self.selectarget.get()], corr, 15)
        self.ady, self.shape = mat2ad(self.mtx)
        kmeans = KMeans(n_clusters=NUM_LABELS, max_iter=1000)
        kmeans.fit(self.ady)
        self.kmeans = kmeans.labels_
        self.timing, lpay = tree_stream_tracer(self.mtx, self.tree_streams[self.selectarget.get()], self.kmeans)
        self.labeltitles = [get_max_wd(string) for string in lpay]
        self.plot_area()
        return None

    def plot_area(self):
        plt.close()
        myfig = plt.figure(figsize=(8.07, 5.06), dpi=75)
        plt.stackplot(range(len(self.mtx)), self.timing, labels=list(range(len(self.timing[0]))))
        plt.title(f'News timing for {NUM_LABELS - 1} news.')
        plt.legend([f'{titl}' for titl in self.labeltitles])
        plt.xlabel('Days')
        plt.ylabel('Time (s / %)')
        if self.canvas is not None:
            self.canvas.get_tk_widget().pack_forget()
            self.toolbar.destroy()
        self.canvas = FigureCanvasTkAgg(myfig, master=self.lf_graph)
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.lf_graph)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack()
        self.buttonup = HoverButton(self.lf_graph, command=self.rotate_up,
                                    bg=self.colors.gray)
        self.buttondown = HoverButton(self.lf_graph, command=self.rotate_down,
                                      bg=self.colors.gray)
        self.buttonnorm = HoverButton(self.lf_graph, text='Normalize', command=self.normalize,
                                      width=8, bg=self.colors.gray)
        self.buttonup.pack()
        self.buttonup.place(x=350, y=384)
        self.buttondown.pack()
        self.buttondown.place(x=400, y=384)
        self.buttonnorm.pack()
        self.buttonnorm.place(x=260, y=387)
        self.buttondown.config(image=self.img_arrdw)
        self.buttonup.config(image=self.img_arrup)
        return None

    def rotate_up(self):
        self.labeltitles = [self.labeltitles[index - 1] for index, _ in enumerate(self.labeltitles)]
        self.timing = [self.timing[index - 1] for index, _ in enumerate(self.timing)]
        self.plot_area()

    def rotate_down(self):
        self.labeltitles = [self.labeltitles[(index + 1) % len(self.labeltitles)]
                            for index, _ in enumerate(self.labeltitles)]
        self.timing = [self.timing[(index + 1) % len(self.timing)]
                       for index, _ in enumerate(self.timing)]
        self.plot_area()

    def normalize(self):
        ret = np.zeros(np.shape(self.timing))
        for ncol, col in enumerate(np.transpose(self.timing)):
            for nrow, element in enumerate(col):
                ret[nrow][ncol] = element/sum(col)
        self.timing = ret
        self.plot_area()
# -----------------------------------------------------------
# Main:


if __name__ == '__main__':
    main()
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
#                        END OF FILE                        #
# - x - x - x - x - x - x - x - x - x - x - x - x - x - x - #
