from enum import IntEnum
from pathlib import Path
import json
import requests

class JsonType(IntEnum):
    LOCAL = 0
    SERVER = 1

class JsonSource(IntEnum):
    COMMON = 0
    IDFP = 1
    FRIENDLY = 2
    TARGET = 3
    FIREMISSION = 4
    MESSAGELOG = 5
    ARTILLERYCONFIG = 6

class CastJson():
    def __init__(self,jsonType: JsonType,StatusMessageErrorDump,exeDir: Path,appData_local: Path | None = None,):
        self.jsonType = jsonType
        self.StatusMessageErrorDump = StatusMessageErrorDump
        self.exeDir = exeDir
        self.appData_local = appData_local
        """
        message = "" #Saves to Json
        privateMessage = None #Only appears on statusbar
        """
        self.jsonType = JsonType.LOCAL
        # if self.jsonType == JsonType.LOCAL:
        #     self.appData_local = appData_local
        # elif self.jsonType == JsonType.SERVER:
        #     self.authToken = None
    def GetStatusMessageErrorDump(self,StatusMessageErrorDump):
        self.StatusMessageErrorDump = StatusMessageErrorDump
    def SyncAuthToken(self,authToken):
        self.authToken=authToken
        if authToken is not None:
            self.jsonType = JsonType.SERVER
        else: self.jsonType = JsonType.LOCAL
    def Load(self,source: JsonSource,localOverride = False) -> dict | str:
        """
        Loads and returns the Json data from the specified source. Takes the "json" arguement and uses the appropriate json source
        """
        if self.jsonType == JsonType.LOCAL or localOverride == True or source == 6 or self.authToken is None:
            try:
                if source == JsonSource.COMMON:
                    with open(self.appData_local/"UKSF"/"CAST"/"common.json","r") as file:
                        return json.load(file)
                elif source == JsonSource.IDFP:
                    with open(self.appData_local/"UKSF"/"CAST"/"IDFP.json","r") as file:
                        return json.load(file)
                elif source == JsonSource.FRIENDLY:
                    with open(self.appData_local/"UKSF"/"CAST"/"Friendly.json","r") as file:
                        return json.load(file)
                elif source == JsonSource.TARGET:
                    with open(self.appData_local/"UKSF"/"CAST"/"Targets.json","r") as file:
                        return json.load(file)
                elif source == JsonSource.FIREMISSION:
                    with open(self.appData_local/"UKSF"/"CAST"/"FireMissions.json","r") as file:
                        return json.load(file)
                elif source == JsonSource.MESSAGELOG:
                    with open(self.appData_local/"UKSF"/"CAST"/"Message_Log.json","r") as file:
                        return str(json.load(file)["message"])
                elif source == JsonSource.ARTILLERYCONFIG:
                    with open(self.exeDir/"Functions"/"ArtilleryConfigs.json",mode="r") as file:
                        return json.load(file)
            except Exception as e:
                if source == JsonSource.COMMON:
                    source = "Common parameters"
                    try:
                        with open(self.appData_local/"UKSF"/"CAST"/"common.json",mode="w") as f:
                            json.dump({},f,indent=4)
                    except: None
                elif source == JsonSource.IDFP:
                    source = "IDFP position data"
                    try:
                        with open(self.appData_local/"UKSF"/"CAST"/"IDFP.json","w") as f:
                            json.dump({},f,indent=4)
                    except: None
                elif source == JsonSource.FRIENDLY:
                    source = "Friendly position data"
                    try:
                        with open(self.appData_local/"UKSF"/"CAST"/"Friendly.json",mode="w") as f:
                            json.dump({},f,indent=4)
                    except: None
                elif source == JsonSource.TARGET:
                    source = "Target position data"
                    try:
                        with open(self.appData_local/"UKSF"/"CAST"/"Targets.json",mode="w") as f:
                            json.dump({},f,indent=4)
                    except: None
                elif source == JsonSource.FIREMISSION:
                    source = "Fire mission data"
                    try:
                        with open(self.appData_local/"UKSF"/"CAST"/"FireMissions.json",mode="w") as f:
                            json.dump({},f,indent=4)
                    except: None
                elif source == JsonSource.MESSAGELOG:
                    try:
                        with open(self.appData_local/"UKSF"/"CAST"/"Message_Log.json",mode="w") as f:
                            json.dump({"message":""},f,indent=4)
                    except: None
                    self.StatusMessageErrorDump(e, errorMessage="Failed to load Message log, returning nothing")
                    return {}
                else: source = "Artillery Configurations"
                self.StatusMessageErrorDump(e, errorMessage=f"Failed to load {source}, returning nothing")
                return ""
                
        elif self.jsonType ==JsonType.SERVER:
            try:
                if source == JsonSource.COMMON:
                    return json.loads(requests.get(url="https://api.uk-sf.co.uk/artillery/common",headers={"Authorization":"Bearer " + self.authToken["token"]}).json()["data"].translate(str.maketrans({"'": '"','"':"'"})))
                elif source == JsonSource.IDFP:
                    return json.loads(requests.get(url="https://api.uk-sf.co.uk/artillery/idfp",headers={"Authorization":"Bearer " + self.authToken["token"]}).json()["data"].translate(str.maketrans({"'": '"','"':"'"})))
                elif source == JsonSource.FRIENDLY:
                    return json.loads(requests.get(url="https://api.uk-sf.co.uk/artillery/friendly",headers={"Authorization":"Bearer " + self.authToken["token"]}).json()["data"].translate(str.maketrans({"'": '"','"':"'"})))
                elif source == JsonSource.TARGET:
                    return json.loads(requests.get(url="https://api.uk-sf.co.uk/artillery/target",headers={"Authorization":"Bearer " + self.authToken["token"]}).json()["data"].translate(str.maketrans({"'": '"','"':"'"})))
                elif source == JsonSource.FIREMISSION:
                    return json.loads(requests.get(url="https://api.uk-sf.co.uk/artillery/fireMissions",headers={"Authorization":"Bearer " + self.authToken["token"]}).json()["data"].translate(str.maketrans({"'": '"','"':"'"})))
                elif source == JsonSource.MESSAGELOG:
                    return str(json.loads(requests.get(url="https://api.uk-sf.co.uk/artillery/message_log",headers={"Authorization":"Bearer " + self.authToken["token"]}).json()["data"].translate(str.maketrans({"'": '"','"':"'"})))["message"])
            except Exception as e:
                if source == JsonSource.COMMON: source = "Common parameters"
                elif source == JsonSource.IDFP: source = "IDFP position data"
                elif source == JsonSource.FRIENDLY: source = "Friendly position data"
                elif source == JsonSource.TARGET: source = "Target position data"
                elif source == JsonSource.FIREMISSION: source = "Fire mission data"
                elif source == JsonSource.MESSAGELOG:
                    self.StatusMessageErrorDump(e, errorMessage="Failed load Message log, returning nothing")
                    return {}
                else: source = "Artillery Configurations"
                self.StatusMessageErrorDump(e, errorMessage=f"Failed load {source}, returning nothing")
                return ""
            
    def Save(self,source: JsonSource,newEntry: dict | str, append = True,localOverride = False) -> bool:
        """
        Loads the Json data from the specified source then saves new data if append = True, otherwise it overwrite the json. Takes the "json" arguement and uses the appropriate json source
        """
        data = {}
        if append:
            if source !=JsonSource.MESSAGELOG:
                try: data = (self.Load(source,localOverride) | newEntry)
                except TypeError: None
            else:
                try:
                    message = self.Load(source,localOverride) + str(newEntry)
                except TypeError:
                    message = ""
                data["message"] = message
        else:
            if source == 5: data["message"] = str(newEntry)
            else: data = newEntry
        if self.jsonType == JsonType.LOCAL or localOverride==True or self.authToken is None:
            try:
                if source == 0:
                    with open(self.appData_local/"UKSF"/"CAST"/"common.json","w") as file:
                        json.dump(data,file,indent=4)
                elif source == 1:
                    with open(self.appData_local/"UKSF"/"CAST"/"IDFP.json","w") as file:
                        json.dump(data,file,indent=4)
                elif source == 2:
                    with open(self.appData_local/"UKSF"/"CAST"/"Friendly.json","w") as file:
                        json.dump(data,file,indent=4)
                elif source == 3:
                    with open(self.appData_local/"UKSF"/"CAST"/"Targets.json","w") as file:
                        json.dump(data,file,indent=4)
                elif source == 4:
                    with open(self.appData_local/"UKSF"/"CAST"/"FireMissions.json","w") as file:
                        json.dump(data,file,indent=4)
                elif source == 5:
                    with open(self.appData_local/"UKSF"/"CAST"/"Message_Log.json","w") as file:
                        json.dump(data,file,indent=4)
                return True
            except Exception as e:
                if source == 0: source = "Common parameters"
                elif source == 1: source = "IDFP position data"
                elif source == 2: source = "Friendly position data"
                elif source == 3: source = "Target position data"
                elif source == 4: source = "Fire mission data"
                elif source == 5: source = "Message log"
                else: source = "Artillery Configurations"
                self.StatusMessageErrorDump(e, errorMessage=f"Failed to save {source}, returning False")
                return False
        elif self.jsonType ==JsonType.SERVER:
            try:
                if source == 0:
                    return requests.put(url="https://api.uk-sf.co.uk/artillery/common",headers={"Authorization":"Bearer " + self.authToken["token"],"Content-Type": "application/json"},json={"data": str(data)})
                if source == 1:
                    return requests.put(url="https://api.uk-sf.co.uk/artillery/idfp",headers={"Authorization":"Bearer " + self.authToken["token"],"Content-Type": "application/json"},json={"data": str(data)})
                if source == 2:
                    return requests.put(url="https://api.uk-sf.co.uk/artillery/friendly",headers={"Authorization":"Bearer " + self.authToken["token"],"Content-Type": "application/json"},json={"data": str(data)})
                if source == 3:
                    return requests.put(url="https://api.uk-sf.co.uk/artillery/target",headers={"Authorization":"Bearer " + self.authToken["token"],"Content-Type": "application/json"},json={"data": str(data)})
                if source == 4:
                    return requests.put(url="https://api.uk-sf.co.uk/artillery/fireMissions",headers={"Authorization":"Bearer " + self.authToken["token"],"Content-Type": "application/json"},json={"data": str(data)})
                if source == 5:
                    return requests.put(url="https://api.uk-sf.co.uk/artillery/message_log",headers={"Authorization":"Bearer " + self.authToken["token"],"Content-Type": "application/json"},json={"data": str(data)})
            except Exception as e:
                if source == JsonSource.COMMON: source = "Common parameters"
                elif source == JsonSource.IDFP: source = "IDFP position data"
                elif source == JsonSource.FRIENDLY: source = "Friendly position data"
                elif source == JsonSource.TARGET: source = "Target position data"
                elif source == JsonSource.FIREMISSION: source = "Fire mission data"
                elif source == JsonSource.MESSAGELOG: source = "Message log"
                else: source = "Artillery Configurations"
                self.StatusMessageErrorDump(e, errorMessage=f"Failed to save {source}, returning False")
                return False
    def Delete(self,source:JsonSource, deleteKey: str | list | tuple | None = None, localOverride = False) -> bool:
        """
        deleteKey specifies the list or string of the key that needs to be deleted from the source
        """
        try:
            if source is not JsonSource.MESSAGELOG:
                data = {}
            else:
                data = ""
            if deleteKey != None:
                data = self.Load(source,localOverride)
                if type(deleteKey) == str: deleteKey = [deleteKey]
                for key in deleteKey:
                    data.pop(str(key),None)
            self.Save(source,data,False,localOverride)
            return True
        except Exception as e:
                if source == JsonSource.COMMON: source = "Common parameters"
                elif source == JsonSource.IDFP: source = "IDFP position data"
                elif source == JsonSource.FRIENDLY: source = "Friendly position data"
                elif source == JsonSource.TARGET: source = "Target position data"
                elif source == JsonSource.FIREMISSION: source = "Fire mission data"
                elif source == JsonSource.MESSAGELOG: source = "Message log"
                else: source = "Artillery Configurations"
                self.StatusMessageErrorDump(e, errorMessage=f"Failed to delete {source}, returning False")
                return False
        

