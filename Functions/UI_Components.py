from tkinter import *
from tkinter import ttk
from tkinter import font
from typing import Literal
import numpy as np
import re
import pyperclip
import threading
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
# from CAST import CastUI
import Functions.ArtilleryFunctions as AF
from Functions.JsonFunctions import JsonSource

class UIComponentBase():
    def __init__(self,UIMaster):
        self.UIMaster = UIMaster

class MainMenus(UIComponentBase):
    def __init__(self,UIMaster):
        super().__init__(UIMaster)
        self.menubar = Menu(self.UIMaster.root)
        self.UIMaster.root.config(menu=self.menubar)
        self.windowResetSafety = StringVar(value="1")
        
    def Initialise(self):
        self.systemMenu = Menu(self.menubar,tearoff=False)
        self.systemMenu.add_radiobutton(label="M6",variable=self.UIMaster.system,value="M6")
        self.systemMenu.add_radiobutton(label="L16",variable=self.UIMaster.system,value="L16")
        self.systemMenu.add_radiobutton(label="L119",variable=self.UIMaster.system,value="L119")
        self.systemMenu.add_radiobutton(label="Sholef",variable=self.UIMaster.system,value="Sholef")
        
        self.terrainMenu = Menu(self.menubar,tearoff=False)
        terrainAddMenu = Menu(self.terrainMenu,tearoff=False)
        self.terrainMenu.add_cascade(label="Add",menu=terrainAddMenu)
        terrainAddMenu.add_command(label="Install New Height Map (Keithenneu)",command=self.UIMaster.NewTerrainHeightMapWindow)
        terrainAddMenu.add_command(label="Download New Image (Plan-ops)",command=self.UIMaster.NewTerrainImageWindow)
        self.terrainMenu.add_separator()
        self.terrainLoadHeightMenu = Menu(self.terrainMenu,tearoff=False)
        self.terrainLoadImageMenu = Menu(self.terrainMenu,tearoff=False)
        self.terrainMenu.add_cascade(label="Load Map Heights",menu=self.terrainLoadHeightMenu)
        self.terrainMenu.add_cascade(label="Load Map Image",menu=self.terrainLoadImageMenu)
        self.terrainMenu.add_separator()
        settingsMenu = Menu(self.menubar,tearoff=False)
        self.loginMenu = Menu(settingsMenu,tearoff=False)
        settingsMenu.add_cascade(label="UKSF Login",menu=self.loginMenu)
        self.loginMenu.add_command(label="Login",command=self.UIMaster.LoginWindow)
        self.loginMenu.add_command(label="Logout",state="disabled",command=self.UIMaster.Logout)
        settingsMenu.add_checkbutton(label="Enable Target Edit",offvalue="0",onvalue="1",variable=self.UIMaster.target.windowFireMissionEditSafety)
        self.UIMaster.target.windowFireMissionEditSafety.trace_add(mode="write",callback=lambda *args: self.UIMaster.target.RequestEditFireMissions())
        settingsMenu.add_command(label="Flip Window Panes",command=self.UIMaster.FlipWindowPanes)
        self.resetMenu = Menu(self.menubar,tearoff=False)
        resetTargetMenu = Menu(self.resetMenu,tearoff=False)
        resetFMMenu = Menu(self.resetMenu,tearoff=False)
        self.resetMenu.add_command(label="Message Log",command=self.UIMaster.ClearMessageLog,state="disabled",activebackground="#F2F2F2")
        self.resetMenu.add_command(label="IDFP Positions",command=self.UIMaster.ClearIDFP,state="disabled",activebackground="#F2F2F2")
        self.resetMenu.add_command(label="Friendly Positions",command=self.UIMaster.ClearFriendlyPositions,state="disabled",activebackground="#F2F2F2")
        self.resetMenu.add_separator()
        self.resetMenu.add_cascade(label="Targets + Fire Missions",menu=resetTargetMenu,state="disabled",activebackground="#F2F2F2")
        self.resetMenu.add_cascade(label="Fire Missions",menu=resetFMMenu,state="disabled",activebackground="#F2F2F2")
        self.resetMenu.add_separator()
        self.resetMenu.add_command(label="Everything",command=self.UIMaster.ClearAll,state="disabled",activebackground="#F2F2F2")
        self.resetMenu.add_separator()
        resetTargetMenu.add_command(label="FPF",command=lambda m = "FPF":self.UIMaster.ClearTargetAndMission(mission=m),activebackground="red")
        resetTargetMenu.add_command(label="LR",command=lambda m = "LR":self.UIMaster.ClearTargetAndMission(mission=m),activebackground="red")
        resetTargetMenu.add_command(label="XY",command=lambda m = "XY":self.UIMaster.ClearTargetAndMission(mission=m),activebackground="red")
        resetTargetMenu.add_separator()
        resetTargetMenu.add_command(label="All",command=self.UIMaster.ClearTargetAndMission,activebackground="red")
        resetFMMenu.add_command(label="FPF",command=lambda m = "FPF": self.UIMaster.ClearFireMission(mission=m,calculated = True),activebackground="red")
        resetFMMenu.add_command(label="LR",command=lambda m = "LR": self.UIMaster.ClearFireMission(mission=m,calculated = True),activebackground="red")
        resetFMMenu.add_command(label="XY",command=lambda m = "XY": self.UIMaster.ClearFireMission(mission=m,calculated = True),activebackground="red")
        resetFMMenu.add_separator()
        resetFMMenu.add_command(label="All",command= self.UIMaster.ClearFireMission,activebackground="red")
        self.resetMenu.add_checkbutton(label="Safety Toggle",onvalue="1",offvalue="0",variable=self.windowResetSafety)
        self.windowResetSafety.trace_add(mode="write",callback=lambda *args: self.UIMaster.target.MenuSafetyClear())
        styleMenu = Menu(self.menubar,tearoff=False)
        styleMenu.add_command(label="Clam",command=lambda: ttk.Style().theme_use('clam'))
        styleMenu.add_command(label="Winnative",command=lambda: ttk.Style().theme_use('winnative'))
        styleMenu.add_command(label="Vista",command=lambda: ttk.Style().theme_use('vista'))
        styleMenu.add_command(label="Alt",command=lambda: ttk.Style().theme_use('alt'))
        styleMenu.add_command(label="Default",command=lambda: ttk.Style().theme_use('default'))
        styleMenu.add_command(label="Classic",command=lambda: ttk.Style().theme_use('classic'))
        helpMenu = Menu(self.menubar,tearoff=False)
        helpMenu.add_command(label=self.UIMaster.version,activebackground="#F2F2F2",activeforeground="black")

        self.menubar.add_cascade(label="System",menu=self.systemMenu)
        self.menubar.add_cascade(label="Terrain",menu=self.terrainMenu)
        self.menubar.add_cascade(label="Settings",menu=settingsMenu)
        self.menubar.add_cascade(label="Clear",menu=self.resetMenu)
        self.menubar.add_cascade(label="Style",menu=styleMenu)
        self.menubar.add_cascade(label="Help",menu=helpMenu,underline=0)
    def LoggedIn(self):
        self.loginMenu.entryconfigure("Login",state=DISABLED)
        self.loginMenu.entryconfigure("Logout",state=NORMAL)
    def LoggedOut(self):
        self.loginMenu.entryconfigure("Login",state=NORMAL)
        self.loginMenu.entryconfigure("Logout",state=DISABLED)
    def ClearTerrains(self):
        ignoreLabels = ("Add","Load Map Heights","Load Map Image")
        for menu in (self.terrainMenu,self.terrainLoadHeightMenu,self.terrainLoadImageMenu):
            i = menu.index("end")
            if i is not None:
                while i >=0:
                    try:
                        if menu.entrycget(i,"label") not in ignoreLabels:
                            menu.delete(i)
                    except TclError:
                        pass
                    i -= 1

    def AddTerrains(self,terrains):
        self.ClearTerrains()
        for terrain in terrains:
            both = 0
            if Path(self.UIMaster.baseDir/"Terrains"/terrain/(terrain+".gzcsv")).exists():
                self.terrainLoadHeightMenu.add_radiobutton(label=terrain,variable=self.UIMaster.terrain,value=terrain,command=lambda t = terrain: self.UIMaster.TerrainChange(t,imageInhibit = True))
                both +=1
            if Path(self.UIMaster.baseDir/"Terrains"/terrain/(terrain+".terrainimage")).exists():
                self.terrainLoadImageMenu.add_radiobutton(label=terrain,variable=self.UIMaster.terrain,value=terrain,command=lambda t = terrain: self.UIMaster.TerrainChange(t,heightInhibit = True))
                both +=1
            if both == 2:
                self.terrainMenu.add_radiobutton(label=terrain,variable=self.UIMaster.terrain,value=terrain,command=lambda t = terrain: self.UIMaster.TerrainChange(t))

class Statusbar(UIComponentBase):
    def __init__(self, UIMaster):
        super().__init__(UIMaster)
    def Initialise(self,frame):
        self.statusBar = ttk.Frame(frame,height=60,relief="ridge",padding="5")
        self.statusBar.grid_columnconfigure(0,weight=3)
        self.statusBar.grid_columnconfigure(1,minsize="195")
        self.statusBar.grid_columnconfigure(2,weight=1)
        self.statusMessageFrame = ttk.Frame(self.statusBar,relief="sunken",padding=3)
        self.statusMessageLabel = ttk.Label(self.statusMessageFrame,text="C.A.S.T. start up")
        self.statusMessageFrame.bind("<Double-1>",self.UIMaster.OpenMessageLog)
        self.statusMessageLabel.bind("<Double-1>",self.UIMaster.OpenMessageLog)
        self.statusGridFrame = ttk.Frame(self.statusBar,relief="sunken",padding=3)
        self.statusGridFrame.grid_columnconfigure((0,1,2),minsize=30,weight=1)
        self.statusReferenceLabel = ttk.Label(self.statusGridFrame,text="",justify="left")
        self.statusGridLabel = ttk.Label(self.statusGridFrame,text="",justify="right")
        self.statusHeightLabel = ttk.Label(self.statusGridFrame,text="",justify="right")
        self.statusProgressBar = ttk.Progressbar(self.statusBar,orient="horizontal")
        self.statusBar.grid(column="0",row="1",sticky="SEW")
        self.statusMessageFrame.grid(column="0",row="0",sticky="EW",)
        self.statusMessageLabel.grid(column="0",row="0",sticky="W")
        self.statusGridFrame.grid(column="1",row="0",sticky="EW")
        self.statusReferenceLabel.grid(column="0",row="0",sticky="W")
        self.statusGridLabel.grid(column="1",row="0",sticky="EW")
        self.statusHeightLabel.grid(column="2",row="0",sticky="E")
        self.statusProgressBar.grid(column="2",row="0",sticky="EW")

class IDFPCreation(UIComponentBase):
    def __init__(self, UIMaster):
        super().__init__(UIMaster)
        # self.UIMaster = CastUI(UIMaster)
        self.idfpName = StringVar()
        self.idfpPosX = StringVar()
        self.idfpPosY = StringVar()
        self.idfpHeight = StringVar()
        self.idfpListBoxContents = StringVar()
        self.idfpUseCharge = StringVar(value="0")
        self.idfpCharge = StringVar()
        self.idfpTraj = StringVar()
    def InitialiseIDFP(self, frame, snapshot = False, idfpListBoxContents = None):
        if snapshot:
            self.idfpListBoxContents = idfpListBoxContents
        idfpListBoxFrame = ttk.Labelframe(frame,text="Selection",height=200,padding=10,relief="groove")
        idfpListBoxFrame.grid_rowconfigure(0,weight=1)
        idfpListBoxFrame.grid_columnconfigure(0,weight=1)
        self.idfpListbox = Listbox(idfpListBoxFrame,height=5,width=7,listvariable=self.idfpListBoxContents,relief="sunken",justify="center",activestyle="dotbox",selectmode="multiple",borderwidth=2,exportselection=False)
        self.idfpListbox.bind("<<ListboxSelect>>",lambda *arg: self.IDFPListUpdate(self.idfpListbox.curselection()))
        idfpListBoxFrame.grid(column="0",row="1",sticky="NEWS")
        self.idfpListbox.grid(column="0",row="0",sticky="NEW")
    def Initialise(self,frame):
        idfpLabelframe = ttk.Labelframe(frame,text="IDFP",height=200,padding=10,relief="groove")
        idfpLabelframe.grid_rowconfigure(0,weight=1)
        idfpLabelframe.grid_rowconfigure(1,weight=0)
        idfpLabelframe.grid_columnconfigure(0,weight=1)
        idfpCreationFrame = ttk.Labelframe(idfpLabelframe,text="Creation",height=200,padding=10,relief="groove")
        idfpCreationFrame.grid_rowconfigure((0,1,2,3,4),weight=1)
        idfpCreationFrame.grid_columnconfigure(0,weight=0,minsize=10)
        idfpCreationFrame.grid_columnconfigure(1,weight=1,minsize=40)
        idfpCreationFrame.grid_columnconfigure(2,weight=1,minsize=40)
        self.idfpNameLabel = ttk.Label(idfpCreationFrame,text="Name:",justify="right",padding=4)
        self.idfpNameCombobox = ttk.Combobox(idfpCreationFrame,justify="center",textvariable=self.idfpName)
        self.idfpNameCombobox.bind("<Return>",lambda event: self.UIMaster.LoadSelectionDetails(event,source=JsonSource.IDFP))
        self.idfpNameCombobox.bind("<Tab>",lambda event: self.UIMaster.LoadSelectionDetails(event,source=JsonSource.IDFP))
        self.idfpName.trace_add("write",callback=lambda *args: self.UIMaster.BoldenLabel(self.idfpNameLabel,"Bold","idfpName"))
        idfpPosLabel = ttk.Label(idfpCreationFrame,text="Position:",justify="right",padding=4)
        idfpPosXEntry  = ttk.Entry(idfpCreationFrame, justify="center",textvariable=self.idfpPosX)
        idfpPosXEntry.bind("<Return>",lambda event:self.UIMaster.HeightAutoFill(event,self.idfpPosX.get(),self.idfpPosY.get(),heightlabel=self.idfpHeight))
        idfpPosXEntry.bind("<Tab>",lambda event:self.UIMaster.HeightAutoFill(event,self.idfpPosX.get(),self.idfpPosY.get(),heightlabel=self.idfpHeight))
        idfpPosYEntry  = ttk.Entry(idfpCreationFrame, justify="center",textvariable=self.idfpPosY)
        idfpPosYEntry.bind("<Return>",lambda event:self.UIMaster.HeightAutoFill(event,self.idfpPosX.get(),self.idfpPosY.get(),heightlabel=self.idfpHeight))
        idfpPosYEntry.bind("<Tab>",lambda event:self.UIMaster.HeightAutoFill(event,self.idfpPosX.get(),self.idfpPosY.get(),heightlabel=self.idfpHeight))
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
        idfpSystemFrame.bind("<Button-3>",lambda event : self.UIMaster.mainMenu.systemMenu.post(event.x_root,event.y_root))
        idfpSystemLabeltag.bind("<Button-3>",lambda event : self.UIMaster.mainMenu.systemMenu.post(event.x_root,event.y_root))
        idfpSystemSep.bind("<Button-3>",lambda event : self.UIMaster.mainMenu.systemMenu.post(event.x_root,event.y_root))
        self.idfpSystemLabel.bind("<Button-3>",lambda event : self.UIMaster.mainMenu.systemMenu.post(event.x_root,event.y_root))
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
        idfpEditChargeCheckbox = ttk.Checkbutton(idfpChargeFrame,variable=self.idfpUseCharge,offvalue="0",onvalue="1",padding=2)
        self.idfpEditChargeComboBox = ttk.Combobox(idfpChargeFrame,textvariable=self.idfpCharge,width=4,state="readonly")
        idfpEditTrajLabel = ttk.Label(idfpControlFrame,text="Trajectory",justify="right",padding=2)
        self.idfpEditTrajComboBox = ttk.Combobox(idfpControlFrame,textvariable=self.idfpTraj,width=4,state="readonly")
        self.InitialiseIDFP(frame)

        idfpLabelframe.grid(column="0",row="0",sticky="NEW")
        idfpCreationFrame.grid(column="0",row="0",sticky="NESW")
        self.idfpNameLabel.grid(column="0",row="0",sticky="NE")
        self.idfpNameCombobox.grid(column="1",columnspan="2",row="0",sticky="NEW")
        idfpPosLabel.grid(column="0",row="1",sticky="NES")
        idfpPosXEntry.grid(column="1",row="1",sticky="NEW")
        idfpPosYEntry.grid(column="2",row="1",sticky="NEW")
        idfpHeightLabel.grid(column="0",row="2",sticky="NES")
        idfpHeightFrame.grid(column="1",row="2",sticky="NEW")
        idfpHeightEntry.grid(column="0",row="0",sticky="NEW")
        idfpHeightUnitLabel.grid(column="1",row="0",sticky="NW")
        idfpButtonFrame.grid(column="2",row="2",rowspan="3",sticky="NEW")
        idfpSystemFrame.grid(column="0",row="0",sticky="NEWS")
        idfpSystemLabeltag.grid(column="0",row="0",sticky="NWS")
        idfpSystemSep.grid(column="1",row="0",sticky="NS")
        self.idfpSystemLabel.grid(column="2",row="0",sticky="NSE")
        idfpAddButton.grid(column="0",row="1",sticky="NEW")
        idfpRemoveButton.grid(column="0",row="2",sticky="NEW")
        idfpSeparator.grid(column="0",columnspan="2",row="3",sticky="EW",pady=4)
        idfpControlFrame.grid(column="0",columnspan="2",row="4",sticky="NEW")
        idfpEditChargeLabel.grid(column="0",row="0",sticky="NE")
        idfpChargeFrame.grid(column="1",row="0",sticky="NEW")
        idfpEditChargeCheckbox.grid(column="0",row="0",sticky="NE")
        self.idfpEditChargeComboBox.grid(column="1",row="0",sticky="NEW")
        idfpEditTrajLabel.grid(column="0",row="1",sticky="NE")
        self.idfpEditTrajComboBox.grid(column="1",row="1",sticky="NEW")

    def InitialiseIDFPList(self):
        try:
            oldLoadedIDFPs = list(self.UIMaster.castJson.Load(source=JsonSource.IDFP).keys())
            self.idfpListBoxContents.set(oldLoadedIDFPs)
            self.idfpNameCombobox.config(values = oldLoadedIDFPs)
        except Exception as e:
            self.UIMaster.StatusMessageErrorDump(e,"Failed to load old IDFPs from JSON")
            return
        try:
            oldSelectedIDFPs = self.UIMaster.castJson.Load(source=JsonSource.COMMON,localOverride=True)["IDFPSelection"]
            if oldSelectedIDFPs!= None or oldSelectedIDFPs != []:
                for select in oldSelectedIDFPs:
                    self.idfpListbox.selection_set(select,select)
        except Exception as e:
            self.UIMaster.StatusMessageErrorDump(e,"Failed to Load last IDFP selections")
            self.UIMaster.castJson.Save(source=JsonSource.COMMON,newEntry={"IDFPSelection": []},localOverride=True)
    def SyncIDFP(self,idfps):
        try:
            self.idfpListBoxContents.set(list(idfps))
            self.idfpNameCombobox.config(values=idfps)
        except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage="Failed to Load IDFPs from JSON")
    def IDFPListUpdate(self,selected):
        oldList = self.UIMaster.castJson.Load(source=JsonSource.COMMON,localOverride=True)["IDFPSelection"]
        try:
            list(set(list(selected)).symmetric_difference(set(oldList)))
        except KeyError: return
        self.UIMaster.castJson.Save(source=JsonSource.COMMON,newEntry={"IDFPSelection": list(selected)},localOverride=True)
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
                try: self.UIMaster.castJson.Load(source=JsonSource.IDFP)[self.idfpName.get()]
                except KeyError: update = False
                except Exception as e:
                    self.UIMaster.StatusMessageErrorDump(e,"Error searching for the IDFP in json")
                    update = False
                else: update = True
                self.UIMaster.castJson.Save(source=JsonSource.IDFP,newEntry=newIDFP)
                self.UIMaster.SyncUpdate(JsonSource.IDFP)
                if update:
                    self.UIMaster.StatusMessageLog(message=f"{self.idfpName.get()} has been updated, position {newIDFP[self.idfpName.get()]['GridX']}, {newIDFP[self.idfpName.get()]['GridY']} at {newIDFP[self.idfpName.get()]['Height']} m")
                else:
                    self.UIMaster.StatusMessageLog(message=f"{self.idfpName.get()} has been added at position {newIDFP[self.idfpName.get()]['GridX']}, {newIDFP[self.idfpName.get()]['GridY']} at {newIDFP[self.idfpName.get()]['Height']} m")
                self.UIMaster.BoldenLabel(label=self.idfpNameLabel,type="Normal",strVarName="idfpName")
                self.UIMaster.boldLabels["idfpName"] = False
        except Exception as e:
            self.UIMaster.StatusMessageErrorDump(e,"Failed to Add/Update IDFP")
    def IDFPRemove(self,name:str,*args):
        if name!="":
            try:
                self.UIMaster.castJson.Delete(source=JsonSource.IDFP,deleteKey=name)
                self.idfpListbox.select_clear(0,END)
                self.UIMaster.SyncUpdate(JsonSource.IDFP)
            except Exception as e:
                self.UIMaster.StatusMessageErrorDump(e,errorMessage=f"Failed to delete {name}")
                return
            else:
                self.UIMaster.StatusMessageLog(message=f"{name} has been deleted")
                try:
                    self.UIMaster.castJson.Delete(source=JsonSource.FIREMISSION,deleteKey=name)
                    for tabId in self.UIMaster.fireMissionNotebook.tabs():
                        if self.UIMaster.fireMissionNotebook.tab(tabId,option="text") == name:
                            self.UIMaster.fireMissionNotebook.forget(tabId)
                            break
                    self.UIMaster.SyncUpdate(JsonSource.FIREMISSION)
                except: None
                else:
                    self.UIMaster.StatusMessageLog(message=f"{name} calculated fire missions have been deleted")
                try:
                    self.UIMaster.BoldenLabel(self.idfpNameLabel,"Normal","idfpName")
                    self.UIMaster.boldLabels["idfpName"] = False
                except: None
    
