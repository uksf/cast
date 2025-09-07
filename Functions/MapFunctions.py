from tkinter import *
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
import matplotlib.image as mpimg
from matplotlib.ticker import MultipleLocator
import matplotlib.patches as patches
from functools import lru_cache

class MatPlotLibWidget():
    def __init__(self,parent):
        self.frame = ttk.Frame(parent)
        self.frame.grid_rowconfigure(1,weight=1)
        self.frame.grid_columnconfigure(0,weight=1)
        self.fig = Figure(figsize=(8,6),dpi=150)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_aspect('equal')
        self.ax.minorticks_on()
        self.ax.grid(visible=True,which="major",axis="both",color="k",linestyle ="-",linewidth=0.5)
        self.ax.grid(visible=True,which="minor",axis="both",color="k",alpha = 0.7,linestyle= "-",linewidth=0.1)
        
        self.maxCacheSize = 100
        self.tileCache = {}

        #self.ax.callbacks.connect('xlim_changed', self.UpdateGrid)
        #self.ax.callbacks.connect('ylim_changed', self.UpdateGrid)
        
        self.mapCanvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.mapCanvas.mpl_connect('draw_event', self.Redrawn)
        self.mapCanvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.mapCanvas, self.frame,pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.grid(row=0, column=0, sticky='ew')
        self.mapCanvas.get_tk_widget().grid(row=1, column=0, sticky='nsew')
        self.frame.grid(row=0,column=0,sticky="NESW")
    def UpdateMap(self,xLimit,yLimit,mapDir:str):
        print(xLimit,yLimit)
        self.ax.set_xlim(left=0.0,right=xLimit)
        self.ax.set_ylim(bottom=0.0,top=yLimit)
        try:
            if mapDir!=None:
                self.img = mpimg.imread(mapDir)
                self.ax.imshow(self.img,extent=[0,xLimit,0,yLimit],aspect="equal")
        except: None 
    def GetTickIntervals(self, rangeSize):
        """Determine appropriate tick intervals based on range size"""
        if rangeSize > 10000:
            return 10000, 1000 # major, minor
        elif rangeSize > 5000:
            return 1000, 100
        elif rangeSize > 500:
            return 100, 10
        else: return 10,1
    def UpdateGrid(self):
        xlim = self.ax.get_xlim()
        x_range = xlim[1] - xlim[0]
        x_major, x_minor = self.GetTickIntervals(x_range)
        y_major, y_minor = self.GetTickIntervals(x_range)
        self.ax.xaxis.set_major_locator(MultipleLocator(x_major))
        self.ax.xaxis.set_minor_locator(MultipleLocator(x_minor))
        self.ax.yaxis.set_major_locator(MultipleLocator(y_major))
        self.ax.yaxis.set_minor_locator(MultipleLocator(y_minor))
        self.ax.grid(visible=True,which="major",axis="both",color="k",linestyle ="-",linewidth=0.5)
        self.ax.grid(visible=True,which="minor",axis="both",color="k",alpha = 0.7,linestyle= "-",linewidth=0.1)

    def Redrawn(self,*args):
        self.UpdateGrid()