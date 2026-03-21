testCommandLine = ["--json","server"]
version = "v0.1.0hotfix"
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import font
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import os
import sys
import traceback
import pandas as pd
import threading
import queue

# from pydub import AudioSegment
# from pydub.playback import play
from Functions import ArtilleryFunctions as AF, MapFunctions as Map
from Functions.JsonFunctions import JsonType, JsonSource, CastJson, UksfAccounts
from Functions.UI_Components import MainMenus,Statusbar,IDFPCreation,Atmospheric,Friendlies,TargetCreation,TargetDetails,Clock,Notes,Targets,FireMissions

class Cast():
    def __init__(self,version):
        self.version = version
        if len(sys.argv) > 1:
            for index,arg in enumerate(sys.argv):
                if str(arg) == "--json":
                    if str(sys.argv[index+1]).lower() == "local":
                        self.jsonType = JsonType.LOCAL
                    elif str(sys.argv[index+1]).lower() == "server":
                        self.jsonType = JsonType.SERVER
        elif testCommandLine != []:
            for index,arg in enumerate(testCommandLine):
                if str(arg) == "--json":
                    if str(testCommandLine[index+1]).lower() == "local":
                        self.jsonType = JsonType.LOCAL
                    elif str(testCommandLine[index+1]).lower() == "server":
                        self.jsonType = JsonType.SERVER
        def GetBaseDir():
            """Get the base directory, works for both development and PyInstaller"""
            if hasattr(sys, '_MEIPASS'):
                # Running as PyInstaller bundle
                return Path(sys.executable).parent
            else:
                # Running as normal Python script
                return Path(__file__).resolve().parent
        self.baseDir = GetBaseDir()
        self.exeDir = Path(__file__).resolve().parent
        self.appData_local = Path(os.getenv("LOCALAPPDATA"))
        os.makedirs(self.appData_local/"UKSF"/"CAST",exist_ok=True)
        self.updateQueue = queue.Queue()

        
        self.UI = CastUI(version=version,exeDir=self.exeDir,baseDir=self.baseDir,appData_local=self.appData_local,updateQueue=self.updateQueue,mainClass=self,startUpClass = self.StartUp)
        self.castJson = CastJson(self.jsonType,self.UI,self.exeDir,self.appData_local)
        self.account = UksfAccounts(self.UI)
        self.UI.GetCastJson(self.castJson)
        self.UI.GetAccount(self.account)
        self.terrainFolders = ()

    def ListTerrainFolders(self):
        folders = []
        terrains = []
        for dirName in os.listdir(self.baseDir/"Terrains"):
            if Path(os.path.join(self.baseDir/"Terrains",dirName)).is_dir():
                try:
                    terrains.append(dirName)
                    terrainPath = os.path.join(self.baseDir/"Terrains",dirName)
                    folders.append(terrainPath)
                    terrainFiles = os.listdir(terrainPath)
                    if str(f"{dirName}.gzcsv") not in terrainFiles: self.UI.StatusMessageLog(message=f"Folder does not have a valid height map file: {dirName}")
                    if (str(f"{dirName}.terrainimage") not in terrainFiles or "Terrain Images" not in terrainFiles): self.UI.StatusMessageLog(message=f"Folder does not have a valid height map file: {dirName}")
                except Exception as e: self.UI.StatusMessageErrorDump(e,errorMessage=f"Folder issue in map: {dirName}")
        return(terrains,folders)
    
    def TerrainFolderCheck(self):
        self.UI.mainMenu.AddTerrains(self.terrainFolders[0])
        #self.UI.mainMenu.terrainMenu.add_radiobutton(label=terrainFolder,variable=self.UI.terrain,value=terrainFolder,command=)    

    def LoginRefresh(self) -> bool:
        refresh = self.account.RefreshAuthToken(self.appData_local)
        if refresh is not None:
            self.UI.StatusMessageLog("Logged back in as " + refresh["displayName"])
            self.user = refresh["displayName"]
            print(self.user)
            self.UI.mainMenu.LoggedIn()
            return True
        else:
            if self.UI.LoginWindow():
                return True
            else:
                None

    def UpdateQueueCheck(self):
        try:
            while True:
                task,*args = self.updateQueue.get_nowait()
                if task == "processResults":
                    json,values = args
                    self.ProcessJson(json,values)
        except queue.Empty:
            pass
        except Exception as e: self.UI.StatusMessageErrorDump(e,errorMessage=f"Failed to update iterative settings, queue size: {str(self.updateQueue.qsize())}")
        
        self.UI.root.after(200,self.UpdateQueueCheck)

    def ProcessJson(self,json,values):
        if 'error' in json:
            self.UI.StatusMessageLog(json['error'])
            return
        def ProcessStep(step=0):
            if step == 0 and values == 0 and 'common' in json:
                try:
                    json['common']
                    self.UI.root.after(1, lambda: self.UI.SyncCommonSettings(json['common']))
                except Exception as e: self.UI.StatusMessageErrorDump(e,errorMessage="Error on processing common JSON")
            elif step == 1 and values == 1 and 'idfp' in json:
                try:
                    list(json['idfp'].keys())
                    self.UI.root.after(1, lambda: self.UI.idfpCreation.SyncIDFP(list(json['idfp'].keys())))
                    for map in self.UI.activeMaps.values():
                        map.toolbar.MapUpdate(marker=[Map.Mark.IDFP,Map.Mark.FPF_BOUNDS,Map.Mark.GROUP_BOUNDS,Map.Mark.LR_BOUNDS,Map.Mark.XY_BOUNDS])
                except Exception as e: self.UI.StatusMessageErrorDump(e,errorMessage="Error on processing IDFP JSON")
            elif step == 2 and values == 2 and 'friend' in json:
                try:
                    list(json['friend'].keys())
                    self.UI.root.after(1, lambda: self.UI.friendly.SyncFriendlies(list(json['friend'].keys())))
                    for map in self.UI.activeMaps.values():
                        map.toolbar.MapUpdate(marker=[Map.Mark.FRIENDLY,Map.Mark.FRIENDLY_BOUNDS])
                except Exception as e: self.UI.StatusMessageErrorDump(e,errorMessage="Error on processing Friendly JSON")
            elif step == 3 and values == 3 and 'targets' in json:
                try:
                    json['targets']
                    self.UI.root.after(1, lambda: self.UI.target.SyncTargets(json['targets']))
                    for map in self.UI.activeMaps.values():
                        map.toolbar.MapUpdate(marker=[Map.Mark.XY,Map.Mark.LR,Map.Mark.GROUP,Map.Mark.FPF])
                except Exception as e: self.UI.StatusMessageErrorDump(e,errorMessage="Error on processing Target JSON")
            elif step == 4 and values == 4 and 'fire mission' in json:
                try:
                    json['fire mission']
                    self.UI.root.after(1, lambda: self.UI.fireMission.SyncFireMissions(json['fire mission']))
                    for map in self.UI.activeMaps.values():
                        map.toolbar.MapUpdate(marker=[Map.Mark.LR_BOUNDS,Map.Mark.FPF_BOUNDS,Map.Mark.XY_BOUNDS,Map.Mark.GROUP_BOUNDS,Map.Mark.NOFLY,Map.Mark.NOFLY_BOUNDS])
                except Exception as e: self.UI.StatusMessageErrorDump(e,errorMessage="Error on processing Fire mission JSON")
        
        # Process the appropriate step
        ProcessStep(values)

    def StartUp(self,login = False,terrainLoad = False):
        def InitialSettings():
            self.terrainFolders = self.ListTerrainFolders()
            self.TerrainFolderCheck()
            self.UI.idfpCreation.InitialiseIDFPList()
            def StartTerrainPrompt():
                def Yes():
                    terrainPrompt.grab_release()
                    terrainPrompt.destroy()
                    self.UI.TerrainChange(self.castJson.Load(source=JsonSource.COMMON,localOverride=True)["terrain"])
                    self.UI.terrain.set(self.castJson.Load(source=JsonSource.COMMON,localOverride=True)["terrain"])
                def No():
                    terrainPrompt.grab_release()
                    terrainPrompt.destroy()
                terrainPrompt = Toplevel(self.UI.root)
                terrainPrompt.grab_set()
                terrainPrompt.attributes("-topmost",True)
                terrainPrompt.title("Load Last Terrain?")
                terrainPrompt.geometry("350x100+900+500")
                terrainPrompt.resizable(False, False)
                terrainPrompt.iconbitmap(self.exeDir/"Functions"/"icons"/"terrain.ico")
                terrainPromptWindow = terrainPrompt.winfo_toplevel()
                terrainPromptWindow.anchor("nw")
                terrainPromptWindow.grid_columnconfigure(0,weight=1)
                terrainPromptWindow.grid_rowconfigure(0,weight=1)
                terrainPromptFrame = ttk.Frame(terrainPromptWindow,padding=20)
                terrainPromptFrame.grid_columnconfigure((0,1),weight=1)
                terrainPromptFrame.grid_rowconfigure((0,1),weight=1)
                try: terrainPromptLabel = ttk.Label(terrainPromptFrame,justify="center",text=f'Do you wish to load the last terrain? "{self.castJson.Load(JsonSource.COMMON,localOverride=True)["terrain"]}"')
                except: terrainPromptLabel = ttk.Label(terrainPromptFrame,justify="center",text="Do you wish to load the last terrain?")
                terrainPromptNo = ttk.Button(terrainPromptFrame,text="No",command=No)
                terrainPromptNo.bind("<Return>",lambda event:No())
                terrainPromptYes = ttk.Button(terrainPromptFrame,text="Yes",command=Yes)
                terrainPromptYes.bind("<Return>",lambda event:Yes())
                terrainPromptFrame.grid(row=0,column=0,sticky="NS")
                terrainPromptLabel.grid(row=0,column=0,columnspan=2,sticky="NESW")
                terrainPromptNo.grid(row=1,column=0,sticky="NESW")
                terrainPromptYes.grid(row=1,column=1,sticky="NESW")
                terrainPromptYes.focus()
                terrainPrompt.protocol("WM_DELETE_WINDOW",No)
            if terrainLoad == True:
                try:
                    if self.castJson.Load(source=JsonSource.COMMON,localOverride=True)["terrain"] != "-1":
                        StartTerrainPrompt()
                except:
                    None
            # self.UI.SyncUpdate()
            self.UpdateQueueCheck()
        
        if login ==True or self.jsonType is JsonType.LOCAL:
            if self.jsonType is JsonType.SERVER:
                self.castJson.SyncAuthToken(self.account.authToken)
            self.UI.StatusMessageLog(message="---New Session---\n")
            InitialSettings()
        elif self.jsonType == JsonType.SERVER:
            if self.LoginRefresh() == True:
                self.castJson.SyncAuthToken(self.account.authToken)
                self.UI.StatusMessageLog(message="---New Session---\n")
                InitialSettings()
        
    def UIInitialise(self):
        self.UI.Initialise()
        