class Atmospheric(UIComponentBase):
    def __init__(self, UIMaster):
        super().__init__(UIMaster)
        self.airTemperature = StringVar()
        self.airHumidity = StringVar()
        self.airPressure = StringVar()
        self.windDirection = StringVar()
        self.windMagnitude = StringVar()
        self.windDynamic = StringVar()
    
    def Initialise(self,frame):
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
        self.airTemperatureTrace = self.airTemperature.trace_add(mode="write",callback=lambda *args: self.UIMaster.BoldenLabel(self.airTemperatureLabel,"Bold","airTemperature"))
        temperatureEntry = ttk.Entry(airLabelFrame,width="5",textvariable=self.airTemperature,justify="right")
        temperatureEntry.bind("<Return>",self.TemperatureEntryValidate)
        temperatureEntry.bind("<Tab>",self.TemperatureEntryValidate)
        temperatureEntry.bind("<Escape>",lambda *args: self.CancelSettingChange(StrVar=self.airTemperature,label=self.airTemperatureLabel,stringvar="airTemperature"))
        temperatureUnits = ttk.Label(airLabelFrame,text="°C")
        self.airHumidityLabel = ttk.Label(airLabelFrame, text="Air Humidity",padding=4)
        self.airHumidityTrace = self.airHumidity.trace_add(mode="write",callback=lambda *args: self.UIMaster.BoldenLabel(self.airHumidityLabel,"Bold","airHumidity"))
        humidityEntry = ttk.Entry(airLabelFrame,width="5",textvariable=self.airHumidity,justify="right")
        humidityEntry.bind("<Return>",self.HumidityEntryValidate)
        humidityEntry.bind("<Tab>",self.HumidityEntryValidate)
        humidityEntry.bind("<Escape>",lambda *args: self.CancelSettingChange(StrVar=self.airHumidity,label=self.airHumidityLabel,stringvar="airHumidity"))
        humidityUnits = ttk.Label(airLabelFrame,text="%")
        self.airPressureLabel = ttk.Label(airLabelFrame, text="Air Pressure",padding=4)
        self.airPressureTrace = self.airPressure.trace_add(mode="write",callback=lambda *args: self.UIMaster.BoldenLabel(self.airPressureLabel,"Bold","airPressure"))
        pressureEntry = ttk.Entry(airLabelFrame,width="7",textvariable=self.airPressure,justify="right")
        pressureEntry.bind("<Return>",self.PressureEntryValidate)
        pressureEntry.bind("<Tab>",self.PressureEntryValidate)
        pressureEntry.bind("<Escape>",lambda *args: self.CancelSettingChange(StrVar=self.airPressure,label=self.airPressureLabel,stringvar="airPressure"))
        pressureUnits = ttk.Label(airLabelFrame,text="hPa")
        windLabelFrame = ttk.Labelframe(atmosphereLabelframe,text="Wind",height=200,padding=2)
        windLabelFrame.grid_columnconfigure(0,weight=1)
        windLabelFrame.grid_columnconfigure(1)
        windLabelFrame.grid_columnconfigure(2,minsize=75)
        windLabelFrame.grid_columnconfigure(3,weight=1)
        windLabelFrame.grid_rowconfigure((0,1,2),weight=1)
        windSeparator = ttk.Separator(windLabelFrame,orient="vertical")
        self.windDirectionLabel = ttk.Label(windLabelFrame, text="Wind Direction",padding=4)
        self.windDirectionTrace = self.windDirection.trace_add(mode="write",callback=lambda *args: self.UIMaster.BoldenLabel(self.windDirectionLabel,"Bold","windDirection"))
        directionEntry = ttk.Entry(windLabelFrame,width="3",textvariable=self.windDirection,justify="right")
        directionEntry.bind("<Return>",self.DirectionEntryValidate)
        directionEntry.bind("<Tab>",self.DirectionEntryValidate)
        directionEntry.bind("<Escape>",lambda *args: self.CancelSettingChange(StrVar=self.windDirection,label=self.windDirectionLabel,stringvar="windDirection"))
        directionUnits = ttk.Label(windLabelFrame,text="°")
        self.windMagnitudeLabel = ttk.Label(windLabelFrame, text="Wind Magnitude",padding=4)
        self.windMagnitudeTrace = self.windMagnitude.trace_add(mode="write",callback=lambda *args: self.UIMaster.BoldenLabel(self.windMagnitudeLabel,"Bold","windMagnitude"))
        magnitudeEntry = ttk.Entry(windLabelFrame,width="5",textvariable=self.windMagnitude,justify="right")
        magnitudeEntry.bind("<Return>",self.MagnitudeEntryValidate)
        magnitudeEntry.bind("<Tab>",self.MagnitudeEntryValidate)
        magnitudeEntry.bind("<Escape>",lambda *args: self.CancelSettingChange(StrVar=self.windMagnitude,label=self.windMagnitudeLabel,stringvar="windMagnitude"))
        magnitudeUnits = ttk.Label(windLabelFrame,text="m/s")
        windDynamicLabel = ttk.Label(windLabelFrame, text="Dynamic Wind",padding=4)
        dynamicCheckBox = ttk.Checkbutton(windLabelFrame,variable=self.windDynamic,onvalue=1,offvalue=0,padding=4)
        self.windDynamicTrace = self.windDynamic.trace_add(mode="write", callback=(lambda *args: self.UIMaster.castJson.Save(source=JsonSource.COMMON,newEntry={"windDynamic" : self.windDynamic.get()})))

        atmosphereLabelframe.grid(column="0",row="1",sticky="NEW",pady=5)
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
                "StringVar": self.UIMaster.system,
                "settingName": "Weapon System",
                "traceName": self.UIMaster.systemTrace,
                "entryLabel": None
            }
        }


    def CancelSettingChange(self,StrVar: StringVar,label: Widget, stringvar = ""):
        StrVar.set(" ")
        self.UIMaster.BoldenLabel(label,type="Normal",strVarName=stringvar)
        self.UIMaster.boldLabels[stringvar] = False
        self.UIMaster.SyncUpdate(JsonSource.COMMON)

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
                self.UIMaster.castJson.Save(source=JsonSource.COMMON,newEntry={"airTemperature" : float(self.airTemperature.get())})
            else:
                self.UIMaster.castJson.Save(source=JsonSource.COMMON,newEntry={"airTemperature" : 0.0})
        except Exception as e: self.UIMaster.StatusMessageErrorDump(e,"Failed to validate the temperature entry")
        self.UIMaster.BoldenLabel(self.airTemperatureLabel,type="Normal",strVarName="airTemperature")
        self.UIMaster.boldLabels["airTemperature"] = False
    
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
                self.UIMaster.castJson.Save(source=JsonSource.COMMON,newEntry={"airHumidity" : float(self.airHumidity.get())})
            else:
                self.UIMaster.castJson.Save(source=JsonSource.COMMON,newEntry={"airHumidity" : 0.0})
        except Exception as e: self.UIMaster.StatusMessageErrorDump(e,"Failed to validate the humidity entry")
        self.UIMaster.BoldenLabel(self.airHumidityLabel,"normal",strVarName="airHumidity")
        self.UIMaster.boldLabels["airHumidity"] = False

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
                self.UIMaster.castJson.Save(source=JsonSource.COMMON,newEntry={"airPressure" : float(self.airPressure.get())})
            else:
                self.UIMaster.castJson.Save(source=JsonSource.COMMON,newEntry={"airPressure" : float(0.0)})
        except Exception as e: self.UIMaster.StatusMessageErrorDump(e,"Failed to validate the pressure entry")
        self.UIMaster.BoldenLabel(self.airPressureLabel,strVarName="airPressure")
        self.UIMaster.boldLabels["airPressure"] = False

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
                self.UIMaster.castJson.Save(source=JsonSource.COMMON,newEntry={"windDirection" : float(self.windDirection.get())})
            else:
                self.UIMaster.castJson.Save(source=JsonSource.COMMON,newEntry={"windDirection" : 0.0})
        except Exception as e: self.UIMaster.StatusMessageErrorDump(e,"Failed to validate the wind direction entry")
        self.UIMaster.BoldenLabel(self.windDirectionLabel,strVarName="windDirection")
        self.UIMaster.boldLabels["windDirection"] = False

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
                self.UIMaster.castJson.Save(source=JsonSource.COMMON,newEntry={"windMagnitude" : float(self.windMagnitude.get())})
            else:
                self.UIMaster.castJson.Save(source=JsonSource.COMMON,newEntry={"windMagnitude" : 0.0})
        except Exception as e: self.UIMaster.StatusMessageErrorDump(e,"Failed to validate the wind magnitude entry")
        self.UIMaster.BoldenLabel(self.windMagnitudeLabel,strVarName="windMagnitude")
        self.UIMaster.boldLabels["windMagnitude"] = False

class Friendlies(UIComponentBase):
    def __init__(self, UIMaster):
        super().__init__(UIMaster)
        self.friendlyName = StringVar()
        self.friendlyPosX = StringVar()
        self.friendlyPosY = StringVar()
        self.friendlyHeight = StringVar()
        self.friendlyDispersion = StringVar()
    def Initialise(self,frame):
        friendlyLabelframe = ttk.Labelframe(frame,text="Friendly Position",height=200,width=500,padding=5,relief="groove")
        friendlyLabelframe.grid_rowconfigure((0,1,2,3),weight=1)
        friendlyLabelframe.grid_columnconfigure(0,weight=1,minsize="68")
        friendlyLabelframe.grid_columnconfigure(1,weight=5,minsize="20")
        friendlyLabelframe.grid_columnconfigure(2,minsize="10")
        friendlyLabelframe.grid_columnconfigure(3,weight=5,minsize="30")
        self.friendlyNameLabel = ttk.Label(friendlyLabelframe,text="Name:",justify="right",padding=4)
        self.friendlyNameCombobox = ttk.Combobox(friendlyLabelframe,justify="center",textvariable=self.friendlyName)
        self.friendlyNameCombobox.bind("<Return>",lambda event: self.UIMaster.LoadSelectionDetails(event, source=JsonSource.FRIENDLY))
        self.friendlyNameCombobox.bind("<Tab>",lambda event: self.UIMaster.LoadSelectionDetails(event, source=JsonSource.FRIENDLY))
        self.friendlyName.trace_add(mode="write", callback=lambda *args: self.UIMaster.BoldenLabel(self.friendlyNameLabel,"Bold","friendlyName"))
        friendlyPosLabel = ttk.Label(friendlyLabelframe,text="Position:",justify="right",padding=4)
        friendlyPosXEntry  = ttk.Entry(friendlyLabelframe, justify="center",textvariable=self.friendlyPosX)
        friendlyPosXEntry.bind("<Return>",lambda event: self.UIMaster.HeightAutoFill(event, self.friendlyPosX.get(),self.friendlyPosY.get(),self.friendlyHeight))
        friendlyPosXEntry.bind("<Tab>",lambda event: self.UIMaster.HeightAutoFill(event, self.friendlyPosX.get(),self.friendlyPosY.get(),self.friendlyHeight))
        friendlyPosYEntry  = ttk.Entry(friendlyLabelframe, justify="center",textvariable=self.friendlyPosY)
        friendlyPosYEntry.bind("<Return>",lambda event: self.UIMaster.HeightAutoFill(event, self.friendlyPosX.get(),self.friendlyPosY.get(),self.friendlyHeight))
        friendlyPosYEntry.bind("<Tab>",lambda event: self.UIMaster.HeightAutoFill(event, self.friendlyPosX.get(),self.friendlyPosY.get(),self.friendlyHeight))
        friendlyHeightLabel = ttk.Label(friendlyLabelframe,text="Height:",justify="right",padding=4)
        friendlyHeightEntry = ttk.Entry(friendlyLabelframe, justify="center",textvariable=self.friendlyHeight)
        friendlyHeightUnitLabel = ttk.Label(friendlyLabelframe,text="m")
        friendlyDispersionLabel = ttk.Label(friendlyLabelframe,text="Dispersion:",justify="right",padding=4)
        friendlyDispersionEntry = ttk.Entry(friendlyLabelframe, justify="center",textvariable=self.friendlyDispersion)
        friendlyDispersionUnitLabel = ttk.Label(friendlyLabelframe,text="m")
        friendlyAddButton = ttk.Button(friendlyLabelframe,text="Add/Update",command=self.FriendlyAddUpdate)
        friendlyRemoveButton = ttk.Button(friendlyLabelframe,text="Remove",command=lambda: self.FriendlyRemove(name=self.friendlyName.get()))
        friendlyLabelframe.grid(column="0",row="0",sticky="NEW")
        self.friendlyNameLabel.grid(column="0",row="0",sticky="NE")
        self.friendlyNameCombobox.grid(column="1",row="0",columnspan=3,sticky="NEW")
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
    def SyncFriendlies(self,friendlies):
        try: self.friendlyNameCombobox["values"] = list(friendlies)
        except KeyError: pass
        except Exception as e: self.UIMaster.StatusMessageErrorDump(e, errorMessage="Failed to Load friendlies from JSON")
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
                try: self.UIMaster.castJson.Load(source=JsonSource.FRIENDLY)[self.friendlyName.get()]
                except KeyError: update = False
                except Exception as e:
                    self.UIMaster.StatusMessageErrorDump(e,"Error searching for the friendly position in json")
                    update = False
                else: update = False
                self.UIMaster.castJson.Save(source=JsonSource.FRIENDLY,newEntry=newPos)
                self.UIMaster.SyncUpdate(JsonSource.FRIENDLY)
                if update: self.UIMaster.StatusMessageLog(message=f"{self.friendlyName.get()} has been updated, position {newPos[self.friendlyName.get()]['GridX']}, {newPos[self.friendlyName.get()]['GridY']} at {newPos[self.friendlyName.get()]['Height']} m")
                else: self.UIMaster.StatusMessageLog(message=f"{self.friendlyName.get()} has been added at position {newPos[self.friendlyName.get()]['GridX']}, {newPos[self.friendlyName.get()]['GridY']} at {newPos[self.friendlyName.get()]['Height']} m")
                self.UIMaster.boldLabels["friendlyName"] = False
        except Exception as e: self.UIMaster.StatusMessageErrorDump(e,"Failed to Add/Update Friendly position")
    def FriendlyRemove(self,name:str,*args):
        if name!= "":
            try:
                self.UIMaster.castJson.Delete(source=JsonSource.FRIENDLY,deleteKey=name)
                self.UIMaster.SyncUpdate(JsonSource.FRIENDLY)
            except Exception as e:
                self.UIMaster.StatusMessageErrorDump(e,errorMessage=f"Failed to delete {name}")
                return
            else:
                self.UIMaster.StatusMessageLog(message=f"{name} has been deleted")
                try:
                    self.UIMaster.BoldenLabel(self.friendlyNameLabel,"Normal","friendlyName")
                    self.UIMaster.boldLabels["friendlyName"] = False
                except: None

class TargetCreation(UIComponentBase):
    def __init__(self,UIMaster):
        super().__init__(UIMaster)
        # self.UIMaster = CastUI(UIMaster)
        self.xylrfpf = StringVar(value="0")
        self.targetReference = StringVar()
        self.targetPosX = StringVar()
        self.targetPosY = StringVar()
        self.targetHeight = StringVar()


    def Initialise(self,frame,mapWindow = False,targetType : Literal["FPF","XY","LR"] | None = None):
        targetInputLabelFrame = ttk.Labelframe(frame,text="Create Target",height=200,width=500,padding=5,relief="groove")
        targetInputLabelFrame.grid_rowconfigure(0,weight=1)
        targetInputLabelFrame.grid_columnconfigure(0,weight=1)
        targetInputFrame = ttk.Frame(targetInputLabelFrame)
        targetInputFrame.grid_columnconfigure(0,minsize=30,weight=1)
        targetInputFrame.grid_columnconfigure(1,minsize=30,weight=2)
        targetInputFrame.grid_columnconfigure(2,minsize=10,weight=2)
        targetInputFrame.grid_columnconfigure(3,minsize=6)
        targetInputFrame.grid_columnconfigure(4,minsize=34,weight=4)
        if mapWindow:
            targetInputFrame.grid_rowconfigure((0,1,2,3),weight=1)
            targetInputTargetType = ttk.Label(targetInputFrame,text=f"{targetType} -",padding=3)
            targetInputTargetType.grid(column=0,row=0,sticky="E")
        else:
            targetInputFrame.grid_rowconfigure((0,1,2,3,4,5),weight=1)
            targetInputXYRadio = ttk.Radiobutton(targetInputFrame,text="LR - ",variable=self.xylrfpf,value="0")
            targetInputLRRadio = ttk.Radiobutton(targetInputFrame,text="XY - ",variable=self.xylrfpf,value="1")
            targetInputFPFRadio = ttk.Radiobutton(targetInputFrame,text="FPF- ",variable=self.xylrfpf,value="2")
            targetInputXYRadio.grid(column="0",row="0",sticky="E")
            targetInputLRRadio.grid(column="0",row="1",sticky="E")
            targetInputFPFRadio.grid(column="0",row="2",sticky="E")
            self.xylrfpf.trace_add(mode="write",callback=lambda *args: self.UIMaster.targetDetail.TargetXYLRFPFChange())
        if mapWindow:
            targetInputReferenceEntry = ttk.Entry(targetInputFrame,width=3,textvariable=self.targetReference)
            targetInputReferenceEntry.grid(column="1",row="0",rowspan=3,columnspan=2,sticky="NW")
        else:
            self.targetInputReferenceEntry = ttk.Entry(targetInputFrame,width=3,textvariable=self.targetReference)
            self.targetInputReferenceEntry.grid(column="1",row="0",rowspan=3,columnspan=2,sticky="NW")
        targetInputAddSeparator = ttk.Separator(targetInputFrame,orient="vertical")
        targetInputSeparator = ttk.Separator(targetInputFrame,orient="horizontal")
        targetInputGridLabel = ttk.Label(targetInputFrame,text="Position:",padding=4)
        targetInputGridXEntry = ttk.Entry(targetInputFrame,justify="center",width=5,textvariable=self.targetPosX)
        targetInputGridXEntry.bind("<Return>",lambda event: self.UIMaster.HeightAutoFill(event,self.targetPosX.get(),self.targetPosY.get(),self.targetHeight))
        targetInputGridXEntry.bind("<Tab>",lambda event: self.UIMaster.HeightAutoFill(event,self.targetPosX.get(),self.targetPosY.get(),self.targetHeight))
        targetInputGridYEntry = ttk.Entry(targetInputFrame,justify="center",width=5,textvariable=self.targetPosY)
        targetInputGridYEntry.bind("<Return>",lambda event: self.UIMaster.HeightAutoFill(event,self.targetPosX.get(),self.targetPosY.get(),self.targetHeight))
        targetInputGridYEntry.bind("<Tab>",lambda event: self.UIMaster.HeightAutoFill(event,self.targetPosX.get(),self.targetPosY.get(),self.targetHeight))
        targetInputHeightLabel = ttk.Label(targetInputFrame,justify="right",text="Height:",padding=4)
        targetInputHeightEntry = ttk.Entry(targetInputFrame,width=5,justify="center",textvariable=self.targetHeight)
        targetInputHeightUnitLabel = ttk.Label(targetInputFrame,justify="left",text="m")
        targetInputReferenceAdd = ttk.Button(targetInputFrame,text="Add",command=lambda *args: self.TargetAdd())
        windowRowAdjustment = 0 if mapWindow else 2
        targetInputLabelFrame.grid(column="0",row="0",sticky="NEW")
        targetInputFrame.grid(column="0",row="0",sticky="NEW")
        targetInputAddSeparator.grid(column="3",row="0",rowspan=str(1+windowRowAdjustment),sticky="NESW")
        targetInputReferenceAdd.grid(column="4",row="0",rowspan=str(1+windowRowAdjustment),sticky="EW")
        targetInputSeparator.grid(column="0",row=str(windowRowAdjustment+1),columnspan=5,sticky="EW")
        targetInputGridLabel.grid(column="0",row=str(windowRowAdjustment+2),sticky="E")
        targetInputGridXEntry.grid(column="1",row=str(windowRowAdjustment+2),columnspan=2,sticky="NEW")
        targetInputGridYEntry.grid(column="3",row=str(windowRowAdjustment+2),columnspan=2,sticky="NEW")
        targetInputHeightLabel.grid(column="0",row=str(windowRowAdjustment+3),sticky="E")
        targetInputHeightEntry.grid(column="1",row=str(windowRowAdjustment+3),sticky="EW")
        targetInputHeightUnitLabel.grid(column="2",row=str(windowRowAdjustment+3),sticky="W")
        if mapWindow:
            return (targetInputLabelFrame,
                    targetInputFrame,
                    targetInputTargetType,
                    targetInputReferenceEntry,
                    targetInputAddSeparator,
                    targetInputReferenceAdd,
                    targetInputSeparator,
                    targetInputGridLabel,
                    targetInputGridXEntry,
                    targetInputGridYEntry,
                    targetInputHeightLabel,
                    targetInputHeightEntry,
                    targetInputHeightUnitLabel)

    def NextTargetInSeq(self,target):
        if str(target)[1:].isdigit():
            if str(target)[1:] == "9":
                nextTarget = str(target)[:-1]+"A"
            else:
                nextTarget = str(target)[:-1]+str(int(target[1:])+1)
        elif str(target)[1:].isalpha():
            if str(target)[1:] == "Z":
                nextTarget = str(target)[:-1]
            else:
                nextTarget = str(target)[:-1]+chr(ord(str(target)[1:]) + 1)
        return nextTarget
    
    def TargetAdd(self, targetType : Literal["FPF","XY","LR"] | None = None):
        newItem = self.targetReference.get().strip()
        if len(newItem)==2 or len(newItem)==3:
            if targetType is None:
                if self.xylrfpf.get() == "0":
                    prefix = "LR"
                elif self.xylrfpf.get() == "1":
                    prefix = "XY"
                elif self.xylrfpf.get() == "2":
                    prefix = "FPF"
            else:
                prefix = targetType
            if newItem and newItem not in self.UIMaster.target.targetListCheckBoxStates[prefix]:
                self.UIMaster.target.targetListCheckBoxStates[prefix][newItem] = (BooleanVar(),BooleanVar())
                sorted_items = self.UIMaster.target.SortFireMissions(self.UIMaster.target.targetListCheckBoxStates[prefix])
                if prefix == "LR":
                    self.UIMaster.target.CreateCheckBoxList(self.UIMaster.target.targetListLRCanvasFrame,{key: self.UIMaster.target.targetListCheckBoxStates[prefix][key] for key in sorted_items},self.UIMaster.target.targetSeriesDict[prefix])
                if prefix == "XY":
                    self.UIMaster.target.CreateCheckBoxList(self.UIMaster.target.targetListXYCanvasFrame,{key: self.UIMaster.target.targetListCheckBoxStates[prefix][key] for key in sorted_items},self.UIMaster.target.targetSeriesDict[prefix])    
                if prefix == "FPF":
                    self.UIMaster.target.CreateCheckBoxList(self.UIMaster.target.targetListFPFCanvasFrame,{key: self.UIMaster.target.targetListCheckBoxStates[prefix][key] for key in sorted_items},self.UIMaster.target.targetSeriesDict[prefix])
                prefixTargetList = {}
                try: prefixTargetList[prefix] = self.UIMaster.castJson.Load(source=JsonSource.TARGET)[prefix]
                except: prefixTargetList[prefix] = {}
                mutator = "None"
                orientation = "None"
                if self.UIMaster.targetDetail.fireMissionWidth.get() != "0" and self.UIMaster.targetDetail.fireMissionWidth.get() != "" and self.UIMaster.targetDetail.fireMissionDepth.get() != "0" and self.UIMaster.targetDetail.fireMissionDepth.get() != "":
                    try:
                        int(self.UIMaster.targetDetail.fireMissionWidth.get())
                        int(self.UIMaster.targetDetail.fireMissionDepth.get())
                        mutator = "Box"
                    except:
                        try: int(self.UIMaster.targetDetail.fireMissionWidth.get())
                        except ValueError: self.UIMaster.StatusMessageLog(message="Incorrect Width dispersion, defaulting to no diserpsion")
                        except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage="Incorrect Width dispersion, defaulting to no diserpsion")
                        try: int(self.UIMaster.targetDetail.fireMissionDepth.get())
                        except ValueError: self.UIMaster.StatusMessageLog(message="Incorrect Depth dispersion, defaulting to no diserpsion")
                        except Exception as e: self.UIMasterStatusMessageErrorDump(e,errorMessage="Incorrect Depth dispersion, defaulting to no diserpsion")
                elif self.UIMaster.targetDetail.fireMissionDepth.get() != "0" and self.UIMaster.targetDetail.fireMissionDepth.get() != "":
                    try:
                        int(self.UIMaster.targetDetail.fireMissionDepth.get())
                        mutator = "Line"
                        orientation = "Vertical"
                    except ValueError: self.UIMaster.StatusMessageLog(message="Incorrect Depth dispersion, defaulting to no diserpsion")
                    except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage="Incorrect Depth dispersion, defaulting to no diserpsion")
                elif self.UIMaster.targetDetail.fireMissionWidth.get() != "0" and self.UIMaster.targetDetail.fireMissionWidth.get() != "":
                    try:
                        int(self.UIMaster.targetDetail.fireMissionWidth.get())
                        mutator = "Line"
                        orientation = "Horizontal"
                    except ValueError: self.UIMaster.StatusMessageLog(message="Incorrect Width dispersion, defaulting to no diserpsion")
                    except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage="Incorrect Width dispersion, defaulting to no diserpsion")
                prefixTargetList[prefix][newItem]= {
                    "GridX" : self.targetPosX.get(),
                    "GridY" : self.targetPosY.get(),
                    "Height" : float(self.targetHeight.get()),
                    "Effect" : self.UIMaster.targetDetail.fireMissionEffect.get(),
                    "Width" : int(self.UIMaster.targetDetail.fireMissionWidth.get())/2,
                    "Depth" : int(self.UIMaster.targetDetail.fireMissionDepth.get())/2,
                    "Length" : self.UIMaster.targetDetail.fireMissionLength.get(),
                    "Condition" : self.UIMaster.targetDetail.fireMissionCondition.get(),
                    "Mutator" : mutator,
                    "Orientation" : orientation,
                    "Time" : {"Hour" : int(self.UIMaster.targetDetail.fireMissionHour.get()),
                            "Minute" : int(self.UIMaster.targetDetail.fireMissionMinute.get()),
                            "Second" : int(self.UIMaster.targetDetail.fireMissionSecond.get())}
                }
                self.UIMaster.castJson.Save(source=JsonSource.TARGET,newEntry=prefixTargetList)
                self.UIMaster.StatusMessageLog(message=f"Added New Fire mission {prefix}-{newItem}, Position: {self.targetPosX.get()} {self.targetPosY.get()}, Height: {self.targetHeight.get()}")
                try: nextTarget = self.NextTargetInSeq(newItem)
                except: nextTarget = newItem
                self.targetReference.set(nextTarget)
                if prefix == "LR":
                    self.UIMaster.target.updateTargetListScrollregion(self.UIMaster.target.targetListLRCanvasFrame,self.UIMaster.target.targetListLRCanvas) 
                elif prefix == "XY":       
                    self.UIMaster.target.updateTargetListScrollregion(self.UIMaster.target.targetListXYCanvasFrame,self.UIMaster.target.targetListXYCanvas) 
                elif prefix =="FPF":
                    self.UIMaster.target.updateTargetListScrollregion(self.UIMaster.target.targetListFPFCanvasFrame,self.UIMaster.target.targetListFPFCanvas) 

