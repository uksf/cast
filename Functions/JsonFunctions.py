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
        self.fileNameDict = {
            JsonSource.COMMON : "common",
            JsonSource.IDFP : "idfp",
            JsonSource.FRIENDLY: "friendly",
            JsonSource.TARGET: "target",
            JsonSource.FIREMISSION : "fireMissions",
            JsonSource.MESSAGELOG: "message_log"
            }
        self.jsonType = JsonType.LOCAL
        self.loaded = {}
        """Loaded Json files, to be used with unimportant operations"""
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
            jsonFile = json.loads(response.json()["data"]) if response.json()["data"] is not None else {}
            if jsonFile is None:
                if jsonName == "message_log":
                    return {'message':''}
                return {}
            return jsonFile
    def Load(self,source: JsonSource,localOverride = False,requestedSave = False) -> dict | str:
        """
        Loads and returns the Json data from the specified source. Takes the "json" arguement and uses the appropriate json source
        """
        if self.jsonType == JsonType.LOCAL or localOverride == True or source == JsonSource.ARTILLERYCONFIG or self.authToken is None:
            try:
                if source != JsonSource.ARTILLERYCONFIG:
                    with open(self.appData_local/"UKSF"/"CAST"/f"{self.fileNameDict[source]}.json","r") as file:
                        loadedDict = json.load(file)
                        if requestedSave == False:
                            self.loaded[source] = loadedDict
                        return loadedDict if source != JsonSource.MESSAGELOG else str(loadedDict["message"])
                else:
                    with open(self.exeDir/"Functions"/"ArtilleryConfigs.json",mode="r") as file:
                        return json.load(file)
            except Exception as e:
                if source != JsonSource.ARTILLERYCONFIG:
                    try:
                        with open(self.appData_local/"UKSF"/"CAST"/f"{self.fileNameDict[source]}.json",mode="w") as f:
                            if source != JsonSource.MESSAGELOG:
                                json.dump({},f,indent=4)
                            else:
                                json.dump({"message":""},f,indent=4)
                                self.UIMaster.StatusMessageErrorDump(e, errorMessage=f"Failed to load {self.fileNameDict[source]}, returning nothing")
                                return ""
                    except: None
                else:
                    self.UIMaster.StatusMessageErrorDump(e, errorMessage="Failed to load Artillery Configurations, returning nothing")
                    return {}
                self.UIMaster.StatusMessageErrorDump(e, errorMessage=f"Failed to load {self.fileNameDict[source]}, returning nothing")
                return {}
                
        elif self.jsonType ==JsonType.SERVER:
            try:
                sourceJson = self._requestHandle(self.fileNameDict[source])
                if type(sourceJson) != str:
                    if source is JsonSource.MESSAGELOG:
                        return sourceJson["message"]
                    else: return sourceJson
                else:
                    self.UIMaster.StatusMessageErrorDump(e, errorMessage=f"Failed to load {source} due to {sourceJson}, returning nothing",localOverride=True)
                    if requestedSave:
                        return requests.RequestException
            except Exception as e:
                if source == JsonSource.MESSAGELOG:
                    self.UIMaster.StatusMessageErrorDump(e, errorMessage="Failed load Message log, returning nothing",localOverride=True)
                    return ""
                else:
                    self.UIMaster.StatusMessageErrorDump(e, errorMessage=f"Failed to load {self.fileNameDict[source]}, returning nothing",localOverride=True)
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
                except TypeError: print("error")
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
            if source == JsonSource.MESSAGELOG: data["message"] = str(newEntry)
            else: data = newEntry
        self.loaded[source] = data
        if self.jsonType == JsonType.LOCAL or localOverride==True or self.authToken is None:
            try:
                with open(self.appData_local/"UKSF"/"CAST"/f"{self.fileNameDict[source]}.json","w") as file:
                    json.dump(data,file,indent=4)
                return True
            except Exception as e:
                self.UIMaster.StatusMessageErrorDump(e, errorMessage=f"Failed to save {self.fileNameDict[source]}, returning False")
                return False
        elif self.jsonType ==JsonType.SERVER:
            try:
                response = requests.put(url=f"https://api.uk-sf.co.uk/artillery/{self.fileNameDict[source]}",headers={"Authorization":"Bearer " + self.authToken["token"],"Content-Type": "application/json"},json={"data":json.dumps(data)})
                return response
            except Exception as e:
                self.UIMaster.StatusMessageErrorDump(e, errorMessage=f"Failed to save {self.fileNameDict[source]}, returning False",localOverride=True)
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
            self.UIMaster.StatusMessageErrorDump(e, errorMessage=f"Failed to delete {self.fileNameDict[source]}, returning False")
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

            