class CastUI():
    def __init__(self,version,exeDir:Path,baseDir,appData_local,updateQueue,mainClass:Cast,startUpClass):
        self.user = "Unknown User"
        self.version = version
        self.exeDir = exeDir
        self.baseDir = baseDir
        self.appData_local = appData_local
        self.updateQueue = updateQueue
        self.mainClass = mainClass
        self.startUpClass = startUpClass

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
        self.content = ttk.Frame(self.root)
        self.content.grid_columnconfigure(0,weight=1)
        self.content.grid_rowconfigure(0,weight=1)
        self.mainframe = ttk.Frame(self.content,padding=1)
        self.mainframe.grid_columnconfigure(0,weight=1)
        self.mainframe.grid_rowconfigure(0,weight=1)
        
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
        window=self.root.winfo_toplevel()
        window.minsize(950,650)
        window.rowconfigure(0,weight=1)
        window.columnconfigure(0,weight=1)

        self.system = StringVar()
        self.systemTrace = self.system.trace_add(mode="write",callback=lambda *args: self.SystemChanged(system=self.system.get(),settingNew=True))
        self.terrain = StringVar()
        self.messageLogOpen = False
        self.messageLogText = Text()
        
        self.oldLoaded = {JsonSource.COMMON:{},
                          JsonSource.IDFP:{},
                          JsonSource.FRIENDLY:{},
                          JsonSource.TARGET:{},
                          JsonSource.FIREMISSION:{},
                          JsonSource.MESSAGELOG:{},}
        #Window
        self.windowFlipPaneSide = StringVar(value="0")

        self.terrainHeightMap = pd.DataFrame()
        self.loadedHeightMap = False
        self.maxRow = 0
        self.maxCol = 0
        self.maxTerrainHeight = 0
        self.activeMaps = {}
        
        self.boldLabels = {
            "idfpName": False,
            "airTemperature": False,
            "airHumidity": False,
            "airPressure": False,
            "windDirection": False,
            "windMagnitude": False,
            "friendlyName": False,
        }
        self.mainMenu = MainMenus(self)
        self.statusbar = Statusbar(self)
        self.idfpCreation = IDFPCreation(self)
        self.atmospheric = Atmospheric(self)
        self.friendly = Friendlies(self)
        self.targetCreation = TargetCreation(self)
        self.targetDetail = TargetDetails(self)
        self.clock = None
        self.notes = Notes(self)
        self.target = Targets(self)
        self.fireMission = FireMissions(self)
        self.mainMap = Map.MatPlotLibWidget(self)
        self.activeMaps["Main"] = self.mainMap
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
        def ConfigureRowAndColumn(frame: ttk.Frame | list | tuple):
            if type(frame) in (list,tuple):
                for f in frame:
                    f.grid_columnconfigure(0,weight=1)
                    f.grid_rowconfigure(0,weight=1)
            else:
                frame.grid_columnconfigure(0,weight=1)
                frame.grid_rowconfigure(0,weight=1)
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
        ConfigureRowAndColumn((self.missionPagePanedWindow.pane1,self.missionPagePanedWindow.pane2,self.missionPagePanedWindow.pane3,self.missionPagePanedWindow.pane4))
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
        self.missionPagePanedWindow.grid(column="0",row="0",sticky="NWS")
        ConfigureRowAndColumn((self.missionPagePanedWindow.pane1.pane1,self.missionPagePanedWindow.pane1.pane2,self.missionPagePanedWindow.pane1.pane3,self.missionPagePanedWindow.pane1.pane4,
                               self.missionPagePanedWindow.pane2.pane1,self.missionPagePanedWindow.pane2.pane2,self.missionPagePanedWindow.pane2.pane3,self.missionPagePanedWindow.pane2.pane4,
                               self.missionPagePanedWindow.pane3.pane1,self.missionPagePanedWindow.pane3.pane2,self.missionPagePanedWindow.pane3.pane3))
        self.missionPagePanedWindow.pane1.paneWindow.grid(column="0",row="0",sticky="NEWS")
        self.missionPagePanedWindow.pane2.paneWindow.grid(column="0",row="0",sticky="NEWS")
        self.missionPagePanedWindow.pane3.paneWindow.grid(column="0",row="0",sticky="NEWS")

    def MapPageSetup(self):
        def ConfigureRowAndColumn(frame: ttk.Frame | list | tuple):
            if type(frame) in (list,tuple):
                for f in frame:
                    f.grid_columnconfigure(0,weight=1)
                    f.grid_rowconfigure(0,weight=1)
            else:
                frame.grid_columnconfigure(0,weight=1)
                frame.grid_rowconfigure(0,weight=1)
        self.mapPagePanedWindow = ttk.Panedwindow(self.mainNotebookMapPage,orient="horizontal")
        self.mapPagePane0 = ttk.Frame(self.mapPagePanedWindow,width=800,padding=1)
        self.mapPagePane1 = ttk.Frame(self.mapPagePanedWindow,width=400,padding=1)
        self.mapPagePane2 = ttk.Frame(self.mapPagePanedWindow,width=400,padding=1)
        self.mapPagePanedWindow.add(self.mapPagePane0)
        self.mapPagePanedWindow.add(self.mapPagePane1)
        self.mapPagePanedWindow.add(self.mapPagePane2)
        self.mapPageFrame0 = ttk.Frame(self.mapPagePane0,height=800,width=800,padding=5)
        self.mapPageFrame1 = ttk.Frame(self.mapPagePane1,height=400,width=400,padding=5)
        self.mapPageFrame2 = ttk.Frame(self.mapPagePane2,height=400,width=400,padding=5)
        ConfigureRowAndColumn((self.mapPagePane0,self.mapPagePane1,self.mapPagePane2,self.mapPageFrame0,self.mapPageFrame1,self.mapPageFrame2))
        self.mapPagePanedWindow.grid(column=0,row=0,sticky="NESW")
        self.mapPageFrame0.grid(column=0,row=0,sticky="NESW")
        self.mapPageFrame1.grid(column=0,row=0,sticky="NESW")
        self.mapPageFrame2.grid(column=0,row=0,sticky="NESW")


    def MiscNotebookUI(self,frame):
        self.miscNotebook = ttk.Notebook(frame,width=420,height=470)
        clockFrame = ttk.Frame(self.miscNotebook)
        settingsFrame = ttk.Frame(self.miscNotebook)
        notesFrame = ttk.Frame(self.miscNotebook)
        self.miscNotebook.add(clockFrame,text="Clock",sticky="NESW",padding=1)
        self.miscNotebook.add(settingsFrame,text="Settings",sticky="NESW",padding=1)
        self.miscNotebook.add(notesFrame,text="Notes",sticky="NESW",padding=1)
        self.clock=Clock(self)
        self.clock.Initialise(clockFrame=clockFrame)
        self.clock.ClockSettingsElements(settingsFrame,popoutOption=True)
        self.notes.Initialise(frame=notesFrame)
        clockFrame.grid_rowconfigure(1,weight=1) 
        self.miscNotebook.grid(column="0",row="0",sticky="NEW")

    def StatusMessageLog(self,message="",privateMessage: str | None = None, localOverride = False):
        """
        Displays message in the status bar and log. Private message is given only to the user in the status bar, if message is "", it's not included in the log.
        """

        tempLocal = True if self.account.authToken is None or self.castJson.jsonType == JsonType.LOCAL or localOverride == True else False
        if privateMessage is None:
            try: self.statusbar.statusMessageLabel.config(text=message)
            except: None
        elif privateMessage == "Empty": None
        else:
            try: self.statusbar.statusMessageLabel.config(text=privateMessage)
            except: None
        if message != "" and localOverride == False:
            self.castJson.Save(source=JsonSource.MESSAGELOG,newEntry=(str(datetime.now(timezone.utc))[:-11] + "\t" + "|" + "\t" + self.user + "\t" + "|" + "\t" + message+"\n"),append=True,localOverride=tempLocal)
            if self.messageLogOpen:
                self.messageLogText.config(state=NORMAL)
                self.messageLogText.delete("1.0","end")
                tempLocal = True if self.account.authToken is None or self.castJson.jsonType == JsonType.LOCAL else False
                self.messageLogText.insert("end",self.castJson.Load(source=JsonSource.MESSAGELOG,localOverride=tempLocal)) 
                self.messageLogText.config(state=DISABLED)
                self.messageLogText.yview_moveto(1)

    def StatusMessageErrorDump(self,e: Exception, errorMessage: str | None =None , localOverride = False):
        if errorMessage is not None:
            self.StatusMessageLog(message=errorMessage,localOverride=localOverride)
        try:
            if e:
                fullTrace = traceback.extract_tb(e.__traceback__)
                fullTraceStr = ""
                for i,frame in enumerate(fullTrace):
                    filename = frame.filename.split('\\')[-1]
                    fullTraceStr+=f"\n\t\t{filename} | {frame.name} | {str(frame.lineno)}"
                print(f"Error details:\n\tVersion: {self.version}\n\tType: {type(e).__name__}\n\tError: {e}\n\tError Line: {fullTrace[-1].lineno} : {fullTrace[-1].line}\n\tFull stack:{fullTraceStr}")
                self.StatusMessageLog(message=f"Error details:\n\tVersion: {self.version}\n\tType: {type(e).__name__}\n\tError: {e}\n\tError Line: {fullTrace[-1].lineno} : {fullTrace[-1].line}\n\tFull stack:{fullTraceStr}",privateMessage="Empty",localOverride=localOverride)
            
            else: self.StatusMessageLog(message=f"Failed error message",localOverride=localOverride)
        except: self.StatusMessageLog(message=f"Failed error message",localOverride=localOverride)
    def LoginWindow(self) -> bool:
        def Login():
            loginMessage.grid()
            if loginUsernameEntry.get().strip() !="":
                if loginPasswordEntry.get() !="":
                    loginMessage.config(text="Logging in")
                    self.account.GetAuthToken(loginUsernameEntry.get(),loginPasswordEntry.get())
                    
                    loginUsernameEntry.delete(0,END)
                    loginPasswordEntry.delete(0,END)
                    accountDetails = self.account.GetAccount(castJson=self.castJson)
                    if accountDetails is not None:
                        self.castJson.SyncAuthToken(self.account.authToken)
                        for tabID in self.fireMission.fireMissionNotebook.tabs():
                            self.fireMission.fireMissionNotebook.forget(tabID)
                        self.mainMenu.LoggedIn()
                        self.StatusMessageLog("Logged in as " + accountDetails["displayName"])
                        self.user = accountDetails["displayName"]
                        loginMessage.config(text="Logged in as " + accountDetails["displayName"])
                        self.account.SaveAuthTokenLocal(self.appData_local)
                        self.mainMenu.loginMenu.entryconfigure("Login",state=DISABLED)
                        self.mainMenu.loginMenu.entryconfigure("Logout",state=NORMAL)
                        loginTopLevel.grab_release()
                        loginTopLevel.destroy()
                        self.startUpClass(login=True)
                else:
                    loginMessage.config(text="Enter Password")
                    loginPasswordEntry.focus_set()
            else:
                loginMessage.config(text="Enter email address")
                loginUsernameEntry.focus_set()
        def LoginClosed():
            loginTopLevel.grab_release()
            loginTopLevel.destroy()
            self.castJson.SyncAuthToken(None)
            self.account.authToken = None
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
    
    def Logout(self):
        try:
            self.account.Logout(self.appData_local)
        except Exception as e:
            self.StatusMessageErrorDump(e,errorMessage="Failed to logout successfully")
        else:
            self.StatusMessageLog("Logged out")
            self.user = "Logged Out User"
            #self.StatusMessageLog("End of Line")
            self.castJson.SyncAuthToken(None)
            self.mainMenu.LoggedOut()
            for tabID in self.fireMission.fireMissionNotebook.tabs():
                self.fireMission.fireMissionNotebook.forget(tabID)
        #self.root.destroy()
    def IDFCalculatorClosed(self) ->None:
        try: self.StatusMessageLog("End of Line")
        except: None
        Path(self.baseDir/"tempstipple.xbm").unlink(missing_ok=True)
        self.root.destroy()
        quit()
    def UpdateStringVar(self,StrVar: StringVar, value,trace = None, entryLabel = None):
        try:
            if trace is not None:
                StrVar.trace_remove(mode="write",cbname=trace)
            StrVar.set(value)
        except Exception as e: self.StatusMessageErrorDump(e,errorMessage=f"Failed to set string variable {StrVar} to {value}")
    def NewTerrainHeightMapWindow(self,*args):
        def HeightMapTopLevelClosed():
            HeightMapTopLevel.grab_release()
            HeightMapTopLevel.destroy()
        def HeightMapAccept(*args):
            if mapName.get().count(",")>0:
                mapName.set("")
            else:
                HeightMapTopLevelClosed()
                if mapName.get()!="":
                    filePath = filedialog.askopenfilename(initialdir="C:/arma3/terrain",title=f"Select corresponding {mapName.get()} terrain height map",filetypes=(("Text files","*txt"),("All files","*.*")))
                    if filePath:
                        Map.Terrain.NewTerrainHeightmap(baseDir=self.baseDir,filePath=filePath,terrainName=mapName.get(),targets = self.target,statusBar = self.statusbar,calculateButton=self.target.targetListCalculate,progressBar = self.statusbar.statusProgressBar,statusMessageLog=self.StatusMessageLog,statusMessageLabel = self.statusbar.statusMessageLabel,statusMessageErrorDump = self.StatusMessageErrorDump)
                        self.root.bell()
                        self.mainClass.terrainFolders = self.ListTerrainFolders()
                        self.mainClass.TerrainFolderCheck()
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
                    self.mainClass.terrainFolders = self.ListTerrainFolders()
                    self.mainClass.TerrainFolderCheck()
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
    # def TerrainChange(self,*args):
    #     if self.terrain.get() != "":
    #         try:
    #             self.StatusMessageLog(privateMessage=F"Loading {self.terrain.get()} Height map")
    #             self.statusbar.statusMessageLabel.update_idletasks()
    #             self.castJson.Save(source=JsonSource.COMMON,newEntry={"terrain" : self.terrain.get()},localOverride=True)
    #             self.terrainHeightMap = pd.read_csv(self.baseDir/"Terrains"/self.terrain.get()/(self.terrain.get()+".gzcsv"),compression="gzip",header=None)#USE THREADING TO MAKE THE PROGRAM RESPONSIVE
    #             self.maxRow, self.maxCol = self.terrainHeightMap.shape
    #             self.mainMap.SetTerrain(self.baseDir/"Terrains"/self.terrain.get())
    #             self.maxTerrainHeight = self.terrainHeightMap.to_numpy().max()
    #             self.StatusMessageLog("Loaded "+self.terrain.get()+ " Height map")
    #             self.root.bell()
    #         except Exception as e:
    #             self.StatusMessageErrorDump(e,errorMessage=f"Could not find terrain height map data for {self.terrain.get()}")
    #             self.terrain.set("")
    #             self.castJson.Save(source=JsonSource.COMMON,newEntry={"terrains" : ""},localOverride=True)
                
                
    def TerrainChange(self,terrainName,imageInhibit = False, heightInhibit = False):
        def TerrainLoadThread(terrain):
            try:
                self.loadedHeightMap = False
                self.terrainHeightMap = pd.read_csv(self.baseDir/"Terrains"/terrain/(terrain+".gzcsv"),compression="gzip",header=None)
                self.maxRow, self.maxCol = self.terrainHeightMap.shape
                self.loadedHeightMap = True
                self.StatusMessageLog("Loaded "+terrainName+ " Height map")
                if Path(self.baseDir/"Terrains"/terrainName/(terrainName+".terrainimage")).exists() and imageInhibit == False:
                    for map in self.activeMaps.values():
                        map.SetTerrain(self.baseDir/"Terrains"/terrainName)
                    self.StatusMessageLog("Loaded "+terrainName+ " map images")
                    self.terrain.set(terrainName)
                    self.root.bell()
            except Exception as e:
                self.StatusMessageErrorDump(e,errorMessage=f"Could not find terrain height map data for {terrainName}")
                self.castJson.Save(source=JsonSource.COMMON,newEntry={"terrains" : ""},localOverride=True)
        if terrainName != "":
            try:
                self.StatusMessageLog(privateMessage=F"Loading {terrainName} Height map")
                self.statusbar.statusMessageLabel.update_idletasks()
                self.castJson.Save(source=JsonSource.COMMON,newEntry={"terrain" : terrainName},localOverride=True)
                if Path(self.baseDir/"Terrains"/terrainName/(terrainName+".gzcsv")).exists() and heightInhibit == False:
                    #self.terrainHeightMap = pd.read_csv(self.baseDir/"Terrains"/terrainName/(terrainName+".gzcsv"),compression="gzip",header=None)
                    threading.Thread(target=lambda terrain = terrainName: TerrainLoadThread(terrain), daemon=True).start()
                else:
                    if Path(self.baseDir/"Terrains"/terrainName/(terrainName+".terrainimage")).exists() and imageInhibit == False:
                        for map in self.activeMaps.values():
                            map.SetTerrain(self.baseDir/"Terrains"/terrainName)
                        self.StatusMessageLog("Loaded "+terrainName+ " map images")
                    self.terrain.set(terrainName)
                    self.root.bell()
            except Exception as e:
                self.StatusMessageErrorDump(e,errorMessage=f"Could not find terrain height map data for {terrainName}")
                self.castJson.Save(source=JsonSource.COMMON,newEntry={"terrains" : ""},localOverride=True)
    def FlipWindowPanes(self):
        """Flip the vertical panes back to front"""
        if self.windowFlipPaneSide.get() == "0":
            self.missionPagePanedWindow.insert(1,self.missionPagePanedWindow.pane4)
            self.missionPagePanedWindow.insert(2,self.missionPagePanedWindow.pane3)
            self.missionPagePanedWindow.insert(3,self.missionPagePanedWindow.pane2)
            self.missionPagePanedWindow.insert(4,self.missionPagePanedWindow.pane1)
            self.windowFlipPaneSide.set("1")
        else:
            self.missionPagePanedWindow.insert(4,self.missionPagePanedWindow.pane4)
            self.missionPagePanedWindow.insert(3,self.missionPagePanedWindow.pane3)
            self.missionPagePanedWindow.insert(2,self.missionPagePanedWindow.pane2)
            self.missionPagePanedWindow.insert(1,self.missionPagePanedWindow.pane1)
            self.windowFlipPaneSide.set("0")
        self.StatusMessageLog("Fire mission window panes flipped")
    def ClearMessageLog(self):
        self.castJson.Delete(source=JsonSource.MESSAGELOG)
        if self.messageLogOpen:
            self.messageLogText.delete("1.0",END)
        self.StatusMessageLog("Status log cleared")
    def ClearFireMission(self,mission: str|None = None, index: list|str|None = None,calculated = False):
        """
        takes the mission (LR,XY,FPF,Group) and take the name suffixes (...-##) and remove it from the target jsons, the calculated ones if calculated == True
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
                        fireMissions = self.castJson.Load(source=JsonSource.FIREMISSION)
                        for idfp,missions in fireMissions.items():
                            for key in list(missions.keys()):
                                if key[:2] == mission:
                                    fireMissions[idfp].pop(key,None)
                        self.castJson.Save(source=JsonSource.FIREMISSION,newEntry=fireMissions,append=False)
                        self.StatusMessageLog(message=f"Deleted calculated {mission} fire missions from JSON")
                    except Exception as e: self.StatusMessageErrorDump(e,errorMessage=f"Failed to delete calculated {mission} fire missions from JSON")
            else:
                names = [index]
                for name in names:
                    if calculated == False:
                        try:
                            targets = self.castJson.Load(source=JsonSource.TARGET)
                            targets[mission].pop(name,None)
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
            
    def ClearTargetAndMission(self,mission: str|None = None, index: list|str|None = None):
        self.ClearFireMission(mission, index,calculated=True)
        self.ClearFireMission(mission, index,calculated=False)
    def ClearIDFP(self,idfp:list|str|None = None):
        if idfp is None:
            try:
                self.castJson.Delete(JsonSource.IDFP)
            except Exception as e: self.StatusMessageErrorDump(e,errorMessage="Failed to delete IDFPs from JSON")
            try:
                self.castJson.Delete(JsonSource.FIREMISSION)
            except Exception as e: self.StatusMessageErrorDump(e,errorMessage="Failed to delete Fire missions from JSON")
            try:
                for tabId in self.fireMission.fireMissionNotebook.tabs():
                    self.fireMission.fireMissionNotebook.forget(tabId)
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
                    for tabId in self.fireMission.fireMissionNotebook.tabs():
                        if self.fireMission.fireMissionNotebook.tab(tabId,option="text") == idfp:
                            self.fireMission.fireMissionNotebook.forget(tabId)
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
        self.system.trace_remove(mode="write",cbname=self.atmospheric.processSettings["system"]["traceName"])
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
            try: self.idfpCreation.idfpSystemLabel.config(text = system)
            except: self.idfpCreation.idfpSystemLabel.config(text = "Error")
            self.StatusMessageLog("System Change: If pre-existing IDFP selections are present, check selection charges, trajectories and old calculations")
        elif system is not None:
            try: 
                oldSystem = self.system.get()
                self.system.set(system)
                self.idfpCreation.idfpSystemLabel.config(text = system)
                self.StatusMessageLog(f"Artillery system has changed from {oldSystem} to {system}") if oldSystem !="" else self.StatusMessageLog(f"Artillery system set to {system}")
                self.StatusMessageLog(message="",privateMessage="System Change: If pre-existing IDFP selections are present, check selection charges, trajectories and old calculations")
            except Exception as e: self.StatusMessageErrorDump(e,"Could not set system from JSON")
        self.systemTrace = self.system.trace_add(mode="write", callback=lambda*args: self.SystemChanged(system=self.system.get(),settingNew=True))
        self.atmospheric.processSettings["system"]["traceName"] = self.systemTrace
        systemConfig = self.castJson.Load(source=JsonSource.ARTILLERYCONFIG)[system]
        try:
            self.idfpCreation.idfpEditChargeComboBox.config(values=systemConfig["Charges"])
            self.idfpCreation.idfpEditTrajComboBox.config(values=systemConfig["Trajectories"])
        except Exception as e: self.StatusMessageErrorDump(e,"Failed to set system combo boxes or load system configurations")

    def HeightAutoFill(self,event,x:str,y:str,heightlabel: StringVar | ttk.Label,noEvent = False):
        if self.loadedHeightMap:
            if noEvent == False:
                if event.keysym == "Return" or event.keysym == "Tab":
                    if len(x) in (4,5) and len(y) in (4,5):
                        if len(x) == 4: x += "0"
                        if len(y) == 4: y += "0"
                        if int(x) > self.maxCol: x = self.maxCol - 1
                        elif int(x) < 0: x = 0
                        if int(y) > self.maxRow: y = self.maxRow - 1
                        elif int(y) < 0: y = 0
                        try: heightlabel.set(self.terrainHeightMap.iat[int(x),int(y)])
                        except: pass
            else:
                if len(x) in (4,5) and len(y) in (4,5):
                    if len(x) == 4: x += "0"
                    if len(y) == 4: y += "0"
                    if int(x) > self.maxCol: x = self.maxCol - 1
                    elif int(x) < 0: x = 0
                    if int(y) > self.maxRow: y = self.maxRow - 1
                    elif int(y) < 0: y = 0
                    try: heightlabel.set(self.terrainHeightMap.iat[int(x),int(y)])
                    except: pass

    def LoadSelectionDetails(self,event,source):
        try:
            if event.keysym=="Return" or event.keysym=="Tab":
                json = self.castJson.Load(source=source)
                for name,details in json.items():
                    if source is JsonSource.IDFP:
                        if self.idfpCreation.idfpName.get() == name:
                            self.idfpCreation.idfpPosX.set(details["GridX"])
                            self.idfpCreation.idfpPosY.set(details["GridY"])
                            self.idfpCreation.idfpHeight.set(details["Height"])
                            self.idfpCreation.idfpUseCharge.set(details["ForceCharge"])
                            self.idfpCreation.idfpCharge.set(details["Charge"])
                            self.idfpCreation.idfpTraj.set(details["Trajectory"])
                    if source is JsonSource.FRIENDLY:
                        if self.friendly.friendlyName.get() == name:
                            self.friendly.friendlyPosX.set(details["GridX"])
                            self.friendly.friendlyPosY.set(details["GridY"])
                            self.friendly.friendlyHeight.set(details["Height"])
                            self.friendly.friendlyDispersion.set(details["Dispersion"])
                    if source is JsonSource.TARGET:
                        if self.targetCreation.xylrfpf.get() == name:
                            for fm, fmDetails in details.items():
                                if self.targetCreation.targetReference.get() == fm:
                                    self.targetCreation.targetPosX.set(fmDetails["GridX"])
                                    self.targetCreation.targetPosY.set(fmDetails["GridY"])
                                    self.targetCreation.targetHeight.set(fmDetails["Height"])
                                    self.targetDetail.fireMissionEffect.set(fmDetails["Effect"])
                                    self.targetDetail.fireMissionWidth.set(fmDetails["Width"])
                                    self.targetDetail.fireMissionDepth.set(fmDetails["Depth"])
                                    self.targetDetail.fireMissionLength.set(fmDetails["Length"])
                                    self.targetDetail.fireMissionCondition.set(fmDetails["Condition"])
                                    self.targetDetail.fireMissionHour.set(fmDetails["Time"]["Hour"])
                                    self.targetDetail.fireMissionMinute.set(fmDetails["Time"]["Minute"])
                                    self.targetDetail.fireMissionSecond.set(fmDetails["Time"]["Second"])
        except Exception as e: self.StatusMessageErrorDump(e,"Failed to set values")
        else:
            if source is JsonSource.IDFP:
                self.BoldenLabel(label=self.idfpCreation.idfpNameLabel,type="Normal",strVarName="idfpName")
                self.boldLabels["idfpName"] = False
            elif source is JsonSource.FRIENDLY:
                self.BoldenLabel(label=self.friendly.friendlyNameLabel,type="Normal",strVarName="friendlyName")
                self.boldLabels["friendlyName"] = False

    def SyncCommonSettings(self,common):
        def UpdateSetting(stringVariable: StringVar, jsonName: str, settingName: str,trace,entryLabel):
            try:
                settingValue = common[jsonName]
            except ValueError:
                self.StatusMessageLog(f"{settingName} from JSON has an erroneous value")
                return
            except KeyError:
                self.StatusMessageLog(f"{settingName} key does not exist in JSON")
                self.castJson.Save(source=JsonSource.COMMON,newEntry={jsonName:""})
                return
            except Exception as e:
                self.StatusMessageErrorDump(e,errorMessage=f"Failed to load {settingName} from JSON")
                return
            try:     
                if stringVariable.get() != str(settingValue) and stringVariable!="":
                    if jsonName == "system":
                        self.SystemChanged(system=settingValue,settingNew=False)
                    else:
                        if jsonName in self.boldLabels.keys():
                            if self.boldLabels[jsonName] == False:
                                self.UpdateStringVar(stringVariable, settingValue,trace)
                                if trace!=None:
                                    if stringVariable == self.atmospheric.windDynamic:
                                        trace = self.atmospheric.windDynamic.trace_add(mode="write", callback=(lambda *args: self.castJson.Save(source=JsonSource.COMMON,newEntry={"windDynamic" : self.atmospheric.windDynamic.get()})))
                                    if entryLabel!=None:
                                        trace = stringVariable.trace_add(mode="write",callback=lambda *args: self.BoldenLabel(entryLabel,"Bold",jsonName))
                                    self.atmospheric.processSettings[jsonName]["traceName"] = trace
                        else:
                            self.UpdateStringVar(stringVariable, settingValue,trace)
                            if trace!=None:
                                if stringVariable == self.atmospheric.windDynamic:
                                    trace = self.atmospheric.windDynamic.trace_add(mode="write", callback=(lambda *args: self.castJson.Save(source=JsonSource.COMMON,newEntry={"windDynamic" : self.atmospheric.windDynamic.get()})))
                                if entryLabel!=None:
                                    trace = stringVariable.trace_add(mode="write",callback=lambda *args: self.BoldenLabel(entryLabel,"Bold",jsonName))
                                self.atmospheric.processSettings[jsonName]["traceName"] = trace
            except Exception as e: self.StatusMessageErrorDump(e,errorMessage=f"Failed to set {settingName}")
        
        # List of settings to process
        # self.atmospheric.processSettings = [
        #     (airTemperature, "airTemperature", "Air Temperature",airTemperatureTrace,temperatureLabel),
        #     (airHumidity, "airHumidity", "Air Humidity",airHumidityTrace,humidityLabel),
        #     (airPressure, "airPressure", "Air Pressure",airPressureTrace,pressureLabel),
        #     (windDirection, "windDirection", "Wind Direction",windDirectionTrace,directionLabel),
        #     (windMagnitude, "windMagnitude", "Wind Magnitude",windMagnitudeTrace,magnitudeLabel),
        #     (windDynamic, "windDynamic", "Dynamic Wind setting",None,None),
        #     (system, "system", "Weapon System",None,None)
        # ]
        
        
        # Process all settings with minimal delays
        for i, (jsonName, items) in enumerate(self.atmospheric.processSettings.items()):
            try:
                if self.boldLabels[jsonName] == False:
                    self.root.after(i*200, lambda sv=items["StringVar"], jn=jsonName, sn=items["settingName"],tr=items["traceName"],lbl=items["entryLabel"]: UpdateSetting(sv, jn, sn, tr, lbl))
            except KeyError:
                self.root.after(i*200, lambda sv=items["StringVar"], jn=jsonName, sn=items["settingName"],tr=items["traceName"],lbl=items["entryLabel"]: UpdateSetting(sv, jn, sn, tr, lbl))

    def SyncUpdate(self,setting: JsonSource | list |tuple | None = None):

        if setting is None:
            settingsList = [JsonSource.COMMON, JsonSource.IDFP, JsonSource.FRIENDLY, JsonSource.TARGET, JsonSource.FIREMISSION]
        elif isinstance(setting, (list,tuple)):
            settingsList = setting
        else:
            settingsList = [setting]
        
        def FetchJSON(setting):
            results = {}
            try:
                if setting is JsonSource.COMMON:
                    results['common'] = self.castJson.Load(source=JsonSource.COMMON)
                    if results['common'] == self.oldLoaded[JsonSource.COMMON]:
                        return
                    else:
                        self.oldLoaded[JsonSource.COMMON] = results['common']
                if setting is JsonSource.IDFP:
                    results['idfp'] = self.castJson.Load(source=JsonSource.IDFP)
                    if results['idfp'] == self.oldLoaded[JsonSource.IDFP]:
                        return
                    else:
                        self.oldLoaded[JsonSource.IDFP] = results['idfp']
                if setting is JsonSource.FRIENDLY:
                    results['friend'] = self.castJson.Load(source=JsonSource.FRIENDLY)
                    if results['friend'] == self.oldLoaded[JsonSource.FRIENDLY]:
                        return
                    else:
                        self.oldLoaded[JsonSource.FRIENDLY] = results['friend']
                if setting is JsonSource.TARGET:
                    results['targets'] = self.castJson.Load(source=JsonSource.TARGET)
                    if results['targets'] == self.oldLoaded[JsonSource.TARGET]:
                        return
                    else:
                        self.oldLoaded[JsonSource.TARGET] = results['targets']
                if setting is JsonSource.FIREMISSION:
                    results['fire mission'] = self.castJson.Load(source=JsonSource.FIREMISSION)
                    if results['fire mission'] == self.oldLoaded[JsonSource.FIREMISSION]:
                        return
                    else:
                        self.oldLoaded[JsonSource.FIREMISSION] = results['fire mission']
            except Exception as e:
                results['error'] = f"Failed to load JSON: {str(e)}"
                self.StatusMessageErrorDump(e,errorMessage=f"Failed to load JSON: {str(e)}")
            self.updateQueue.put(('processResults', results, setting))
        
        # Start background threads for all settings
        for s in settingsList:
            threading.Thread(target=lambda setting=s: FetchJSON(setting), daemon=True).start()
        
        if setting is None: self.root.after(5000,self.SyncUpdate)
    

    def NotebookTabMenu(self,event):
        if not hasattr(self,"mapNumber"):
            setattr(self,"mapNumber",0)
        def PopoutMap():
            def Close(number):
                self.activeMaps.pop(number,None)
                mapToplevel.destroy()
            mapToplevel = Toplevel(self.root)
            mapToplevel.attributes("-topmost",True)
            mapToplevel.title(f"Main map")
            mapToplevel.geometry("1000x900+5+5")
            mapToplevel.resizable(True,True)
            mapToplevel.iconbitmap(self.exeDir/"Functions"/"icons"/"terrain.ico")
            mapWindow = mapToplevel.winfo_toplevel()
            mapWindow.anchor("n")
            mapWindow.grid_columnconfigure(0,weight=1)
            mapWindow.grid_rowconfigure(0,weight=1)
            mapFrame = ttk.Frame(mapWindow,padding=3)
            mapFrame.grid_columnconfigure(0,weight=1)
            mapFrame.grid_rowconfigure(0,weight=1)
            popoutMap = Map.MatPlotLibWidget(self)
            self.activeMaps[str(self.mapNumber)] = popoutMap
            popoutMap.Initialise(mapFrame,True)
            popoutMap.toolbar.markSettings = self.mainMap.toolbar.markSettings
            popoutMap.toolbar.MapUpdate([Map.Mark.IDFP,Map.Mark.FPF,Map.Mark.LR,Map.Mark.XY,Map.Mark.GROUP,Map.Mark.NOFLY,Map.Mark.FRIENDLY])
            mapFrame.grid(row=0,column=0,sticky="NESW")
            mapToplevel.protocol("WM_DELETE_WINDOW",lambda n = str(self.mapNumber): Close(n))
            self.mapNumber += 1

        clickedTab = self.mainNotebook.tk.call(self.mainNotebook,"identify", "tab", event.x, event.y)
        if self.mainNotebook.tab(clickedTab,option="text") == "Maps":
            MapPopoutMenu = Menu(self.root,tearoff=False)
            MapPopoutMenu.add_command(label=f"Popout Main Map",command=PopoutMap)
            MapPopoutMenu.post(event.x_root,event.y_root)

    def Initialise(self):
        self.SyncUpdate()
        self.statusbar.Initialise(self.mainframe)
        self.MissionPageSetup()
        self.MapPageSetup()
        self.idfpCreation.Initialise(self.missionPagePanedWindow.pane1.pane1)
        self.atmospheric.Initialise(self.missionPagePanedWindow.pane1.pane2)
        self.friendly.Initialise(self.missionPagePanedWindow.pane1.pane3)
        self.targetCreation.Initialise(self.missionPagePanedWindow.pane2.pane1)
        self.targetDetail.Initialise(self.missionPagePanedWindow.pane2.pane2)
        self.MiscNotebookUI(self.missionPagePanedWindow.pane2.pane3)
        self.target.Initialise(self.missionPagePanedWindow.pane3.pane1)
        self.fireMission.Initialise(self.missionPagePanedWindow.pane4)
        self.mainMap.Initialise(self.mapPageFrame0)
        self.mainNotebook.bind("<Button-3>",self.NotebookTabMenu)
        self.mainMenu.Initialise()
        
        
cast = Cast(version)
cast.UIInitialise()
cast.UI.root.after(10,lambda: cast.StartUp(terrainLoad=True))
cast.UI.root.mainloop()