class TargetDetails(UIComponentBase):
    def __init__(self, UIMaster):
        super().__init__(UIMaster)
        # self.UIMaster = CastUI(UIMaster)
        self.fireMissionGroupSelectionReverse = False
        self.fireMissionEffect = StringVar(value="Destroy")
        self.previousMissionEffect = "Destroy"
        self.fireMissionWidth = StringVar(value="0")
        self.fireMissionDepth = StringVar(value="0")
        self.fireMissionLength = StringVar(value="Fig 1")
        self.lengthTrace = ""
        self.fireMissionCondition = StringVar(value="FWR")
        self.conditionTrace = ""
        self.fireMissionHour = StringVar(value=datetime.now().strftime("%H"))
        self.fireMissionMinute = StringVar(value=datetime.now().strftime("%M"))
        self.fireMissionSecond = StringVar(value=datetime.now().strftime("%S"))
        self.fireMissionGroupEffect = StringVar(value="Line")
        self.fireMissionGroupSpacing = StringVar(value="30")
        self.fireMissionGroupWidth = StringVar(value="150")
        self.xylrfpfPositionDict = {
            "0" : "NW",
            "1" : "W",
            "2" : "SW"
        }
    def Initialise(self,frame,mapWindow = False, targetType: Literal['FPF', 'XY', 'LR'] | None = None):
        if mapWindow:
            fireMissionSelectionLabelframe = ttk.Labelframe(frame,text="Fire Mission Selection",height=200,width=500,padding=5,relief="groove")
            fireMissionSelectionLabelframe.grid_columnconfigure((0,1,2,3),minsize=70,weight=1)
            fireMissionSelectionLabelframe.grid_rowconfigure((0,1,2,3),weight=1)
            fireMissionSelectionLabelframe.grid(column="0",row="0",sticky="NEW")
            fireMissionSelectionEffectLabelframe = ttk.Labelframe(fireMissionSelectionLabelframe,text="Effect",relief="groove")
        else:
            self.fireMissionSelectionLabelframe = ttk.Labelframe(frame,text="Fire Mission Selection",height=200,width=500,padding=5,relief="groove")
            self.fireMissionSelectionLabelframe.grid_columnconfigure((0,1,2,3),minsize=70,weight=1)
            self.fireMissionSelectionLabelframe.grid_rowconfigure((0,1,2,3),weight=1)
            self.fireMissionSelectionLabelframe.grid(column="0",row="0",sticky="NEW")
            fireMissionSelectionEffectLabelframe = ttk.Labelframe(self.fireMissionSelectionLabelframe,text="Effect",relief="groove")
        fireMissionSelectionEffectLabelframe.grid_columnconfigure(0,weight=5)
        fireMissionSelectionEffectLabelframe.grid_rowconfigure((0,1,2,3,4,5,6,7),weight=1)
        if mapWindow:
            if targetType == "FPF":
                self.dummyStringVar = StringVar(value="dummy")
                fireMissionSelectionEffectFPFRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="FPF",variable=self.dummyStringVar,value="dummy")
                fireMissionSelectionEffectFPFRadio.grid(column="1",row="0",rowspan="7",sticky="EW",padx=4)
            else:
                self.fireMissionEffect.set(self.previousMissionEffect)
                fireMissionSelectionEffectDestroyRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Destroy",variable=self.fireMissionEffect,value="Destroy")
                fireMissionSelectionEffectNeutraliseRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Neutralise",variable=self.fireMissionEffect,value="Neutralise")
                fireMissionSelectionEffectCheckRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Check",variable=self.fireMissionEffect,value="Checkround")
                fireMissionSelectionEffectSaturationRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Saturation",variable=self.fireMissionEffect,value="Saturate")
                fireMissionSelectionEffectAreaDenialRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Area Denial",variable=self.fireMissionEffect,value="Area_Denial")
                fireMissionSelectionEffectSmokeRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Smoke",variable=self.fireMissionEffect,value="Smoke")
                fireMissionSelectionEffectIllumRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Illum",variable=self.fireMissionEffect,value="Illum")
                fireMissionSelectionEffectDestroyRadio.grid(column="1",row="0",sticky="EW",padx=4)
                fireMissionSelectionEffectNeutraliseRadio.grid(column="1",row="1",sticky="EW",padx=4)
                fireMissionSelectionEffectCheckRadio.grid(column="1",row="2",sticky="EW",padx=4)
                fireMissionSelectionEffectSaturationRadio.grid(column="1",row="3",sticky="EW",padx=4)
                fireMissionSelectionEffectAreaDenialRadio.grid(column="1",row="5",sticky="EW",padx=4)
                fireMissionSelectionEffectSmokeRadio.grid(column="1",row="6",sticky="EW",padx=4)
                fireMissionSelectionEffectIllumRadio.grid(column="1",row="7",sticky="EW",padx=4)
        else:
            self.fireMissionSelectionEffectDestroyRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Destroy",variable=self.fireMissionEffect,value="Destroy")
            self.fireMissionSelectionEffectNeutraliseRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Neutralise",variable=self.fireMissionEffect,value="Neutralise")
            self.fireMissionSelectionEffectCheckRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Check",variable=self.fireMissionEffect,value="Checkround")
            self.fireMissionSelectionEffectSaturationRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Saturation",variable=self.fireMissionEffect,value="Saturate")
            self.fireMissionSelectionEffectFPFRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="FPF",variable=self.fireMissionEffect,value="FPF")
            self.fireMissionSelectionEffectAreaDenialRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Area Denial",variable=self.fireMissionEffect,value="Area_Denial")
            self.fireMissionSelectionEffectSmokeRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Smoke",variable=self.fireMissionEffect,value="Smoke")
            self.fireMissionSelectionEffectIllumRadio = ttk.Radiobutton(fireMissionSelectionEffectLabelframe,text="Illum",variable=self.fireMissionEffect,value="Illum")
            self.fireMissionEffect.trace_add(mode="write",callback=self.FireMissionEffectChange)
            self.fireMissionSelectionUpdateMission = ttk.Button(self.fireMissionSelectionLabelframe,text="Update",command=lambda: self.FireMissionEffectUpdate())
            self.fireMissionSelectionEffectFPFRadio.grid(column="1",row="0",rowspan="7",sticky="EW",padx=4)
            self.fireMissionSelectionEffectFPFRadio.grid_remove()
            self.fireMissionSelectionEffectDestroyRadio.grid(column="1",row="0",sticky="EW",padx=4)
            self.fireMissionSelectionEffectNeutraliseRadio.grid(column="1",row="1",sticky="EW",padx=4)
            self.fireMissionSelectionEffectCheckRadio.grid(column="1",row="2",sticky="EW",padx=4)
            self.fireMissionSelectionEffectSaturationRadio.grid(column="1",row="3",sticky="EW",padx=4)
            self.fireMissionSelectionEffectAreaDenialRadio.grid(column="1",row="5",sticky="EW",padx=4)
            self.fireMissionSelectionEffectSmokeRadio.grid(column="1",row="6",sticky="EW",padx=4)
            self.fireMissionSelectionEffectIllumRadio.grid(column="1",row="7",sticky="EW",padx=4)
            self.fireMissionSelectionUpdateMission.grid(column="0",row="2",sticky="NESW",padx=4)
            self.fireMissionSelectionUpdateMission.grid_remove()
        if mapWindow:
            fireMissionSelectionDispersionLabelframe = ttk.Labelframe(fireMissionSelectionLabelframe,text="Dispersion",padding=4)
        else:
            fireMissionSelectionDispersionLabelframe = ttk.Labelframe(self.fireMissionSelectionLabelframe,text="Dispersion",padding=4)
        fireMissionSelectionDispersionLabelframe.grid_columnconfigure(0,weight=1,minsize=30)
        fireMissionSelectionDispersionLabelframe.grid_columnconfigure(1)
        fireMissionSelectionDispersionLabelframe.grid_rowconfigure(0,weight=1)
        fireMissionSelectionWidthLabel = ttk.Label(fireMissionSelectionDispersionLabelframe,text="Wid",padding=4,justify="right")
        fireMissionSelectionDepthLabel = ttk.Label(fireMissionSelectionDispersionLabelframe,text="Dep",padding=4,justify="right")
        fireMissionSelectionWidthCombobox = ttk.Combobox(fireMissionSelectionDispersionLabelframe,textvariable=self.fireMissionWidth,justify="right",width=4,values=("0","10","20","40","50","100","150","200","250"))
        fireMissionSelectionDepthCombobox = ttk.Combobox(fireMissionSelectionDispersionLabelframe,textvariable=self.fireMissionDepth,justify="right",width=4,values=("0","10","20","40","50","100","150","200","250"))
        fireMissionSelectionWidthUnitLabel = ttk.Label(fireMissionSelectionDispersionLabelframe,text="m",padding=4,justify="left")
        fireMissionSelectionDepthUnitLabel = ttk.Label(fireMissionSelectionDispersionLabelframe,text="m",padding=4,justify="left")
        if mapWindow:
            fireMissionSelectionLengthLabelframe = ttk.Labelframe(fireMissionSelectionLabelframe,text="Length",padding=4)
        else:
            fireMissionSelectionLengthLabelframe = ttk.Labelframe(self.fireMissionSelectionLabelframe,text="Length",padding=4)
        fireMissionSelectionLengthLabelframe.grid_columnconfigure(0,weight=1,minsize=30)
        fireMissionSelectionLengthLabelframe.grid_columnconfigure(1)
        fireMissionSelectionLengthLabelframe.grid_rowconfigure(0,weight=1)
        fireMissionSelectionLengthCombobox = ttk.Combobox(fireMissionSelectionLengthLabelframe,width=5,textvariable=self.fireMissionLength,justify="right",values=("30","Fig 1","90","Fig 2","Fig 3","Fig 4"))
        
        fireMissionSelectionLengthUnitLabel = ttk.Label(fireMissionSelectionLengthLabelframe,text=" ",padding=4,justify="left")
        lengthTrace = self.fireMissionLength.trace_add(mode="write",callback=lambda *args, l = fireMissionSelectionLengthUnitLabel: self.FireMissionLengthChange(l))
        if mapWindow:
            fireMissionSelectionConditionLabelframe = ttk.Labelframe(fireMissionSelectionLabelframe,text="Condition",padding=4)       
        else:
            self.lengthTrace = lengthTrace
            fireMissionSelectionConditionLabelframe = ttk.Labelframe(self.fireMissionSelectionLabelframe,text="Condition",padding=4)
        fireMissionSelectionConditionLabelframe.grid_columnconfigure(0,weight=1)
        fireMissionSelectionConditionLabelframe.grid_rowconfigure(0,weight=1)
        fireMissionSelectionConditionCombobox = ttk.Combobox(fireMissionSelectionConditionLabelframe,textvariable=self.fireMissionCondition,values=("FWR","Time"),width=10,justify="center")
        if mapWindow:
            fireMissionSelectionTimeLabelframe = ttk.Labelframe(fireMissionSelectionLabelframe,text="Time",padding=4)
        else:
            fireMissionSelectionTimeLabelframe = ttk.Labelframe(self.fireMissionSelectionLabelframe,text="Time",padding=4)
        conditionTrace = self.fireMissionCondition.trace_add(mode="write",callback=lambda *args, timeLabelFrame = fireMissionSelectionTimeLabelframe:self.FireMissionConditionChange(timeLabelFrame))            
        fireMissionSelectionTimeLabelframe.grid_columnconfigure((0,2,4),minsize=20,weight=1)
        fireMissionSelectionTimeLabelframe.grid_rowconfigure(0,weight=1)
        fireMissionSelectionTimeHoursEntry = ttk.Entry(fireMissionSelectionTimeLabelframe,width=2,textvariable=self.fireMissionHour,justify="center")
        fireMissionSelectionTimeColonLabel1 = ttk.Label(fireMissionSelectionTimeLabelframe,text=" : ")
        fireMissionSelectionTimeMinutesEntry = ttk.Entry(fireMissionSelectionTimeLabelframe,width=2,textvariable=self.fireMissionMinute,justify="center")
        fireMissionSelectionTimeColonLabel2 = ttk.Label(fireMissionSelectionTimeLabelframe,text=" : ")
        fireMissionSelectionTimeSecondsEntry = ttk.Entry(fireMissionSelectionTimeLabelframe,width=2,textvariable=self.fireMissionSecond,justify="center")
        if mapWindow == False:
            self.conditionTrace = conditionTrace
            self.fireMissionGroupSelectionLabelframe = ttk.Labelframe(frame,text="Grouped Fire Mission Selection",padding=3)
            self.fireMissionGroupSelectionLabelframe.grid_columnconfigure((0,1,2,3),weight=1)
            self.fireMissionGroupSelectionLabelframe.grid_rowconfigure((0,1,2,3),weight=1)
            fireMissionGroupSelectionTargetFrame = ttk.Frame(self.fireMissionGroupSelectionLabelframe,padding=3,relief="raised")
            fireMissionGroupSelectionTargetFrame.bind("<Button-3>",self.ReverseFireMissionGroupSelections)
            fireMissionGroupSelection1Label = ttk.Label(fireMissionGroupSelectionTargetFrame,text="Target 1 : ")
            fireMissionGroupSelection2Label = ttk.Label(fireMissionGroupSelectionTargetFrame,text="Target 2 : ")
            self.fireMissionGroupSelection1NameLabel = ttk.Label(fireMissionGroupSelectionTargetFrame)
            self.fireMissionGroupSelection2NameLabel = ttk.Label(fireMissionGroupSelectionTargetFrame)
            fireMissionGroupSelection1Label.bind("<Button-3>",self.ReverseFireMissionGroupSelections)
            fireMissionGroupSelection2Label.bind("<Button-3>",self.ReverseFireMissionGroupSelections)
            self.fireMissionGroupSelection1NameLabel.bind("<Button-3>",self.ReverseFireMissionGroupSelections)
            self.fireMissionGroupSelection2NameLabel.bind("<Button-3>",self.ReverseFireMissionGroupSelections)
            fireMissionGroupSelectionReverseButton = ttk.Button(self.fireMissionGroupSelectionLabelframe,text="Reverse\n Targets",command=lambda: self.ReverseFireMissionGroupSelections())
            fireMissionGroupSelectionAddButton = ttk.Button(self.fireMissionGroupSelectionLabelframe,text="Add\nGroup",command=lambda:self.AddGroupMission())
            fireMissionGroupSelectionEffectLabelFrame = ttk.LabelFrame(self.fireMissionGroupSelectionLabelframe,text="Group Effect",relief="groove",padding=3)
            fireMissionGroupSelectionEffectLine = ttk.Radiobutton(fireMissionGroupSelectionEffectLabelFrame,text="Line",variable=self.fireMissionGroupEffect,value="Line")
            fireMissionGroupSelectionEffectExplicitLine = ttk.Radiobutton(fireMissionGroupSelectionEffectLabelFrame,text="Explicit Line",variable=self.fireMissionGroupEffect,value="Explicit Line")
            fireMissionGroupSelectionEffectCreepingBarrage = ttk.Radiobutton(fireMissionGroupSelectionEffectLabelFrame,text="Creeping Barrage",variable=self.fireMissionGroupEffect,value="Creeping Barrage")
            self.fireMissionGroupEffect.trace_add(mode="write",callback=lambda *args: self.FireMissionGroupEffectChange())
            fireMissionGroupSelectionDispersionLabelframe = ttk.Labelframe(self.fireMissionGroupSelectionLabelframe,text="Dispersion",padding=3)
            fireMissionGroupSelectionDispersionLabelframe.grid_columnconfigure(0,weight=1)
            fireMissionGroupSelectionDispersionLabelframe.grid_columnconfigure(1,minsize=20)
            fireMissionGroupSelectionDispersionLabelframe.grid_columnconfigure(2,minsize=9)
            fireMissionGroupSelectionDispersionLabelframe.grid_rowconfigure((0,1),weight=1)
            fireMissionGroupSelectionDispersionSpacingLabel = ttk.Label(fireMissionGroupSelectionDispersionLabelframe,text="Spacing")
            fireMissionGroupSelectionDispersionSpacingCombobox = ttk.Combobox(fireMissionGroupSelectionDispersionLabelframe,justify="center",width=5,textvariable=self.fireMissionGroupSpacing,values=("10","20","30","40","50","60","70","80","90","100"))
            fireMissionGroupSelectionDispersionSpacingUnitLabel = ttk.Label(fireMissionGroupSelectionDispersionLabelframe,text="m")
            self.fireMissionGroupSelectionDispersionWidthLabel = ttk.Label(fireMissionGroupSelectionDispersionLabelframe,text="Width")
            self.fireMissionGroupSelectionDispersionWidthCombobox = ttk.Combobox(fireMissionGroupSelectionDispersionLabelframe,justify="center",width=5,textvariable=self.fireMissionGroupWidth,values=("100","150","200","250","300","350","400"))
            self.fireMissionGroupSelectionDispersionWidthUnitLabel = ttk.Label(fireMissionGroupSelectionDispersionLabelframe,text="m")

        
        fireMissionSelectionEffectLabelframe.grid(column="0",row="0",rowspan=2,sticky="NEW",padx=4)
        
        fireMissionSelectionDispersionLabelframe.grid(column="1",row="0",sticky="NEW",padx=4)
        fireMissionSelectionWidthLabel.grid(column="0",row="0",sticky="NEW")
        fireMissionSelectionDepthLabel.grid(column="0",row="1",sticky="NEW")
        fireMissionSelectionWidthCombobox.grid(column="1",row="0",sticky="NEW")
        fireMissionSelectionDepthCombobox.grid(column="1",row="1",sticky="NEW")
        fireMissionSelectionWidthUnitLabel.grid(column="2",row="0",sticky="NW")
        fireMissionSelectionDepthUnitLabel.grid(column="2",row="1",sticky="NW")
        fireMissionSelectionLengthLabelframe.grid(column="2",row="0",sticky="NEW",padx=4)
        fireMissionSelectionLengthCombobox.grid(column="0",row="0",sticky="NEW")
        fireMissionSelectionLengthUnitLabel.grid(column="1",row="0",sticky="NW")
        fireMissionSelectionConditionLabelframe.grid(column="3",row="0",sticky="NEW",padx=4)
        fireMissionSelectionConditionCombobox.grid(column="0",row="0",sticky="NEW")
        fireMissionSelectionTimeLabelframe.grid(column="2",row="1",columnspan=2,sticky="NEW",padx=4)
        fireMissionSelectionTimeHoursEntry.grid(column="0",row="0",sticky="NEW")
        fireMissionSelectionTimeColonLabel1.grid(column="1",row="0",sticky="NEW")
        fireMissionSelectionTimeMinutesEntry.grid(column="2",row="0",sticky="NEW")
        fireMissionSelectionTimeColonLabel2.grid(column="3",row="0",sticky="NEW")
        fireMissionSelectionTimeSecondsEntry.grid(column="4",row="0",sticky="NEW")
        fireMissionSelectionTimeLabelframe.grid_remove()
        if mapWindow == False:
            self.fireMissionGroupSelectionLabelframe.grid(column="0",row="1",sticky="NW")
            fireMissionGroupSelectionTargetFrame.grid(column="0",row="0",rowspan="3",sticky="NESW",padx=4)
            fireMissionGroupSelection1Label.grid(column="0",row="0",sticky="NW")
            fireMissionGroupSelection2Label.grid(column="0",row="1",sticky="NW")
            self.fireMissionGroupSelection1NameLabel.grid(column="1",row="0",sticky="NW")
            self.fireMissionGroupSelection2NameLabel.grid(column="1",row="1",sticky="NW")
            self.fireMissionGroupSelectionLabelframe.grid_remove()
            fireMissionGroupSelectionReverseButton.grid(column="1",row="0",rowspan=3,sticky="NW",padx="3")
            fireMissionGroupSelectionAddButton.grid(column="2",row="0",rowspan=3,sticky="NW",padx="3")
            fireMissionGroupSelectionEffectLabelFrame.grid(column="0",row="3",sticky="NW",padx="3")
            fireMissionGroupSelectionEffectLine.grid(column="0",row="0",sticky="NW")
            fireMissionGroupSelectionEffectExplicitLine.grid(column="0",row="1",sticky="NW")
            fireMissionGroupSelectionEffectCreepingBarrage.grid(column="0",row="2",sticky="NW")
            fireMissionGroupSelectionDispersionLabelframe.grid(column="1",row="3",columnspan=2,sticky="NESW",padx="3")
            fireMissionGroupSelectionDispersionSpacingLabel.grid(column="0",row="0",sticky="NE")
            fireMissionGroupSelectionDispersionSpacingCombobox.grid(column="1",row="0",sticky="NEW",pady="3")
            fireMissionGroupSelectionDispersionSpacingUnitLabel.grid(column="2",row="0",sticky="NW")
            self.fireMissionGroupSelectionDispersionWidthLabel.grid(column="0",row="1",sticky="NE")
            self.fireMissionGroupSelectionDispersionWidthCombobox.grid(column="1",row="1",sticky="NEW",pady="3")
            self.fireMissionGroupSelectionDispersionWidthUnitLabel.grid(column="2",row="1",sticky="NW")
            self.fireMissionGroupSelectionDispersionWidthLabel.grid_remove()
            self.fireMissionGroupSelectionDispersionWidthCombobox.grid_remove()
            self.fireMissionGroupSelectionDispersionWidthUnitLabel.grid_remove()
        return (lengthTrace,conditionTrace)
    
    def TargetXYLRFPFChange(self,*args):
        def SetOriginalGrid():
            self.fireMissionSelectionEffectDestroyRadio.grid()
            self.fireMissionSelectionEffectNeutraliseRadio.grid()
            self.fireMissionSelectionEffectCheckRadio.grid()
            self.fireMissionSelectionEffectSaturationRadio.grid()
            self.fireMissionSelectionEffectAreaDenialRadio.grid()
            self.fireMissionSelectionEffectSmokeRadio.grid()
            self.fireMissionSelectionEffectIllumRadio.grid()
            self.fireMissionSelectionEffectFPFRadio.grid_remove()

        self.UIMaster.targetCreation.targetInputReferenceEntry.grid(sticky=self.xylrfpfPositionDict[self.UIMaster.targetCreation.xylrfpf.get()])
        if self.UIMaster.targetCreation.xylrfpf.get() == "0":
            self.UIMaster.targetDetail.fireMissionEffect.set(self.UIMaster.targetDetail.previousMissionEffect)
            SetOriginalGrid()
        elif self.UIMaster.targetCreation.xylrfpf.get() == "1":
            self.UIMaster.targetDetail.fireMissionEffect.set(self.UIMaster.targetDetail.previousMissionEffect)
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

    def ReverseFireMissionGroupSelections(self,event = None):
            def Reverse():
                if self.fireMissionGroupSelectionReverse:
                    self.fireMissionGroupSelectionReverse = False
                else:
                    self.fireMissionGroupSelectionReverse = True
                self.UIMaster.target.RequestEditFireMissions()
            if event != None:
                fireMissionGroupSelectionReverseMenu = Menu(self.UIMaster.root,tearoff=False)
                fireMissionGroupSelectionReverseMenu.add_command(label="Reverse targets",command=lambda: Reverse())
                fireMissionGroupSelectionReverseMenu.post(event.x_root,event.y_root)
            else: Reverse()
    def FireMissionEffectChange(self,*args):
        if self.fireMissionEffect.get() != "FPF" and self.UIMaster.targetCreation.xylrfpf.get() != "2":
            self.previousMissionEffect = self.fireMissionEffect.get()
    def FireMissionLengthChange(self,unitLabel : Label | None = None):
        try:
            if self.fireMissionLength.get().isnumeric()==True:
                unitLabel.config(text="s")
            else:
                unitLabel.config(text=" ")
        except: None
    def FireMissionConditionChange(self,labelFrame : LabelFrame | None = None):
        try:
            if self.fireMissionCondition.get() in ("Time","time"):
                if labelFrame is not None:
                    labelFrame.grid()
                else:
                    self.fireMissionSelectionTimeLabelframe.grid()
                self.fireMissionHour.set(datetime.now().strftime("%H"))
                self.fireMissionMinute.set(datetime.now().strftime("%M"))
                self.fireMissionSecond.set(datetime.now().strftime("%S"))
            else:
                if labelFrame is not None:
                    labelFrame.grid_remove()
                else:
                    self.fireMissionSelectionTimeLabelframe.grid_remove()
        except: None
    def FireMissionGroupEffectChange(self,*args):
        if self.fireMissionGroupEffect.get() == "Creeping Barrage":
            self.fireMissionGroupSelectionDispersionWidthLabel.grid()
            self.fireMissionGroupSelectionDispersionWidthCombobox.grid()
            self.fireMissionGroupSelectionDispersionWidthUnitLabel.grid()
        else:
            self.fireMissionGroupSelectionDispersionWidthLabel.grid_remove()
            self.fireMissionGroupSelectionDispersionWidthCombobox.grid_remove()
            self.fireMissionGroupSelectionDispersionWidthUnitLabel.grid_remove()
    def FireMissionEffectUpdate(self,*args):
        editedFireMission = ""
        def SaveSettings(prefix,target,targets,fireMissions):
            mutator = "None"
            orientation = "None"
            if self.fireMissionWidth.get() != "0" and self.fireMissionWidth.get() != "" and self.fireMissionDepth.get() != "0" and self.fireMissionDepth.get() != "":
                try:
                    int(self.fireMissionWidth.get())
                    int(self.fireMissionDepth.get())
                    mutator = "Box"
                except ValueError:
                    try: int(self.fireMissionWidth.get())
                    except: self.UIMaster.StatusMessageLog(message="Incorrect Width dispersion, defaulting to no diserpsion")
                    try: int(self.fireMissionDepth.get())
                    except: self.UIMaster.StatusMessageLog(message="Incorrect Depth dispersion, defaulting to no diserpsion")
                except Exception as e:
                    self.UIMaster.StatusMessageErrorDump(e,errorMessage="Failed to Update fire mission due to width/depth")
                    return
            elif self.fireMissionDepth.get() != "0" and self.fireMissionDepth.get() != "":
                try:
                    int(self.fireMissionDepth.get())
                    mutator = "Line"
                    orientation = "Vertical"
                except ValueError: self.UIMaster.StatusMessageLog(message="Incorrect Depth dispersion, defaulting to no diserpsion")
                except Exception as e:
                    self.UIMaster.StatusMessageErrorDump(e,errorMessage="Failed to Update fire mission due to depth")
                    return
            elif self.fireMissionWidth.get() != "0" and self.fireMissionWidth.get() != "":
                try:
                    int(self.fireMissionWidth.get())
                    mutator = "Line"
                    orientation = "Horizontal"
                except ValueError: self.UIMaster.StatusMessageLog(message="Incorrect Width dispersion, defaulting to no diserpsion")
                except Exception as e:
                    self.UIMaster.StatusMessageErrorDump(e,errorMessage="Failed to Update fire mission due to width/depth")
                    return
            changeFiremission = (int(float(targets[prefix][target]["Width"])*2) == int(self.fireMissionWidth.get()) and
                                int(float(targets[prefix][target]["Depth"])*2) == int(self.fireMissionDepth.get()))
            if changeFiremission: 
                for idfp,missions in list(fireMissions.items()):
                    if f"{prefix}-{target}" in missions.keys():
                        fireMissions[idfp][f"{prefix}-{target}"]["Effect"] = self.fireMissionEffect.get()
                        fireMissions[idfp][f"{prefix}-{target}"]["Length"] = self.fireMissionLength.get()
                        fireMissions[idfp][f"{prefix}-{target}"]["Condition"] = self.fireMissionCondition.get()
                        if self.fireMissionCondition.get() == "Time":
                            fireMissions[idfp][f"{prefix}-{target}"]["Time"] = {
                                "Hour": int(self.fireMissionHour.get()),
                                "Minute": int(self.fireMissionMinute.get()),
                                "Second": int(self.fireMissionSecond.get())
                                }
                        elif self.fireMissionCondition.get() != "Time":
                            fireMissions[idfp][f"{prefix}-{target}"].pop("Time",None)
            else:
                self.UIMaster.StatusMessageLog(message=f"{prefix}-{target} requires recalculation to change dispersion")
            targets[prefix][target]["Effect"] = self.fireMissionEffect.get()
            targets[prefix][target]["Width"] = int(self.fireMissionWidth.get())/2
            targets[prefix][target]["Depth"] = int(self.fireMissionDepth.get())/2
            targets[prefix][target]["Length"] = self.fireMissionLength.get()
            targets[prefix][target]["Condition"] = self.fireMissionCondition.get()
            targets[prefix][target]["Mutator"] = mutator
            targets[prefix][target]["Orientation"] = orientation
            targets[prefix][target]["Time"]["Hour"] = int(self.fireMissionHour.get())
            targets[prefix][target]["Time"]["Minute"] = int(self.fireMissionMinute.get())
            targets[prefix][target]["Time"]["Second"] = int(self.fireMissionSecond.get())
            return targets,fireMissions
            
        targets = self.UIMaster.castJson.Load(source=JsonSource.TARGET)
        fireMissions = self.UIMaster.castJson.Load(source=JsonSource.FIREMISSION)
        for target, (edit, calculate) in self.UIMaster.target.targetListCheckBoxStates["LR"].items():
            if edit.get() == True:
                targets,fireMissions = SaveSettings("LR",target,targets,fireMissions)
                editedFireMission += (str("LR")+"-"+str(target)+", ")

        for target, (edit, calculate) in self.UIMaster.target.targetListCheckBoxStates["XY"].items():
            if edit.get() == True:
                targets,fireMissions = SaveSettings("XY",target,targets,fireMissions)
                editedFireMission += (str("XY")+"-"+str(target)+", ")

        for target, (edit, calculate) in self.UIMaster.target.targetListCheckBoxStates["FPF"].items():
            if edit.get() == True:
                targets,fireMissions = SaveSettings("FPF",target,targets,fireMissions)
                editedFireMission += (str("FPF")+"-"+str(target)+", ")
        try:
            self.UIMaster.castJson.Save(source=JsonSource.TARGET,newEntry=targets)
            self.UIMaster.StatusMessageLog(message=f"Updated Targets {editedFireMission[:-2]}")
        except Exception as e:
            self.UIMaster.StatusMessageErrorDump(e, errorMessage="Failed to update targets")
        try:
            self.UIMaster.castJson.Save(source=JsonSource.FIREMISSION,newEntry=fireMissions)
            self.UIMaster.StatusMessageLog(message=f"Updated fire missions {editedFireMission[:-2]}")
        except Exception as e:
            self.UIMaster.StatusMessageErrorDump(e, errorMessage="Failed to update fire missions")
    
    def AddGroupMission(self):
        newItem = f"{self.fireMissionGroupSelection1NameLabel.cget('text')} | {self.fireMissionGroupSelection2NameLabel.cget('text')}"
        targets = {"1":self.fireMissionGroupSelection1NameLabel.cget('text'),"2": self.fireMissionGroupSelection2NameLabel.cget('text')}
        if newItem and newItem not in self.UIMaster.target.targetListCheckBoxStates["Group"]:
            self.UIMaster.target.targetListCheckBoxStates["Group"][newItem] = (BooleanVar(),BooleanVar(value=True))
            self.UIMaster.target.CreateCheckBoxList(self.UIMaster.target.targetListGroupCanvasFrame,self.UIMaster.target.targetListCheckBoxStates["Group"],None,GroupSelection=True)
            groupTargetList = {}
            try: groupTargetList["Group"] = self.UIMaster.castJson.Load(source=JsonSource.TARGET)["Group"]
            except: groupTargetList["Group"] = {}
            try: int(self.fireMissionGroupSpacing.get())
            except Exception as e:
                self.UIMaster.StatusMessageErrorDump(e,errorMessage="Incorrect spacing value, using 30m as default")
                self.fireMissionGroupSpacing.set("30")
            else:
                if int(self.fireMissionGroupSpacing.get()) <= 0:
                    self.UIMaster.StatusMessageLog("Spacing value needs to be greater than 0, setting as 30m as default")
                    self.fireMissionGroupSpacing.set("30")
            if self.fireMissionGroupEffect.get() == "Creeping Barrage":
                try: int(self.fireMissionGroupWidth.get())
                except Exception as e:
                    self.UIMaster.StatusMessageErrorDump(e,errorMessage="Incorrect creeping barrage width value, using 30m as default")
                    self.fireMissionGroupSpacing.set("30")
                else:
                    if int(self.fireMissionGroupWidth.get()) <= 0:
                        self.UIMaster.StatusMessageLog("Width value needs to be greater than 0, setting as 150m as default")
                        self.fireMissionGroupWidth.set("150")
                groupTargetList["Group"][newItem] = {"Targets" : targets,
                                                "Effect" : self.fireMissionGroupEffect.get(),
                                                "Spacing" : self.fireMissionGroupSpacing.get(),
                                                "Width" : self.fireMissionGroupWidth.get()}
            else:
                groupTargetList["Group"][newItem] = {"Targets" : targets,
                                                "Effect" : self.fireMissionGroupEffect.get(),
                                                "Spacing" : self.fireMissionGroupSpacing.get()}
            self.UIMaster.castJson.Save(source=JsonSource.TARGET,newEntry=groupTargetList)
            self.UIMaster.StatusMessageLog(message=f"Added new Grouped fire mission between {newItem} of {self.fireMissionGroupEffect.get()} effect")

