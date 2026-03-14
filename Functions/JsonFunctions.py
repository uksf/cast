from enum import IntEnum
from pathlib import Path
import json
import requests
import ast

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
    def __init__(self,jsonType: JsonType,UIMaster,exeDir: Path,appData_local: Path | None = None,):
        self.jsonType = jsonType
        self.UIMaster = UIMaster
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
    def SyncAuthToken(self,authToken):
        self.authToken=authToken
        if authToken is not None:
            self.jsonType = JsonType.SERVER
        else: self.jsonType = JsonType.LOCAL

    def _requestHandle(self,jsonName:str):
        response = requests.get(url=f"https://api.uk-sf.co.uk/artillery/{jsonName}",headers={"Authorization":"Bearer " + self.authToken["token"]})
        if response.status_code!= 200:
            return f"{response.status_code}: {response.reason}"
        else:
            jsonFile = ast.literal_eval(response.json()["data"])
            return jsonFile
    def Load(self,source: JsonSource,localOverride = False,requestedSave = False) -> dict | str:
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
                    return ""
                else: source = "Artillery Configurations"
                self.UIMaster.StatusMessageErrorDump(e, errorMessage=f"Failed to load {source}, returning nothing")
                return {}
                
        elif self.jsonType ==JsonType.SERVER:
            try:
                if source == JsonSource.COMMON:
                    sourceJson = self._requestHandle("common")
                elif source == JsonSource.IDFP:
                    sourceJson = self._requestHandle("idfp")
                elif source == JsonSource.FRIENDLY:
                    sourceJson = self._requestHandle("friendly")
                elif source == JsonSource.TARGET:
                    sourceJson = self._requestHandle("target")
                elif source == JsonSource.FIREMISSION:
                    sourceJson = self._requestHandle("fireMissions")
                elif source == JsonSource.MESSAGELOG:
                    sourceJson = self._requestHandle("message_log")
                if type(sourceJson) != str:
                    if source is JsonSource.MESSAGELOG:
                        return sourceJson["message"]
                    else: return sourceJson
                else:
                    self.UIMaster.StatusMessageErrorDump(e, errorMessage=f"Failed to load {source} due to {sourceJson}, returning nothing",localOverride=True)
                    if requestedSave:
                        return requests.RequestException
            except Exception as e:
                if source == JsonSource.COMMON: source = "Common parameters"
                elif source == JsonSource.IDFP: source = "IDFP position data"
                elif source == JsonSource.FRIENDLY: source = "Friendly position data"
                elif source == JsonSource.TARGET: source = "Target position data"
                elif source == JsonSource.FIREMISSION: source = "Fire mission data"
                elif source == JsonSource.MESSAGELOG:
                    self.UIMaster.StatusMessageErrorDump(e, errorMessage="Failed load Message log, returning nothing",localOverride=True)
                    return ""
                else: source = "Artillery Configurations"
                self.UIMaster.StatusMessageErrorDump(e, errorMessage=f"Failed load {source}, returning nothing",localOverride=True)
                return {}
            
    def Save(self,source: JsonSource,newEntry: dict | str, append = True,localOverride = False) -> bool:
        """
        Loads the Json data from the specified source then saves new data if append = True, otherwise it overwrite the json. Takes the "json" arguement and uses the appropriate json source
        """
        data = {}
        if append:
            if source !=JsonSource.MESSAGELOG:
                try:
                    dataLoad = self.Load(source,localOverride,requestedSave=True)
                    if dataLoad is not requests.RequestException:
                        data = (dataLoad | newEntry)
                    else: return False
                except TypeError: None
            else:
                try:
                    dataLoad = self.Load(source,localOverride,requestedSave=True)
                    if dataLoad is not requests.RequestException:
                        message = dataLoad + str(newEntry)
                    else: return False
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
                self.UIMaster.StatusMessageErrorDump(e, errorMessage=f"Failed to save {source}, returning False")
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
                self.UIMaster.StatusMessageErrorDump(e, errorMessage=f"Failed to save {source}, returning False",localOverride=True)
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
                self.UIMaster.StatusMessageErrorDump(e, errorMessage=f"Failed to delete {source}, returning False")
                return False
        

class UksfAccounts():
    def __init__(self,UIMaster):
        self.UIMaster = UIMaster
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
            except Exception as e: self.UIMaster.StatusMessageErrorDump(e,"Failed to produce login error")
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
            self.UIMaster.user = account["displayName"]
        except:
            return None
        else:
            with open(file=appData_local/"UKSF"/"auth.json",mode="w") as file:
                json.dump(requests.get(url="https://api.uk-sf.co.uk/auth/refresh",headers={"Authorization":"Bearer " + self.authToken["token"]}).json(),file,indent=4)
            return account
    def Logout(self,appData_local):
        with open(file=appData_local/"UKSF"/"CAST"/"auth.json",mode="w") as file:
            file.write("")

            




