from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import font
from datetime import datetime, timezone
import numpy as np
import re
import requests
import json
import traceback
import pandas as pd
import threading
import pyperclip
from collections import Counter
from enum import IntEnum


class CastUI():
    def __init__(self,exeDir:Path,baseDir,appData_local):
        self.user = "Unknown User"
        self.accountDetails = {}
        self.exeDir = exeDir
        self.baseDir = baseDir
        self.appData_local = appData_local

        xbm_data = """
        #define tempstipple_width 32
        #define tempstipple_height 32
        static unsigned char tempstipple_bits[] = {
        0x01, 0x00, 0xfe, 0xff, 0x00, 0x00, 0xff, 0xff, 0x00, 0x80, 0xff, 0x7f,
        0x00, 0xc0, 0xff, 0x3f, 0x00, 0xe0, 0xff, 0x1f, 0x00, 0xf0, 0xff, 0x0f,
        0x00, 0xf8, 0xff, 0x07, 0x00, 0xfc, 0xff, 0x03, 0x00, 0xfe, 0xff, 0x01,
        0x00, 0xff, 0xff, 0x00, 0x80, 0xff, 0x7f, 0x00, 0xc0, 0xff, 0x3f, 0x00,
        0xe0, 0xff, 0x1f, 0x00, 0xf0, 0xff, 0x0f, 0x00, 0xf8, 0xff, 0x07, 0x00,
        0xfc, 0xff, 0x03, 0x00, 0xfe, 0xff, 0x00, 0x00, 0xff, 0x7f, 0x00, 0x80,
        0xff, 0x3f, 0x00, 0xc0, 0xff, 0x1f, 0x00, 0xe0, 0xff, 0x0f, 0x00, 0xf0,
        0xff, 0x07, 0x00, 0xf8, 0xff, 0x03, 0x00, 0xfc, 0xff, 0x01, 0x00, 0xfe,
        0xff, 0x00, 0x00, 0xff, 0x7f, 0x00, 0x80, 0xff, 0x3f, 0x00, 0xc0, 0xff,
        0x1f, 0x00, 0xe0, 0xff, 0x0f, 0x00, 0xf0, 0xff, 0x07, 0x00, 0xf8, 0xff,
        0x03, 0x00, 0xfc, 0xff, 0x01, 0x00, 0xfe, 0xff, 0x00, 0x00, 0x00, 0x00 };
        """
        with open((self.baseDir/"tempstipple.xbm"),"w") as f:
            f.write(xbm_data)
        
        self.root = Tk()
        self.root.iconbitmap(bitmap=str(exeDir/"Functions"/"icons"/"uksf.ico"))
        self.root.title("Coordinated Artillery Support Tool")
        self.root.state("zoomed")
        self.root.protocol("WM_DELETE_WINDOW",self.IDFCalculatorClosed)
        self.menubar = Menu(self.root)
        self.content = ttk.Frame(self.root)
        self.content.grid_columnconfigure(0,weight=1)
        self.content.grid_rowconfigure(0,weight=1)
        self.mainframe = ttk.Frame(self.content,padding=1)
        self.mainframe.grid_columnconfigure(0,weight=1)
        self.mainframe.grid_rowconfigure(0,weight=1)
        self.statusBar = ttk.Frame(self.mainframe,height=60,relief="ridge",padding="5")
        self.statusBar.grid_columnconfigure(0,weight=3)
        self.statusBar.grid_columnconfigure(1,minsize="195")
        self.statusBar.grid_columnconfigure(2,weight=1)
        self.statusMessageFrame = ttk.Frame(self.statusBar,relief="sunken",padding=3)
        self.statusMessageLabel = ttk.Label(self.statusMessageFrame,text="C.A.S.T. start up")
        self.statusMessageFrame.bind("<Double-1>",self.OpenMessageLog)
        self.statusMessageLabel.bind("<Double-1>",self.OpenMessageLog)
        self.StatusGridFrame = ttk.Frame(self.statusBar,relief="sunken",padding=3)
        self.StatusGridFrame.grid_columnconfigure((0,1,2),minsize=30,weight=1)
        self.statusReferenceLabel = ttk.Label(self.StatusGridFrame,text="",justify="left")
        self.statusGridLabel = ttk.Label(self.StatusGridFrame,text="",justify="right")
        self.statusHeightLabel = ttk.Label(self.StatusGridFrame,text="",justify="right")
        self.statusProgressBar = ttk.Progressbar(self.statusBar,orient="horizontal")
        self.mainNotebook = ttk.Notebook(self.mainframe)
        self.mainNotebookMissionPage = ttk.Frame(self.mainNotebook,relief="groove",padding=10)
        self.mainNotebookMapPage = ttk.Frame(self.mainNotebook,relief="groove",padding=10)
        self.mainNotebook.add(self.mainNotebookMissionPage,text="Mission",sticky="NESW",padding=1)
        self.mainNotebook.add(self.mainNotebookMapPage,text="Maps",sticky="NESW",padding=1)
        self.mainNotebookMissionPage.grid_columnconfigure(0,weight=1)
        self.mainNotebookMissionPage.grid_rowconfigure(0,weight=1)
        self.mainNotebookMapPage.grid_columnconfigure(0,weight=1)
        self.mainNotebookMapPage.grid_rowconfigure(0,weight=1)

        self.content.grid(column="0",row="0",sticky="NESW")
        self.mainframe.grid(column="0",row="0",sticky="NESW",padx=4, pady=4)
        self.mainNotebook.grid(column="0",row="0",sticky="NESW")

        self.system = StringVar()
        """IDF system. e.g. M6, L16, L119, Sholef"""
        self.systemTrace = ""
        self.terrain = StringVar()
        self.terrainTrace = None
        self.messageLogOpen = False
        self.messageLogText = Text()
        self.fireMissionWindowOpen = False
        """Message log text"""

        # IDFP
        self.idfpName = StringVar()
        self.idfpPosX = StringVar()
        self.idfpPosY = StringVar()
        self.idfpHeight = StringVar()
        self.idfpListBoxContents = StringVar()
        self.idfpUseCharge = StringVar()
        self.idfpCharge = StringVar()
        self.idfpTraj = StringVar()
        
        # Atmosphere
        self.airTemperature = StringVar()
        self.airHumidity = StringVar()
        self.airPressure = StringVar()
        self.windDirection = StringVar()
        self.windMagnitude = StringVar()
        self.windDynamic = StringVar()
        
        # Friendlies
        self.friendlyName = StringVar()
        self.friendlyPosX = StringVar()
        self.friendlyPosY = StringVar()
        self.friendlyHeight = StringVar()
        self.friendlyDispersion = StringVar()
        
        # Target Creation
        self.xylrfpf = StringVar()
        self.xylrfpfPositionDict = {
            "0" : "NW",
            "1" : "W",
            "2" : "SW"
        }
        self.targetReference = StringVar()
        self.targetPosX = StringVar()
        self.targetPosY = StringVar()
        self.targetHeight = StringVar()
        
        # Fire Mission
        self.fireMissionEffect = StringVar()
        self.previousMissionEffect = StringVar()
        self.fireMissionWidth = StringVar()
        self.fireMissionDepth = StringVar()
        self.fireMissionLength = StringVar()
        self.fireMissionCondition = StringVar()
        self.fireMissionHour = StringVar()
        self.fireMissionMinute = StringVar()
        self.fireMissionSecond = StringVar()

        # Fire Mission Group
        self.fireMissionGroupEffect = StringVar()
        self.fireMissionGroupSpacing = StringVar()
        self.fireMissionGroupWidth = StringVar()

        # Clock
        self.clockOffset = StringVar()
        self.clockSize = StringVar()
        self.clockRimWidth = StringVar()
        self.clockFontSize = StringVar()
        self.clockHandSize = StringVar()
        self.clockSecHandSize = StringVar()

        #Window
        self.windowFlipPaneSide = StringVar()
        self.windowFireMissionEditSafety = StringVar()
        self.windowResetSafety = StringVar()

        self.terrainHeightMap = pd.DataFrame()
        self.maxRow = 0
        self.maxCol = 0
        self.maxTerrainHeight = 0

        self.targetList = {
            "FPF": {},
            "LR": {},
            "XY": {},
            "Group": {}
            }
        self.seriesDict = {
            "FPF": {},
            "LR": {},
            "XY": {}
            }
        self.targetListCheckBoxStates = {
            "FPF": {},
            "LR": {},
            "XY": {},
            "Group": {}
            }
        self.FPFEditSelected = False
        self.idfpNotebookFrameDict = {}
        self.terrainFolders = []
        self.processSettings = {
            "airTemperature": {
                "StringVar": self.airTemperature,
                "settingName": "Air Temperature",
                "traceName": self.airTemperatureTrace,
                "entryLabel": self.airTemperatureLabel
            },
            "airHumidity": {
                "StringVar": self.airHumidity,
                "settingName": "Air Humidity",
                "traceName": self.airHumidityTrace,
                "entryLabel": self.airHumidityLabel
            },
            "airPressure": {
                "StringVar": self.airPressure,
                "settingName": "Air Pressure",
                "traceName": self.airPressureTrace,
                "entryLabel": self.airPressureLabel
            },
            "windDirection": {
                "StringVar": self.windDirection,
                "settingName": "Wind Direction",
                "traceName": self.windDirectionTrace,
                "entryLabel": self.windDirectionLabel
            },
            "windMagnitude": {
                "StringVar": self.windMagnitude,
                "settingName": "Wind Magnitude",
                "traceName": self.windMagnitudeTrace,
                "entryLabel": self.windMagnitudeLabel
            },
            "windDynamic": {
                "StringVar": self.windDynamic,
                "settingName": "Dynamic Wind setting",
                "traceName": self.windDynamicTrace,
                "entryLabel": None
            },
            "system": {
                "StringVar": self.system,
                "settingName": "Weapon System",
                "traceName": self.systemTrace,
                "entryLabel": None
            }
        }
        self.boldLabels = {
            "idfpName": False,
            "airTemperature": False,
            "airHumidity": False,
            "airPressure": False,
            "windDirection": False,
            "windMagnitude": False,
            "friendlyName": False,
        }
    def GetCastJson(self,castJson: CastJson):
        self.castJson = castJson
    def GetAccount(self,account: UksfAccounts):
        self.account = account
    def BoldenLabel(self,label: Widget,type = "Normal", strVarName = ""):
        label.config(font=("Microsoft Tai Le",9,"bold")) if type.lower() == "bold" else label.config(font=("Microsoft Tai Le",9))
        if strVarName != "":
            if type.lower() == "bold":
                self.boldLabels[strVarName] = True
    def MissionPageSetup(self):
        self.missionPagePanedWindow = ttk.PanedWindow(self.mainNotebookMissionPage,orient="horizontal")
        self.missionPagePanedWindow.pane0 = ttk.Frame(self.missionPagePanedWindow,width=0,padding=1)
        self.missionPagePanedWindow.pane1 = ttk.Frame(self.missionPagePanedWindow,width=500,padding=1)
        self.missionPagePanedWindow.pane2 = ttk.Frame(self.missionPagePanedWindow,width=500,padding=1)
        self.missionPagePanedWindow.pane3 = ttk.Frame(self.missionPagePanedWindow,width=500,padding=1)
        self.missionPagePanedWindow.pane4 = ttk.Frame(self.missionPagePanedWindow,width=500,padding=1)
        self.missionPagePanedWindow.pane5 = ttk.Frame(self.missionPagePanedWindow,width=1,padding=1)
        self.missionPagePanedWindow.add(self.missionPagePanedWindow.pane0)
        self.missionPagePanedWindow.add(self.missionPagePanedWindow.pane1)
        self.missionPagePanedWindow.add(self.missionPagePanedWindow.pane2)
        self.missionPagePanedWindow.add(self.missionPagePanedWindow.pane3)
        self.missionPagePanedWindow.add(self.missionPagePanedWindow.pane4)
        self.missionPagePanedWindow.add(self.missionPagePanedWindow.pane5)
        self.missionPagePanedWindow.pane1.grid_rowconfigure(0,weight=1)
        self.missionPagePanedWindow.pane1.grid_columnconfigure(0,weight=1)
        self.missionPagePanedWindow.pane2.grid_rowconfigure(0,weight=1)
        self.missionPagePanedWindow.pane2.grid_columnconfigure(0,weight=1)
        self.missionPagePanedWindow.pane3.grid_rowconfigure(0,weight=1)
        self.missionPagePanedWindow.pane3.grid_columnconfigure(0,weight=1)
        self.missionPagePanedWindow.pane4.grid_rowconfigure(0,weight=1)
        self.missionPagePanedWindow.pane4.grid_columnconfigure(0,weight=1)
        self.missionPagePanedWindow.pane1.paneWindow = ttk.PanedWindow(self.missionPagePanedWindow.pane1,orient="vertical")
        self.missionPagePanedWindow.pane1.pane1 = ttk.Frame(self.missionPagePanedWindow.pane1.paneWindow,height=200,padding=5)
        self.missionPagePanedWindow.pane1.pane2 = ttk.Frame(self.missionPagePanedWindow.pane1.paneWindow,height=200,padding=5)
        self.missionPagePanedWindow.pane1.pane3 = ttk.Frame(self.missionPagePanedWindow.pane1.paneWindow,height=200,padding=5)
        self.missionPagePanedWindow.pane1.pane4 = ttk.Frame(self.missionPagePanedWindow.pane1.paneWindow,height=450,padding=5)
        self.missionPagePanedWindow.pane1.paneWindow.add(self.missionPagePanedWindow.pane1.pane1,weight=0)
        self.missionPagePanedWindow.pane1.paneWindow.add(self.missionPagePanedWindow.pane1.pane2,weight=0)
        self.missionPagePanedWindow.pane1.paneWindow.add(self.missionPagePanedWindow.pane1.pane3,weight=0)
        self.missionPagePanedWindow.pane1.paneWindow.add(self.missionPagePanedWindow.pane1.pane4,weight=0)
        self.missionPagePanedWindow.pane2.paneWindow = ttk.PanedWindow(self.missionPagePanedWindow.pane2,orient="vertical")
        self.missionPagePanedWindow.pane2.pane1 = ttk.Frame(self.missionPagePanedWindow.pane2.paneWindow,height=200,padding=5)
        self.missionPagePanedWindow.pane2.pane2 = ttk.Frame(self.missionPagePanedWindow.pane2.paneWindow,height=200,padding=5)
        self.missionPagePanedWindow.pane2.pane3 = ttk.Frame(self.missionPagePanedWindow.pane2.paneWindow,height=200,padding=5)
        self.missionPagePanedWindow.pane2.pane4 = ttk.Frame(self.missionPagePanedWindow.pane2.paneWindow,height=450,padding=5)
        self.missionPagePanedWindow.pane2.paneWindow.add(self.missionPagePanedWindow.pane2.pane1,weight=0)
        self.missionPagePanedWindow.pane2.paneWindow.add(self.missionPagePanedWindow.pane2.pane2,weight=0)
        self.missionPagePanedWindow.pane2.paneWindow.add(self.missionPagePanedWindow.pane2.pane3,weight=0)
        self.missionPagePanedWindow.pane2.paneWindow.add(self.missionPagePanedWindow.pane2.pane4,weight=0)
        self.missionPagePanedWindow.pane3.paneWindow = ttk.PanedWindow(self.missionPagePanedWindow.pane3,orient="vertical")
        self.missionPagePanedWindow.pane3.pane1 = ttk.Frame(self.missionPagePanedWindow.pane3.paneWindow,height=200,padding=5)
        self.missionPagePanedWindow.pane3.pane2 = ttk.Frame(self.missionPagePanedWindow.pane3.paneWindow,height=200,padding=5)
        self.missionPagePanedWindow.pane3.pane3 = ttk.Frame(self.missionPagePanedWindow.pane3.paneWindow,height=450,padding=5)
        self.missionPagePanedWindow.pane3.paneWindow.add(self.missionPagePanedWindow.pane3.pane1,weight=0)
        self.missionPagePanedWindow.pane3.paneWindow.add(self.missionPagePanedWindow.pane3.pane2,weight=0)
        self.missionPagePanedWindow.pane3.paneWindow.add(self.missionPagePanedWindow.pane3.pane3,weight=0)
        self.missionPagePanedWindow.pane4.paneWindow = ttk.PanedWindow(self.missionPagePanedWindow.pane4,orient="vertical")
        self.missionPagePanedWindow.pane4.pane1 = ttk.Frame(self.missionPagePanedWindow.pane4.paneWindow,height=200,padding=5)
        self.missionPagePanedWindow.pane4.pane2 = ttk.Frame(self.missionPagePanedWindow.pane4.paneWindow,height=450,padding=5)
        self.missionPagePanedWindow.pane4.paneWindow.add(self.missionPagePanedWindow.pane4.pane1,weight=0)
        self.missionPagePanedWindow.pane4.paneWindow.add(self.missionPagePanedWindow.pane4.pane2,weight=0)
        self.missionPagePanedWindow.grid(column="0",row="0",sticky="NWS")
        self.missionPagePanedWindow.pane1.paneWindow.grid(column="0",row="0",sticky="NEWS")
        self.missionPagePanedWindow.pane2.paneWindow.grid(column="0",row="0",sticky="NEWS")
        self.missionPagePanedWindow.pane3.paneWindow.grid(column="0",row="0",sticky="NEWS")
        self.missionPagePanedWindow.pane4.paneWindow.grid(column="0",row="0",sticky="NEWS")


    def IDFPCreationUI(self,frame):
        idfpLabelframe = ttk.Labelframe(frame,text="IDFP",height=200,padding=10,relief="groove")
        idfpLabelframe.grid_rowconfigure(0,weight=1)
        idfpLabelframe.grid_rowconfigure(1,weight=0)
        idfpLabelframe.grid_columnconfigure(0,weight=1)
        idfpCreationFrame = ttk.Labelframe(idfpLabelframe,text="Creation",height=200,padding=10,relief="groove")
        idfpCreationFrame.grid_rowconfigure((0,1,2,3,4),weight=1)
        idfpCreationFrame.grid_columnconfigure(0,weight=0,minsize=10)
        idfpCreationFrame.grid_columnconfigure(1,weight=1,minsize=40)
        idfpCreationFrame.grid_columnconfigure(2,weight=1,minsize=40)
        idfpNameLabel = ttk.Label(idfpCreationFrame,text="Name:",justify="right",padding=4)
        idfpNameCombobox = ttk.Combobox(idfpCreationFrame,justify="center",textvariable=self.idfpName)
        idfpNameCombobox.bind("<Return>",lambda event: self.LoadSelectionDetails(event,source=JsonSource.IDFP))
        idfpNameCombobox.bind("<Tab>",lambda event: self.LoadSelectionDetails(event,source=JsonSource.IDFP))
        self.idfpName.trace_add("write",callback=lambda *args: self.BoldenLabel(idfpNameLabel,"Bold","idfpName"))
        idfpPosLabel = ttk.Label(idfpCreationFrame,text="Position:",justify="right",padding=4)
        idfpPosXEntry  = ttk.Entry(idfpCreationFrame, justify="center",textvariable=self.idfpPosX)
        idfpPosXEntry.bind("<Return>",lambda event:self.HeightAutoFill(event,self.idfpPosX,self.idfpPosY,heightlabel=self.idfpHeight))
        idfpPosXEntry.bind("<Tab>",lambda event:self.HeightAutoFill(event,self.idfpPosX,self.idfpPosY,heightlabel=self.idfpHeight))
        idfpPosYEntry  = ttk.Entry(idfpCreationFrame, justify="center",textvariable=self.idfpPosY)
        idfpPosYEntry.bind("<Return>",lambda event:self.HeightAutoFill(event,self.idfpPosX,self.idfpPosY,heightlabel=self.idfpHeight))
        idfpPosYEntry.bind("<Tab>",lambda event:self.HeightAutoFill(event,self.idfpPosX,self.idfpPosY,heightlabel=self.idfpHeight))
        idfpHeightLabel = ttk.Label(idfpCreationFrame,text="Height:",justify="right",padding=4)
        idfpHeightFrame = ttk.Frame(idfpCreationFrame)
        idfpHeightFrame.grid_rowconfigure(0,weight=1)
        idfpHeightFrame.grid_columnconfigure(0,weight=1,minsize=30)
        idfpHeightFrame.grid_columnconfigure(1,weight=0,minsize=5)
        idfpHeightEntry = ttk.Entry(idfpHeightFrame, justify="center",textvariable=self.idfpHeight)
        idfpHeightUnitLabel = ttk.Label(idfpHeightFrame,text="m")
        idfpButtonFrame = ttk.Frame(idfpCreationFrame,padding=5)
        idfpButtonFrame.grid_columnconfigure(0,weight=1)
        idfpButtonFrame.grid_rowconfigure((0,1,2),weight=1)
        idfpSystemFrame = ttk.Frame(idfpButtonFrame,padding=4,relief="solid")
        idfpSystemFrame.grid_columnconfigure(0,minsize=9,weight=1)
        idfpSystemFrame.grid_columnconfigure(1,minsize=4)
        idfpSystemFrame.grid_columnconfigure(2,minsize=9,weight=5)
        idfpSystemFrame.grid_rowconfigure(0,weight=1)
        idfpSystemLabeltag = ttk.Label(idfpSystemFrame,text="System")
        idfpSystemSep = ttk.Separator(idfpSystemFrame,orient="vertical")
        self.idfpSystemLabel = ttk.Label(idfpSystemFrame,text="None",justify="right")
        idfpAddButton = ttk.Button(idfpButtonFrame,text="Add/Update",command=self.IDFPAddUpdate)
        idfpRemoveButton = ttk.Button(idfpButtonFrame,text="Remove",command=lambda: self.IDFPRemove(name=self.idfpName.get()))
        idfpSeparator = ttk.Separator(idfpCreationFrame,orient="horizontal")
        idfpControlFrame = ttk.Frame(idfpCreationFrame)
        idfpControlFrame.grid_columnconfigure(0,weight=0,minsize=10)
        idfpControlFrame.grid_columnconfigure(1,weight=1)
        idfpControlFrame.grid_rowconfigure((0,1),weight=1)
        idfpEditChargeLabel = ttk.Label(idfpControlFrame,text="Charge",justify="right",padding=2)
        idfpChargeFrame = ttk.Frame(idfpControlFrame)
        idfpChargeFrame.grid_columnconfigure(0,weight=0,minsize=5)
        idfpChargeFrame.grid_columnconfigure(1,weight=1)
        idfpChargeFrame.grid_rowconfigure(0,weight=1)
        idfpEditChargeCheckbox = ttk.Checkbutton(idfpChargeFrame,variable=self.idfpUseCharge,offvalue=0,onvalue=1,padding=2)
        self.idfpUseCharge.set(0)
        idfpEditChargeComboBox = ttk.Combobox(idfpChargeFrame,textvariable=self.idfpCharge,width=4,state="readonly")
        idfpEditTrajLabel = ttk.Label(idfpControlFrame,text="Trajectory",justify="right",padding=2)
        idfpEditTrajComboBox = ttk.Combobox(idfpControlFrame,textvariable=self.idfpTraj,width=4,state="readonly")
        idfpListBoxFrame = ttk.Labelframe(frame,text="Selection",height=200,padding=10,relief="groove")
        idfpListBoxFrame.grid_rowconfigure(0,weight=1)
        idfpListBoxFrame.grid_columnconfigure(0,weight=1)
        idfpListbox = Listbox(idfpListBoxFrame,height=5,width=7,listvariable=self.idfpListBoxContents,relief="sunken",justify="center",activestyle="dotbox",selectmode="multiple",borderwidth=2,exportselection=False)
        idfpListbox.bind("<<ListboxSelect>>",lambda *arg: self.IDFPListUpdate(idfpListbox.curselection()))

        idfpCreationFrame.grid(column="0",row="0",sticky="NESW")
        idfpNameLabel.grid(column="0",row="0",sticky="NE")
        idfpNameCombobox.grid(column="1",columnspan=2,row="0",sticky="NEW")
        idfpPosLabel.grid(column=0,row=1,sticky="NES")
        idfpPosXEntry.grid(column=1,row=1,sticky="NEW")
        idfpPosYEntry.grid(column=2,row=1,sticky="NEW")
        idfpHeightLabel.grid(column=0,row=2,sticky="NES")
        idfpHeightFrame.grid(column=1,row=2,sticky="NEW")
        idfpHeightEntry.grid(column=0,row=0,sticky="NEW")
        idfpHeightUnitLabel.grid(column=1,row=0,sticky="NW")
        idfpButtonFrame.grid(column=2,row=2,rowspan=3,sticky="NEW")
        idfpSystemFrame.grid(column=0,row=0,sticky="NEWS")
        idfpSystemLabeltag.grid(column=0,row=0,sticky="NWS")
        idfpSystemSep.grid(column=1,row=0,sticky="NS")
        self.idfpSystemLabel.grid(column=2,row=0,sticky="NSE")
        idfpAddButton.grid(column=0,row=1,sticky="NEW")
        idfpRemoveButton.grid(column=0,row=2,sticky="NEW")
        idfpSeparator.grid(column=0,columnspan=2,row=3,sticky="EW",pady=4)
        idfpControlFrame.grid(column=0,columnspan=2,row=4,sticky="NEW")
        idfpEditChargeLabel.grid(column=0,row=0,sticky="NE")
        idfpChargeFrame.grid(column=1,row=0,sticky="NEW")
        idfpEditChargeCheckbox.grid(column=0,row=0,sticky="NE")
        idfpEditChargeComboBox.grid(column=1,row=0,sticky="NEW")
        idfpEditTrajLabel.grid(column=0,row=1,sticky="NE")
        idfpEditTrajComboBox.grid(column=1,row=1,sticky="NEW")
        idfpListBoxFrame.grid(column="0",row="1",sticky="NEWS")
        idfpListbox.grid(column="0",row="0",sticky="NEW")

    def AtmosphericUI(self,frame):
        atmosphereLabelframe = ttk.Labelframe(frame,text="Atmosphere",width=200,height=200,padding=5,relief="groove")
        atmosphereLabelframe.grid_rowconfigure((0,1),weight=1)
        atmosphereLabelframe.grid_columnconfigure(0,weight=1)
        airLabelFrame = ttk.Labelframe(atmosphereLabelframe,text="Air",height=200,padding=2)
        airLabelFrame.grid_columnconfigure(0,weight=5)
        airLabelFrame.grid_columnconfigure(1)
        airLabelFrame.grid_columnconfigure(2,minsize=75)
        airLabelFrame.grid_columnconfigure(3,weight=4)
        airLabelFrame.grid_rowconfigure((0,1,2),weight=1)
        airSeparator = ttk.Separator(airLabelFrame,orient="vertical")
        self.airTemperatureLabel = ttk.Label(airLabelFrame, text="Temperature",padding=4)
        self.airTemperatureTrace = self.airTemperature.trace_add(mode="write",callback=lambda *args: self.BoldenLabel(self.airTemperatureLabel,"Bold","airTemperature"))
        temperatureEntry = ttk.Entry(airLabelFrame,width="5",textvariable=self.airTemperature,justify="right")
        temperatureEntry.bind("<Return>",self.TemperatureEntryValidate)
        temperatureEntry.bind("<Tab>",self.TemperatureEntryValidate)
        temperatureEntry.bind("<Escape>",lambda *args: self.CancelSettingChange(StrVar=self.airTemperature,label=self.airTemperatureLabel,stringvar="airTemperature"))
        temperatureUnits = ttk.Label(airLabelFrame,text="°C")
        self.airHumidityLabel = ttk.Label(airLabelFrame, text="Air Humidity",padding=4)
        self.airHumidityTrace = self.airHumidity.trace_add(mode="write",callback=lambda *args: self.BoldenLabel(self.airHumidityLabel,"Bold","airHumidity"))
        humidityEntry = ttk.Entry(airLabelFrame,width="5",textvariable=self.airHumidity,justify="right")
        humidityEntry.bind("<Return>",self.HumidityEntryValidate)
        humidityEntry.bind("<Tab>",self.HumidityEntryValidate)
        humidityEntry.bind("<Escape>",lambda *args: self.CancelSettingChange(StrVar=self.airHumidity,label=self.airHumidityLabel,stringvar="airHumidity"))
        humidityUnits = ttk.Label(airLabelFrame,text="%")
        self.airPressureLabel = ttk.Label(airLabelFrame, text="Air Pressure",padding=4)
        self.airPressureTrace = self.airPressure.trace_add(mode="write",callback=lambda *args: self.BoldenLabel(self.airPressureLabel,"Bold","airPressure"))
        pressureEntry = ttk.Entry(airLabelFrame,width="7",textvariable=self.airPressure,justify="right")
        pressureEntry.bind("<Return>",self.PressureEntryValidate)
        pressureEntry.bind("<Tab>",self.PressureEntryValidate)
        pressureEntry.bind("<Escape>",lambda *args: self.CancelSettingChange(StrVar=self.airPressure,label=self.airPressureLabel,stringvar="airPressure"))
        pressureUnits = ttk.Label(airLabelFrame,text="hPa")
        windLabelFrame = ttk.Labelframe(frame,text="Wind",height=200,padding=2)
        windLabelFrame.grid_columnconfigure(0,weight=1)
        windLabelFrame.grid_columnconfigure(1)
        windLabelFrame.grid_columnconfigure(2,minsize=75)
        windLabelFrame.grid_columnconfigure(3,weight=1)
        windLabelFrame.grid_rowconfigure((0,1,2),weight=1)
        windSeparator = ttk.Separator(windLabelFrame,orient="vertical")
        self.windDirectionLabel = ttk.Label(windLabelFrame, text="Wind Direction",padding=4)
        self.windDirectionTrace = self.windDirection.trace_add(mode="write",callback=lambda *args: self.BoldenLabel(self.windDirectionLabel,"Bold","windDirection"))
        directionEntry = ttk.Entry(windLabelFrame,width="3",textvariable=self.windDirection,justify="right")
        directionEntry.bind("<Return>",self.DirectionEntryValidate)
        directionEntry.bind("<Tab>",self.DirectionEntryValidate)
        directionEntry.bind("<Escape>",lambda *args: self.CancelSettingChange(StrVar=self.windDirection,label=self.windDirectionLabel,stringvar="windDirection"))
        directionUnits = ttk.Label(windLabelFrame,text="°")
        self.windMagnitudeLabel = ttk.Label(windLabelFrame, text="Wind Magnitude",padding=4)
        self.windMagnitudeTrace = self.windMagnitude.trace_add(mode="write",callback=lambda *args: self.BoldenLabel(self.windMagnitudeLabel,"Bold","windMagnitude"))
        magnitudeEntry = ttk.Entry(windLabelFrame,width="5",textvariable=self.windMagnitude,justify="right")
        magnitudeEntry.bind("<Return>",self.MagnitudeEntryValidate)
        magnitudeEntry.bind("<Tab>",self.MagnitudeEntryValidate)
        magnitudeEntry.bind("<Escape>",lambda *args: self.CancelSettingChange(StrVar=self.windMagnitude,label=self.windMagnitudeLabel,stringvar="windMagnitude"))
        magnitudeUnits = ttk.Label(windLabelFrame,text="m/s")
        windDynamicLabel = ttk.Label(windLabelFrame, text="Dynamic Wind",padding=4)
        dynamicCheckBox = ttk.Checkbutton(windLabelFrame,variable=self.windDynamic,onvalue=1,offvalue=0,padding=4)
        self.windDynamicTrace = self.windDynamic.trace_add(mode="write", callback=(lambda *args: self.castJson.Save(source=JsonSource.COMMON,newEntry={"windDynamic" : self.windDynamic.get()})))

        airLabelFrame.grid(column="0",row="0",sticky="NEW",pady=5)
        airSeparator.grid(column=1,row=0,rowspan=3,sticky="NESW")
        self.airTemperatureLabel.grid(column="0",row="0",sticky="E")
        temperatureEntry.grid(column="2",row="0",sticky="E",padx=4)
        temperatureUnits.grid(column="3",row="0",sticky="W",padx=4)
        self.airHumidityLabel.grid(column="0",row="1",sticky="E")
        humidityEntry.grid(column="2",row="1",sticky="E",padx=4)
        humidityUnits.grid(column="3",row="1",sticky="W",padx=4)
        self.airPressureLabel.grid(column="0",row="2",sticky="E")
        pressureEntry.grid(column="2",row="2",sticky="E",padx=4)
        pressureUnits.grid(column="3",row="2",sticky="W",padx=4)
        windLabelFrame.grid(column="0",row="1",sticky="NEW",pady=5)
        windSeparator.grid(column=1,row=0,rowspan=3,sticky="NESW")
        self.windDirectionLabel.grid(column=0,row=0,sticky="E")
        directionEntry.grid(column=2,row=0,sticky="E",padx=4)
        directionUnits.grid(column=3,row=0,sticky="W",padx=4)
        self.windMagnitudeLabel.grid(column=0,row=1,sticky="E")
        magnitudeEntry.grid(column=2,row=1,sticky="E",padx=4)
        magnitudeUnits.grid(column=3,row=1,sticky="W",padx=4)
        windDynamicLabel.grid(column=0,row=2,sticky="NSE")
        dynamicCheckBox.grid(column=2,row=2,sticky="NSE")

    def FriendlyUI(self,frame):
        friendlyLabelframe = ttk.Labelframe(frame,text="Friendly Position",height=200,width=500,padding=5,relief="groove")
        friendlyLabelframe.grid_rowconfigure((0,1,2,3),weight=1)
        friendlyLabelframe.grid_columnconfigure(0,weight=1,minsize="68")
        friendlyLabelframe.grid_columnconfigure(1,weight=5,minsize="20")
        friendlyLabelframe.grid_columnconfigure(2,minsize="10")
        friendlyLabelframe.grid_columnconfigure(3,weight=5,minsize="30")
        self.friendlyNameLabel = ttk.Label(friendlyLabelframe,text="Name:",justify="right",padding=4)
        friendlyNameCombobox = ttk.Combobox(friendlyLabelframe,justify="center",textvariable=self.friendlyName)
        friendlyNameCombobox.bind("<Return>",lambda event: self.LoadSelectionDetails(event, source=JsonSource.FRIENDLY))
        friendlyNameCombobox.bind("<Tab>",lambda event: self.LoadSelectionDetails(event, source=JsonSource.FRIENDLY))
        self.friendlyName.trace_add(mode="write", callback=lambda *args: self.BoldenLabel(self.friendlyNameLabel,"Bold","friendlyName"))
        friendlyPosLabel = ttk.Label(friendlyLabelframe,text="Position:",justify="right",padding=4)
        friendlyPosXEntry  = ttk.Entry(friendlyLabelframe, justify="center",textvariable=self.friendlyPosX)
        friendlyPosXEntry.bind("<Return>",lambda event: self.HeightAutoFill(event, self.friendlyPosX.get(),self.friendlyPosY.get(),self.friendlyHeight))
        friendlyPosXEntry.bind("<Tab>",lambda event: self.HeightAutoFill(event, self.friendlyPosX.get(),self.friendlyPosY.get(),self.friendlyHeight))
        friendlyPosYEntry  = ttk.Entry(friendlyLabelframe, justify="center",textvariable=self.friendlyPosY)
        friendlyPosYEntry.bind("<Return>",lambda event: self.HeightAutoFill(event, self.friendlyPosX.get(),self.friendlyPosY.get(),self.friendlyHeight))
        friendlyPosYEntry.bind("<Tab>",lambda event: self.HeightAutoFill(event, self.friendlyPosX.get(),self.friendlyPosY.get(),self.friendlyHeight))
        friendlyHeightLabel = ttk.Label(friendlyLabelframe,text="Height:",justify="right",padding=4)
        friendlyHeightEntry = ttk.Entry(friendlyLabelframe, justify="center",textvariable=self.friendlyHeight)
        friendlyHeightUnitLabel = ttk.Label(friendlyLabelframe,text="m")
        friendlyDispersionLabel = ttk.Label(friendlyLabelframe,text="Dispersion:",justify="right",padding=4)
        friendlyDispersionEntry = ttk.Entry(friendlyLabelframe, justify="center",textvariable=self.friendlyDispersion)
        friendlyDispersionUnitLabel = ttk.Label(friendlyLabelframe,text="m")
        friendlyAddButton = ttk.Button(friendlyLabelframe,text="Add/Update",command=self.FriendlyAddUpdate)
        friendlyRemoveButton = ttk.Button(friendlyLabelframe,text="Remove",command=lambda: self.FriendlyRemove(name=self.friendlyName.get()))
        self.friendlyNameLabel.grid(column="0",row="0",sticky="NE")
        friendlyNameCombobox.grid(column="1",row="0",columnspan=3,sticky="NEW")
        friendlyPosLabel.grid(column="0",row="1",sticky="NE")
        friendlyPosXEntry.grid(column="1",row="1",columnspan=2,sticky="NEW")
        friendlyPosYEntry.grid(column="3",row="1",sticky="NEW")
        friendlyHeightLabel.grid(column="0",row="2",sticky="E")
        friendlyHeightEntry.grid(column="1",row="2",sticky="EW")
        friendlyHeightUnitLabel.grid(column="2",row="2",sticky="W")
        friendlyDispersionLabel.grid(column="0",row="3",sticky="E")
        friendlyDispersionEntry.grid(column="1",row="3",sticky="EW")
        friendlyDispersionUnitLabel.grid(column="2",row="3",sticky="W")
        friendlyAddButton.grid(column="3",row="2",sticky="NESW")
        friendlyRemoveButton.grid(column="3",row="3",sticky="NESW")

    def TargetCreationUI(self,frame):
        targetInputLabelFrame = ttk.Labelframe(frame,text="Create Target",height=200,width=500,padding=5,relief="groove")
        targetInputLabelFrame.grid_rowconfigure(0,weight=1)
        targetInputLabelFrame.grid_columnconfigure(0,weight=1)
        targetInputFrame = ttk.Frame(targetInputLabelFrame)
        targetInputFrame.grid_columnconfigure(0,minsize=30,weight=1)
        targetInputFrame.grid_columnconfigure(1,minsize=30,weight=2)
        targetInputFrame.grid_columnconfigure(2,minsize=10,weight=2)
        targetInputFrame.grid_columnconfigure(3,minsize=6)
        targetInputFrame.grid_columnconfigure(4,minsize=34,weight=4)
        targetInputFrame.grid_rowconfigure((0,1,2,3,4,5),weight=1)
        targetInputXYRadio = ttk.Radiobutton(targetInputFrame,text="LR - ",variable=self.xylrfpf,value=0)
        targetInputLRRadio = ttk.Radiobutton(targetInputFrame,text="XY - ",variable=self.xylrfpf,value=1)
        targetInputFPFRadio = ttk.Radiobutton(targetInputFrame,text="FPF- ",variable=self.xylrfpf,value=2)
        self.xylrfpf.trace_add(mode="write",callback=self.TargetXYLRFPFChange)
        self.targetInputReferenceEntry = ttk.Entry(targetInputFrame,width=3,textvariable=self.targetReference)
        targetInputAddSeparator = ttk.Separator(targetInputFrame,orient="vertical")
        targetInputSeparator = ttk.Separator(targetInputFrame,orient="horizontal")
        targetInputGridLabel = ttk.Label(targetInputFrame,text="Position:",padding=4)
        targetInputGridXEntry = ttk.Entry(targetInputFrame,justify="center",width=5,textvariable=self.targetPosX)
        targetInputGridXEntry.bind("<Return>",lambda event: self.HeightAutoFill(event,self.friendlyPosX.get(),self.friendlyPosY.get(),self.friendlyHeight))
        targetInputGridXEntry.bind("<Tab>",lambda event: self.HeightAutoFill(event,self.friendlyPosX.get(),self.friendlyPosY.get(),self.friendlyHeight))
        targetInputGridYEntry = ttk.Entry(targetInputFrame,justify="center",width=5,textvariable=self.targetPosY)
        targetInputGridYEntry.bind("<Return>",lambda event: self.HeightAutoFill(event,self.friendlyPosX.get(),self.friendlyPosY.get(),self.friendlyHeight))
        targetInputGridYEntry.bind("<Tab>",lambda event: self.HeightAutoFill(event,self.friendlyPosX.get(),self.friendlyPosY.get(),self.friendlyHeight))
        targetInputHeightLabel = ttk.Label(targetInputFrame,justify="right",text="Height:",padding=4)
        targetInputHeightEntry = ttk.Entry(targetInputFrame,width=5,justify="center",textvariable=self.targetHeight)
        targetInputHeightUnitLabel = ttk.Label(targetInputFrame,justify="left",text="m")
        targetInputReferenceAdd = ttk.Button(targetInputFrame,text="Add",command=lambda *args: self.TargetAdd())

        targetInputLabelFrame.grid(column="0",row="0",sticky="NEW")
        targetInputFrame.grid(column="0",row="0",sticky="NEW")
        targetInputXYRadio.grid(column="0",row="0",sticky="E")
        targetInputLRRadio.grid(column="0",row="1",sticky="E")
        targetInputFPFRadio.grid(column="0",row="2",sticky="E")
        self.targetInputReferenceEntry.grid(column="1",row="0",rowspan=3,columnspan=2,sticky="W")
        targetInputAddSeparator.grid(column="3",row="0",rowspan=2,sticky="NESW")
        targetInputReferenceAdd.grid(column="4",row="0",rowspan=2,sticky="EW")
        targetInputSeparator.grid(column="0",row="3",columnspan=5,sticky="EW")
        targetInputGridLabel.grid(column="0",row="4",sticky="E")
        targetInputGridXEntry.grid(column="1",row="4",columnspan=2,sticky="NEW")
        targetInputGridYEntry.grid(column="3",row="4",columnspan=2,sticky="NEW")
        targetInputHeightLabel.grid(column="0",row="5",sticky="E")
        targetInputHeightEntry.grid(column="1",row="5",sticky="EW")
        targetInputHeightUnitLabel.grid(column="2",row="5",sticky="W")

    def TargetDetailSelection(self,frame):
        self.fireMissionSelectionLabelframe = ttk.Labelframe(frame,text="Fire Mission Selection",height=200,width=500,padding=5,relief="groove")
        self.fireMissionSelectionLabelframe.grid_columnconfigure((0,1,2,3),minsize=70,weight=1)
        self.fireMissionSelectionLabelframe.grid_rowconfigure((0,1,2,3),weight=1)
        fireMissionSelectionEffectLabelframe = ttk.Labelframe(self.fireMissionSelectionLabelframe,text="Effect",relief="groove")
        fireMissionSelectionEffectLabelframe.grid_columnconfigure(0,weight=5)
        fireMissionSelectionEffectLabelframe.grid_rowconfigure((0,1,2,3,4,5,6,7),weight=1)
        self.fireMissionSelectionEffectDestroyRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Destroy",variable=self.fireMissionEffect,value="Destroy")
        self.fireMissionSelectionEffectNeutraliseRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Neutralise",variable=self.fireMissionEffect,value="Neutralise")
        self.fireMissionSelectionEffectCheckRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Check",variable=self.fireMissionEffect,value="Checkround")
        self.fireMissionSelectionEffectSaturationRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Saturation",variable=self.fireMissionEffect,value="Saturate")
        self.fireMissionSelectionEffectFPFRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="FPF",variable=self.fireMissionEffect,value="FPF")
        self.fireMissionSelectionEffectAreaDenialRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Area Denial",variable=self.fireMissionEffect,value="Area_Denial")
        self.fireMissionSelectionEffectSmokeRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Smoke",variable=self.fireMissionEffect,value="Smoke")
        self.fireMissionSelectionEffectIllumRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Illum",variable=self.fireMissionEffect,value="Illum")
        self.fireMissionEffect.set("Destroy")
        self.fireMissionEffect.trace_add(mode="write",callback=self.FireMissionEffectChange)
        fireMissionSelectionUpdateMission = ttk.Button(self.fireMissionSelectionLabelframe,text="Update",command=lambda: self.FireMissionEffectUpdate())
        fireMissionSelectionDispersionLabelframe = ttk.Labelframe(self.fireMissionSelectionLabelframe,text="Dispersion",padding=4)
        fireMissionSelectionDispersionLabelframe.grid_columnconfigure(0,weight=1,minsize=30)
        fireMissionSelectionDispersionLabelframe.grid_columnconfigure(1)
        fireMissionSelectionDispersionLabelframe.grid_rowconfigure(0,weight=1)
        fireMissionSelectionWidthLabel = ttk.Label(fireMissionSelectionDispersionLabelframe,text="Wid",padding=4,justify="right")
        fireMissionSelectionDepthLabel = ttk.Label(fireMissionSelectionDispersionLabelframe,text="Dep",padding=4,justify="right")
        fireMissionSelectionWidthCombobox = ttk.Combobox(fireMissionSelectionDispersionLabelframe,textvariable=self.fireMissionWidth,justify="right",width=4,values=("0","10","20","40","50","100","150","200","250"))
        self.fireMissionWidth.set("0")
        fireMissionSelectionDepthCombobox = ttk.Combobox(fireMissionSelectionDispersionLabelframe,textvariable=self.fireMissionDepth,justify="right",width=4,values=("0","10","20","40","50","100","150","200","250"))
        self.fireMissionDepth.set("0")
        fireMissionSelectionWidthUnitLabel = ttk.Label(fireMissionSelectionDispersionLabelframe,text="m",padding=4,justify="left")
        fireMissionSelectionDepthUnitLabel = ttk.Label(fireMissionSelectionDispersionLabelframe,text="m",padding=4,justify="left")
        fireMissionSelectionLengthLabelframe = ttk.Labelframe(self.fireMissionSelectionLabelframe,text="Length",padding=4)
        fireMissionSelectionLengthLabelframe.grid_columnconfigure(0,weight=1,minsize=30)
        fireMissionSelectionLengthLabelframe.grid_columnconfigure(1)
        fireMissionSelectionLengthLabelframe.grid_rowconfigure(0,weight=1)
        fireMissionSelectionLengthCombobox = ttk.Combobox(fireMissionSelectionLengthLabelframe,width=5,textvariable=self.fireMissionLength,justify="right",values=("30","Fig 1","90","Fig 2","Fig 3","Fig 4"))
        self.fireMissionLength.set("Fig 1")
        self.fireMissionLength.trace_add(mode="write",callback=self.FireMissionLengthChange)
        self.fireMissionSelectionLengthUnitLabel = ttk.Label(fireMissionSelectionLengthLabelframe,text=" ",padding=4,justify="left")
        fireMissionSelectionConditionLabelframe = ttk.Labelframe(self.fireMissionSelectionLabelframe,text="Condition",padding=4)
        fireMissionSelectionConditionLabelframe.grid_columnconfigure(0,weight=1)
        fireMissionSelectionConditionLabelframe.grid_rowconfigure(0,weight=1)
        fireMissionSelectionConditionCombobox = ttk.Combobox(fireMissionSelectionConditionLabelframe,textvariable=self.fireMissionCondition,values=("FWR","Time"),width=10,justify="center")
        self.fireMissionCondition.set("FWR")
        self.fireMissionCondition.trace_add(mode="write",callback=self.FireMissionConditionChange)
        self.fireMissionSelectionTimeLabelframe = ttk.Labelframe(self.fireMissionSelectionLabelframe,text="Time",padding=4)
        self.fireMissionSelectionTimeLabelframe.grid_columnconfigure((0,2,4),minsize=20,weight=1)
        self.fireMissionSelectionTimeLabelframe.grid_rowconfigure(0,weight=1)
        fireMissionSelectionTimeHoursEntry = ttk.Entry(self.fireMissionSelectionTimeLabelframe,width=2,textvariable=self.fireMissionHour,justify="center")
        self.fireMissionHour.set(datetime.now().strftime("%H"))
        fireMissionSelectionTimeColonLabel1 = ttk.Label(self.fireMissionSelectionTimeLabelframe,text=" : ")
        fireMissionSelectionTimeMinutesEntry = ttk.Entry(self.fireMissionSelectionTimeLabelframe,width=2,textvariable=self.fireMissionMinute,justify="center")
        self.fireMissionMinute.set(datetime.now().strftime("%M"))
        fireMissionSelectionTimeColonLabel2 = ttk.Label(self.fireMissionSelectionTimeLabelframe,text=" : ")
        fireMissionSelectionTimeSecondsEntry = ttk.Entry(self.fireMissionSelectionTimeLabelframe,width=2,textvariable=self.fireMissionSecond,justify="center")
        self.fireMissionSecond.set(datetime.now().strftime("%S"))
        fireMissionGroupSelectionLabelframe = ttk.Labelframe(frame,text="Grouped Fire Mission Selection",padding=3)
        fireMissionGroupSelectionLabelframe.grid_columnconfigure((0,1,2,3),weight=1)
        fireMissionGroupSelectionLabelframe.grid_rowconfigure((0,1,2,3),weight=1)
        fireMissionGroupSelectionTargetFrame = ttk.Frame(fireMissionGroupSelectionLabelframe,padding=3,relief="raised")
        fireMissionGroupSelectionTargetFrame.bind("<Button-3>",self.ReverseFireMissionGroupSelections)
        fireMissionGroupSelection1Label = ttk.Label(fireMissionGroupSelectionTargetFrame,text="Target 1 : ")
        fireMissionGroupSelection2Label = ttk.Label(fireMissionGroupSelectionTargetFrame,text="Target 2 : ")
        fireMissionGroupSelection1NameLabel = ttk.Label(fireMissionGroupSelectionTargetFrame)
        fireMissionGroupSelection2NameLabel = ttk.Label(fireMissionGroupSelectionTargetFrame)
        fireMissionGroupSelection1Label.bind("<Button-3>",self.ReverseFireMissionGroupSelections)
        fireMissionGroupSelection2Label.bind("<Button-3>",self.ReverseFireMissionGroupSelections)
        fireMissionGroupSelection1NameLabel.bind("<Button-3>",self.ReverseFireMissionGroupSelections)
        fireMissionGroupSelection2NameLabel.bind("<Button-3>",self.ReverseFireMissionGroupSelections)
        fireMissionGroupSelectionReverseButton = ttk.Button(fireMissionGroupSelectionLabelframe,text="Reverse\n Targets",command=lambda: self.ReverseFireMissionGroupSelections())
        fireMissionGroupSelectionAddButton = ttk.Button(fireMissionGroupSelectionLabelframe,text="Add\nGroup",command=lambda:self.AddGroupMission())
        fireMissionGroupSelectionEffectLabelFrame = ttk.LabelFrame(fireMissionGroupSelectionLabelframe,text="Group Effect",relief="groove",padding=3)
        fireMissionGroupSelectionEffectLine = ttk.Radiobutton(fireMissionGroupSelectionEffectLabelFrame,text="Line",variable=self.fireMissionGroupEffect,value="Line")
        fireMissionGroupSelectionEffectExplicitLine = ttk.Radiobutton(fireMissionGroupSelectionEffectLabelFrame,text="Explicit Line",variable=self.fireMissionGroupEffect,value="Explicit Line")
        fireMissionGroupSelectionEffectCreepingBarrage = ttk.Radiobutton(fireMissionGroupSelectionEffectLabelFrame,text="Creeping Barrage",variable=self.fireMissionGroupEffect,value="Creeping Barrage")
        self.fireMissionGroupEffect.set("Line")
        self.fireMissionGroupEffect.trace_add(mode="write",callback=lambda *args: self.FireMissionGroupEffectChange())
        fireMissionGroupSelectionDispersionLabelframe = ttk.Labelframe(fireMissionGroupSelectionLabelframe,text="Dispersion",padding=3)
        fireMissionGroupSelectionDispersionLabelframe.grid_columnconfigure(0,weight=1)
        fireMissionGroupSelectionDispersionLabelframe.grid_columnconfigure(1,minsize=20)
        fireMissionGroupSelectionDispersionLabelframe.grid_columnconfigure(2,minsize=9)
        fireMissionGroupSelectionDispersionLabelframe.grid_rowconfigure((0,1),weight=1)
        fireMissionGroupSelectionDispersionSpacingLabel = ttk.Label(fireMissionGroupSelectionDispersionLabelframe,text="Spacing")
        fireMissionGroupSelectionDispersionSpacingCombobox = ttk.Combobox(fireMissionGroupSelectionDispersionLabelframe,justify="center",width=5,textvariable=self.fireMissionGroupSpacing,values=("10","20","30","40","50","60","70","80","90","100"))
        self.fireMissionGroupSpacing.set("30")
        fireMissionGroupSelectionDispersionSpacingUnitLabel = ttk.Label(fireMissionGroupSelectionDispersionLabelframe,text="m")
        self.fireMissionGroupSelectionDispersionWidthLabel = ttk.Label(fireMissionGroupSelectionDispersionLabelframe,text="Width")
        self.fireMissionGroupSelectionDispersionWidthCombobox = ttk.Combobox(fireMissionGroupSelectionDispersionLabelframe,justify="center",width=5,textvariable=self.fireMissionGroupWidth,values=("100","150","200","250","300","350","400"))
        self.fireMissionGroupWidth.set("150")
        fireMissionGroupSelectionDispersionWidthUnitLabel = ttk.Label(fireMissionGroupSelectionDispersionLabelframe,text="m")
    def StatusMessageLog(self,message="",privateMessage: str | None = None):
        """
        Displays message in the status bar and log. Private message is given only to the user in the status bar, if message is "", it's not included in the log.
        """
        if privateMessage is None:
            try: self.statusMessageLabel.config(text=privateMessage)
            except: None
        if message != "":
            CastJson.Save(source=JsonSource.MESSAGELOG,newEntry=(str(datetime.now(timezone.utc))[:-11] + "\t" + "|" + "\t" + self.user + "\t" + "|" + "\t" + message+"\n"),append=True)
            if self.messageLogOpen:
                self.messageLogText.config(state=NORMAL)
                self.messageLogText.delete("1.0","end")
                self.messageLogText.insert("end",self.castJson.Load(source=5)) 
                self.messageLogText.config(state=DISABLED)
                self.messageLogText.yview_moveto(1)
    def StatusMessageErrorDump(self,e: Exception, errorMessage: str | None =None):
        if errorMessage is not None:
            self.StatusMessageLog(message=errorMessage)
        try:
            if e:
                fullTrace = traceback.extract_tb(e.__traceback__)
                fullTraceStr = ""
                for i,frame in enumerate(fullTrace):
                    filename = frame.filename.split('\\')[-1]
                    fullTraceStr+=f"\n\t\t{filename} | {frame.name} | {str(frame.lineno)}"
                self.StatusMessageLog(message=f"Error details:\n\tVersion: {version}\n\tType: {type(e).__name__}\n\tError: {e}\n\tError Line: {fullTrace[-1].lineno} : {fullTrace[-1].line}\n\tFull stack:{fullTraceStr}",privateMessage="Empty")
            else: self.StatusMessageLog(message=f"Failed error message")
        except: self.StatusMessageLog(message=f"Failed error message")
    def LoginWindow(self,startup=False) -> bool:
        def Login():
            loginMessage.grid()
            if loginUsernameEntry.get().strip() !="":
                if loginPasswordEntry.get() !="":
                    loginMessage.config(text="Logging in")
                    self.account.GetAuthToken(loginUsernameEntry.get(),loginPasswordEntry.get())
                    loginUsernameEntry.set("")
                    loginPasswordEntry.set("")
                    self.accountDetails = self.account.GetAccount()
                    if self.accountDetails is not None:
                        self.StatusMessageLog("Logged in as " + self.accountDetails["displayName"])
                        self.user = self.accountDetails["displayName"]
                        loginMessage.config(text="Logged in as " + self.accountDetails["displayName"])
                        self.account.SaveAuthTokenLocal(self.appData_local)
                        if startup:
                            self.StartUp(login=True)
                        self.loginMenu.entryconfigure("Login",state=DISABLED)
                        self.loginMenu.entryconfigure("Logout",state=NORMAL)
                        loginTopLevel.grab_release()
                        loginTopLevel.destroy()
                        return True
                else:
                    loginMessage.config(text="Enter Password")
                    loginPasswordEntry.focus_set()
            else:
                loginMessage.config(text="Enter email address")
                loginUsernameEntry.focus_set()
        def LoginClosed():
            loginTopLevel.grab_release()
            self.root.destroy()
            return False
        loginTopLevel = Toplevel(self.root)
        loginTopLevel.grab_set()
        loginTopLevel.attributes("-topmost",True)
        loginTopLevel.title("UKSF Login")
        loginTopLevel.geometry("350x200")
        loginTopLevel.iconbitmap(self.exeDir/"Functions"/"icons"/"uksf.ico")
        loginWindow = loginTopLevel.winfo_toplevel()
        loginWindow.anchor("nw")
        loginWindow.grid_columnconfigure(0,weight=1)
        loginWindow.grid_rowconfigure(0,weight=1)
        loginFrame = ttk.Frame(loginWindow,padding=20)
        loginFrame.grid_columnconfigure(0,weight=1)
        loginFrame.grid_rowconfigure(0,minsize=50,weight=2)
        loginFrame.grid_rowconfigure((1,2),weight=1)
        loginLabelframe = ttk.LabelFrame(loginFrame,text="uk-sf.co.uk",padding=5)
        loginLabelframe.grid_columnconfigure(0,minsize=60)
        loginLabelframe.grid_columnconfigure(1,weight=1)
        loginLabelframe.grid_rowconfigure((0,1),minsize=20,weight=1)
        loginUsernameLabel = ttk.Label(loginLabelframe,text="Email:",justify="right")
        loginPasswordLabel = ttk.Label(loginLabelframe,text="Password:",justify="right")
        loginUsernameEntry = ttk.Entry(loginLabelframe,justify="center")
        loginPasswordEntry = ttk.Entry(loginLabelframe,justify="center",show="*")
        loginMessage = ttk.Label(loginFrame,text="",justify="right")
        loginButton = ttk.Button(loginFrame,text="Login",command=Login)
        loginFrame.grid(row=0,column=0,sticky="NESW")
        loginLabelframe.grid(row=0,column=0,sticky="NESW")
        loginUsernameLabel.grid(row=0,column=0,sticky="E")
        loginPasswordLabel.grid(row=1,column=0,sticky="E")
        loginUsernameEntry.grid(row=0,column=1,sticky="EW")
        loginPasswordEntry.grid(row=1,column=1,sticky="EW")
        loginMessage.grid(row=1,column=0,sticky="NS")
        loginMessage.grid_remove()
        loginButton.grid(row=2,column=0,sticky="EW")
        loginTopLevel.protocol("WM_DELETE_WINDOW",LoginClosed)
    def LoginRefresh(self) -> bool:
        refresh = self.account.RefreshAuthToken(self.appData_local)
        if refresh is not None:
            self.StatusMessageLog("Logged back in as " + refresh["displayName"])
            self.account = refresh
            self.user = refresh["displayName"]
            return True
        else:
            if self.LoginWindow(startup= True):
                return True
            else:
                quit()   
    def IDFCalculatorClosed(self) ->None:
        self.StatusMessageLog("End of Line")
        Path(self.baseDir/"tempstipple.xbm").unlink(missing_ok=True)
        self.root.destroy()
        quit()
    def UpdateStringVar(self,StrVar: StringVar, value,trace = None, entryLabel = None):
        try:
            if trace is not None:
                StrVar.trace_remove(mode="write",cbname=trace)
            StrVar.set(value)
        except Exception as e: self.StatusMessageErrorDump(e,errorMessage=f"Failed to set string variable {StrVar} to {value}")
    def NewTerrainHeightMapWindow(self,filePath:str, terrainName: str, compression = True):
        def HeightMapTopLevelClosed():
            None
        def HeightMapAccept(*args):
            if mapName.get().count(",")>0:
                mapName.set("")
            else:
                HeightMapTopLevelClosed()
                if mapName.get()!="":
                    filePath = filedialog.askopenfilename(initialdir="C:/arma3/terrain",title=f"Select corresponding {mapName.get()} terrain height map",filetypes=(("Text files","*txt"),("All files","*.*")))
                    if filePath:
                        Map.Terrain.NewTerrainHeightmap(baseDir=self.baseDir,filePath=filePath,terrainName=mapName.get())
                        self.root.bell()
                        ########################Terrain List Check###############
        HeightMapTopLevel = Toplevel(self.root)
        HeightMapTopLevel.grab_set()
        HeightMapTopLevel.attributes("-topmost",True)
        HeightMapTopLevel.title("Select terrain name")
        HeightMapTopLevel.geometry("350x70")
        HeightMapTopLevel.resizable(width=True,height=True)
        HeightMapTopLevel.iconbitmap(self.exeDir/"Functions"/"icons"/"terrain.ico")
        HeightMapWindow = HeightMapTopLevel.winfo_toplevel()
        HeightMapWindow.anchor("nw")
        HeightMapWindow.grid_columnconfigure(0,weight=1)
        HeightMapWindow.grid_rowconfigure(0,weight=1)
        HeightMapFrame = ttk.Frame(HeightMapWindow,padding=10)
        HeightMapFrame.grid(row="0",column="0",sticky="nesw")
        HeightMapFrame.grid_columnconfigure((0,2),minsize=10)
        HeightMapFrame.grid_columnconfigure(1,weight=1)
        HeightMapFrame.grid_rowconfigure(0,weight=1)
        mapName = StringVar()
        HeightMapLabel =ttk.Label(HeightMapFrame,text="Map Name:",justify="right")
        HeightMapEntry = ttk.Entry(HeightMapFrame,textvariable=mapName,justify="center")
        HeightMapButton = ttk.Button(HeightMapFrame,text="Accept",command=HeightMapAccept)
        HeightMapFrame.grid(row="0",column="0",sticky="nesw")
        HeightMapLabel.grid(row="0",column="0",sticky="nesw")
        HeightMapEntry.grid(row="0",column="1",sticky="ew")
        HeightMapButton.grid(row="0",column="2",sticky="ew")
        HeightMapEntry.focus()
        HeightMapEntry.bind("<Return>",HeightMapAccept)
        HeightMapTopLevel.protocol("WM_DELETE_WINDOW",HeightMapTopLevelClosed)
    def NewTerrainImageWindow(self):
        terrainImageTerrainName = StringVar()
        terrainImageTerrainURL = StringVar()
        def Download():
            try:
                if (terrainImageTerrainName.get()!=""):
                    terrainImageTopLevel.attributes("-topmost",False)
                    terrainImageTopLevel.grab_release()
                    terrainImagePreviewTopLevel = Toplevel(self.root)
                    terrainImagePreviewTopLevel.grab_set()
                    terrainImagePreviewTopLevel.title("Map Download")
                    terrainImagePreviewTopLevel.geometry("746x323+0+0")
                    terrainImagePreviewTopLevel.iconbitmap(self.exeDir/"Functions"/"icons"/"terrain.ico")
                    terrainImagePreviewWindow = terrainImagePreviewTopLevel.winfo_toplevel()
                    terrainImagePreviewWindow.anchor("nw")
                    terrainImagePreviewWindow.grid_columnconfigure(0,weight=1)
                    terrainImagePreviewWindow.grid_rowconfigure(0,weight=1)
                    terrainImagePreviewFrame = ttk.Frame(terrainImagePreviewWindow)
                    terrainImagePreviewMap = ttk.Label(terrainImagePreviewFrame)
                    terrainImagePreviewStitch = ttk.Label(terrainImagePreviewFrame)
                    terrainImagePreviewFrame.grid(column="0",row="0",sticky="NESW")
                    terrainImagePreviewMap.grid(column="0",row="0",sticky="NW")
                    terrainImagePreviewStitch.grid(column="1",row="0",sticky="NW")
                    imageState = Map.Terrain.NewTerrainImage(url= terrainImageTerrainURL.get(),
                                                             terrainImagePreviewSquare=terrainImagePreviewMap,
                                                             terrainStitchDiagram=terrainImagePreviewStitch,
                                                             toplevel=terrainImagePreviewTopLevel,
                                                             baseDir = self.baseDir,
                                                             terrainImageTerrainName=terrainImageTerrainName.get())
                    
                    if type(imageState) == Exception:
                        self.StatusMessageErrorDump(e=imageState,errorMessage="Failed to Save images to file")
                    else:
                        self.StatusMessageLog(message=f"Downloaded {terrainImageTerrainName.get()} terrain map")
                    if terrainImageTopLevel.terrainImagePackage.get():
                        Map.Terrain.CompressImages(self.baseDir/"Terrains",terrainImageTerrainName.get())
                        self.StatusMessageLog(message=f"Packaged, then removed {terrainImageTerrainName.get()} terrain images")
                    terrainImagePreviewTopLevel.grab_release()
                    self.root.bell()
                    terrainImagePreviewTopLevel.destroy()
                    terrainImageTopLevel.destroy()
            except Exception as e:
                self.StatusMessageErrorDump(e, errorMessage=f"Issue when Downloading terrain map for {terrainImageTerrainName.get()}")
        terrainImageTopLevel = Toplevel(self.root)
        terrainImageTopLevel.terrainImagePackage = BooleanVar(value=True)
        terrainImageTopLevel.grab_set()
        terrainImageTopLevel.attributes("-topmost",True)
        terrainImageTopLevel.title("Terrain image creation")
        terrainImageTopLevel.geometry("800x560")
        terrainImageTopLevel.resizable(width=True,height=True)
        terrainImageTopLevel.iconbitmap(self.exeDir/"Functions"/"icons"/"terrain.ico")
        terrainImageWindow = terrainImageTopLevel.winfo_toplevel()
        terrainImageWindow.minsize(400,260)
        terrainImageWindow.anchor("nw")
        terrainImageWindow.grid_columnconfigure(0,weight=1)
        terrainImageWindow.grid_rowconfigure(0,weight=1)
        terrainImageFrame = ttk.Frame(terrainImageWindow,padding=10)
        terrainImageFrame.grid_columnconfigure(0,minsize=35)
        terrainImageFrame.grid_columnconfigure(1,minsize=5)
        terrainImageFrame.grid_columnconfigure((2,3),weight=1,minsize=40)
        terrainImageFrame.grid_rowconfigure(2,minsize=5)
        terrainImageNameLabel = ttk.Label(terrainImageFrame,text="Terrain Name",justify="right")
        terrainImageUrlLabel = ttk.Label(terrainImageFrame,text="Terrain URL",justify="right")
        terrainImageSeparator1 = ttk.Separator(terrainImageFrame,orient="vertical")
        terrainImageNameEntry = ttk.Entry(terrainImageFrame,justify="center",textvariable=terrainImageTerrainName)
        terrainImageURLEntry = ttk.Entry(terrainImageFrame,justify="center",textvariable=terrainImageTerrainURL)
        terrainImageTerrainURL.set("https://atlas.plan-ops.fr/data/1/maps/???/???/")
        terrainImageCompress = ttk.Checkbutton(terrainImageFrame,text="Package Files",variable=terrainImageTopLevel.terrainImagePackage,offvalue=False,onvalue=True)
        terrainImageDownloadButton = ttk.Button(terrainImageFrame,text="Download",command=lambda: Download())
        terrainImageFrame.grid(column="0",row="0",sticky="NEW")
        terrainImageNameLabel.grid(column="0",row="0",sticky="NW")
        terrainImageUrlLabel.grid(column="0",row="1",sticky="NW")
        terrainImageSeparator1.grid(column="1",row="0",rowspan="2",sticky="NS")
        terrainImageNameEntry.grid(column="2",row="0",columnspan="2",sticky="NEW",pady="4")
        terrainImageURLEntry.grid(column="2",row="1",columnspan="2",sticky="NEW",pady="4")
        terrainImageCompress.grid(column="0",columnspan=3,row="2",sticky="NE")
        terrainImageDownloadButton.grid(column="0",row="10",columnspan="4",sticky="NEW")
    def TerrainChange(self,*args):
        if self.terrain.get() != "":
            try:
                self.StatusMessageLog(privateMessage=F"Loading {self.terrain.get()} Height map")
                self.statusMessageLabel.update_idletasks()
                self.castJson.Save(source=JsonSource.COMMON,newEntry={"terrain" : self.terrain.get()},localOverride=True)
                self.terrainHeightMap = pd.read_csv(self.baseDir/"Terrains"/self.terrain.get()/(self.terrain.get()+".gzcsv"),compression="gzip")#USE THREADING TO MAKE THE PROGRAM RESPONSIVE
                self.maxRow, self.maxCol = self.terrainHeightMap.shape
                self.maxTerrainHeight = self.terrainHeightMap.to_numpy().max()
                self.StatusMessageLog("Loaded "+self.terrain.get()+ " Height map")
                self.root.bell()
            except Exception as e:
                self.StatusMessageErrorDump(e,errorMessage=f"Could not find terrain height map data for {self.terrain.get()}")
                self.terrain.set("")
                self.castJson.Save(source=JsonSource.COMMON,newEntry={"terrains" : ""},localOverride=True)
    def FlipWindowPanes(self):
        """Flip the vertical panes back to front"""
        if int(self.windowFlipPaneSide.get()) == 0:
            self.missionPagePanedWindow.insert(1,self.missionPagePanedWindow.pane4)
            self.missionPagePanedWindow.insert(2,self.missionPagePanedWindow.pane3)
            self.missionPagePanedWindow.insert(3,self.missionPagePanedWindow.pane2)
            self.missionPagePanedWindow.insert(4,self.missionPagePanedWindow.pane1)
            self.windowFlipPaneSide.set(1)
        else:
            self.missionPagePanedWindow.insert(4,self.missionPagePanedWindow.pane4)
            self.missionPagePanedWindow.insert(3,self.missionPagePanedWindow.pane3)
            self.missionPagePanedWindow.insert(2,self.missionPagePanedWindow.pane2)
            self.missionPagePanedWindow.insert(1,self.missionPagePanedWindow.pane1)
            self.windowFlipPaneSide.set(0)
        self.StatusMessageLog("Fire mission window panes flipped")
    def ClearMessageLog(self):
        self.castJson.Delete(source=JsonSource.MESSAGELOG)
        self.messageLogText.delete("1.0","end")
        self.StatusMessageLog("Status log cleared")
    def ClearFireMission(self,mission: str|None = None, index: list|str|None = None,calculated = False):
        """
        takes the mission (LR,XY,FPF,Group) and take the name suffixes (...-##) and remove it from the target jsons, the calculated ones to if calculated == True
        If name is left empty ("") then all targets/fire missions of the selected mission will be deleted. if mission is not specified. all is removed.
        """
        if mission is None:
            if calculated == False:
                try:
                    self.castJson.Delete(source=JsonSource.TARGET)
                    self.StatusMessageLog(message=f"Deleted all target positions from JSON")
                except Exception as e:
                    self.StatusMessageErrorDump(e,errorMessage=f"Failed to delete target positions from JSON")
            if calculated:
                try:
                    self.castJson.Delete(source=JsonSource.FIREMISSION)
                    self.StatusMessageLog(message=f"Deleted all calculated fire missions from JSON")
                except Exception as e: self.StatusMessageErrorDump(e,errorMessage=f"Failed to delete calculated fire missions from JSON")
        else:
            if index is None:
                if calculated == False:
                    try:
                        self.castJson.Delete(source=JsonSource.TARGET,deleteKey=mission)
                        self.StatusMessageLog(message=f"Deleted {mission} target positions from JSON")
                    except Exception as e: self.StatusMessageErrorDump(e,errorMessage=f"Failed to delete {mission} target positions from JSON")
                if calculated:
                    try:
                        fireMissions = self.castJson.Load(source=JsonSource.TARGET)
                        for idfp,missions in fireMissions.items():
                            for key in list(missions.keys()):
                                if key[:2] == mission:
                                    fireMissions[idfp].pop(key,None)
                        self.castJson.Save(source=JsonSource.FIREMISSION,newEntry=fireMissions,append=False)
                        self.StatusMessageLog(message=f"Deleted calculated {mission} fire missions from JSON")
                    except Exception as e: self.StatusMessageErrorDump(e,errorMessage=f"Failed to delete calculated {mission} fire missions from JSON")
            else:
                names = list(index)
                for name in names:
                    if calculated == False:
                        try:
                            targets = self.castJson.Load(source=JsonSource.TARGET)
                            targets[mission].pop(name)
                            self.castJson.Save(source=JsonSource.TARGET,newEntry=targets)
                            self.StatusMessageLog(f"Deleted {mission}-{name} target position from JSON")
                        except Exception as e: self.StatusMessageErrorDump(e,errorMessage=f"Failed to delete {mission}-{name} target position from JSON")
                    if calculated:
                        try:
                            fireMissions = self.castJson.Load(source=JsonSource.FIREMISSION)
                            for idfp, missions in fireMissions.items():
                                fireMissions[idfp].pop(f"{mission}-{name}",None)
                            self.castJson.Save(source=JsonSource.FIREMISSION, newEntry=fireMissions,append = False)
                            self.StatusMessageLog(message=f"Deleted calculated mission {mission}-{name} from JSON")
                        except Exception as e: self.StatusMessageErrorDump(e,errorMessage=f"Failed to delete calculated mission {mission}-{name} from JSON")
        if calculated:
            self.SyncUpdate(JsonSource.FIREMISSION)
        if calculated == False:
            self.SyncUpdate(JsonSource.TARGET)
    def ClearIDFP(self,idfp:list|str|None = None):
        if idfp is None:
            try:
                self.castJson.Delete(JsonSource.IDFP)
            except Exception as e: self.StatusMessageErrorDump(e,errorMessage="Failed to delete IDFPs from JSON")
            try:
                self.castJson.Delete(JsonSource.FIREMISSION)
            except Exception as e: self.StatusMessageErrorDump(e,errorMessage="Failed to delete Fire missions from JSON")
            try:
                for tabId in self.fireMissionNotebook.tabs():
                    self.fireMissionNotebook.forget(tabId)
                self.SyncUpdate([JsonSource.IDFP,JsonSource.FIREMISSION])   
                self.StatusMessageLog("Cleared IDFPs")
            except Exception as e:
                self.StatusMessageErrorDump(e,errorMessage="Failed to conform deletion of IDFPs from JSON")
        else:
            idfps = list(idfp)
            for idfp in idfps:
                try:
                    self.castJson.Delete(source=JsonSource.IDFP,deleteKey=idfp)
                except Exception as e: self.StatusMessageErrorDump(e,errorMessage=f"Failed to delete {idfp} from JSON")    
                try:
                    self.castJson.Delete(source=JsonSource.FIREMISSION,deleteKey=idfp)
                except Exception as e: self.StatusMessageErrorDump(e,errorMessage=f"Failed to delete {idfp} fire missions from JSON")    
                try:
                    for tabId in self.fireMissionNotebook.tabs():
                        if self.fireMissionNotebook.tab(tabId,option="text") == idfp:
                            self.fireMissionNotebook.forget(tabId)
                            break
                    self.SyncUpdate([JsonSource.IDFP,JsonSource.FIREMISSION])
                except Exception as e: self.StatusMessageErrorDump(e,errorMessage=f"Failed confirm deletion of {idfp} from JSON")   
    def ClearFriendlyPositions(self,name = None):
        if name is None:
            try:
                self.castJson.Delete(source=JsonSource.FRIENDLY)
                self.SyncUpdate(JsonSource.FRIENDLY)
                self.StatusMessageLog("Cleared friendly positions")
            except Exception as e: self.StatusMessageErrorDump(e,errorMessage="Failed to clear friendly positions")
        else:
            names = list(name)
            for name in names:
                try:
                    self.castJson.Delete(source=JsonSource.FRIENDLY,deleteKey=name)
                    self.SyncUpdate(JsonSource.FRIENDLY)
                    self.StatusMessageLog(f"Cleared {name} friendly position")
                except Exception as e: self.StatusMessageErrorDump(e,errorMessage=f"Failed to clear {name} from JSON")       
    def ClearAll(self):
        try:
            self.ClearMessageLog()
            self.ClearFireMission(calculated=False)
            self.ClearFireMission(calculated=True)
            self.ClearIDFP()
            self.ClearFriendlyPositions()
            self.StatusMessageLog("All position(s) cleared")
        except Exception as e: self.StatusMessageErrorDump(e,errorMessage="Failed to clear all")
    def ClearConfirmation(self,source: JsonSource | str | None = None) -> bool: ###### Make shorter by only including confirmation and use a bool to action in the above 
        def Yes():
            if source is None: self.ClearAll()
            elif source == JsonSource.IDFP: self.ClearIDFP()
            elif source == JsonSource.FRIENDLY: self.ClearFriendlyPositions()
            elif source == JsonSource.TARGET:
                self.ClearFireMission()
                self.ClearFireMission(calculated=True)
            elif source == "FPF":
                self.ClearFireMission(mission="FPF",calculated=False)
                self.ClearFireMission(mission="FPF",calculated=True)
            elif source == "LR":
                self.ClearFireMission(mission="LR",calculated=False)
                self.ClearFireMission(mission="LR",calculated=True)
            elif source == "XY":
                self.ClearFireMission(mission="XY",calculated=False)
                self.ClearFireMission(mission="XY",calculated=True)
            elif source == "Group":
                self.ClearFireMission(mission="Group",calculated=False)
                self.ClearFireMission(mission="Group",calculated=True)
            elif source == JsonSource.FIREMISSION: self.ClearFireMission(calculated=True)
            elif source == JsonSource.MESSAGELOG: self.ClearMessageLog()
            else: return
        def No():
            confirmationTopLevel.destroy()
        confirmationTopLevel = Toplevel(self.root)
        confirmationTopLevel.grab_set()
        confirmationTopLevel.attributes("-topmost",True)
        confirmationTopLevel.title("Confirm Clear?")
        confirmationTopLevel.geometry("800x560")
        confirmationTopLevel.resizable(width=False,height=False)
        confirmationTopLevel.iconbitmap(self.exeDir/"Functions"/"icons"/"settings.ico")
        confirmationWindow = confirmationTopLevel.winfo_toplevel()
        confirmationWindow.minsize(400,260)
        confirmationWindow.anchor("nw")
        confirmationWindow.grid_columnconfigure(0,weight=1)
        confirmationWindow.grid_rowconfigure(0,weight=1)
        confirmationFrame = ttk.Frame(confirmationWindow,padding=10)
        confirmationFrame.grid_columnconfigure((0,1),minsize=55)
        confirmationFrame.grid_rowconfigure((0,1),minsize=24)
        if source is None: confirmationLabel = ttk.Label(confirmationFrame,text="Clear all?",justify="right")
        elif source == JsonSource.IDFP: confirmationLabel = ttk.Label(confirmationFrame,text="Clear IDFPs, targets and fire missions?",justify="right")
        elif source == JsonSource.FRIENDLY: confirmationLabel = ttk.Label(confirmationFrame,text="Clear friendlies?",justify="right")
        elif source == JsonSource.TARGET: confirmationLabel = ttk.Label(confirmationFrame,text="Clear targets and fire missions?",justify="right")
        elif source == "FPF": confirmationLabel = ttk.Label(confirmationFrame,text="Clear FPF targets and fire missions?",justify="right")
        elif source == "LR": confirmationLabel = ttk.Label(confirmationFrame,text="Clear LR targets and fire missions?",justify="right")
        elif source == "XY": confirmationLabel = ttk.Label(confirmationFrame,text="Clear XY targets and fire missions?",justify="right")
        elif source == "Group": confirmationLabel = ttk.Label(confirmationFrame,text="Clear grouped?",justify="right")
        elif source == JsonSource.FIREMISSION: confirmationLabel = ttk.Label(confirmationFrame,text="Clear calculated fire missions?",justify="right")
        elif source == JsonSource.MESSAGELOG: confirmationLabel = ttk.Label(confirmationFrame,text="Clear message log?",justify="right")
        else: return
        confirmationNoButton = ttk.Button(confirmationFrame,text="No",command=No,padding=8)
        confirmationNoButton.bind("<Return>",No)
        confirmationYesButton = ttk.Button(confirmationFrame,text="Yes",command=Yes,padding=8)
        confirmationFrame.grid(row="0",column="0",sticky="NESW")
        confirmationLabel.grid(row="0",column="0",columnspan="2",sticky="NS")
        confirmationNoButton.grid(row="1",column="0",sticky="NESW")
        confirmationYesButton.grid(row="1",column="1",sticky="NESW")
        confirmationYesButton.focus_set()
        confirmationTopLevel.protocol("WM_DELETE_WINDOW",No)


    def OpenMessageLog(self,*arg):
        self.messageLogOpen = True
        def MessageLogClosed():
            self.messageLogOpen = False
            messageLog.destroy()
        messageLog = Toplevel(self.root)
        messageLog.attributes("-topmost",True)
        messageLog.title("Status Log")
        messageLog.geometry("950x100")
        messageLog.iconbitmap(self.exeDir/"Functions"/"icons"/"statuslog.ico")
        messageLogWindow = messageLog.winfo_toplevel()
        messageLogWindow.anchor("nw")
        messageLogWindow.grid_columnconfigure(0,weight=1)
        messageLogWindow.grid_rowconfigure(0,weight=1)
        messageLogWindow.minsize(550,150)
        messageLogContent = ttk.Frame(messageLogWindow)
        messageLogContent.grid_columnconfigure(0,weight=1)
        messageLogContent.grid_rowconfigure(0,weight=1)
        self.messageLogText = Text(messageLogContent,wrap="none",width="500")
        yScroll = Scrollbar(messageLogContent,orient="vertical",command=self.messageLogText.yview)
        xScroll = Scrollbar(messageLogContent,orient="horizontal",command=self.messageLogText.xview)
        self.messageLogText.config(yscrollcommand=yScroll.set,xscrollcommand=xScroll.set)
        self.messageLogText.insert("1.0",self.castJson.Load(source=JsonSource.MESSAGELOG))
        self.messageLogText.config(state="disabled")
        messageLogContent.grid(column=0,row=0,sticky="NESW")
        self.messageLogText.grid(column=0,row=0,sticky="NESW")
        yScroll.grid(column=1,row=0,sticky="NS")
        xScroll.grid(column=0,row=1,sticky="WE")
        self.messageLogText.yview_moveto(1)
        messageLog.protocol("WM_DELETE_WINDOW",MessageLogClosed)
    
    def SystemChanged(self,system: str | None = None,settingNew = False):
        self.system.trace_remove(mode="write",cbname=self.processSettings["system"]["traceName"])
        if settingNew and system is not None:
            try:
                oldSystem = self.castJson.Load(source=JsonSource.COMMON)["system"]
            except:
                try:
                    self.castJson.Save(source=JsonSource.COMMON,newEntry={"system": system})
                except Exception as e: self.StatusMessageErrorDump(e,"Could not save current system to JSON after not finding the original system in JSON")
                else:
                    self.StatusMessageLog(f"Changed artillery system to {system}")
                    self.StatusMessageLog(message="",privateMessage="Could not find original system in JSON")
            else:
                try: self.castJson.Save(source=JsonSource.COMMON,newEntry={"system" : system})
                except Exception as e: self.StatusMessageErrorDump(e,errorMessage="Could not save current system to JSON")
                else: self.StatusMessageLog(f"Changed artillery system from {oldSystem} to {system}")
            try: self.idfpSystemLabel.config(text = system)
            except: self.idfpSystemLabel.config(text = "Error")
            self.StatusMessageLog("System Change: If pre-existing IDFP selections are present, check selection charges, trajectories and old calculations")
        elif system is not None:
            try: 
                oldSystem = self.system.get()
                self.system.set(system)
                self.idfpSystemLabel.config(text = system)
                self.StatusMessageLog(f"Artillery system has changed from {oldSystem} to {system}") if oldSystem !="" else self.StatusMessageLog(f"Artillery system set to {system}")
                self.StatusMessageLog(message="",privateMessage="System Change: If pre-existing IDFP selections are present, check selection charges, trajectories and old calculations")
            except Exception as e: self.StatusMessageErrorDump(e,"Could not set system from JSON")
        self.systemTrace = self.system.trace_add(mode="write", callback=lambda: self.SystemChanged(system=self.system.get(),settingNew=True))
        self.processSettings["system"]["traceName"] = self.systemTrace
        systemConfig = self.castJson.Load(source=JsonSource.ARTILLERYCONFIG)[system.get()]
        try:
            self.idfpChargeCombobox.config(values=systemConfig["Charges"])
            self.idfpTrajectoryCombobox.config(values=systemConfig["Trajectories"])
        except Exception as e: self.StatusMessageErrorDump(e,"Failed to set system combo boxes or load system configurations")
        
    def InitialiseIDFPList(self):
        try:
            oldLoadedIDFPs = list(self.castJson.Load(source=JsonSource.IDFP).keys())
            self.idfpListBoxContents.set(oldLoadedIDFPs)
            self.idfpNameCombobox.config(values = oldLoadedIDFPs)
        except Exception as e:
            self.StatusMessageErrorDump(e,"Failed to load old IDFPs from JSON")
            return
        try:
            oldSelectedIDFPs = self.castJson.Load(source=JsonSource.COMMON,localOverride=True)["IDFPSelection"]
            if oldSelectedIDFPs!= None or oldSelectedIDFPs != []:
                for select in oldSelectedIDFPs:
                    self.idfpListBox.selection_set(select,select)
        except Exception as e:
            self.StatusMessageErrorDump(e,"Failed to Load last IDFP selections")
            self.castJson.Save(source=JsonSource.COMMON,newEntry={"IDFPSelection": []},localOverride=True)


    def IDFPListUpdate(self,selected):
        oldList = self.castJson.Load(source=JsonSource.COMMON,localOverride=True)["IDFPSelection"]
        try:
            list(set(list(selected)).symmetric_difference(set(oldList)))
        except KeyError: return
        self.castJson.Save(source=JsonSource.COMMON,newEntry={"IDFPSelection": list(selected)},localOverride=True)
    
    def SyncIDFP(self,idfps):
        try:
            self.idfpListBoxContents.set(list(idfps))
            self.idfpNameCombobox.config(values=idfps)
        except Exception as e: self.StatusMessageErrorDump(e,errorMessage="Failed to Load IDFPs from JSON")
    
    #def SyncFriendlies(self,)

    def HeightAutoFill(self,event,x:str,y:str,heightlabel: StringVar | ttk.Label):
        if event.keysym == "Return" or event.keysym == "Tab":
            if len(x) in (4,5) and len(y) in [4,5]:
                if len(x) == 4: x += "0"
                if len(y) == 4: y += "0"
                if int(x) > self.maxCol: x = self.maxCol - 1
                elif int(x) < 0: x = 0
                if int(y) > self.maxRow: x = self.maxRow - 1
                elif int(y) < 0: y = 0
                try: self.idfpHeight.set(self.terrainHeightMap.iat[int(x),int(y)])
                except: pass

    def LoadSelectionDetails(self,event,source):
        try:
            if event.keysym=="Return" or event.keysym=="Tab":
                json = self.castJson.Load(source=source)
                for name,details in json.items():
                    if source is JsonSource.IDFP:
                        if self.idfpName.get() == name:
                            self.idfpPosX.set(details["GridX"])
                            self.idfpPosY.set(details["GridY"])
                            self.idfpHeight.set(details["Height"])
                            self.idfpUseCharge.set(details["ForceCharge"])
                            self.idfpCharge.set(details["Charge"])
                            self.idfpTraj.set(details["Trajectory"])
                    if source is JsonSource.FRIENDLY:
                        if self.friendlyName.get() == name:
                            self.friendlyPosX.set(details["GridX"])
                            self.friendlyPosY.set(details["GridY"])
                            self.friendlyHeight.set(details["Height"])
                            self.friendlyDispersion.set(details["Dispersion"])
                    if source is JsonSource.TARGET:
                        if self.xylrfpf.get() == name:
                            for fm, fmDetails in details.items():
                                if self.targetReference.get() == fm:
                                    self.targetPosX.set(fmDetails["GridX"])
                                    self.targetPosY.set(fmDetails["GridY"])
                                    self.targetHeight.set(fmDetails["Height"])
                                    self.fireMissionEffect.set(fmDetails["Effect"])
                                    self.fireMissionWidth.set(fmDetails["Width"])
                                    self.fireMissionDepth.set(fmDetails["Depth"])
                                    self.fireMissionLength.set(fmDetails["Length"])
                                    self.fireMissionCondition.set(fmDetails["Condition"])
                                    self.fireMissionHour.set(fmDetails["Time"]["Hour"])
                                    self.fireMissionMinute.set(fmDetails["Time"]["Minute"])
                                    self.fireMissionSecond.set(fmDetails["Time"]["Second"])
        except Exception as e: self.StatusMessageErrorDump(e,"Failed to set values")
        else:
            if source is JsonSource.IDFP:
                self.BoldenLabel(label=self.idfpNameLabel,type="Normal",strVarName="idfpName")
                self.boldLabels["idfpName"] = False
            elif source is JsonSource.FRIENDLY:
                self.BoldenLabel(label=self.friendlyNameLabel,type="Normal",strVarName="friendlyName")
                self.boldLabels["friendlyName"] = False

    def IDFPAddUpdate(self):
        try:
            if len(self.idfpPosX.get()) in (4,5) and len(self.idfpPosY.get()) in (4,5) and all(not var for var in (self.idfpName.get().isspace(),
                                                                                                                   self.idfpHeight.get().isspace(),
                                                                                                                   self.idfpHeight.get().isalpha())):
                charge = int(self.idfpCharge.get()) if self.idfpCharge.get() != "" else 1
                traj = self.idfpTraj.get() if self.idfpTraj.get() != "" else "High"
                newIDFP = {
                    self.idfpName.get() : {
                        "GridX" : self.idfpPosX.get(),
                        "GridY" : self.idfpPosY.get(),
                        "Height" : float(self.idfpHeight.get()),
                        "ForceCharge" : int(self.idfpUseCharge.get()),
                        "Charge" : charge,
                        "Trajectory" : traj
                    }
                }
                try: self.castJson.Load(source=JsonSource.IDFP)[self.idfpName.get()]
                except KeyError: update = True
                except Exception as e:
                    self.StatusMessageErrorDump(e,"Error searching for the IDFP in json")
                    update = False
                else: update = False
                self.castJson.Save(source=JsonSource.IDFP,newEntry=newIDFP)
                self.SyncUpdate(JsonSource.IDFP)
                if update:
                    self.StatusMessageLog(message=f"{self.idfpName.get()} has been updated, position {newIDFP["GridX"]}, {newIDFP["GridY"]} at {newIDFP["Height"]} m")
                else:
                    self.StatusMessageLog(message=f"{self.idfpName.get()} has been added at position {newIDFP["GridX"]}, {newIDFP["GridY"]} at {newIDFP["Height"]} m")
                self.BoldenLabel(label=self.idfpNameLabel,type="Normal",strVarName="idfpName")
                self.boldLabels["idfpName"] = False
        except Exception as e:
            self.StatusMessageErrorDump(e,"Failed to Add/Update IDFP")

    def FriendlyAddUpdate(self):
        try:
            if len(self.friendlyPosX.get()) in (4,5) and len(self.friendlyPosY.get()) in (4,5) and all(not var for var in (self.friendlyName.get().isspace(),
                                                                                                                           self.friendlyHeight.get().isspace(),
                                                                                                                           self.friendlyHeight.get().isalpha())):
                dispersion = float(self.friendlyDispersion.get()) if self.friendlyDispersion.get() != "" else 0.0
                newPos = {
                    self.friendlyName.get() : {
                        "GridX" : self.friendlyPosX.get(),
                        "GridY" : self.friendlyPosY.get(),
                        "Height" : self.friendlyHeight.get(),
                        "Dispersion" : dispersion
                    }
                }
                try: self.castJson.Load(source=JsonSource.FRIENDLY)[self.friendlyName.get()]
                except KeyError: update = True
                except Exception as e:
                    self.StatusMessageErrorDump(e,"Error searching for the friendly position in json")
                    update = False
                else: update = False
                self.castJson.Save(source=JsonSource.FRIENDLY,newEntry=newPos)
                self.SyncUpdate(JsonSource.FRIENDLY)
                if update: self.StatusMessageLog(message=f"{self.friendlyName.get()} has been updated, position {newPos["GridX"]}, {newPos["GridY"]} at {newPos["Height"]} m")
                else: self.StatusMessageLog(message=f"{self.friendlyName.get()} has been added at position {newPos["GridX"]}, {newPos["GridY"]} at {newPos["Height"]} m")
                self.BoldenLabel["friendlyName"] = False
        except Exception as e: self.StatusMessageErrorDump(e,"Failed to Add/Update Friendly position")

    def IDFPRemove(self,name:str,*args):
        if name!="":
            try:
                self.castJson.Delete(source=JsonSource.IDFP,deleteKey=name)
                self.idfpListBox.select_clear(0,END)
                self.SyncUpdate(JsonSource.IDFP)
            except Exception as e:
                self.StatusMessageErrorDump(e,errorMessage=f"Failed to delete {name}")
                return
            else:
                self.StatusMessageLog(message=f"{name} has been deleted")
                try:
                    self.castJson.Delete(source=JsonSource.FIREMISSION,deleteKey=name)
                    for tabId in self.fireMissionNotebook.tabs():
                        if self.fireMissionNotebook.tab(tabId,option="text") == name:
                            self.fireMissionNotebook.forget(tabId)
                            break
                    self.SyncUpdate(JsonSource.FIREMISSION)
                except: None
                else:
                    self.StatusMessageLog(message=f"{name} calculated fire missions have been deleted")
                try:
                    self.BoldenLabel(self.idfpNameLabel,"Normal","idfpName")
                    self.boldLabels["idfpName"] = False
                except: None
    def FriendlyRemove(self,name:str,*args):
        if name!= "":
            try:
                self.castJson.Delete(source=JsonSource.FRIENDLY,deleteKey=name)
                self.SyncUpdate(JsonSource.FRIENDLY)
            except Exception as e:
                self.StatusMessageErrorDump(e,errorMessage=f"Failed to delete {name}")
                return
            else:
                self.StatusMessageLog(message=f"{name} has been deleted")
                try:
                    self.BoldenLabel(self.friendlyNameLabel,"Normal","friendlyName")
                    self.boldLabels["friendlyName"] = False
                except: None

    def TargetXYLRFPFChange(self):
        def SetOriginalGrid():
            self.fireMissionSelectionEffectDestroyRadio.grid()
            self.fireMissionSelectionEffectNeutraliseRadio.grid()
            self.fireMissionSelectionEffectCheckRadio.grid()
            self.fireMissionSelectionEffectSaturationRadio.grid()
            self.fireMissionSelectionEffectAreaDenialRadio.grid()
            self.fireMissionSelectionEffectSmokeRadio.grid()
            self.fireMissionSelectionEffectIllumRadio.grid()
            self.fireMissionSelectionEffectFPFRadio.grid_remove()

        self.targetInputReferenceEntry.grid(sticky=self.xylrfpfPositionDict[self.xylrfpf.get()])
        if self.xylrfpf.get() == "0":
            self.fireMissionEffect = self.previousMissionEffect
            SetOriginalGrid()
        elif self.xylrfpf.get() == "1":
            self.fireMissionEffect = self.previousMissionEffect
            SetOriginalGrid()
        else: 
            self.fireMissionEffect.set("FPF")
            if self.fireMissionSelectionLabelframe.cget("text") == "Fire Mission Selection":
                self.fireMissionSelectionEffectDestroyRadio.grid_remove()
                self.fireMissionSelectionEffectNeutraliseRadio.grid_remove()
                self.fireMissionSelectionEffectCheckRadio.grid_remove()
                self.fireMissionSelectionEffectSaturationRadio.grid_remove()
                self.fireMissionSelectionEffectAreaDenialRadio.grid_remove()
                self.fireMissionSelectionEffectSmokeRadio.grid_remove()
                self.fireMissionSelectionEffectIllumRadio.grid_remove()
                self.fireMissionSelectionEffectFPFRadio.grid()

    def FireMissionEffectChange(self,*args):
        if self.fireMissionEffect.get() != "FPF" and self.xylrfpf.get() != "2":
            self.previousMissionEffect = self.fireMissionEffect.get()
    
    def FireMissionLengthChange(self,*args):
        if self.fireMissionLength.get().isnumeric()==True:
            self.fireMissionSelectionLengthUnitLabel.config(text="s")
        else:
            self.fireMissionSelectionLengthUnitLabel.config(text=" ")

    def FireMissionConditionChange(self,*args):
        if self.fireMissionCondition.get() in ("Time","time"):
            self.fireMissionSelectionTimeLabelframe.grid()
            self.fireMissionHour.set(datetime.now().strftime("%H"))
            self.fireMissionMinute.set(datetime.now().strftime("%M"))
            self.fireMissionSecond.set(datetime.now().strftime("%S"))
        else:
            self.fireMissionSelectionTimeLabelframe.grid_remove()

    def FireMissionGroupEffectChange(self,*args):
        if self.fireMissionGroupEffect.get() == "Creeping Barrage":
            self.fireMissionGroupSelectionDispersionWidthLabel.grid()
            self.fireMissionGroupSelectionDispersionWidthCombobox.grid()
            self.fireMissionGroupSelectionDispersionWidthUnitLabel.grid()
        else:
            self.fireMissionGroupSelectionDispersionWidthLabel.grid_remove()
            self.fireMissionGroupSelectionDispersionWidthCombobox.grid_remove()
            self.fireMissionGroupSelectionDispersionWidthUnitLabel.grid_remove()

    def CancelSettingChange(self,StrVar: StringVar,label: Widget, stringvar = ""):
        StrVar.set(" ")
        self.BoldenLabel(label,type="Normal",stringvar=stringvar)
        self.boldLabels[stringvar] = False

    def TemperatureEntryValidate(self,*args):
        value = (str(self.airTemperature.get()))
        try:
            if str(self.airTemperature.get()) != "":
                if value.count("-")>1:
                    value = value[::-1].replace("-","",1)[::-1]
                    self.airTemperature.set(value)
                if value.count(".")>1:
                    value = value.replace(".","",1)
                    self.airTemperature.set(value)
                if (value.isnumeric() and ((len(value) <= 5 and self.airTemperature.get()[:1] == "-") or (len(value) <= 4))):
                    pass
                elif (value.isnumeric() == False and ((len(value) <= 5 and self.airTemperature.get()[:1] == "-") or (len(value) <= 4))):
                    self.airTemperature.set(re.sub('[^0.-9-]',"",value,flags=re.IGNORECASE))
                else:
                    self.airTemperature.set(re.sub('[^0.-9-]',"",value,flags=re.IGNORECASE)[0:-1])
                self.castJson.Save(source=JsonSource.COMMON,newEntry={"airTemperature" : float(self.airTemperature.get())})
            else:
                self.castJson.Save(source=JsonSource.COMMON,newEntry={"airTemperature" : 0.0})
        except Exception as e: self.StatusMessageErrorDump(e,"Failed to validate the temperature entry")
        self.BoldenLabel(self.airTemperatureLabel,"airTemperature")
        self.boldLabels["airTemperature"] = False
    
    def HumidityEntryValidate(self,*args):
        value = (str(self.airHumidity.get()))
        try:
            if str(self.airHumidity.get()) != "":
                if value.count(".")>1:
                    value = value.replace(".","",1)
                    self.airHumidity.set(value)
                if (value.isnumeric() and (len(value) <= 4 )):
                    pass
                elif (value.isnumeric() is False and (len(value) <= 4 )):
                    self.airHumidity.set(re.sub('[^0.-9]',"",value,flags=re.IGNORECASE))
                else:
                    self.airHumidity.set(re.sub('[^0.-9]',"",value,flags=re.IGNORECASE)[0:-1])
                self.castJson.Save(source=JsonSource.COMMON,newEntry={"airHumidity" : float(self.airHumidity.get())})
            else:
                self.castJson.Save(source=JsonSource.COMMON,newEntry={"airHumidity" : 0.0})
        except Exception as e: self.StatusMessageErrorDump(e,"Failed to validate the humidity entry")
        self.BoldenLabel(self.airHumidityLabel,"normal",stringvar="airHumidity")
        self.boldLabels["airHumidity"] = False

    def PressureEntryValidate(self,*args):
        value = (str(self.airPressure.get()))
        try:
            if str(self.airPressure.get()) != "":
                if value.count(".")>1:
                    value = value.replace(".","",1)
                    self.airPressure.set(value)
                if (value.isnumeric() and (len(value) <= 7 )):
                    pass
                elif (value.isnumeric() is False and (len(value) <= 7 )):
                    self.airPressure.set(re.sub('[^0.-9]',"",value,flags=re.IGNORECASE))
                else:
                    self.airPressure.set(re.sub('[^0.-9]',"",value,flags=re.IGNORECASE)[0:-1])
                self.castJson.Save(source=JsonSource.COMMON,newEntry={"airPressure" : float(self.airPressure.get())})
            else:
                self.castJson.Save(source=JsonSource.COMMON,newEntry={"airPressure" : float(0.0)})
        except Exception as e: self.StatusMessageErrorDump(e,"Failed to validate the pressure entry")
        self.BoldenLabel(self.airPressureLabel,stringvar="airPressure")
        self.boldLabels["airPressure"] = False

    def DirectionEntryValidate(self,*args):
        value = (str(self.windDirection.get()))
        try:
                
            if str(self.windDirection.get()) != "":
                if (value.isnumeric() and (len(value) <= 3 )):
                    pass
                elif (value.isnumeric() is False and (len(value) <= 3 )):
                    self.windDirection.set(re.sub('[^0-9]',"",value,flags=re.IGNORECASE))
                else:
                    self.windDirection.set(re.sub('[^0-9]',"",value,flags=re.IGNORECASE)[0:-1])
                if (float(value) > 360.0):
                    self.windDirection.set(0.0)
                self.castJson.Save(source=JsonSource.COMMON,newEntry={"windDirection" : float(self.windDirection.get())})
            else:
                self.castJson.Save(source=JsonSource.COMMON,newEntry={"windDirection" : 0.0})
        except Exception as e: self.StatusMessageErrorDump(e,"Failed to validate the wind direction entry")
        self.BoldenLabel(self.windDirectionLabel,stringvar="windDirection")
        self.boldLabels["windDirection"] = False

    def MagnitudeEntryValidate(self,*args):
        value = (str(self.windMagnitude.get()))
        try:
            if str(self.windMagnitude.get()) != "":
                if value.count(".")>1:
                    value = value.replace(".","",1)
                    self.windMagnitude.set(value)
                if (value.isnumeric() and (len(value) <= 4 )):
                    pass
                elif (value.isnumeric() is False and (len(value) <= 4 )):
                    self.windMagnitude.set(re.sub('[^0.-9]',"",value,flags=re.IGNORECASE))
                else:
                    self.windMagnitude.set(self.windMagnitude.get()[0:-1])
                self.castJson.Save(source=JsonSource.COMMON,newEntry={"windMagnitude" : float(self.windMagnitude.get())})
            else:
                self.castJson.Save(source=JsonSource.COMMON,newEntry={"windMagnitude" : 0.0})
        except Exception as e: self.StatusMessageErrorDump(e,"Failed to validate the wind magnitude entry")
        self.BoldenLabel(self.windMagnitudeLabel,stringvar="windMagnitude")
        self.boldLabels["windMagnitude"] = False
    
    def StartUp(self,login = False,terrainLoad = False):
        None