class Clock(UIComponentBase):
    def __init__(self,UIMaster):
        super().__init__(UIMaster)
        try:
            common = self.UIMaster.castJson.Load(source=JsonSource.COMMON,localOverride=True)
        except Exception as e:
            None
            # self.UIMaster.StatusMessageErrorDump(e,errorMessage="Failed to load Json for clock settings")
        try:
            self.clockWidth = float(common["clockSize"])*1.05
            self.clockHeight = float(common["clockSize"])*1.05
            self.clockRadius = int(np.round(float(common["clockSize"])//2))
        except:
            self.clockWidth = 420
            self.clockHeight = 420
            self.clockRadius = 200
        try: self.clockRim = int(common["clockRim"])
        except: self.clockRim = 4
        try: self.clockFont = int(common["clockNumeralFontSize"])
        except: self.clockFont = 14
        try: self.clockHand = int(common["clockHandSize"])
        except: self.clockHand = 5
        try: self.clockSecHand = int(common["clockSecHandSize"])
        except: self.clockSecHand = 1
        self.clockTextSize = 0.9
        self.clockOffsetStrVar = StringVar(value="0")
        self.clockHandOffset = 0.0
        self.listedClocks = {}
        self.popoutImage = PhotoImage(file=self.UIMaster.exeDir/"Functions"/"icons"/"popout.png")
    
    def Initialise(self,clockFrame:ttk.Frame):
        """Set the one main clock UI onto the selected frame"""
        
        clockFrame.grid_columnconfigure(0,weight=1)
        clockCanvas = Canvas(clockFrame,width=self.clockWidth,height=self.clockHeight,bg="white")
        self.listedClocks["main"] = clockCanvas
        clockOffsetFrame = ttk.Frame(clockFrame,padding=4)
        clockOffsetFrame.grid_columnconfigure(0,weight=0,minsize=25)
        clockOffsetFrame.grid_columnconfigure(1,weight=0,minsize=4)
        clockOffsetFrame.grid_columnconfigure(2,weight=1,minsize=10)
        clockOffsetFrame.grid_rowconfigure(0,weight=1)
        clockOffsetLabel = ttk.Label(clockOffsetFrame,text="Splash Offset")
        clockOffsetSeparator = ttk.Separator(clockOffsetFrame,orient="vertical")
        clockOffsetEntry = ttk.Entry(clockOffsetFrame,textvariable=self.clockOffsetStrVar,justify="left",width=10)
        clockOffsetEntry.bind("<Return>",lambda event:self.ClockOffsetTime(self.clockOffsetStrVar.get()))
        clockPopoutButton = ttk.Button(clockOffsetFrame,image=self.popoutImage,command=self.ClockPopout)
        clockCanvas.grid(column="0",row="0",sticky="NW")
        clockOffsetFrame.grid(column="0",row="1",sticky="NEW")
        clockOffsetLabel.grid(column="0",row="0",sticky="EW")
        clockOffsetSeparator.grid(column="1",row="0",sticky="NS")
        clockOffsetEntry.grid(column="2",row="0",sticky="WE")
        clockPopoutButton.grid(column="3",row="0",sticky="WE")
        self.UpdateClockFrames()
        self.UpdateClockHands(clockCanvas=clockCanvas)

    def ClockSettingsElements(self,clockSettingsFrame:ttk.Frame,popoutOption = False):
        """Set clock settings UI onto the selected frame"""
        clockSettingSizeLabel = ttk.Label(clockSettingsFrame,text="Size")
        clockSettingRimWidthLabel = ttk.Label(clockSettingsFrame,text="Rim width")
        clockSettingFontSizeLabel = ttk.Label(clockSettingsFrame,text="Font size")
        clockSettingHandSizeLabel = ttk.Label(clockSettingsFrame,text="Hand Size")
        clockSettingSecHandSizeLabel = ttk.Label(clockSettingsFrame,text="Sec. Hand Size")
        clockSettingSeparator = ttk.Separator(clockSettingsFrame,orient="vertical")
        clockSettingSizeFrame = ttk.Frame(clockSettingsFrame,padding=0)
        clockSettingSizeFrame.grid_columnconfigure(0,minsize=10,weight=1)
        clockSettingSizeFrame.grid_columnconfigure(1,minsize=5)
        clockSettingSizeEntry = ttk.Entry(clockSettingSizeFrame,justify="left",width=5)
        clockSettingSizeEntry.bind("<Return>",lambda event:
                                   self.ClockApplySettings(clockSize=clockSettingSizeEntry.get())
                                   )
        clockSettingSizeUnitLabel = ttk.Label(clockSettingSizeFrame,text="Px")
        clockSettingRimFrame = ttk.Frame(clockSettingsFrame,padding=0)
        clockSettingRimFrame.grid_columnconfigure(0,minsize=10,weight=1)
        clockSettingRimFrame.grid_columnconfigure(1,minsize=5)
        clockSettingRimWidthEntry = ttk.Entry(clockSettingRimFrame,justify="left",width=2)
        clockSettingRimWidthEntry.bind("<Return>",lambda event:self.ClockApplySettings(clockRim = clockSettingRimWidthEntry.get()))
        clockSettingRimUnitLabel = ttk.Label(clockSettingRimFrame,text="Px")
        clockSettingFontFrame = ttk.Frame(clockSettingsFrame,padding=0)
        clockSettingFontFrame.grid_columnconfigure(0,minsize=10,weight=1)
        clockSettingFontFrame.grid_columnconfigure(1,minsize=5)
        clockSettingFontSizeEntry = ttk.Entry(clockSettingFontFrame,justify="left",width=2)
        clockSettingFontSizeEntry.bind("<Return>",lambda event:self.ClockApplySettings(clockNumeralFontSize=clockSettingFontSizeEntry.get()))
        clockSettingFontUnitLabel = ttk.Label(clockSettingFontFrame,text="Px")
        clockSettingHandSizeFrame = ttk.Frame(clockSettingsFrame,padding=0)
        clockSettingHandSizeFrame.grid_columnconfigure(0,minsize=10,weight=1)
        clockSettingHandSizeFrame.grid_columnconfigure(1,minsize=5)
        clockSettingHandSizeEntry = ttk.Entry(clockSettingHandSizeFrame,justify="left",width=2)
        clockSettingHandSizeEntry.bind("<Return>",lambda event:self.ClockApplySettings(clockHandSize=clockSettingHandSizeEntry.get()))
        clockSettingHandSizeUnitLabel = ttk.Label(clockSettingHandSizeFrame,text="Px")
        clockSettingSecHandSizeFrame = ttk.Frame(clockSettingsFrame,padding=0)
        clockSettingSecHandSizeFrame.grid_columnconfigure(0,minsize=10,weight=1)
        clockSettingSecHandSizeFrame.grid_columnconfigure(1,minsize=5)
        clockSettingSecHandSizeEntry = ttk.Entry(clockSettingSecHandSizeFrame,justify="left",width=2)
        clockSettingSecHandSizeEntry.bind("<Return>",lambda event:self.ClockApplySettings(clockSecHandSize=clockSettingSecHandSizeEntry.get()))
        clockSettingSecHandSizeUnitLabel = ttk.Label(clockSettingSecHandSizeFrame,text="Px")
        clockSettingsApplyFrame = ttk.Frame(clockSettingsFrame)
        clockSettingsApplyFrame.grid_columnconfigure(0,weight=1)
        clockSettingApplyButton = ttk.Button(clockSettingsApplyFrame,text="Apply",command= lambda: self.ClockApplySettings(clockSize=clockSettingSizeEntry.get(),clockRim=clockSettingRimWidthEntry.get(),clockNumeralFontSize=clockSettingFontSizeEntry.get(),clockHandSize=clockSettingHandSizeEntry.get(),clockSecHandSize=clockSettingSecHandSizeEntry.get()))
        try:
            jsonSettings = self.UIMaster.castJson.Load(source=JsonSource.COMMON,localOverride=True)
            clockSettingSizeEntry.insert(0,jsonSettings["clockSize"])
            clockSettingRimWidthEntry.insert(0,jsonSettings["clockRim"])
            clockSettingFontSizeEntry.insert(0,jsonSettings["clockNumeralFontSize"])
            clockSettingHandSizeEntry.insert(0,jsonSettings["clockHandSize"])
            clockSettingSecHandSizeEntry.insert(0,jsonSettings["clockSecHandSize"])
        except: None
        if popoutOption:
            clockSettingsApplyFrame.grid_columnconfigure(0,weight=5)
            clockSettingPopoutButton = ttk.Button(clockSettingsApplyFrame,image=self.popoutImage,command= lambda: self.ClockSettingsPopout())
            clockSettingPopoutButton.grid(column="1",row="0",sticky="NEWS",pady="4",padx="2")
        clockSettingSizeLabel.grid(column="0",row="0",sticky="NE")
        clockSettingRimWidthLabel.grid(column="0",row="1",sticky="NE")
        clockSettingFontSizeLabel.grid(column="0",row="2",sticky="NE")
        clockSettingHandSizeLabel.grid(column="0",row="3",sticky="NE")
        clockSettingSecHandSizeLabel.grid(column="0",row="4",sticky="NE")
        clockSettingSeparator.grid(column="1",row="0",rowspan="5",sticky="NS")
        clockSettingSizeFrame.grid(column="2",row="0",sticky="NW",pady=4)
        clockSettingSizeEntry.grid(column="0",row="0",sticky="NW")
        clockSettingSizeUnitLabel.grid(column="1",row="0",sticky="SW")
        clockSettingRimFrame.grid(column="2",row="1",sticky="NW",pady=4)
        clockSettingRimWidthEntry.grid(column="0",row="0",sticky="NW")
        clockSettingRimUnitLabel.grid(column="1",row="0",sticky="SW")
        clockSettingFontFrame.grid(column="2",row="2",sticky="NW",pady=4)
        clockSettingFontSizeEntry.grid(column="0",row="0",sticky="NW")
        clockSettingFontUnitLabel.grid(column="1",row="0",sticky="SW")
        clockSettingHandSizeFrame.grid(column="2",row="3",sticky="NW",pady=4)
        clockSettingHandSizeEntry.grid(column="0",row="0",sticky="NW")
        clockSettingHandSizeUnitLabel.grid(column="1",row="0",sticky="SW")
        clockSettingSecHandSizeFrame.grid(column="2",row="4",sticky="NW",pady=4)
        clockSettingSecHandSizeEntry.grid(column="0",row="0",sticky="NW")
        clockSettingSecHandSizeUnitLabel.grid(column="1",row="0",sticky="SW")
        clockSettingsApplyFrame.grid(column="0",columnspan="3",row="5",sticky="NESW")
        clockSettingApplyButton.grid(column="0",row="0",sticky="NESW",pady="4",padx="2")

    def ClockApplySettings(self,**kwargs):
        """
        Apply and save settings
        kwarg : default value
        clockSize : 400
        clockRim :4
        clockNumeralFontSize : 14
        clockTextRatio : 0.9
        clockHandSize : 5
        clockSecHandSize : 1
        """
        for setting, value in kwargs.items():
            try:
                if value != "" and not value.isalpha():
                    value = float(value)
                    if setting == "clockSize":
                        self.clockWidth = value*1.05
                        self.clockHeight = value*1.05
                        self.clockRadius = int(np.round(float(value)/2))
                    elif setting == "clockRim": self.clockRim = value
                    elif setting == "clockNumeralFontSize": self.clockFont = value
                    elif setting == "clockTextRatio": self.clockTextSize = value
                    elif setting == "clockHandSize": self.clockHand = value
                    elif setting == "clockSecHandSize": self.clockSecHand = value
                else: None
            except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage=f"Failed to set {setting} clock setting")
        try: self.UIMaster.castJson.Save(source=JsonSource.COMMON,newEntry=kwargs,localOverride=True)
        except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage="Failed to save clock settings to JSON")
        self.UpdateClockFrames()

    def UpdateClockFrames(self):
        "Update faces"
        for clock in self.listedClocks.values():
            if (type(clock) == Canvas):
                clock.delete("all")
                self.DrawClockFace(clock)
            else:
                clock[0].delete("all")
                self.DrawClockFace(clock[0])
                clock[1].geometry(str(int(self.clockWidth+10))+"x"+str(int(self.clockHeight+10)))



    def DrawClockFace(self,clockCanvas: Canvas):
        "Draw clock faces"
        clockCanvas.config(width = self.clockWidth)
        clockCanvas.config(height= self.clockHeight)
        clockCenterX = self.clockWidth//2
        clockCenterY = self.clockHeight//2
        for i in range(int(self.clockRadius)):
            radius = self.clockRadius-i
            if radius % 2 == 0:
                clockCanvas.create_oval(clockCenterX-radius,clockCenterY-radius,clockCenterX+radius,clockCenterY+radius,width=1,outline="#FEFEFE")
        clockCanvas.create_oval(clockCenterX-self.clockRadius,clockCenterY-self.clockRadius,clockCenterX+self.clockRadius,clockCenterY+self.clockRadius,width=self.clockRim)

        for i in range(12):
            angle = np.radians(i*30)
            sinA = np.sin(angle)
            cosA = np.cos(angle)
            if i in [3,6,9,0]:
                innerRadius = self.clockRadius * 0.65
                outerRadius = self.clockRadius * 0.8
                handSize = self.clockRadius * self.clockTextSize
                width = self.clockRim
                numeral = {0:"12", 3:"3", 6:"6", 9:"9"}[i]
                xText = clockCenterX + handSize * sinA
                yText = clockCenterY - handSize * cosA
                clockCanvas.create_text(xText,yText,text=numeral,font=("Microsoft Tai Le",round(self.clockFont),"bold"))
            else:
                innerRadius = self.clockRadius * 0.75
                outerRadius = self.clockRadius * 0.95
                handSize = self.clockRadius * (self.clockTextSize-0.1)
                width = self.clockRim / 2
            xOuter = clockCenterX + outerRadius * sinA
            yOuter = clockCenterY - outerRadius * cosA
            xInner = clockCenterX + innerRadius * sinA
            yInner = clockCenterY - innerRadius * cosA
            clockCanvas.create_line(xInner,yInner,xOuter,yOuter,width=width)
        for i in range(60):
            if i not in [15,30,45,0]:
                angle = np.radians(i * 6)
                sinA = np.sin(angle)
                cosA = np.cos(angle)
                outer = self.clockRadius*0.95
                inner = self.clockRadius*0.85
                xOuter = clockCenterX + outer * sinA
                yOuter = clockCenterY - outer * cosA
                xInner = clockCenterX + inner * sinA
                yInner = clockCenterY - inner * cosA
                clockCanvas.create_line(xInner,yInner,xOuter,yOuter,width=1)
        clockCanvas.create_text(clockCenterX,clockCenterY+self.clockRadius/2,text="ZULU",fill="lightgrey",font=("Microsoft Tai Le",round(self.clockFont),"bold"))

    def UpdateClockHands(self,clockCanvas: Canvas):
        "Draw clock hands"
        try:
            clockCanvas.delete("hand")
            now = datetime.now(timezone.utc)
            microsecond = now.microsecond
            second = now.second + microsecond / 1000000
            minute = now.minute
            hour = now.hour % 12

            offSecAngle = np.radians(second*6-self.clockHandOffset*6)
            secAngle = np.radians(second*6)
            minAngle = np.radians(minute * 6 + second * 0.1)
            hourAngle = np.radians(hour *30 + minute * 0.5)

            clockCenterX = self.clockWidth/2
            clockCenterY = self.clockWidth/2

            if self.clockHandOffset!= 0.0:
                xOffSec = clockCenterX + self.clockRadius * 0.9 * np.sin(offSecAngle)
                yOffSec = clockCenterY - self.clockRadius * 0.9 * np.cos(offSecAngle)
                clockCanvas.create_line(clockCenterX,clockCenterY, xOffSec,yOffSec,fill="red",width=self.clockSecHand,tag="hand")
                if self.clockHandOffset < 60.0: clockCanvas.create_arc(int(clockCenterX-self.clockRadius/2),int(clockCenterY-self.clockRadius/2),int(clockCenterX+self.clockRadius/2),int(clockCenterY+self.clockRadius/2),start=-np.rad2deg(secAngle-np.pi/2),extent=self.clockHandOffset*6,style=PIESLICE,fill="#FFAAAA",outline="#FF0000",tag="hand",width=self.clockSecHand)
                elif self.clockHandOffset < 120:
                    clockCanvas.create_arc(int(clockCenterX-self.clockRadius/1.5),int(clockCenterY-self.clockRadius/1.5),int(clockCenterX+self.clockRadius/1.5),int(clockCenterY+self.clockRadius/1.5),start=-np.rad2deg(secAngle-np.pi/2),extent=self.clockHandOffset*6,style=PIESLICE,fill="#FFAAAA",outline="#FF0000",tag="hand",width=self.clockSecHand)
                    clockCanvas.create_oval(int(clockCenterX-self.clockRadius/2),int(clockCenterY-self.clockRadius/2),int(clockCenterX+self.clockRadius/2),int(clockCenterY+self.clockRadius/2),fill="#FF7777",outline="#FF0000",tag="hand",width=self.clockSecHand)
            xSec = clockCenterX + self.clockRadius * 0.9 * np.sin(secAngle)
            ySec = clockCenterY - self.clockRadius * 0.9 * np.cos(secAngle)
            xSecCircle = clockCenterX + (self.clockRadius * 0.9+5) * np.sin(secAngle)
            ySecCircle = clockCenterY - (self.clockRadius * 0.9+5) * np.cos(secAngle)
            clockCanvas.create_line(clockCenterX,clockCenterY, xSec,ySec,fill="blue",width=self.clockSecHand,tag="hand")
            clockCanvas.create_oval(xSecCircle-5,ySecCircle-5,xSecCircle+5,ySecCircle+5,width=self.clockSecHand,outline="blue",tag="hand")
            xMin = clockCenterX + self.clockRadius * 0.75 * np.sin(minAngle)
            YMin = clockCenterY - self.clockRadius * 0.75 * np.cos(minAngle)
            clockCanvas.create_line(clockCenterX,clockCenterY, xMin,YMin,fill="black",width=int(np.round(self.clockHand/2)),tag="hand")
            clockCanvas.create_oval(xMin-int(np.round(self.clockHand/4)),YMin-int(np.round(self.clockHand/4)),xMin+int(np.round(self.clockHand/4)),YMin+int(np.round(self.clockHand/4)),fill="black",outline="black",tag="hand")
            xHour = clockCenterX + self.clockRadius * 0.5 * np.sin(hourAngle)
            yHour = clockCenterY - self.clockRadius * 0.5 * np.cos(hourAngle)
            clockCanvas.create_line(clockCenterX,clockCenterY, xHour,yHour,fill="black",width=int(np.round(self.clockHand)),tag="hand")
            clockCanvas.create_oval(clockCenterX-int(np.round(self.clockHand)/2),clockCenterY-int(np.round(self.clockHand)/2),clockCenterX+int(np.round(self.clockHand)/2),clockCenterY+int(np.round(self.clockHand)/2),fill="black",outline="black",tag="hand")
            clockCanvas.create_oval(xHour-int(np.round(self.clockHand)/2),yHour-int(np.round(self.clockHand)/2),xHour+int(np.round(self.clockHand)/2),yHour+int(np.round(self.clockHand)/2),fill="black",outline="black",tag="hand")
            delay = int(50 - (microsecond / 1000) % 50)
            if delay == 0: delay = 50
            self.UIMaster.root.after(delay, lambda: self.UpdateClockHands(clockCanvas))
        except: None
    
    def ClockOffsetTime(self,offset):
        "Change the clock offset"
        if offset.isspace() == False or offset != "0":
            try: self.clockHandOffset = float(offset)
            except ValueError:
                try: self.clockHandOffset = float(self.UIMaster.castJson.Load(source=JsonSource.FIREMISSION)[self.UIMaster.fireMission.fireMissionNotebook.tab(self.UIMaster.fireMission.fireMissionNotebook.select(),"text")][offset]["TOF"])
                except: return False
            except: None
        else:
            self.clockHandOffset = 0.0
            self.clockOffsetStrVar.set("0")

    def ClockPopout(self):
        "Popout clock window"
        mouseStartX,mouseStartY = 0,0
        def ClockMenu(event):
            clockCloseMenu = Menu(self.UIMaster.root,tearoff=False)
            clockCloseMenu.add_command(label="Close",command=ClockClose)
            clockCloseMenu.post(event.x_root,event.y_root)
        def ClockClose():
            self.listedClocks.pop("window",None)
            clockTopLevel.destroy()
        clockTopLevel = Toplevel(self.UIMaster.root)
        clockTopLevel.attributes("-topmost",True)
        clockTopLevel.wm_attributes("-transparentcolor","white")
        clockTopLevel.configure(bg="white")
        clockTopLevel.overrideredirect(True)
        clockTopLevel.title("Clock")
        try: clockTopLevel.geometry(f"{str(int(self.clockWidth+10))}x{str(int(self.clockHeight+10))}+50+50")
        except: clockTopLevel.geometry("430x430+100+100")
        clockTopLevel.resizable(False,False)
        clockTopLevel.iconbitmap(self.UIMaster.exeDir/"Functions"/"icons"/"clock.ico")
        def DragStart(event):
            nonlocal mouseStartX, mouseStartY
            mouseStartX, mouseStartY = event.x, event.y
        def DragMove(event):
            nonlocal mouseStartX, mouseStartY
            clockTopLevel.geometry(f"+{clockTopLevel.winfo_x() + (event.x-mouseStartX)}+{clockTopLevel.winfo_y() + (event.y-mouseStartY)}")
        clockTopLevel.bind("<Button-3>", ClockMenu)
        clockTopLevel.bind("<Button-1>", DragStart)
        clockTopLevel.bind("<B1-Motion>", DragMove)
        clockWindow = clockTopLevel.winfo_toplevel()
        clockWindow.anchor("center")
        clockWindow.grid_columnconfigure(0,weight=1)
        clockWindow.grid_rowconfigure(0,weight=1)
        clockWindowFrame = ttk.Frame(clockWindow,padding=5,relief="sunken")
        clockWindowCanvas = Canvas(clockWindow,width=self.clockWidth,height=self.clockHeight,bg="white")
        self.listedClocks["window"] = [clockWindowCanvas,clockTopLevel]
        self.DrawClockFace(clockWindowCanvas)
        self.UpdateClockHands(clockWindowCanvas)
        clockWindowFrame.grid(column="0",row="0",sticky="NW")
        clockWindowCanvas.grid(column="0",row="0",sticky="NW")
        clockTopLevel.protocol("WM_DELETE_WINDOW",ClockClose)
    
    def ClockSettingsPopout(self):
        "Popout clock settings"
        self.UIMaster.miscNotebook.select(self.UIMaster.root.nametowidget(self.listedClocks["main"].winfo_parent()))
        clockSettings = Toplevel(self.UIMaster.root)
        clockSettings.title("Clock Settings")
        clockSettings.geometry("150x200+200+500")
        clockSettings.resizable(False,True)
        clockSettings.iconbitmap(self.UIMaster.exeDir/"Functions"/"icons"/"settings.ico")
        clockSettingsWindow = clockSettings.winfo_toplevel()
        clockSettingsWindow.anchor("nw")
        clockSettingsWindow.grid_columnconfigure(0,weight=1)
        clockSettingsWindow.grid_rowconfigure(0,weight=1)
        clockSettingsFrame = ttk.Frame(clockSettingsWindow,padding=5,relief="groove")
        self.ClockSettingsElements(clockSettingsFrame)
        clockSettingsFrame.grid()

