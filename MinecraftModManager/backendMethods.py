import translate
from usefulVariables import *  # local variables
import locale
from packaging.version import Version
from pathlib import Path
import PyQt5.QtWidgets as Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore, QtGui
from bs4 import BeautifulSoup
from datetime import datetime
import minecraft_launcher_lib
import traceback
import platformdirs
import threading
import subprocess
import requests
import logging
import shutil
import glob
import json
import time
import os

localPath = Path(__file__).resolve().parent  # path of the software folder
appDataDir = Path(platformdirs.user_data_dir("MinecraftModManager", appauthor="Ilwan"))  # path to the save data folder

langLocale, _ = locale.getlocale()
if langLocale: userLanguage = langLocale.split("_")[0]
else:
    langLocale = os.environ.get("LANG")
    if langLocale: userLanguage = langLocale.split("_")[0]
    else: userLanguage = "en"
Language = translate.Translator(Path(__file__).resolve().parent/"locales", userLanguage)
lang = Language.translate

log = logging.getLogger(__name__)


class Methods():
    def __init__(self):
        """a class containing usefull methods and threads"""
        self.curseforgeModloaders = {"fabric": 4, "forge": 1, "neoforge": 6, "quilt": 5}
        self.curseforgeReleases = {1: "release", 2: "beta", 3: "alpha"}
        profilesDir.mkdir(parents=True, exist_ok=True)
        cacheDir.mkdir(parents=True, exist_ok=True)

        if not settingsFile.exists():
            with open(settingsFile, "w", encoding="utf-8") as f:
                json.dump({"minecraftFolder": minecraft_launcher_lib.utils.get_minecraft_directory(),
                           "offlineUsername": "Player"}, f, indent=4)
        self.loadSettings()
        self.minecraftModsPath.mkdir(parents=True, exist_ok=True)

    def loadSettings(self):
        """load values from the settings the settings"""
        if settingsFile.exists():
            with open(settingsFile, "r") as file:
                settings = json.load(file)
            self.minecraftAppdataPath = Path(settings["minecraftFolder"])
            self.minecraftModsPath = self.minecraftAppdataPath/"mods"
            self.offlineUsername = settings["offlineUsername"]

    def curseforgeRequest(self, endpoint, **params) -> dict:
        """make a generic request to the curseforge api via the proxy containing the api key"""
        url = f"{curseForgeApi}/{endpoint}"

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # check if response is valid
            if response.status_code != 200:
                log.warning(f"got status code {response.status_code} while requesting curseforge proxy\nusing endpoint '{endpoint}' with params {params}")
            return response.json()
        except requests.exceptions.RequestException as e:
            log.error(f"error while requesting to curseforge proxy : {e}\nusing endpoint '{endpoint}' with params {params}")
            return None
    
    def curseforgeSearchMod(self, query:str, modloader:str, onlyCompatible:bool=False, version:str=None, nbResults:int=50) -> dict:
        """search for a mod on curseforge"""
        if onlyCompatible:
            result = self.curseforgeRequest(endpoint="mods/search", gameId=432, searchFilter=query, modLoaderType=self.curseforgeModloaders[modloader.lower()], pageSize=nbResults, classId=6, gameVersion=version)
        else:
            result = self.curseforgeRequest(endpoint="mods/search", gameId=432, searchFilter=query, modLoaderType=self.curseforgeModloaders[modloader.lower()], pageSize=nbResults, classId=6)
        result = {"data": [mod for mod in result["data"] if mod["allowModDistribution"]]}  # filter out mods that don't allow distribution
        log.info(f"searched for mod on curseforge: {query}")
        return result

    def modrinthRequest(self, endpoint:str, **params) -> dict:
        """directly make a generic request to the modrinth api"""
        url = f"{modrinthApi}/{endpoint}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            if response.status_code != 200:
                log.warning(f"got status code {response.status_code} while requesting curseforge proxy\nusing endpoint '{endpoint}' with params {params}")
            return response.json()
        except requests.exceptions.RequestException as e:
            log.error(f"error while requesting to modrinth api : {e}\nusing endpoint '{endpoint}' with params {params}")
            return None
    
    def modrinthSearchMod(self, query:str, modloader:str, onlyCompatible:bool=False, version:str=None, nbResults:int=100) -> dict:
        """search for a mod on modrinth"""
        if onlyCompatible:
            result = self.modrinthRequest(endpoint="search", query=query, facets=f'[["categories:{modloader.lower()}"],["versions:{version}"]]', limit=nbResults)
        else:
            result = self.modrinthRequest(endpoint="search", query=query, facets=f'[["categories:{modloader.lower()}"]]', limit=nbResults)
        log.info(f"searched for mod on modrinth: {query}")
        return result

    def searchMod(self, query:str, platform:str, modloader:str, onlyCompatible:bool=False, version:str=None, nbResults:int=50) -> dict:
        """search for a mod on a specific platform"""
        if platform.lower() == "modrinth":
            return self.modrinthSearchMod(query, modloader.lower(), onlyCompatible, version, nbResults)
        elif platform.lower() == "curseforge":
            return self.curseforgeSearchMod(query, modloader.lower(), onlyCompatible, version, nbResults)
    
    def listMcVersions(self, onlyReleases:bool=True) -> list:
        """returns a list of all the minecraft versions"""
        acceptedTypes = ["release"]
        if not onlyReleases:
            acceptedTypes.append("snapshot")
        self.allMcVersions = minecraft_launcher_lib.utils.get_version_list()
        self.filteredMcVersions = [version for version in self.allMcVersions if version["type"] in acceptedTypes]
        self.onlyMinecraftVersions = [version["id"] for version in self.filteredMcVersions]
        return self.onlyMinecraftVersions

    def getProfiles(self) -> dict:
        """get a dictionary of all the profiles and their properties"""
        self.profiles = {}
        for profile in [Path(item).name for item in glob.glob(str(profilesDir/"*"))]:
            with open(profilesDir/profile/"properties.json", "r", encoding="utf-8") as f:
                self.profiles[profile] = json.load(f)
        return self.profiles
    
    def modrinthSearchToMods(self, searchResult:dict) -> list:
        """convert a search result from modrinth to a list of mods data with the name, author, id, platform and icon path in cache, and the complete raw data"""
        iconCacheDir = cacheDir/"modIcons"/"modrinth"
        self.mods = []
        for mod in searchResult["hits"]:
            if mod["project_type"] == "mod": # only accept mods, no modpacks
                self.mods.append({"name": mod["title"], "author": mod["author"], "id": mod["project_id"], "platform": "modrinth",
                                  "icon": iconCacheDir/f"{mod['project_id']}.png", "webpage": f"https://modrinth.com/mod/{mod['slug']}", "rawData": mod})
        return self.mods

    def curseforgeSearchToMods(self, searchResult:dict) -> list:
        """convert a search result from curseforge to a list of mods data with the name, author, id, platform and icon path in cache, and the complete raw data"""
        iconCacheDir = cacheDir/"modIcons"/"curseforge"
        self.mods = []
        for mod in searchResult["data"]:
            authors = ", ".join([author["name"] for author in mod["authors"]])
            self.mods.append({"name": mod["name"], "author": authors, "id": str(mod["id"]), "platform": "curseforge",
                              "icon": iconCacheDir/f"{mod['id']}.png", "webpage": mod["links"]["websiteUrl"], "rawData": mod})
        return self.mods
    
    def downloadIcon(self, platform:str, id:str, iconUrl:str, modWidget=None):
        """download the icon of a mod in cache, eventually updating the widget when downloaded"""
        iconCacheDir = cacheDir/"modIcons"/platform.lower()
        iconCacheDir.mkdir(parents=True, exist_ok=True)
        if not (iconCacheDir/f"{id}.png").exists():
            if iconUrl:  # if the mod has an icon
                with open(iconCacheDir/f"{id}.png", "wb") as f:
                    f.write(requests.get(iconUrl).content)
                if modWidget:
                    modWidget.updateIcon()

    def getModInfos(self, modId:str, platform:str) -> dict:
        """do a request to get every informations about a mod"""
        if platform.lower() == "modrinth":
            return self.modrinthRequest(f"project/{modId}")
        elif platform.lower() == "curseforge":
            return self.curseforgeRequest(f"mods/{modId}")
    
    def cleanHtml(self, html:str) -> str:
        """clean an html string from all the links and images, replacing them with a textual version"""
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a"):
            p = soup.new_string(a.get_text())
            p.string = a.get_text()
            a.replace_with(p)
        for img in soup.find_all("img"):
            img.decompose()
        return str(soup)
    
    def getVersionsInfos(self, modId:str, platform:str, modloader:str, onlyCompatible:bool=False, mcVersion:str=None) -> dict:
        """get a dictionary of all the versions of a mod with version as key,
        then the minecraft versions, version id, the mod id, the platform, the modloader, the release type, the download url and the filename"""
        self.modVersions = {}
        self.modVersionsData = []
        self.modVersionThreads = []

        versionsDataCache = cacheDir/"modsVersions"/platform.lower()/modId
        modsDataCache = cacheDir/"modsData"/platform.lower()
        modsDataCache.mkdir(parents=True, exist_ok=True)

        if platform.lower() == "modrinth":
            # either request and save or load the mod data
            if (modsDataCache/f"{modId}.json").exists():
                with open(modsDataCache/f"{modId}.json", "r", encoding="utf-8") as f:
                    modData = json.load(f)
            else:
                modData = self.getModInfos(modId, platform.lower())
                with open(modsDataCache/f"{modId}.json", "w", encoding="utf-8") as f:
                    json.dump(modData, f, indent=4)
            
            teamData = self.modrinthRequest(f"project/{modId}/members") if "team" in modData else None
            if teamData:
                authors = ", ".join([member["user"]["username"] for member in teamData])
            else:
                authors = ""
            iconUrl = modData["icon_url"]
            
            versionsIds = modData["versions"]
            if (versionsDataCache).exists():
                self.modVersionsData = [json.load(open(versionsDataCache/f"{versionId}.json", "r", encoding="utf-8")) for versionId in versionsIds if (versionsDataCache/f"{versionId}.json").exists()]
            else:
                versionsDataCache.mkdir(parents=True, exist_ok=True)
                self.modVersionsData = self.modrinthRequest("versions", ids=str(versionsIds).replace("'", '"'))
                for versionData in self.modVersionsData:
                    with open(versionsDataCache/f"{versionData['id']}.json", "w", encoding="utf-8") as f:
                        json.dump(versionData, f, indent=4)
            
            self.modVersionsData.sort(key=lambda data: datetime.fromisoformat(data["date_published"].replace("Z", "")), reverse=True)
            for versionData in self.modVersionsData:
                if modloader.lower() in versionData["loaders"]:
                    if onlyCompatible:
                        if mcVersion not in versionData["game_versions"]:
                            continue
                    self.modVersions[versionData["version_number"]] = {"mcVersions": versionData["game_versions"],
                                                                       "versionId": versionData["id"],
                                                                       "modId": modId, "platform": platform.lower(), "modloader": modloader.lower(),
                                                                       "releaseType": versionData["version_type"],
                                                                       "downloadUrl": versionData["files"][0]["url"],
                                                                       "fileName": versionData["files"][0]["filename"],
                                                                       "versionName": versionData["version_number"],
                                                                       "modName": modData["title"],
                                                                       "authors": authors,
                                                                       "iconUrl": iconUrl,
                                                                       "webpage": f"https://modrinth.com/mod/{modData['slug']}"}
        elif platform.lower() == "curseforge":
            # either request and save or load the mod data
            if (modsDataCache/f"{modId}.json").exists():
                with open(modsDataCache/f"{modId}.json", "r", encoding="utf-8") as f:
                    modData = json.load(f)
            else:
                modData = self.getModInfos(modId, platform.lower())
                with open(modsDataCache/f"{modId}.json", "w", encoding="utf-8") as f:
                    json.dump(modData, f, indent=4)

            authors = ", ".join([author["name"] for author in modData["data"]["authors"]])
            iconUrl = modData["data"]["logo"]["thumbnailUrl"] if "logo" in modData["data"] else None

            versionsIds = [modVersion["fileId"] for modVersion in modData["data"]["latestFilesIndexes"]]
            if (versionsDataCache).exists():
                self.modVersionsData = [json.load(open(versionsDataCache/f"{versionId}.json", "r", encoding="utf-8")) for versionId in versionsIds if (versionsDataCache/f"{versionId}.json").exists()]
            else:
                versionsDataCache.mkdir(parents=True, exist_ok=True)
                index = 0
                self.modVersionsData = []
                while index < len(versionsIds):
                    self.modVersionsData.extend([{"data": version} for version in self.curseforgeRequest(f"mods/{modId}/files", pageSize=50, index=index)["data"]])
                    index += 50
                for versionData in self.modVersionsData:
                    with open(versionsDataCache/f"{versionData['data']['id']}.json", "w", encoding="utf-8") as f:
                        json.dump(versionData, f, indent=4)

            self.modVersionsData.sort(key=lambda data: datetime.fromisoformat(data["data"]["fileDate"].replace("Z", "")), reverse=True)
            for versionData in self.modVersionsData:
                if modloader.lower() in [version.lower() for version in versionData["data"]["gameVersions"]]:
                    if onlyCompatible:
                        if mcVersion not in versionData["data"]["gameVersions"]:
                            continue
                    self.modVersions[versionData["data"]["displayName"]] = {"mcVersions": [mcVersion["gameVersion"] for mcVersion in versionData["data"]["sortableGameVersions"] if mcVersion["gameVersion"]],
                                                                "versionId": versionData["data"]["id"],
                                                                "modId": modId, "platform": platform.lower(), "modloader": modloader.lower(),
                                                                "releaseType": self.curseforgeReleases[versionData["data"]["releaseType"]],
                                                                "downloadUrl": versionData["data"]["downloadUrl"],
                                                                "fileName": versionData["data"]["fileName"],
                                                                "versionName": versionData["data"]["displayName"],
                                                                "modName": modData["data"]["name"],
                                                                "authors": authors,
                                                                "iconUrl": iconUrl,
                                                                "webpage": modData["data"]["links"]["websiteUrl"]}
        else:
            log.error(f"platform {platform} is not supported, cannot get versions infos")
        return self.modVersions
    
    def removeCurrentMod(self, profile:str, modId:str, platform:str, auto:bool=False):
        """remove the currently selected mod"""
        currentModPath = profilesDir/profile/platform.lower()/modId
        if os.path.exists(currentModPath):
            if not auto:
                confirm = QMessageBox.question(None, lang("removeMod"), lang("removeModConfirm"), QMessageBox.Yes | QMessageBox.No)
                if confirm == QMessageBox.No:
                    return -1  # removal cancelled
            shutil.rmtree(currentModPath)
            log.info(f"Removed mod at {currentModPath}")
            if not auto:
                QMessageBox.information(None, lang("success"), lang("modRemoved"))
        else:
            log.warning(f"Mod at {currentModPath} not found")

    def installCurrentMod(self, profile:str, modId:str, platform:str, modVersionData:str):
        """install the currently selected mod"""
        #TODO: put a window during download
        if modVersionData is None:
            log.warning("No mod version data provided, cannot install the mod")
            QMessageBox.warning(None, lang("error"), lang("noVersionSelected"))
            return
        currentModPath = profilesDir/profile/platform.lower()/modId
        # check if the mod is already installed
        if os.path.exists(currentModPath):
            previousVersionId = json.load(open(currentModPath/"properties.json", "r", encoding="utf-8"))["versionId"]
            if previousVersionId != modVersionData["versionId"]:  # if the mod is already installed but with a different version
                confirm = QMessageBox.question(None, lang("updateMod"), lang("updateModConfirm"), QMessageBox.Yes | QMessageBox.No)
                if confirm == QMessageBox.No:
                    return -1
                log.warning(f"Mod at {currentModPath} already installed, updating")
                self.removeCurrentMod(profile, modId, platform, auto=True)
            else:
                return # the mod is already installed with the same version
        QMessageBox.information(None, lang("success"), lang("modInstalled"))
        # install the mod
        currentModPath.mkdir(parents=True, exist_ok=True)
        with open(currentModPath/"properties.json", "w", encoding="utf-8") as f:
            json.dump(modVersionData, f, indent=4)
        with open(currentModPath/modVersionData["fileName"], "wb") as f:
            f.write(requests.get(modVersionData["downloadUrl"]).content)
        log.info(f"Installed mod '{modVersionData['modName']}' version '{modVersionData['versionName']}' in profile {profile}")
    
    def getInstalledMods(self, profile:str) -> list:
        """get a list of the data of all the installed mods in a profile, sorted by name then the custom jar mods"""
        if profile is None:
            log.warning("No profile provided, cannot get installed mods")
            return []
        currentProfileDir = profilesDir/profile
        installedMods = []
        if currentProfileDir.exists():
            for platform in availablePlatforms:
                if (currentProfileDir/platform).exists():
                    for mod in glob.glob(str(currentProfileDir/platform/"*")):
                        if os.path.isdir(mod):
                            with open(Path(mod)/"properties.json", "r", encoding="utf-8") as f:
                                installedMods.append(json.load(f))
        else:
            log.error(f"Profile {profile} not found")
        installedMods.sort(key=lambda mod: mod["modName"])
        installedMods.extend([Path(file).name for file in glob.glob(str(currentProfileDir/"jar"/"*")) if os.path.isfile(Path(file))])
        return installedMods

    def removeProfile(self, profile:str):
        """remove a profile with all its mods"""
        if profile is None:
            log.warning("No profile provided, cannot remove profile")
            return
        profilePath = profilesDir/profile
        if profilePath.exists():
            shutil.rmtree(profilePath)
            log.info(f"Removed profile {profile}")
            QMessageBox.information(None, lang("success"), lang("profileRemoved"))
        else:
            log.error(f"Profile {profile} not found")
    
    def applyProfile(self, profile:str, auto:bool=False):
        """apply a profile to the minecraft game directory"""
        if not profile:
            log.warning("No profile provided, cannot apply profile")
            return
        profilePath = profilesDir/profile
        if not profilePath.exists():
            log.error(f"Profile {profile} not found")
            return
        if not auto:
            confirm = QMessageBox.question(None, lang("applyProfileTitle"), lang("applyProfileConfirm"), QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.No:
                return -1
        for previousMod in glob.glob(str(self.minecraftModsPath/"*")):
            if os.path.isfile(previousMod):
                os.remove(previousMod)
        for platform in availablePlatforms:
            if (profilePath/platform).exists():
                for mod in glob.glob(str(profilePath/platform/"*")):
                    if os.path.isdir(mod):
                        with open(Path(mod)/"properties.json", "r", encoding="utf-8") as f:
                            modData = json.load(f)
                        shutil.copyfile(Path(mod)/modData["fileName"], self.minecraftModsPath/modData["fileName"])
        for jarMod in glob.glob(str(profilePath/"jar"/"*")):
            if os.path.isfile(jarMod):
                shutil.copyfile(jarMod, self.minecraftModsPath/Path(jarMod).name)
        log.info(f"Applied profile {profile}")
        if not auto:
            QMessageBox.information(None, lang("success"), lang("profileApplied"))
    
    def installJarMod(self, profile:str, modPath:Path):
        """install a jar mod to the profile"""
        jarFolder = profilesDir/profile/"jar"
        jarFolder.mkdir(parents=True, exist_ok=True)
        filename = modPath.name
        if (jarFolder/modPath.name).exists():
            confirm = QMessageBox.question(None, lang("jarConflictTitle"), f"{lang("jarConflictMessage1")} {filename} {lang("jarConflictMessage2")}", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if confirm == QMessageBox.Yes:
                os.remove(jarFolder/modPath.name)
            elif confirm == QMessageBox.No:
                ext = filename.split(".")[-1]
                filename = f"{'.'.join(modPath.name.split('.')[:-1])}_1"
                num = 1
                while (jarFolder/f"{filename}.{ext}").exists():
                    num += 1
                    filename = f"{'_'.join(filename.split('_')[:-1])}_{num}"
                filename = f"{filename}.{ext}"
            else:
                log.info(f"Cancelled installation of jar mod {filename} in profile {profile}")
                return -1
        shutil.copyfile(modPath, jarFolder/filename)
        log.info(f"Installed jar mod {filename} in profile {profile}")
    
    def renameProfile(self, currentName:str, newName:str):
        """rename a profile"""
        if not currentName:
            log.warning("No profile provided, cannot rename profile")
            return
        
        currentProfilePath = profilesDir/currentName
        newProfilePath = profilesDir/newName
        oldProperties = json.load(open(currentProfilePath/"properties.json", "r", encoding="utf-8"))
        oldProperties["name"] = newName
        with open(currentProfilePath/"properties.json", "w", encoding="utf-8") as f:
            json.dump(oldProperties, f, indent=4)
        shutil.move(currentProfilePath, newProfilePath)
        log.info(f"Renamed profile {currentName} to {newName}")
        QMessageBox.information(None, lang("success"), lang("profileRenamed"))
    
    def launchGame(self, profile:str):
        """launch the minecraft game"""
        if not profile:
            log.warning("No profile provided, cannot launch game")
            return
        profilePath = profilesDir/profile
        if not profilePath.exists():
            log.error(f"Profile {profile} not found")
            return
        with open(profilePath/"properties.json", "r", encoding="utf-8") as f:
            properties = json.load(f)
            modloader = properties["modloader"].lower()
            version = properties["version"]

        bestLoaderVersion = self.getBestLoaderVersion(modloader, version)
        if bestLoaderVersion == -1:
            log.error(f"Error while getting best loader version for profile {profile}, cannot launch game")
            QMessageBox.critical(None, lang("error"), lang("invalidGameFolder"))
            return
        if not bestLoaderVersion:
            log.warning(f"Loader {modloader} not found for version {version}, cannot launch game")
            QMessageBox.warning(None, lang("error"), lang("versionNotFound"))
            self.openLoaderDownloadWebsite(modloader)
            return

        options = {
            "username": self.offlineUsername,
            "uuid": "00000000-0000-0000-0000-000000000000",  # Placeholder UUID
            "token": "token",  # Placeholder token
            "launcherName": "Minecraft Mod Manager",
            "launcherVersion": appVersion
        }  #TODO: implement login
        
        log.info("saving previous mods")
        self.savePreviousMods()
        log.info(f"applying profile {profile}")
        self.applyProfile(profile, auto=True)
        log.info(f"Launching game in offline mode with profile {profile}")
        self.runningPopup = Qt.QMessageBox(Qt.QMessageBox.Information, lang("launchedGame"), lang("launchedGameMessage"), Qt.QMessageBox.NoButton)
        self.gameRunning = True  # true until the game is closed
        gameThread = threading.Thread(target=self.openGame, args=(bestLoaderVersion, options))
        gameThread.start()
        self.runningPopup.exec_()
        while self.gameRunning:
            self.runningPopup.exec_()
    
    def openGame(self, version, options):
        """open the minecraft game once everything is set up"""
        try:
            subprocess.run(minecraft_launcher_lib.command.get_minecraft_command(version, self.minecraftAppdataPath, options))
        except Exception as e:
            log.error(f"Error while launching game : {e}")
            error_message = f"Error while launching game: {e}\n\n{traceback.format_exc()}"
            QMessageBox.critical(None, lang("error"), error_message)
        self.restorePreviousMods()
        self.gameRunning = False
        log.info("game closed, restored previous mods")
    
    def savePreviousMods(self):
        """save the previous mods to restore them after the game is closed"""
        modsStorage = cacheDir/"previousMods"
        modsStorage.mkdir(parents=True, exist_ok=True)
        for mod in glob.glob(str(self.minecraftModsPath/"*")):
            if os.path.isfile(mod):
                shutil.copyfile(mod, modsStorage/Path(mod).name)
                os.remove(mod)
        

    def restorePreviousMods(self):
        """restore the previous mods after the game is closed"""
        modsStorage = cacheDir/"previousMods"
        if modsStorage.exists():
            # delete the current mods
            while True:
                try:
                    for currentMod in glob.glob(str(self.minecraftModsPath/"*")):
                        if os.path.isfile(currentMod):
                            os.remove(currentMod)
                    break
                except PermissionError:
                    log.warning("Permission error while deleting current mods, retrying")
                    time.sleep(0.1)
            # restore the previous mods
            for mod in glob.glob(str(modsStorage/"*")):
                if os.path.isfile(mod):
                    shutil.copyfile(mod, self.minecraftModsPath/Path(mod).name)
            shutil.rmtree(modsStorage)
        else:
            log.error("No previous mods found to restore")

    def getBestLoaderVersion(self, modloader:str, mcVersion:str) -> str:
        """get the latest version of a modloader for a minecraft version from the installed versions"""
        mcVersionIndex = {"fabric": 3, "forge": 0, "neoforge": None, "quilt": 3}  # the index of the minecraft version when split by '-', neoforge will he handled differently
        candidates = []
        installedVersions = self.listInstalledVersions()
        if installedVersions == -1:
            return -1  # error while listing installed versions
        for version in installedVersions:
            if modloader in version:
                if modloader == "neoforge":
                    if mcVersion.split(".")[1:] in version.split("-")[1]:  # adapt to the naming convention of neoforge (for mc 1.21 and neo 167, 'neoforge-21.0.167')
                        candidates.append(version)
                else:
                    if mcVersion == version.split("-")[mcVersionIndex[modloader]]:
                        candidates.append(version)
        if candidates:
            candidates = self.semanticSort(candidates, modloader)
            return candidates[-1]
    
    def semanticSort(self, versions:list, loader:str) -> list:
        """sort a list of modloader versions semantically"""
        semanticIndex = {"fabric": 2, "forge": 2, "neoforge": 2, "quilt": 2}  # the index of the "pure" semantic version when split by '-'
        return sorted(versions, key=lambda version: Version(version.split("-")[semanticIndex[loader]]))

    def listInstalledVersions(self) -> list:
        """list all the installed versions of the modloaders"""
        versionsFolder = self.minecraftAppdataPath/"versions"
        if not versionsFolder.exists():
            log.error(f"Versions folder {versionsFolder} not found, the game folder is probably incorrect")
            return -1
        installedVersions = []
        for version in os.listdir(versionsFolder):
            if os.path.isdir(versionsFolder/version):
                installedVersions.append(version)
        return installedVersions

    def openLoaderDownloadWebsite(self, modloader:str):
        """open the download website for a modloader"""
        modloader = modloader.lower()
        websites = {"fabric": "https://fabricmc.net/", "forge": "https://files.minecraftforge.net/net/minecraftforge/forge/", "neoforge": "https://projects.neoforged.net/neoforged/neoforge", "quilt": "https://quiltmc.org/"}
        if modloader in websites:
            log.info(f"Opening website for modloader {modloader}")
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(websites[modloader]))
        else:
            log.warning(f"Modloader {modloader} not found in the list of websites")
    
    def exportProfile(self, profile:str, exportPath:str):
        """export a profile to a zip file"""
        exportPath = Path(exportPath).with_suffix("")
        if not profile:
            log.warning("No profile provided, cannot export profile")
            return -1
        profilePath = profilesDir/profile
        if not profilePath.exists():
            log.error(f"Profile {profile} not found")
            return -1
        tempProfilePath = cacheDir/"tempProfile"
        tempProfilePath.mkdir(parents=True, exist_ok=True)
        shutil.copytree(profilePath, tempProfilePath/profile)
        shutil.make_archive(str(exportPath), "zip", root_dir=str(tempProfilePath))
        shutil.rmtree(tempProfilePath)
    
    def importProfile(self, importPath:str):
        """import a profile from a zip file"""
        if not Path(importPath).exists():
            log.error(f"Import file {importPath} not found")
            return -1
        tempProfilePath = cacheDir/"tempProfile"
        tempProfilePath.mkdir(parents=True, exist_ok=True)
        shutil.unpack_archive(importPath, extract_dir=str(tempProfilePath))
        profileName = Path(importPath).stem
        if (profilesDir/profileName).exists():
            confirm = QMessageBox.question(None, lang("profileExists"), lang("profileExistsMessage"), QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if confirm == QMessageBox.Yes:
                shutil.rmtree(profilesDir/profileName)
                shutil.move(tempProfilePath/profileName, profilesDir)
            elif confirm == QMessageBox.No:
                newName = f"{profileName}_1"
                num = 1
                while (profilesDir/newName).exists():
                    num += 1
                    filename = f"{'_'.join(filename.split('_')[:-1])}_{num}"
                shutil.copytree(tempProfilePath/profileName, profilesDir/newName)
                shutil.rmtree(tempProfilePath)
                oldData = json.load(open(profilesDir/newName/"properties.json", "r", encoding="utf-8"))
                oldData["name"] = newName
                with open(profilesDir/newName/"properties.json", "w", encoding="utf-8") as f:
                    json.dump(oldData, f, indent=4)
            else:
                log.info(f"Cancelled import of profile {profileName}")
                return -1
        else:
            shutil.move(tempProfilePath/profileName, profilesDir)
    
    def getInstalledVersion(self, profile:str, modId:str, platform:str):
        """get the installed version of a mod if installed, else return None"""
        modPath = profilesDir/profile/platform.lower()/modId
        if modPath.exists():
            with open(modPath/"properties.json", "r", encoding="utf-8") as f:
                return json.load(f)["versionName"]
        else:
            return None
