import translate
from usefulVariables import *  # local variables
import locale
from pathlib import Path
import PyQt5.QtWidgets as Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore, QtGui
from bs4 import BeautifulSoup
from datetime import datetime
import minecraft_launcher_lib
import platformdirs
import requests
import logging
import asyncio
import aiohttp
import shutil
import glob
import json
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


class Start():
    """a class that setups the software before launching the interface"""
    def start(self):
        """code to directly execute at the start of the program"""
        profilesDir.mkdir(parents=True, exist_ok=True)
        cacheDir.mkdir(parents=True, exist_ok=True)
        minecraftModsPath.mkdir(parents=True, exist_ok=True)


class Methods():
    def __init__(self):
        """a class containing usefull methods"""
        self.curseforgeModloaders = {"fabric": 4, "forge": 1, "neoforge": 6, "quilt": 5}
        self.curseforgeReleases = {1: "release", 2: "beta", 3: "alpha"}

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
                self.mods.append({"name": mod["title"], "author": mod["author"], "id": mod["project_id"], "platform": "modrinth", "icon": iconCacheDir/f"{mod['project_id']}.png", "rawData": mod})
        return self.mods

    def curseforgeSearchToMods(self, searchResult:dict) -> list:
        """convert a search result from curseforge to a list of mods data with the name, author, id, platform and icon path in cache, and the complete raw data"""
        iconCacheDir = cacheDir/"modIcons"/"curseforge"
        self.mods = []
        for mod in searchResult["data"]:
            authors = ", ".join([author["name"] for author in mod["authors"]])
            self.mods.append({"name": mod["name"], "author": authors, "id": str(mod["id"]), "platform": "curseforge", "icon": iconCacheDir/f"{mod['id']}.png", "rawData": mod})
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
                                                                       "iconUrl": modData["icon_url"]}
        elif platform.lower() == "curseforge":
            # either request and save or load the mod data
            if (modsDataCache/f"{modId}.json").exists():
                with open(modsDataCache/f"{modId}.json", "r", encoding="utf-8") as f:
                    modData = json.load(f)
            else:
                modData = self.getModInfos(modId, platform.lower())
                with open(modsDataCache/f"{modId}.json", "w", encoding="utf-8") as f:
                    json.dump(modData, f, indent=4)

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
                                                                "iconUrl": modData["data"]["logo"]["thumbnailUrl"] if "logo" in modData["data"] else None}
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
            confirm = QMessageBox.question(None, lang("removeProfileTitle"), lang("removeProfileConfirm"), QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.No:
                return -1
            shutil.rmtree(profilePath)
            log.info(f"Removed profile {profile}")
            QMessageBox.information(None, lang("success"), lang("profileRemoved"))
        else:
            log.error(f"Profile {profile} not found")
    
    def applyProfile(self, profile:str):
        """apply a profile to the minecraft game directory"""
        if not profile:
            log.warning("No profile provided, cannot apply profile")
            return
        profilePath = profilesDir/profile
        if not profilePath.exists():
            log.error(f"Profile {profile} not found")
            return
        confirm = QMessageBox.question(None, lang("applyProfileTitle"), lang("applyProfileConfirm"), QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.No:
            return -1
        for previousMod in glob.glob(str(minecraftModsPath/"*")):
            if os.path.isfile(previousMod):
                os.remove(previousMod)
        for platform in availablePlatforms:
            if (profilePath/platform).exists():
                for mod in glob.glob(str(profilePath/platform/"*")):
                    if os.path.isdir(mod):
                        with open(Path(mod)/"properties.json", "r", encoding="utf-8") as f:
                            modData = json.load(f)
                        shutil.copyfile(Path(mod)/modData["fileName"], minecraftModsPath/modData["fileName"])
        for jarMod in glob.glob(str(profilePath/"jar"/"*")):
            if os.path.isfile(jarMod):
                shutil.copyfile(jarMod, minecraftModsPath/Path(jarMod).name)
        log.info(f"Applied profile {profile}")
        QMessageBox.information(None, lang("success"), lang("profileApplied"))
    
    def installJarMod(self, profile:str, modPath:Path):
        """install a jar mod to the profile"""
        jarFolder = profilesDir/profile/"jar"
        jarFolder.mkdir(parents=True, exist_ok=True)
        filename = modPath.name
        if (jarFolder/modPath.name).exists():
            confirm = QMessageBox.question(None, lang("jarConflictTitle"), f"{lang("jarConflictMessage1")} {filename} {lang("jarConflictMessage2")}", QMessageBox.Yes | QMessageBox.No)
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
        shutil.copyfile(modPath, jarFolder/filename)
        log.info(f"Installed jar mod {filename} in profile {profile}")