class UksfAccounts():
    def __init__(self,StatusMessageErrorDump):
        self.StatusMessageErrorDump = StatusMessageErrorDump
        self.authToken = None
    def GetAuthToken(self,email:str, password:str) -> str:
        self.authToken = requests.post(url="https://api.uk-sf.co.uk/auth/login",json={"email" : email.strip(), "password" : password}).json()
        return self.authToken
    def GetAccount(self,authToken: dict | None = None,castJson: CastJson | None = None) -> dict | None:
        if authToken is None:
            authToken = self.authToken
        try:
            account = requests.get(url="https://api.uk-sf.co.uk/accounts",headers={"Authorization":"Bearer " + authToken["token"]}).json()
            account["displayName"]
        except:
            try:
                if castJson is CastJson:
                    castJson.SyncAuthToken(None)
                return authToken["error"]
            except Exception as e: self.StatusMessageErrorDump(e,"Failed to produce login error")
            return None
        else: return account
    def SaveAuthTokenLocal(self,appData_local,authToken: dict | None = None) -> None:
        if authToken is None:
            authToken = self.authToken
        with open(file=appData_local/"UKSF"/"CAST"/"auth.json",mode="w") as file:
            json.dump(self.authToken,file,indent=4)
    def RefreshAuthToken(self,appData_local) -> None:
        try:
            with open(file=appData_local/"UKSF"/"CAST"/"auth.json",mode="r") as file:
                self.authToken = json.loads(file.read())
            account = requests.get(url="https://api.uk-sf.co.uk/accounts",headers={"Authorization":"Bearer " + self.authToken["token"]}).json()
            account["displayName"]
        except:
            return None
        else:
            with open(file=appData_local/"UKSF"/"auth.json",mode="w") as file:
                json.dump(requests.get(url="https://api.uk-sf.co.uk/auth/refresh",headers={"Authorization":"Bearer " + self.authToken["token"]}).json(),file,indent=4)
            return account
    def Logout(self,appData_local):
        with open(file=appData_local/"UKSF"/"CAST"/"auth.json",mode="w") as file:
            file.write("")

            