class Notes(UIComponentBase):
    def __init__(self, UIMaster):
        super().__init__(UIMaster)
        # self.UIMaster = CastUI(UIMaster)
    def Initialise(self,frame:ttk.Frame):
        frame.grid_rowconfigure(0,weight=1)
        frame.grid_columnconfigure(0,weight=1)
        self.noteText = Text(frame,font=("Microsoft Tai Le",12),wrap="word")
        self.noteText.bind("<Return>",lambda *args: self.SaveNote())
        self.noteText.grid(column="0",row="0",sticky="NESW")
        self.LoadNote()
    def SaveNote(self):self.UIMaster.castJson.Save(source=JsonSource.COMMON,localOverride=True,newEntry={"notes": self.noteText.get("1.0", END).strip()})
    def LoadNote(self):
        try:
            note = self.UIMaster.castJson.Load(source=JsonSource.COMMON,localOverride=True)["notes"]
            if note.isspace() or note == "":
                self.noteText.insert(END,"Pressing 'return' in this text box will save the contents")
            else: self.noteText.insert(END,note)
        except: self.noteText.insert(END,"Pressing 'return' in this text box will save the contents")

class Targets(UIComponentBase):
    def __init__(self,UIMaster):
        super().__init__(UIMaster)
        # self.UIMaster = CastUI(UIMaster)
        self.windowFireMissionEditSafety = StringVar(value="1")
        self.FPFEditSelected = False
        self.RefreshTargetDictionaries()
        
    def Initialise(self,frame):
        targetListLabelframe = ttk.Labelframe(frame,text="Target List",height=200,width=500,padding=5,relief="groove")
        targetListLabelframe.grid_columnconfigure((0,1,2,3,4),weight=1)
        targetListLabelframe.grid_columnconfigure(5,weight=10000)
        targetListLabelframe.grid_rowconfigure((0,1),minsize=30)
        targetListEditImage = PhotoImage(file=self.UIMaster.exeDir/"Functions"/"icons"/"edit.png")
        targetListCalcImage = PhotoImage(file=self.UIMaster.exeDir/"Functions"/"icons"/"calc.png")
        targetListHeaderImageEmpty = ttk.Frame(targetListLabelframe,width=25)
        targetListSeriesEditImage = ttk.Label(targetListLabelframe,image=targetListEditImage)
        targetListSeriesCalcImage = ttk.Label(targetListLabelframe,image=targetListCalcImage)
        targetListHeaderSeparator = ttk.Separator(targetListLabelframe,orient="vertical")
        targetListIndexEditImage = ttk.Label(targetListLabelframe,image=targetListEditImage)
        targetListIndexCalcImage = ttk.Label(targetListLabelframe,image=targetListCalcImage)
        targetListSeriesEditImage.image = targetListEditImage
        targetListSeriesCalcImage.image = targetListCalcImage
        targetListIndexEditImage.image = targetListEditImage
        targetListIndexCalcImage.image = targetListCalcImage
        self.targetListCalculate = ttk.Button(targetListLabelframe,text="Calculate",command=self.CalculateThread ,image=targetListCalcImage,compound="left")
        self.targetListCalculate.image = targetListCalcImage
        targetListFrame = ttk.Frame(targetListLabelframe)
        targetListFrame.grid_columnconfigure(0,weight=1)
        targetListFrame.grid_rowconfigure(0,weight=1)
        targetListPanedwindow = ttk.Panedwindow(targetListFrame,orient="vertical")
        targetListPanedwindowLRFrame = ttk.Frame(targetListPanedwindow,padding="5")
        targetListPanedwindowXYFrame = ttk.Frame(targetListPanedwindow,padding="5")
        targetListPanedwindowFPFFrame = ttk.Frame(targetListPanedwindow,padding="5")
        targetListPanedwindowGroupFrame = ttk.Frame(targetListPanedwindow,padding="5")
        targetListPanedwindowEmptyFrame = ttk.Frame(targetListPanedwindow,padding="5")
        targetListPanedwindow.add(targetListPanedwindowLRFrame,weight=1)
        targetListPanedwindow.add(targetListPanedwindowXYFrame,weight=1)
        targetListPanedwindow.add(targetListPanedwindowFPFFrame,weight=1)
        targetListPanedwindow.add(targetListPanedwindowGroupFrame,weight=1)
        targetListPanedwindow.add(targetListPanedwindowEmptyFrame,weight=0)
        targetListPanedwindowLRFrame.grid_columnconfigure(0)
        targetListPanedwindowLRFrame.grid_rowconfigure(0,weight=1)
        targetListPanedwindowXYFrame.grid_columnconfigure(0)
        targetListPanedwindowXYFrame.grid_rowconfigure(0,weight=1)
        targetListPanedwindowFPFFrame.grid_columnconfigure(0)
        targetListPanedwindowFPFFrame.grid_rowconfigure(0,weight=1)
        targetListPanedwindowGroupFrame.grid_columnconfigure(0)
        targetListPanedwindowGroupFrame.grid_rowconfigure(0,weight=1)
        self.targetContextMenu = Menu(self.UIMaster.root,tearoff=False)

        targetListFPFLabelframe = ttk.Labelframe(targetListPanedwindowFPFFrame,text="FPF",padding=5,relief="groove")
        self.targetListFPFCanvas = Canvas(targetListFPFLabelframe,bg="white",width=128,height=120)
        self.targetListFPFCanvasFrame = ttk.Frame(self.targetListFPFCanvas, padding=10)
        self.targetListFPFCanvas.create_window((0, 0), window=self.targetListFPFCanvasFrame, anchor="nw")
        targetListFPFScrollbar = ttk.Scrollbar(targetListFPFLabelframe, orient="vertical", command=self.targetListFPFCanvas.yview)
        self.targetListFPFCanvas.configure(yscrollcommand=targetListFPFScrollbar.set)
        self.targetListFPFCanvas.pack(side="left", fill="both", expand=True)
        targetListFPFLabelframe.grid(row=0, column=0, sticky="nsew")
        targetListFPFScrollbar.pack(side="right", fill="y")

        targetListLRLabelframe = ttk.Labelframe(targetListPanedwindowLRFrame,text="LR",padding=5,relief="groove")
        self.targetListLRCanvas = Canvas(targetListLRLabelframe,bg="white",width=128,height=120)
        self.targetListLRCanvasFrame = ttk.Frame(self.targetListLRCanvas, padding=10)
        self.targetListLRCanvas.create_window((0, 0), window=self.targetListLRCanvasFrame, anchor="nw")
        targetListLRScrollbar = ttk.Scrollbar(targetListLRLabelframe, orient="vertical", command=self.targetListLRCanvas.yview)
        self.targetListLRCanvas.configure(yscrollcommand=targetListLRScrollbar.set)
        self.targetListLRCanvas.pack(side="left", fill="both", expand=True)
        targetListLRLabelframe.grid(row=0, column=0, sticky="nsew")
        targetListLRScrollbar.pack(side="right", fill="y")

        targetListXYLabelframe = ttk.Labelframe(targetListPanedwindowXYFrame,text="XY",padding=5,relief="groove")
        self.targetListXYCanvas = Canvas(targetListXYLabelframe,bg="white",width=128,height=120)
        self.targetListXYCanvasFrame = ttk.Frame(self.targetListXYCanvas, padding=10)
        self.targetListXYCanvas.create_window((0, 0), window=self.targetListXYCanvasFrame, anchor="nw")
        targetListXYScrollbar = ttk.Scrollbar(targetListXYLabelframe, orient="vertical", command=self.targetListXYCanvas.yview)
        self.targetListXYCanvas.configure(yscrollcommand=targetListXYScrollbar.set)
        self.targetListXYCanvas.pack(side="left", fill="both", expand=True)
        targetListXYLabelframe.grid(row=0, column=0, sticky="nsew")
        targetListXYScrollbar.pack(side="right", fill="y")

        targetListGroupLabelframe = ttk.Labelframe(targetListPanedwindowGroupFrame,text="Group",padding=5,relief="groove")
        self.targetListGroupCanvas = Canvas(targetListGroupLabelframe,bg="white",height=120)
        self.targetListGroupCanvasFrame = ttk.Frame(self.targetListGroupCanvas, padding=10)
        self.targetListGroupCanvas.create_window((0, 0), window=self.targetListGroupCanvasFrame, anchor="nw")
        targetListGroupScrollbar = ttk.Scrollbar(targetListGroupLabelframe, orient="vertical", command=self.targetListGroupCanvas.yview)
        self.targetListGroupCanvas.configure(yscrollcommand=targetListGroupScrollbar.set)
        self.targetListGroupCanvas.pack(side="left", fill="both", expand=True)
        targetListGroupLabelframe.grid(row=0, column=0, sticky="nsew")

        targetListLabelframe.grid(column="0",row="0",sticky="NESW")
        targetListHeaderImageEmpty.grid(row="0", column="0", sticky="NW")
        targetListSeriesEditImage.grid(row="0", column="1", sticky="NW")
        targetListSeriesCalcImage.grid(row="0", column="2", sticky="NW")
        targetListHeaderSeparator.grid(row="0", column="3", sticky="NEWS",padx="2")
        targetListIndexEditImage.grid(row="0", column="4", sticky="NW")
        targetListIndexCalcImage.grid(row="0", column="5", sticky="NW")
        self.targetListCalculate.grid(row="0", column="6", sticky="NESW")
        targetListFrame.grid(column="0",row="1",columnspan="6",sticky="NW")
        targetListPanedwindow.grid(row="1", column="0", sticky="nsew")

    def RefreshTargetDictionaries(self,mission: str | None = None):
        if mission:
            self.targetListCheckBoxStates[mission] = {}
        else:
            self.targetList = {
                "FPF": {},
                "LR": {},
                "XY": {},
                "Group": {}
                }
            self.targetSeriesDict = {
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

    def SortFireMissions(self,items):
        def sortKey(item: str):
            segments = []
            for char in item:
                if char.isdigit():
                    segments.append((False, int(char)))
                else:
                    segments.append((True,char))
            return segments
        return sorted(items.keys(),key=sortKey)

    def RequestEditFireMissions(self):
        editListStr = ""
        editList = []
        editCount = 0
        self.FPFEditSelected = False
        for target, (edit,calculate) in self.targetListCheckBoxStates["FPF"].items():
            if edit.get() == True:
                self.FPFEditSelected = True
        if self.FPFEditSelected == False:
            self.UIMaster.targetDetail.fireMissionEffect.set(self.UIMaster.targetDetail.previousMissionEffect)
            for target, (edit, calculate) in self.targetListCheckBoxStates["LR"].items():
                if edit.get() == True:
                    editCount +=1
                    editListStr += ("LR "+target + " | ")
                    editList.append(f"LR-{target}")
            for target, (edit, calculate) in self.targetListCheckBoxStates["XY"].items():
                if edit.get() == True:
                    editCount +=1
                    editListStr += ("XY "+target + " | ")
                    editList.append(f"XY-{target}")
            for target, (edit, calculate) in self.targetListCheckBoxStates["Group"].items():
                if edit.get() == True:
                    editCount +=1
                    editListStr += ("Group "+target + " | ")
            self.CreateCheckBoxList(self.targetListFPFCanvasFrame,{key: self.targetListCheckBoxStates["FPF"][key] for key in self.SortFireMissions(self.targetListCheckBoxStates["FPF"])},self.targetSeriesDict["FPF"],True)
            self.CreateCheckBoxList(self.targetListLRCanvasFrame,{key: self.targetListCheckBoxStates["LR"][key] for key in self.SortFireMissions(self.targetListCheckBoxStates["LR"])},self.targetSeriesDict["LR"])
            self.CreateCheckBoxList(self.targetListXYCanvasFrame,{key: self.targetListCheckBoxStates["XY"][key] for key in self.SortFireMissions(self.targetListCheckBoxStates["XY"])},self.targetSeriesDict["XY"])
            self.CreateCheckBoxList(self.targetListGroupCanvasFrame,self.targetListCheckBoxStates["Group"],None,False,True)
            if self.UIMaster.targetCreation.xylrfpf.get() !="2":
                self.UIMaster.targetDetail.fireMissionSelectionEffectFPFRadio.grid_remove()
                self.UIMaster.targetDetail.fireMissionSelectionEffectDestroyRadio.grid()
                self.UIMaster.targetDetail.fireMissionSelectionEffectNeutraliseRadio.grid()
                self.UIMaster.targetDetail.fireMissionSelectionEffectCheckRadio.grid()
                self.UIMaster.targetDetail.fireMissionSelectionEffectSaturationRadio.grid()
                self.UIMaster.targetDetail.fireMissionSelectionEffectAreaDenialRadio.grid()
                self.UIMaster.targetDetail.fireMissionSelectionEffectSmokeRadio.grid()
                self.UIMaster.targetDetail.fireMissionSelectionEffectIllumRadio.grid()
        else:
            self.UIMaster.targetDetail.fireMissionEffect.set("FPF")
            for target, (edit, calculate) in self.targetListCheckBoxStates["FPF"].items():
                if edit.get() == True:
                    editCount +=1
                    editListStr += ("FPF "+target + " | ")
                    editList.append(f"FPF-{target}")
            for target, (edit, calculate) in self.targetListCheckBoxStates["LR"].items():
                edit.set(False)
            for target, (edit, calculate) in self.targetSeriesDict["LR"].items():
                edit.set(False)
            for target, (edit, calculate) in self.targetListCheckBoxStates["XY"].items():
                edit.set(False)
            for target, (edit, calculate) in self.targetSeriesDict["XY"].items():
                edit.set(False)
            for target, (edit, calculate) in self.targetListCheckBoxStates["Group"].items():
                edit.set(False)
            for target, (edit, calculate) in self.targetSeriesDict["Group"].items():
                edit.set(False)
            self.CreateCheckBoxList(self.targetListFPFCanvasFrame,{key: self.targetListCheckBoxStates["FPF"][key] for key in self.SortFireMissions(self.targetListCheckBoxStates["FPF"])},self.targetSeriesDict["FPF"],True)
            self.CreateCheckBoxList(self.targetListLRCanvasFrame,{key: self.targetListCheckBoxStates["LR"][key] for key in self.SortFireMissions(self.targetListCheckBoxStates["LR"])},self.targetSeriesDict["LR"])
            self.CreateCheckBoxList(self.targetListXYCanvasFrame,{key: self.targetListCheckBoxStates["XY"][key] for key in self.SortFireMissions(self.targetListCheckBoxStates["XY"])},self.targetSeriesDict["XY"])
            self.CreateCheckBoxList(self.targetListGroupCanvasFrame,self.targetListCheckBoxStates["Group"],None,False,True)
            self.UIMaster.targetDetail.fireMissionSelectionEffectDestroyRadio.grid_remove()
            self.UIMaster.targetDetail.fireMissionSelectionEffectNeutraliseRadio.grid_remove()
            self.UIMaster.targetDetail.fireMissionSelectionEffectCheckRadio.grid_remove()
            self.UIMaster.targetDetail.fireMissionSelectionEffectSaturationRadio.grid_remove()
            self.UIMaster.targetDetail.fireMissionSelectionEffectAreaDenialRadio.grid_remove()
            self.UIMaster.targetDetail.fireMissionSelectionEffectSmokeRadio.grid_remove()
            self.UIMaster.targetDetail.fireMissionSelectionEffectIllumRadio.grid_remove()
            self.UIMaster.targetDetail.fireMissionSelectionEffectFPFRadio.grid()
        if editListStr == "":
            self.UIMaster.targetDetail.fireMissionSelectionLabelframe.config(text = "Fire Mission Selection")
            if self.UIMaster.targetCreation.xylrfpf.get() =="2":
                self.UIMaster.targetDetail.fireMissionSelectionEffectDestroyRadio.grid_remove()
                self.UIMaster.targetDetail.fireMissionSelectionEffectNeutraliseRadio.grid_remove()
                self.UIMaster.targetDetail.fireMissionSelectionEffectCheckRadio.grid_remove()
                self.UIMaster.targetDetail.fireMissionSelectionEffectSaturationRadio.grid_remove()
                self.UIMaster.targetDetail.fireMissionSelectionEffectAreaDenialRadio.grid_remove()
                self.UIMaster.targetDetail.fireMissionSelectionEffectSmokeRadio.grid_remove()
                self.UIMaster.targetDetail.fireMissionSelectionEffectIllumRadio.grid_remove()
                self.UIMaster.targetDetail.fireMissionSelectionEffectFPFRadio.grid()
            else:
                self.UIMaster.targetDetail.fireMissionSelectionEffectFPFRadio.grid_remove()
                self.UIMaster.targetDetail.fireMissionSelectionEffectDestroyRadio.grid()
                self.UIMaster.targetDetail.fireMissionSelectionEffectNeutraliseRadio.grid()
                self.UIMaster.targetDetail.fireMissionSelectionEffectCheckRadio.grid()
                self.UIMaster.targetDetail.fireMissionSelectionEffectSaturationRadio.grid()
                self.UIMaster.targetDetail.fireMissionSelectionEffectAreaDenialRadio.grid()
                self.UIMaster.targetDetail.fireMissionSelectionEffectSmokeRadio.grid()
                self.UIMaster.targetDetail.fireMissionSelectionEffectIllumRadio.grid()
            self.UIMaster.targetDetail.fireMissionSelectionUpdateMission.grid_remove()
        else:
            self.UIMaster.targetDetail.fireMissionSelectionLabelframe.config(text = editListStr + "Edit missions")
            self.UIMaster.targetDetail.fireMissionSelectionUpdateMission.grid()
            if editCount == 1:
                self.FireMissionEdit()
            if editCount == 2:
                self.UIMaster.targetDetail.fireMissionGroupSelectionLabelframe.grid()
                if self.UIMaster.targetDetail.fireMissionGroupSelectionReverse:
                    self.UIMaster.targetDetail.fireMissionGroupSelection1NameLabel.config(text = editList[1])
                    self.UIMaster.targetDetail.fireMissionGroupSelection2NameLabel.config(text = editList[0])
                else:
                    self.UIMaster.targetDetail.fireMissionGroupSelection1NameLabel.config(text = editList[0])
                    self.UIMaster.targetDetail.fireMissionGroupSelection2NameLabel.config(text = editList[1])
            else:
                self.UIMaster.targetDetail.fireMissionGroupSelectionLabelframe.grid_remove()

    def FireMissionEdit(self,*args):
        targets = self.UIMaster.castJson.Load(source=JsonSource.TARGET)
        for target, (edit, calculate) in self.targetListCheckBoxStates["LR"].items():
            if edit.get() == True:
                self.FireMissionEditPasteSettings("LR",target,targets)

        for target, (edit, calculate) in self.targetListCheckBoxStates["XY"].items():
            if edit.get() == True:
                self.FireMissionEditPasteSettings("XY",target,targets)

        for target, (edit, calculate) in self.targetListCheckBoxStates["FPF"].items():
            if edit.get() == True:
                self.FireMissionEditPasteSettings("FPF",target,targets)
        
    def FireMissionEditPasteSettings(self,prefix,target,targets):
        self.UIMaster.targetDetail.fireMissionEffect.set(targets[prefix][target]["Effect"])
        self.UIMaster.targetDetail.fireMissionWidth.set(str(int(float(targets[prefix][target]["Width"])*2)))
        self.UIMaster.targetDetail.fireMissionDepth.set(str(int(float(targets[prefix][target]["Depth"])*2)))
        self.UIMaster.targetDetail.fireMissionLength.set(targets[prefix][target]["Length"])
        self.UIMaster.targetDetail.fireMissionCondition.set(targets[prefix][target]["Condition"])
        self.UIMaster.targetDetail.fireMissionHour.set(targets[prefix][target]["Time"]["Hour"])
        self.UIMaster.targetDetail.fireMissionMinute.set(targets[prefix][target]["Time"]["Minute"])
        self.UIMaster.targetDetail.fireMissionSecond.set(targets[prefix][target]["Time"]["Second"])

    def SyncTargets(self,targetJson):
        self.targetList = targetJson
        try: self.targetList.items()
        except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage="Target json error")
        else:
            for mission, targets in list(targetJson.items()):
                if mission == "FPF":
                    prefix = "FPF"
                    canvas = self.targetListFPFCanvas
                    canvasFrame = self.targetListFPFCanvasFrame
                    dictionary = self.targetSeriesDict["FPF"]
                    FPF = True
                    Group = False
                elif mission == "LR":
                    prefix = "LR"
                    canvas = self.targetListLRCanvas
                    canvasFrame = self.targetListLRCanvasFrame
                    dictionary = self.targetSeriesDict["LR"]
                    FPF = False
                    Group = False
                elif mission == "XY":
                    prefix = "XY"
                    canvas = self.targetListXYCanvas
                    canvasFrame = self.targetListXYCanvasFrame
                    dictionary = self.targetSeriesDict["XY"]
                    FPF = False
                    Group = False
                elif mission == "Group":
                    prefix = "Group"
                    canvas = self.targetListGroupCanvas
                    canvasFrame = self.targetListGroupCanvasFrame
                    dictionary = None
                    FPF = False
                    Group = True
                for target in list(targets.keys()):
                    if target not in self.targetListCheckBoxStates[prefix]:
                        try:
                            self.targetListCheckBoxStates[prefix][target]
                        except KeyError:
                            self.targetListCheckBoxStates[prefix][target] = (BooleanVar(),BooleanVar())
                            listedTargets = self.targetListCheckBoxStates[prefix]
                            self.CreateCheckBoxList(canvasFrame,listedTargets,dictionary,FPF,Group)
                            self.updateTargetListScrollregion(canvasFrame,canvas)
            for mission, targets in self.targetListCheckBoxStates.items():
                if mission == "FPF":
                    prefix = "FPF"
                    canvas = self.targetListFPFCanvas
                    canvasFrame = self.targetListFPFCanvasFrame
                    listedTargets = {key: self.targetListCheckBoxStates[prefix][key] for key in self.SortFireMissions(self.targetListCheckBoxStates[prefix])}
                    dictionary = self.targetSeriesDict["FPF"]
                    FPF = True
                    Group = False
                elif mission == "LR":
                    prefix = "LR"
                    canvas = self.targetListLRCanvas
                    canvasFrame = self.targetListLRCanvasFrame
                    listedTargets = {key: self.targetListCheckBoxStates[prefix][key] for key in self.SortFireMissions(self.targetListCheckBoxStates[prefix])}
                    dictionary = self.targetSeriesDict["LR"]
                    FPF = False
                    Group = False
                elif mission == "XY":
                    prefix = "XY"
                    canvas = self.targetListXYCanvas
                    canvasFrame = self.targetListXYCanvasFrame
                    listedTargets = {key: self.targetListCheckBoxStates[prefix][key] for key in self.SortFireMissions(self.targetListCheckBoxStates[prefix])}
                    dictionary = self.targetSeriesDict["XY"]
                    FPF = False
                    Group = False
                elif mission == "Group":
                    prefix = "Group"
                    canvas = self.targetListGroupCanvas
                    canvasFrame = self.targetListGroupCanvasFrame
                    listedTargets = self.targetListCheckBoxStates["Group"]
                    dictionary = None
                    FPF = False
                    Group = True
                for target in list(targets.keys()):
                    try: targetJson[prefix][target]
                    except KeyError:
                        listedTargets.pop(target,None)
                        self.targetListCheckBoxStates[prefix] = listedTargets
                        if not Group:
                            for delSeries in [digit for digit in list(dictionary.keys()) if Counter(key[:1] for key in listedTargets.keys()).get(digit,0) <= 1]:
                                dictionary.pop(delSeries,None)
                        self.CreateCheckBoxList(canvasFrame,listedTargets,dictionary,FPF,Group)
                        self.updateTargetListScrollregion(canvasFrame,canvas)



    def CreateCheckBoxList(self,frame: ttk.Frame, CheckBoxStates,seriesDict,FPFSelection = False,GroupSelection = False):
        def ShowContextMenu(event,widget: Widget):
            text = widget.cget("text") if widget.winfo_exists() else None
            targetContextMenu.delete(0,END)
            prefix = frame.master.master.cget("text")
            if GroupSelection == False:
                targetContextMenu.add_command(label="Copy Grid",command=lambda w=widget,t=text,p=prefix: CopyGrid(w,t,p))
                targetContextMenu.add_command(label="Clock Splash Offset",command=lambda w=widget,t=text,p=prefix: ClockSplashOffset(w,t,p))
            targetContextMenu.add_command(label="Delete Fire mission",command=lambda: self.UIMaster.ClearTargetAndMission(mission=prefix,index=text))
            targetContextMenu.post(event.x_root,event.y_root)
        def CopyGrid(widget: Widget,text,prefix):
            try:
                if widget.winfo_exists():
                    loadedTarget = self.UIMaster.castJson.Load(source=JsonSource.TARGET)[prefix][widget.cget("text")]
                    grid = loadedTarget["GridX"]+loadedTarget["GridY"]
                    pyperclip.copy(grid)
                    text = widget.cget("text")
                else:
                    loadedTarget = self.UIMaster.castJson.Load(source=JsonSource.TARGET)[prefix][text]
                    grid = loadedTarget["GridX"]+loadedTarget["GridY"]
                    pyperclip.copy(grid)
                self.UIMaster.StatusMessageLog(privateMessage=f"Copied {prefix}-{text} grid {grid} to clipboard")
            except Exception as e:
                self.UIMaster.StatusMessageErrorDump(e,errorMessage=f"Failed to copy grid from {prefix}-{text}")
        def ClockSplashOffset(widget: Widget,text,prefix):
            try:
                if widget.winfo_exists():
                    self.UIMaster.clock.clockHandOffset = (float(self.UIMaster.castJson.Load(source=JsonSource.FIREMISSION)[self.UIMaster.fireMission.fireMissionNotebook.tab(self.UIMaster.fireMission.fireMissionNotebook.select(),"text")][f"{prefix}-{widget.cget('text')}"]["TOF"]))
                    textTemp = widget.cget("text")
                    self.UIMaster.clock.clockOffsetStrVar.set(f"{prefix}-{textTemp}")
                else:
                    self.UIMaster.clock.clockHandOffset = (float(self.UIMaster.castJson.Load(source=JsonSource.FIREMISSION)[self.UIMaster.fireMission.fireMissionNotebook.tab(self.UIMaster.fireMission.fireMissionNotebook.select(),"text")][text]["TOF"]))
                    self.UIMaster.clock.clockOffsetStrVar.set(text)
            except KeyError: self.UIMaster.StatusMessageLog(message=f"Calculated Fire Mission {prefix}-{text} is not found or calculated")
            except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage=f"Failed to send Clock splash offset from {prefix}-{text}")
        targetContextMenu = Menu(self.UIMaster.root,tearoff=False)
        for widget in frame.winfo_children():
            widget.destroy()
        series = []
        for key in CheckBoxStates.keys():
            series.append(str(key)[:1])
        row = 0
        currentSeries = ""
        for item, (var1, var2) in CheckBoxStates.items():
            if series.count(item[:1]) ==1 or GroupSelection:
                sep = ttk.Separator(frame,orient="horizontal")
                sep.grid(row=row,column=0,columnspan=5,sticky="WE",pady="4")
                row+=1
                if self.windowFireMissionEditSafety.get() == "1":
                    chk1 = ttk.Checkbutton(frame, variable=var1,command=self.RequestEditFireMissions,state="disabled")
                elif FPFSelection == False and self.FPFEditSelected ==True:
                    chk1 = ttk.Checkbutton(frame, variable=var1,command=self.RequestEditFireMissions,state="disabled")
                else:
                    chk1 = ttk.Checkbutton(frame, variable=var1,command=self.RequestEditFireMissions,state="normal")
                chk2 = ttk.Checkbutton(frame, variable=var2)
                lbl = ttk.Label(frame,text=item)
                if GroupSelection == False:
                    chk1.bind("<Enter>",self.OnMouseEnter)
                    chk2.bind("<Enter>",self.OnMouseEnter)
                    lbl.bind("<Enter>",self.OnMouseEnter)
                lbl.bind("<Button-3>",lambda event,widget=lbl: ShowContextMenu(event,widget))
                chk1.grid(row=row,column=0,padx=0,pady=0,sticky="w")
                chk2.grid(row=row,column=1,padx=0,pady=0,sticky="w")
                lbl.grid(row=row,column=2,columnspan=3,padx=0,pady=0,sticky="w")
                row += 1
            else:
                if currentSeries != item[:1]:
                    currentSeries = item[:1]
                    sep = ttk.Separator(frame,orient="horizontal")
                    sep.grid(row=row,column=0,columnspan=5,sticky="WE",pady="4")
                    row+=1
                    try:
                        if self.windowFireMissionEditSafety.get() == "1":
                            but1 = ttk.Checkbutton(frame,variable=seriesDict[item[:1]][0],command=lambda *args: self.SeriesSelect(1,frame,CheckBoxStates),state="disabled")
                        elif FPFSelection == False and self.FPFEditSelected ==True:
                            but1 = ttk.Checkbutton(frame,variable=seriesDict[item[:1]][0],command=lambda *args: self.SeriesSelect(1,frame,CheckBoxStates),state="disabled")
                        else:
                            but1 = ttk.Checkbutton(frame,variable=seriesDict[item[:1]][0],command=lambda *args: self.SeriesSelect(1,frame,CheckBoxStates),state="normal")
                    except:
                        seriesDict[item[:1]] = (BooleanVar(),BooleanVar())
                        if self.windowFireMissionEditSafety.get() == "1":
                            but1 = ttk.Checkbutton(frame,variable=seriesDict[item[:1]][0],command=lambda *args: self.SeriesSelect(1,frame,CheckBoxStates),state="disabled")
                        elif FPFSelection == False and self.FPFEditSelected ==True:
                            but1 = ttk.Checkbutton(frame,variable=seriesDict[item[:1]][0],command=lambda *args: self.SeriesSelect(1,frame,CheckBoxStates),state="disabled")
                        else:
                            but1 = ttk.Checkbutton(frame,variable=seriesDict[item[:1]][0],command=lambda *args: self.SeriesSelect(1,frame,CheckBoxStates),state="normal")
                    but2 = ttk.Checkbutton(frame,variable=seriesDict[item[:1]][1],command=lambda *args: self.SeriesSelect(2,frame,CheckBoxStates))
                    lblS = ttk.Label(frame,text=item[:1])
                    but1.grid(row=row,column=0,padx=0,pady=0,sticky="w")
                    but2.grid(row=row,column=1,padx=0,pady=0,sticky="w")
                    lblS.grid(row=row,column=2,padx=0,pady=0,sticky="w")
                    row += 1
                    sep = ttk.Separator(frame,orient="vertical")
                    sep.grid(row=row,column=1,rowspan=series.count(item[:1]),sticky="NES")
                if self.windowFireMissionEditSafety.get() == "1":
                    chk1 = ttk.Checkbutton(frame, variable=var1,command=self.RequestEditFireMissions,state="disabled")
                elif FPFSelection == False and self.FPFEditSelected ==True:
                    chk1 = ttk.Checkbutton(frame, variable=var1,command=self.RequestEditFireMissions,state="disabled")
                else:
                    chk1 = ttk.Checkbutton(frame, variable=var1,command=self.RequestEditFireMissions,state="normal")
                chk1.bind("<Enter>",self.OnMouseEnter)
                chk2 = ttk.Checkbutton(frame, variable=var2)
                chk2.bind("<Enter>",self.OnMouseEnter)
                lbl = ttk.Label(frame,text=item)
                lbl.bind("<Enter>",self.OnMouseEnter)
                lbl.bind("<Button-3>",lambda event,widget=lbl: ShowContextMenu(event,widget))
                chk1.grid(row=row,column=2,padx=0,pady=0,sticky="w")
                chk2.grid(row=row,column=3,padx=0,pady=0,sticky="w")
                lbl.grid(row=row,column=4,padx=0,pady=0,sticky="w")
                row += 1
            if currentSeries != item[:1]:
                currentSeries = item[:1]
        return CheckBoxStates
    
    def SeriesSelect(self,checkbox,frame,Checkbox_vars):
        focusedWidget = frame.focus_get()
        grid_info = focusedWidget.grid_info()
        focused_row = grid_info.get("row")
        selection=""
        for widget in frame.winfo_children():
            if widget.grid_info().get("row")==focused_row and type(widget) == ttk.Label:
                selection = widget["text"]
        for item, (var1, var2) in Checkbox_vars.items():
            if item[:1] == selection and self.UIMaster.root.tk.getboolean(self.UIMaster.root.tk.globalgetvar(focusedWidget.cget("variable"))) == True:
                if checkbox == 1:
                    var1.set(True)
                elif checkbox == 2:
                    var2.set(True)
            if item[:1] == selection and self.UIMaster.root.tk.getboolean(self.UIMaster.root.tk.globalgetvar(focusedWidget.cget("variable"))) == False:
                if checkbox == 1:
                    var1.set(False)
                elif checkbox == 2:
                    var2.set(False)
        if checkbox == 1:
            self.RequestEditFireMissions()
    
    def OnMouseEnter(self,event):
        widget: Widget = event.widget
        grid_info = widget.grid_info()
        focused_row = grid_info.get("row")
        try:
            for widg in self.UIMaster.root.nametowidget(widget.winfo_parent()).winfo_children():
                if widg.grid_info().get("row") == focused_row:
                    if type(widg) == ttk.Label:
                        labelframe = self.UIMaster.root.nametowidget(self.UIMaster.root.nametowidget(self.UIMaster.root.nametowidget(widget.winfo_parent()).winfo_parent()).winfo_parent())
                        if labelframe["text"] == "LR":
                            self.UIMaster.statusbar.statusReferenceLabel["text"] = "LR-"+ widg["text"]
                            self.UIMaster.statusbar.statusGridLabel["text"] = self.targetList["LR"][widg["text"]]["GridX"]+","+ self.targetList["LR"][widg["text"]]["GridY"]
                            self.UIMaster.statusbar.statusHeightLabel["text"] = self.targetList["LR"][widg["text"]]["Height"]
                        if labelframe["text"] == "XY":
                            self.UIMaster.statusbar.statusReferenceLabel["text"] = "XY-"+ widg["text"]
                            self.UIMaster.statusbar.statusGridLabel["text"] = self.targetList["XY"][widg["text"]]["GridX"]+","+ self.targetList["XY"][widg["text"]]["GridY"]
                            self.UIMaster.statusbar.statusHeightLabel["text"] = self.targetList["XY"][widg["text"]]["Height"]
                        if labelframe["text"] == "FPF":
                            self.UIMaster.statusbar.statusReferenceLabel["text"] = "FPF-"+widg["text"]
                            self.UIMaster.statusbar.statusGridLabel["text"] = self.targetList["FPF"][widg["text"]]["GridX"]+","+ self.targetList["FPF"][widg["text"]]["GridY"]
                            self.UIMaster.statusbar.statusHeightLabel["text"] = self.targetList["FPF"][widg["text"]]["Height"]
                        if labelframe["text"] == "Group":
                            self.UIMaster.statusbar.statusReferenceLabel["text"] = widg["text"]
                            self.UIMaster.statusbar.statusGridLabel["text"] = self.targetList["Group"][widg["text"]]["GridX"]+","+ self.targetList["Group"][widg["text"]]["GridY"]
                            self.UIMaster.statusbar.statusHeightLabel["text"] = self.targetList["Group"][widg["text"]]["Height"]
        except:self.UIMaster.StatusMessageLog(message="",privateMessage="Unable to display target details on the status bar")


    def updateTargetListScrollregion(self,frame: ttk.Frame,canvas: Canvas):
        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def CalculateSnapshot(self,IDFPDict,IDFP,width, depth,tgtX,tgtY,tgtHeight,temperature,humidity,pressure,windDirection,windMagnitude,windDynamic):
        try:
            self.targetListCalculate.config(state="disabled")
            self.UIMaster.statusbar.statusProgressBar.config(value=0,mode="determinate")
            if int(depth) > 0:
                calculations = 3
            else:
                calculations = 1
            self.UIMaster.statusbar.statusProgressBar["maximum"] = int(calculations)
            states = self.UIMaster.castJson.Load(source=JsonSource.COMMON)
            charge = -1 if IDFPDict[IDFP]["ForceCharge"] == 0 else int(IDFPDict[IDFP]["Charge"])
            if width == 0 and depth == 0:
                solution = AF.Solution(self.UIMaster.exeDir,
                                        artyX=IDFPDict[IDFP]["GridX"],
                                        artyY=IDFPDict[IDFP]["GridY"],
                                        system=states["system"],
                                        fireAngle=IDFPDict[IDFP]["Trajectory"],
                                        tgtX=tgtX,
                                        tgtY=tgtY,
                                        artyHeight=IDFPDict[IDFP]["Height"],
                                        targetHeight=tgtHeight,
                                        maxHeight=self.UIMaster.maxTerrainHeight,
                                        windDirection=windDirection,
                                        windMagnitude=windMagnitude,
                                        windDynamic=windDynamic,
                                        temperature=temperature,
                                        humidity=humidity,
                                        pressure=pressure,
                                        charge=charge
                                        )
            elif width != 0 or depth != 0:
                solution = AF.Box(self.UIMaster.exeDir,
                                    deviationLength=depth/2,
                                    deviationWidth=width/2,
                                    artyX=IDFPDict[IDFP]["GridX"],
                                    artyY=IDFPDict[IDFP]["GridY"],
                                    system=states["system"],
                                    fireAngle=IDFPDict[IDFP]["Trajectory"],
                                    tgtX=tgtX,
                                    tgtY=tgtY,
                                    artyHeight=IDFPDict[IDFP]["Height"],
                                    targetHeight=tgtHeight,
                                    maxHeight=self.UIMaster.maxTerrainHeight,
                                    windDirection=windDirection,
                                    windMagnitude=windMagnitude,
                                    windDynamic=windDynamic,
                                    temperature=temperature,
                                    humidity=humidity,
                                    pressure=pressure,
                                    charge=charge,
                                    progressbar=self.UIMaster.statusbar.statusProgressBar
                                    )
            elif width != 0 and depth == 0:
                solution = AF.Line(self.UIMaster.exeDir,
                                    orientation="Horizontal",
                                    deviation=width/2,
                                    artyX=IDFPDict[IDFP]["GridX"],
                                    artyY=IDFPDict[IDFP]["GridY"],
                                    system=states["system"],
                                    fireAngle=IDFPDict[IDFP]["Trajectory"],
                                    tgtX=tgtX,
                                    tgtY=tgtY,
                                    artyHeight=IDFPDict[IDFP]["Height"],
                                    targetHeight=tgtHeight,
                                    maxHeight=self.UIMaster.maxTerrainHeight,
                                    windDirection=windDirection,
                                    windMagnitude=windMagnitude,
                                    windDynamic=windDynamic,
                                    temperature=temperature,
                                    humidity=humidity,
                                    pressure=pressure,
                                    charge=charge,
                                    progressbar=self.UIMaster.statusbar.statusProgressBar
                                    )
            else:
                solution = AF.Line(self.UIMaster.exeDir,
                                    orientation="Vertical",
                                    deviation=depth/2,
                                    artyX=IDFPDict[IDFP]["GridX"],
                                    artyY=IDFPDict[IDFP]["GridY"],
                                    system=states["system"],
                                    fireAngle=IDFPDict[IDFP]["Trajectory"],
                                    tgtX=tgtX,
                                    tgtY=tgtY,
                                    artyHeight=IDFPDict[IDFP]["Height"],
                                    targetHeight=tgtHeight,
                                    maxHeight=self.UIMaster.maxTerrainHeight,
                                    windDirection=windDirection,
                                    windMagnitude=windMagnitude,
                                    windDynamic=windDynamic,
                                    temperature=temperature,
                                    humidity=humidity,
                                    pressure=pressure,
                                    charge=charge,
                                    progressbar=self.UIMaster.statusbar.statusProgressBar
                                    )
            self.UIMaster.StatusMessageLog(message="Calculated snapshot, Range: {}m, Bearing: {:03d}°".format(int(solution["Range"]),int(solution["Bearing"]*180/np.pi)))
            self.UIMaster.statusbar.statusProgressBar.config(value = self.UIMaster.statusbar.statusProgressBar.cget("value") + 1)
            self.UIMaster.statusbar.statusProgressBar.update()
            return solution
        except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage="Failed to calculate snapshot")
        finally: self.targetListCalculate.config(state="normal")



    def Calculate(self):
        try:
            self.targetListCalculate.config(state="disabled")
            self.UIMaster.statusbar.statusProgressBar.config(value=0,mode="determinate")
            calculations = 0
            targets = self.UIMaster.castJson.Load(source=JsonSource.TARGET)
            def CalculationPhasesTotal(mission):
                nonlocal calculations
                for target, (edit, calculate) in self.targetListCheckBoxStates[mission].items():
                    if calculate.get() == True:
                        calculations += 1
                        try:
                            if targets[mission][target]["Mutator"] == "Line":
                                if targets[mission][target]["Orientation"] == "Vertical":
                                    calculations += 2
                            elif targets[mission][target]["Mutator"] == "Box":
                                calculations += 2
                            elif targets[mission][target]["Mutator"] == "LineMultiPoint":
                                if targets[mission][target]["Explicit"] == True:
                                    calculations += 1
                        except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage=f"Failed to get {mission}-{target} mutator")
                            

            CalculationPhasesTotal("FPF")
            CalculationPhasesTotal("LR")
            CalculationPhasesTotal("XY")
            for target, (edit, calculate) in self.targetListCheckBoxStates["Group"].items():
                if calculate.get() == True:
                    calculations += 1
                    try:
                        if targets["Group"][target]["Mutator"] == "Line":
                            if targets["Group"][target]["Orientation"] == "Vertical":
                                calculations += 2
                        elif targets["Group"][target]["Mutator"] == "Box":
                            calculations += 2
                        elif targets["Group"][target]["Mutator"] == "LineMultiPoint":
                            if targets["Group"][target]["Explicit"] == True:
                                calculations += 2
                    except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage=f"Failed to get Group mission-{target} mutator")

            self.UIMaster.statusbar.statusProgressBar["maximum"] = int(calculations)
            states = {}
            IDFPDict = {}
            states = self.UIMaster.castJson.Load(source=JsonSource.COMMON)
            IDFPDict = self.UIMaster.castJson.Load(source=JsonSource.IDFP)
            def solutions (details,idfp):
                charge = -1 if IDFPDict[idfp]["ForceCharge"] == 0 else int(IDFPDict[idfp]["Charge"])
                if details["Mutator"] == "None":
                    solution = AF.Solution(baseDir=self.UIMaster.exeDir,
                                            artyX=IDFPDict[idfp]["GridX"],
                                            artyY=IDFPDict[idfp]["GridY"],
                                            system=states["system"],
                                            fireAngle=IDFPDict[idfp]["Trajectory"],
                                            tgtX=details["GridX"],tgtY=details["GridY"],
                                            artyHeight=IDFPDict[idfp]["Height"],
                                            targetHeight=details["Height"],
                                            maxHeight=self.UIMaster.maxTerrainHeight,
                                            windDirection=states["windDirection"],
                                            windMagnitude=states["windMagnitude"],
                                            windDynamic=int(states["windDynamic"]),
                                            humidity=states["airHumidity"],
                                            temperature=states["airTemperature"],
                                            pressure=states["airPressure"],
                                            charge=charge
                                        )
                    #############TERRAIN AVOIDANCE +1 Charge
                    solution["Effect"],solution["Length"],solution["Condition"],solution["Mutator"],solution["Trajectory"] = details["Effect"],details["Length"],details["Condition"],details["Mutator"],IDFPDict[idfp]["Trajectory"]
                    if details["Condition"] == "Time":
                        solution["Time"] = {
                            "Hour": details["Time"]["Hour"],
                            "Minute": details["Time"]["Minute"],
                            "Second": details["Time"]["Second"]
                        }
                    del solution["LowPositions"]
                    return solution
                elif details["Mutator"] == "Line":
                    deviation = details["Depth"] if details["Orientation"] == "Vertical" else details["Width"]
                    solution = AF.Line(baseDir=self.UIMaster.exeDir,
                            orientation=details["Orientation"],
                            deviation=deviation,
                            artyX=IDFPDict[idfp]["GridX"],
                            artyY=IDFPDict[idfp]["GridY"],
                            system=states["system"],
                            fireAngle=IDFPDict[idfp]["Trajectory"],
                            tgtX=details["GridX"],tgtY=details["GridY"],
                            artyHeight=IDFPDict[idfp]["Height"],
                            targetHeight=details["Height"],
                            maxHeight=self.UIMaster.maxTerrainHeight,
                            windDirection=states["windDirection"],
                            windMagnitude=states["windMagnitude"],
                            windDynamic=int(states["windDynamic"]),
                            humidity=states["airHumidity"],
                            temperature=states["airTemperature"],
                            pressure=states["airPressure"],
                            charge=charge,
                            progressbar=self.UIMaster.statusbar.statusProgressBar
                    )
                    solution["Effect"],solution["Length"],solution["Condition"],solution["Mutator"],solution["Orientation"],solution["Deviation"],solution["Trajectory"] = details["Effect"],details["Length"],details["Condition"],details["Mutator"],details["Orientation"],deviation,IDFPDict[idfp]["Trajectory"]
                    if details["Condition"] == "Time":
                        solution["Time"] = {
                            "Hour": details["Time"]["Hour"],
                            "Minute": details["Time"]["Minute"],
                            "Second": details["Time"]["Second"]
                        }
                    del solution["LowPositions"]
                    return solution
                
                elif details["Mutator"] == "Box":
                    solution = AF.Box(baseDir=self.UIMaster.exeDir,
                            deviationLength=details["Depth"],
                            deviationWidth=details["Width"],
                            artyX=IDFPDict[idfp]["GridX"],
                            artyY=IDFPDict[idfp]["GridY"],
                            system=states["system"],
                            fireAngle=IDFPDict[idfp]["Trajectory"],
                            tgtX=details["GridX"],tgtY=details["GridY"],
                            artyHeight=IDFPDict[idfp]["Height"],
                            targetHeight=details["Height"],
                            maxHeight=self.UIMaster.maxTerrainHeight,
                            windDirection=states["windDirection"],
                            windMagnitude=states["windMagnitude"],
                            windDynamic=int(states["windDynamic"]),
                            humidity=states["airHumidity"],
                            temperature=states["airTemperature"],
                            pressure=states["airPressure"],
                            charge=charge,
                            progressbar=self.UIMaster.statusbar.statusProgressBar
                    )
                    solution["Effect"],solution["Length"],solution["Condition"],solution["Mutator"],solution["Trajectory"] = details["Effect"],details["Length"],details["Condition"],details["Mutator"],IDFPDict[idfp]["Trajectory"]
                    if details["Condition"] == "Time":
                        solution["Time"] = {
                            "Hour": details["Time"]["Hour"],
                            "Minute": details["Time"]["Minute"],
                            "Second": details["Time"]["Second"]
                        }
                    del solution["LowPositions"]
                    return solution
                else:
                    None
                    #################BOXBOXBOX
            def CalculationIteration(mission):
                for target, (edit,calculate) in self.targetListCheckBoxStates[mission].items():
                    if calculate.get() == True:
                        details = targets[mission][target]
                        idfpSelection = self.UIMaster.castJson.Load(source=JsonSource.COMMON,localOverride=True)["IDFPSelection"]
                        for idfp in [list(IDFPDict.keys())[i] for i in list(idfpSelection)]:
                            try :
                                self.UIMaster.StatusMessageLog(message=f"Beginning calculation of {mission}-{target}")
                                solution = solutions(details,idfp)
                            except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage=f"Failed to calculate {mission}-{target}")
                            else:
                                fireMissions = self.UIMaster.castJson.Load(source=JsonSource.FIREMISSION)
                                try: fireMissions[idfp][f"{mission}-{target}"] = solution
                                except KeyError: fireMissions[idfp] = {f"{mission}-{target}" : solution}
                                self.UIMaster.castJson.Save(source=JsonSource.FIREMISSION,newEntry=fireMissions)
                                self.UIMaster.SyncUpdate(JsonSource.FIREMISSION)
                                self.UIMaster.StatusMessageLog(message="Calculated {}-{}, Range: {}m, Bearing: {:03d}°".format(mission,target,int(solution["Range"]),int(solution["Bearing"]*180/np.pi)))
                                self.UIMaster.statusbar.statusMessageLabel.update()
                                self.UIMaster.statusbar.statusProgressBar.config(value = self.UIMaster.statusbar.statusProgressBar.cget("value") + 1)
                                self.UIMaster.statusbar.statusProgressBar.update()
            CalculationIteration("FPF")
            CalculationIteration("LR")
            CalculationIteration("XY")
            CalculationIteration("Group")
        except Exception as e:
            self.UIMaster.StatusMessageErrorDump(e,errorMessage=f"Failed to Calculate fire missions")
        finally:
            self.targetListCalculate.config(state="normal")
            self.UIMaster.root.bell()

    def CalculateThread(self):
        if hasattr(self,"thread"):
            if not self.thread.is_alive():
                self.thread = threading.Thread(target=self.Calculate,daemon=True)
                self.thread.start()
        else:
            self.thread = threading.Thread(target=self.Calculate,daemon=True)
            self.thread.start()



    def MenuSafetyClear(self,*args):
        if int(self.UIMaster.mainMenu.windowResetSafety.get())==0:
            self.UIMaster.mainMenu.resetMenu.entryconfigure("Message Log",state="normal",activebackground="red")
            self.UIMaster.mainMenu.resetMenu.entryconfigure("IDFP Positions",state="normal",activebackground="red")
            self.UIMaster.mainMenu.resetMenu.entryconfigure("Friendly Positions",state="normal",activebackground="red")
            self.UIMaster.mainMenu.resetMenu.entryconfigure("Targets + Fire Missions",state="normal",activebackground=self.UIMaster.mainMenu.resetMenu.cget("activebackground"))
            self.UIMaster.mainMenu.resetMenu.entryconfigure("Fire Missions",state="normal",activebackground=self.UIMaster.mainMenu.resetMenu.cget("activebackground"))
            self.UIMaster.mainMenu.resetMenu.entryconfigure("Everything",state="normal",activebackground="red")
        else:
            self.UIMaster.mainMenu.resetMenu.entryconfigure("Message Log",state="disabled",activebackground="#F2F2F2")
            self.UIMaster.mainMenu.resetMenu.entryconfigure("IDFP Positions",state="disabled",activebackground="#F2F2F2")
            self.UIMaster.mainMenu.resetMenu.entryconfigure("Friendly Positions",state="disabled",activebackground="#F2F2F2")
            self.UIMaster.mainMenu.resetMenu.entryconfigure("Targets + Fire Missions",state="disabled",activebackground="#F2F2F2")
            self.UIMaster.mainMenu.resetMenu.entryconfigure("Fire Missions",state="disabled",activebackground="#F2F2F2")
            self.UIMaster.mainMenu.resetMenu.entryconfigure("Everything",state="disabled",activebackground="#F2F2F2")

class FireMissions(UIComponentBase):
    def __init__(self, UIMaster):
        super().__init__(UIMaster)
        self.fireMissionWindowOpen = False
        self.fireMissionNotebookFrameDict = {}
        self.fireMissions = {}
        self.preSortedFireMissions = {}
    def Initialise(self,frame):
        self.fireMissionNotebook = ttk.Notebook(frame,width=500)
        self.fireMissionNotebook.bind("<Button-3>", self.NotebookTabMenu)
        self.fireMissionNotebook.grid(column="0",row="0", sticky="NESW")
    def NotebookTabMenu(self,event):
        clickedTab = self.fireMissionNotebook.tk.call(self.fireMissionNotebook,"identify", "tab", event.x, event.y)
        if clickedTab != "":
            tabName = self.fireMissionNotebook.tab(clickedTab,option="text")
            IDFPMenu = Menu(self.UIMaster.root,tearoff=False)
            IDFPMenu.add_command(label=f"Popout {tabName}",command=lambda: self.FireMissionIDFPpopout(tabName))
            IDFPMenu.post(event.x_root,event.y_root)
    def FireMissionIDFPpopout(self,tabName):
        def Close():
            self.fireMissionNotebookFrameDict.pop(tabName,None)
            fireMissionToplevel.destroy()
        fireMissionToplevel = Toplevel(self.UIMaster.root)
        fireMissionToplevel.attributes("-topmost",True)
        fireMissionToplevel.title(f"{tabName} Fire missions")
        fireMissionToplevel.geometry("500x1000")
        fireMissionToplevel.resizable(False,True)
        fireMissionToplevel.iconbitmap(self.UIMaster.exeDir/"Functions"/"icons"/"scope.ico")
        fireMissionWindow = fireMissionToplevel.winfo_toplevel()
        fireMissionWindow.anchor("n")
        fireMissionWindow.grid_columnconfigure(0,weight=1)
        fireMissionWindow.grid_rowconfigure(0,weight=1)
        fireMissionWindowFrame = ttk.Frame(fireMissionWindow,width="500",padding = 0)
        self.fireMissionNotebookFrameDict[tabName] = [fireMissionWindowFrame,fireMissionToplevel]
        self.FireMisisonTextFrameConfiguration(fireMissionWindowFrame)
        self.fireMissionWindowOpen = True
        fireMissionToplevel.protocol("WM_DELETE_WINDOW",Close)

    def SortFireMissions(self,fireMissions:dict):
        def sortKey(item: str):
                    segments = []
                    for char in item.split("-")[1]:
                        if char.isdigit():
                            segments.append((False, int(char)))
                        else:
                            segments.append((True,char))
                    return segments
        sortedFireMission = {}
        for idfp,missions in fireMissions.items():
            if missions != {}:
                for mission in missions.keys():
                    if mission != "Group":
                        sortedFireMission[idfp] =  {key: fireMissions[idfp][key] for key in sorted(fireMissions[idfp].keys(),key=sortKey)}
                    else:
                        sortedFireMission[idfp][mission]=mission.values()
        return sortedFireMission
                


    def SyncFireMissions(self,newFireMissions):
        if newFireMissions != self.preSortedFireMissions or self.fireMissionWindowOpen:
            self.preSortedFireMissions = newFireMissions
            print(newFireMissions)
            self.fireMissions = self.SortFireMissions(newFireMissions)
            self.FireMissionTab(self.fireMissions)
            self.FireMissionDisplayUpdate(self.fireMissions)
            self.fireMissionWindowOpen = False
    
    def FireMissionTab(self,fireMissions):
        tabs = []
        try: fireMissions.keys()
        except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage="Fire Mission JSON error")
        else:
            for tabId in self.fireMissionNotebook.tabs():
                tabs.append(self.fireMissionNotebook.tab(tabId,option="text"))
                if self.fireMissionNotebook.tab(tabId,option="text") not in fireMissions.keys():
                    self.fireMissionNotebook.forget(tabId)
                    try:
                        if self.fireMissionNotebook.tab(tabId,option="text") in self.fireMissionNotebookFrameDict.keys():
                            try: Toplevel(self.fireMissionNotebookFrameDict[1]).destroy()
                            except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage=f"Failed to close {self.fireMissionNotebook.tab(tabId,option='text')} window")
                            try: self.fireMissionNotebookFrameDict.pop(self.fireMissionNotebook.tab(tabId,option="text"),None)
                            except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage=f"Failed to remove {self.fireMissionNotebook.tab(tabId,option='text')} window from dictionary")
                        elif "cast"+self.fireMissionNotebook.tab(tabId,option="text") in self.fireMissionNotebookFrameDict.keys():
                            try: self.fireMissionNotebookFrameDict.pop("cast"+self.fireMissionNotebook.tab(tabId,option="text"),None)
                            except Exception as e: self.UIMaster.StatusMessageErrorDump(e,errorMessage=f"Failed to remove {self.fireMissionNotebook.tab(tabId,option='text')} reference from dictionary")
                    except: None
                    try: del self.fireMissionNotebookFrameDict[self.fireMissionNotebook.tab(tabId,option="text")]
                    except: None
            for idfp in fireMissions.keys():
                if idfp not in tabs:
                    self.fireMissionNotebookFrame = ttk.Frame(self.fireMissionNotebook,width="500")
                    self.fireMissionNotebookFrameDict["cast"+idfp] = self.fireMissionNotebookFrame
                    self.FireMisisonTextFrameConfiguration(self.fireMissionNotebookFrame)
                    self.fireMissionNotebook.add(self.fireMissionNotebookFrame,text=idfp,sticky="NESW",padding="10")
    def FireMisisonTextFrameConfiguration(self,fireMissionNotebookFrame: ttk.Frame):
        fireMissionNotebookFrame.grid(row=0,column=0,sticky="NESW")
        fireMissionNotebookFrame.grid_rowconfigure(0,weight=1)
        fireMissionNotebookFrame.grid_rowconfigure(1,minsize=20)
        fireMissionNotebookFrame.grid_columnconfigure(0,weight=1)
        fireMissionNotebookFrame.grid_columnconfigure(1,minsize=20)
        fireMissionNotebookFrameText = Text(fireMissionNotebookFrame,wrap="none",background="black",foreground="black",width=55,tabs=("2c","5c","6.5c","3c"))#bg="#BBBBBB",
        fireMissionNotebookFrameText.tag_configure("default",font=("Microsoft Tai Le",10),background="white")
        fireMissionNotebookFrameText.tag_configure("line",font=("Microsoft Tai Le",4),background="white")
        fireMissionNotebookFrameText.tag_configure("XY",font=("Microsoft Tai Le",12,"bold"),relief="ridge",borderwidth="3",spacing1=5,spacing2=5,spacing3=5,background="#2C5F2D",foreground="#FFE77A")
        fireMissionNotebookFrameText.tag_configure("LR",font=("Microsoft Tai Le",12,"bold"),relief="ridge",borderwidth="3",spacing1=5,spacing2=5,spacing3=5,background="#5B84B1",foreground="#FC766A")
        fireMissionNotebookFrameText.tag_configure("FPF",font=("Microsoft Tai Le",12,"bold"),relief="ridge",borderwidth="3",spacing1=5,spacing2=5,spacing3=5,foreground="white",background="#BB5050",bgstipple="@tempstipple.xbm")
        fireMissionNotebookFrameText.tag_configure("Group",font=("Microsoft Tai Le",12,"bold"),relief="ridge",borderwidth="3",spacing1=5,spacing2=5,spacing3=5,foreground="#D9514E",background="#006747",bgstipple="@tempstipple.xbm")
        fireMissionNotebookFrameText.tag_configure("bold",font=("Microsoft Tai Le",10,"bold"),background="white")
        fireMissionNotebookFrameText.tag_configure("border",relief="ridge",borderwidth="2",background="white")
        fireMissionNotebookFrameText.tag_configure("highlight",relief="raised",borderwidth="2",background="white")
        fireMissionNotebookFrameText.tag_configure("divide",font=("Microsoft Tai Le",4),background="grey",bgstipple="@tempstipple.xbm")
        yScroll = Scrollbar(fireMissionNotebookFrame,orient="vertical",command=fireMissionNotebookFrameText.yview)
        xScroll = Scrollbar(fireMissionNotebookFrame,orient="horizontal",command=fireMissionNotebookFrameText.xview)
        fireMissionNotebookFrameText.config(yscrollcommand = yScroll.set,xscrollcommand = xScroll.set,state="disabled")
        fireMissionNotebookFrameText.grid(row=0,column=0,sticky="nesw")
        yScroll.grid(row=0,column=1,sticky="ns")
        xScroll.grid(row=1,column=0,sticky="ew")

    def FireMissionDisplayUpdate(self,fireMissions):
        if self.fireMissionNotebookFrameDict!= {}:
            for idfp in fireMissions.keys():
                for tab,frame in self.fireMissionNotebookFrameDict.items():
                    if tab == idfp:
                        for widget in frame[0].winfo_children():
                            if type(widget) == Text:
                                widget["state"] = "normal"
                                widget.delete("1.0",END)
                                self.StandardFireMissionOutput(fireMissions,idfp,widget)
                    if tab == "cast"+idfp:
                        for widget in frame.winfo_children():
                            if type(widget) == Text:
                                widget["state"] = "normal"
                                widget.delete("1.0",END)
                                self.StandardFireMissionOutput(fireMissions,idfp,widget)   
        return True


    def StandardFireMissionOutput(self,fireMissions: dict,idfp: str,textWidget: Text):
        def Standard(details):
            try: 
                if details["Notes"]!= "":
                    textWidget.insert(END,"\t\t| Note: {}\n".format(details["Notes"]),("default","border"))
                else: textWidget.insert(END,"\n","border")
            except: textWidget.insert(END,"\n","border")
            textWidget.insert(END,"\t-----------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
            textWidget.insert(END,"\tEffect\t| {}\n\tLength\t| {}\n\tCondition\t| {}\n\tSystem\t| {}\n".format(details["Effect"],details["Length"],details["Condition"],details["System"]),("default","border"))
            textWidget.insert(END,"\t-----------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
            textWidget.insert(END,"\tRange\t| {:04d}".format(int(details["Range"])),("default","border"))
            try:
                if float(details["DeviationLength"]) > 1.0:
                    textWidget.insert(END," ± {} m\n".format(int(np.round(details["DeviationLength"]))),("default","border"))
                else:
                    textWidget.insert(END," m\n",("default","border"))
            except: textWidget.insert(END," m\n",("default","border"))
            try:
                if float(details["DeviationWidth"]) > 1.0:
                    textWidget.insert(END,"\tWidth\t| ± {} m\n".format(int(np.round(details["DeviationWidth"]))),("default","border"))
            except: None
            try:vertex = int(np.ceil(list(details["Vertex"])[2]/5)*5)
            except:vertex = details["Vertex"]
            textWidget.insert(END,"\tTrajectory\t| {} \n\tTOF\t| {:0.1f} s\n\tVertex\t| FL {:03d}\n\tImpact:\n\t         Angle\t| {:0.1f}°\n\t         Speed\t| {:0.1f} m/s\n".format(details["Trajectory"],float(details["TOF"]),vertex,details["ImpactAngle"],details["ImpactSpeed"]),("default","border"))
            try:
                details["ParallelCorrection"]
                textWidget.insert(END,"\t",("default","border"))
                textWidget.insert(END,"Wind Magnitude\t| {:0.1f} m/s\t".format(np.round(float(details["WindMagnitude"])*10)/10),("default"))
                textWidget.insert(END,"\n\t",("default","border"))
                textWidget.insert(END,"Crosswind\t| ±",("default"))
                textWidget.insert(END," {} ".format(int(np.round(float(details["PerpendicularCorrection"])))),("bold"))
                textWidget.insert(END,"mils\t",("default"))
                textWidget.insert(END,"\n\t",("default","border"))
                textWidget.insert(END,"Head/Tailwind\t| ±",("default"))
                textWidget.insert(END," {} ".format(int(np.round(float(details["ParallelCorrection"])))),("bold"))
                textWidget.insert(END,"mils\t",("default"))
                textWidget.insert(END,"\n",("default","border"))
                textWidget.insert(END,"\t-----------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
            except:
                None
            textWidget.insert(END,"")
            textWidget.insert(END,"\tCharge\t| ".format(details["Trajectory"],float(details["TOF"]),vertex),("default","border"))
            textWidget.insert(END," {} ".format(details["Charge"]),("bold","highlight"))
            textWidget.insert(END,"\n\t-----------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
            textWidget.insert(END,"\tAzimuth\t| ",("default","border"))
            
            textWidget.insert(END," {:06.1f} ".format(details["Azimuth"]*3200/np.pi),("bold","highlight"))
            try:
                if float(details["DeviationWidth"]) > 1.0:
                    azimuthDeviation = details["Azimuth"]-details["Left"] if (details["Azimuth"]-details["Left"]) > 0 else (details["Azimuth"]-details["Left"])+2*np.pi
                    textWidget.insert(END," ± {} mils\n\t⇐      ".format(np.round(azimuthDeviation*3200/np.pi)),("default","border"))
                    textWidget.insert(END,"{:04d}".format(int(np.round(details["Left"]*3200/np.pi))),("bold","border"))
                    textWidget.insert(END,"\t|",("default","border"))
                    textWidget.insert(END,"\t{:04d}".format(int(np.round(details["Right"]*3200/np.pi))),("bold","border"))
                    textWidget.insert(END,"      ⇒ \n",("default","border"))
                else: textWidget.insert(END," mils\n",("default","border"))
            except: textWidget.insert(END," mils\n",("default","border"))
            textWidget.insert(END,"\t-----------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
            textWidget.insert(END,"\tElevation\t| ",("default","border"))
            textWidget.insert(END," {:06.1f} ".format(details["Elevation"]),("bold","highlight"))
            try:
                if float(details["DeviationLength"]) > 1.0:
                    elevationDeviation = (abs(details["Elevation"]-details["Near"])+abs(details["Elevation"]-details["Far"]))/2
                    textWidget.insert(END," ± {} mils\n".format(np.round(elevationDeviation)),("default","border"))
                    textWidget.insert(END,"\t⇓       ",("default","border"))
                    textWidget.insert(END,"{:04d}".format(int(np.round(details["Near"]))),("bold","border"))
                    textWidget.insert(END,"\t| ",("default","border"))
                    textWidget.insert(END,"\t{:04d}".format(int(np.round(details["Far"]))),("bold","border"))
                    textWidget.insert(END,"       ⇑\n",("default","border"))
                else: textWidget.insert(END," mils\n",("default","border"))
            except: textWidget.insert(END," mils\n",("default","border"))
        #FPF
        for reference, details in fireMissions[idfp].items():
            if reference[:2] == "FP" and reference.count(",") == 0:
                if textWidget.get("1.0", END).strip()!="": textWidget.insert(END,"\n",("default","divide"))
                textWidget.insert(END," {} ".format(reference),"FPF")
                Standard(details)
        #LR
        for reference, details in fireMissions[idfp].items():
            if reference[:2] == "LR" and reference.count(",") == 0:
                if textWidget.get("1.0", END).strip()!="": textWidget.insert(END,"\n",("default","divide"))
                textWidget.insert(END," {} ".format(reference),"LR")
                Standard(details)
        #XY
        for reference, details in fireMissions[idfp].items():
            if reference[:2] == "XY" and reference.count(",") == 0:
                if textWidget.get("1.0", END).strip()!="": textWidget.insert(END,"\n",("default","divide"))
                textWidget.insert(END," {} ".format(reference),"XY")
                Standard(details)
        #Pairs
        for reference, details in fireMissions[idfp].items():
            if reference.count(",") > 0:
                if textWidget.get("1.0", END).strip()!="": textWidget.insert(END,"\n",("default","divide"))
                commaCount = 0
                textWidget.insert(END," ","Group")
                for char in reference:
                    if char !=",":
                        textWidget.insert(END,"{}".format(char),"Group")
                    elif commaCount == 0:
                        commaCount +=1
                        textWidget.insert(END," ","Group")
                        try:
                            if details["Notes"] != "":
                                textWidget.insert(END,"\t\t| Note: {}\n".format(details["Notes"]),("default","border"))
                            else:
                                textWidget.insert(END,"\n",("default","border"))
                        except:
                            textWidget.insert(END,"\n",("default","border"))
                        textWidget.insert(END," ","Group")
                    else:
                        commaCount+=1
                        textWidget.insert(END," ","Group")
                        textWidget.insert(END,"\n",("default","border"))
                        textWidget.insert(END," ","Group")
                textWidget.insert(END," ","Group")
                textWidget.insert(END,"\n",("default","border"))
                textWidget.insert(END,"\t-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
                textWidget.insert(END,"\tEffect\t| {}\t({})\n\tCondition\t| {}\n\tSystem\t| {}\n\tDistance\t| {} ± {} m\n\tWidth\t| {} ± {} m\n".format(details["PairedEffect"],details["Effect"],details["Condition"],details["System"],details["Distance"],details["Dispersion"],details["Width"],details["Dispersion"]),("default","border"))
                textWidget.insert(END,"\t-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
                textWidget.insert(END,"\tTrajectory\t| {} \n\tTOF\t| {:0.1f} s\n\tVertex\t| FL {} \n\tRound Count\t| ".format(details["Trajectory"],float(details["TOF"]),details["Vertex"]),("default","border"))
                textWidget.insert(END,"{} rounds\n".format(details["RoundCount"]),("bold","border"))
                textWidget.insert(END,"\tCharge\t| ",("default","border"))
                textWidget.insert(END,"{}\n".format(details["Charge"]),("bold","border"))
                textWidget.insert(END,"\t-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
                textWidget.insert(END,"\tAzimuth\t| ",("default","border"))
                textWidget.insert(END,"{:04d}".format(details["Azimuth"]),("bold","border"))
                textWidget.insert(END," ± ",("default","border"))
                textWidget.insert(END," {} ".format(details["AzimuthDeviation"]),("bold","highlight"))
                textWidget.insert(END," mils with ",("default","border"))
                textWidget.insert(END,"{}".format(details["AzimuthRounds"]),("bold","border"))
                textWidget.insert(END," rounds or lines\n\t⇐      ",("default","border"))
                textWidget.insert(END," {:04d} ".format(details["AzimuthLeft"]),("bold","highlight"))
                textWidget.insert(END,"\t|\t",("default","border"))
                textWidget.insert(END," {:04d} ".format(details["AzimuthRight"]),("bold","highlight"))
                textWidget.insert(END,"      ⇒ \n",("default","border"))
                textWidget.insert(END,"\t-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n",("line","border"))
                textWidget.insert(END,"\tElevation\t| ",("default","border"))
                textWidget.insert(END,"{:04d}".format(details["Elevation"]),("bold","border"))
                textWidget.insert(END," ± ",("default","border"))
                textWidget.insert(END," {} ".format(details["ElevationDeviation"]),("bold","highlight"))
                textWidget.insert(END," mils with ",("default","border"))
                textWidget.insert(END,"{}".format(details["ElevationRounds"]),("bold","border"))
                textWidget.insert(END," lines or rounds\n",("default","border"))
                if details["Trajectory"] == "High":
                    textWidget.insert(END,"\t⇓       ",("default","border"))
                    textWidget.insert(END," {:04d} ".format(details["ElevationHigh"]),("bold","highlight"))
                    textWidget.insert(END,"\t|\t",("default","border"))
                    textWidget.insert(END," {:04d} ".format(details["ElevationLow"]),("bold","highlight"))
                    textWidget.insert(END,"       ⇑\n",("default","border"))
                else:
                    textWidget.insert(END,"\t⇓       ",("default","border"))
                    textWidget.insert(END," {:04d} ".format(details["ElevationLow"]),("bold","highlight"))
                    textWidget.insert(END,"\t|\t",("default","border"))
                    textWidget.insert(END," {:04d} ".format(details["ElevationHigh"]),("bold","highlight"))
                    textWidget.insert(END,"       ⇑\n",("default","border"))
        textWidget["state"] = "disabled"
        return True
