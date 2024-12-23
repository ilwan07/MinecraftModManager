import translate
from usefulVariables import *  # local variables
import locale
from pathlib import Path
import PyQt5.QtWidgets as Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore, QtGui
import minecraft_launcher_lib
import platformdirs
import requests
import logging
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


class Methods():
    """a class containing usefull methods"""
    def curseforgeRequest(self, endpoint, **params) -> dict:
        """make a generic request to the curseforge api via the proxy containing the api key"""
        serverUrl = "http://mmm.ilwan.hackclub.app/curseforge"
        url = f"{serverUrl}/{endpoint}"

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # check if response is valid
            if response.status_code != 200:
                log.warning(f"got status code {response.status_code} while requesting curseforge proxy\nusing endpoint '{endpoint}' with params {params}")
            return response.json()
        except requests.exceptions.RequestException as e:
            log.error(f"error while requesting to curseforge proxy : {e}\nusing endpoint '{endpoint}' with params {params}")
            return None
    
    def curseforgeSearchMod(self, query:str, modloader:str, onlyCompatible:bool=False, version:str=None, nbResults:int=20) -> dict:
        """search for a mod on curseforge"""
        modloaders = {"fabric": 4, "forge": 1, "neoforge": 6, "quilt": 5}
        if onlyCompatible:
            result = self.curseforgeRequest(endpoint="mods/search", gameId=432, searchFilter=query, modLoaderType=modloaders[modloader.lower()], gameVersion=version, pageSize=nbResults)
        else:
            result = self.curseforgeRequest(endpoint="mods/search", gameId=432, searchFilter=query, modLoaderType=modloaders[modloader.lower()], pageSize=nbResults)
        log.info(f"searched for mod on curseforge: {query}")
        return result

    def modrinthRequest(self, endpoint:str, **params) -> dict:
        """directly make a generic request to the modrinth api"""
        url = f"https://api.modrinth.com/v2/{endpoint}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            if response.status_code != 200:
                log.warning(f"got status code {response.status_code} while requesting curseforge proxy\nusing endpoint '{endpoint}' with params {params}")
            return response.json()
        except requests.exceptions.RequestException as e:
            log.error(f"error while requesting to modrinth api : {e}\nusing endpoint '{endpoint}' with params {params}")
            return None
    
    def modrinthSearchMod(self, query:str, modloader:str, onlyCompatible:bool=False, version:str=None, nbResults:int=20) -> dict:
        """search for a mod on modrinth"""
        if onlyCompatible:
            result = self.modrinthRequest(endpoint="search", query=query, facets=f'[["categories:{modloader.lower()}"],["versions:{version}"]]', limit=nbResults)
        else:
            result = self.modrinthRequest(endpoint="search", query=query, facets=f'[["categories:{modloader.lower()}"]]', limit=nbResults)
        log.info(f"searched for mod on modrinth: {query}")
        return result

    def searchMod(self, query:str, platform:str, modloader:str, onlyCompatible:bool=False, version:str=None, nbResults:int=20) -> dict:
        """search for a mod on a specific platform"""
        if platform.lower() == "modrinth":
            return self.modrinthSearchMod(query, modloader, onlyCompatible, version, nbResults)
        elif platform.lower() == "curseforge":
            return self.curseforgeSearchMod(query, modloader, onlyCompatible, version, nbResults)
    
    def listMcVersions(self, onlyReleases:bool=True) -> list:
        """returns a list of all the minecraft version"""
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
            with open(profilesDir/profile/"properties.json", "r") as f:
                self.profiles[profile] = json.load(f)
        return self.profiles
    
    def modrinthSearchToMods(self, searchResult:dict) -> list:
        """convert a search result from modrinth to a list of mods data with the name, id, platform and icon path in cache"""
        iconCacheDir = cacheDir/"modIcons"/"modrinth"
        iconCacheDir.mkdir(parents=True, exist_ok=True)
        self.mods = []
        for mod in searchResult["hits"]:
            if mod["project_type"] == "mod": # only accept mods, no modpacks
                self.mods.append({"name": mod["title"], "id": mod["project_id"], "platform": "modrinth", "icon": iconCacheDir/f"{mod['project_id']}.png"})
                # download the icon in cache
                if not (iconCacheDir/f"{mod['project_id']}.png").exists():
                    try:
                        with open(iconCacheDir/f"{mod['project_id']}.png", "wb") as f:
                            f.write(requests.get(mod["icon_url"]).content)
                    except:
                        log.warning(f"unable to download the icon of the mod {mod['title']} on modrinth")
        return self.mods

    def curseforgeSearchToMods(self, searchResult:dict) -> list:
        """convert a search result from curseforge to a list of mods data with the name, id, platform and icon path in cache"""
        iconCacheDir = cacheDir/"modIcons"/"curseforge"
        iconCacheDir.mkdir(parents=True, exist_ok=True)
        self.mods = []
        for mod in searchResult["data"]:
            self.mods.append({"name": mod["name"], "id": str(mod["id"]), "platform": "curseforge", "icon": iconCacheDir/f"{mod['id']}.png"})
            # download the icon in cache
            if not (iconCacheDir/f"{mod['id']}.png").exists():
                try:
                    with open(iconCacheDir/f"{mod['id']}.png", "wb") as f:
                        f.write(requests.get(mod["logo"]["url"]).content)
                except:
                    log.warning(f"unable to download the icon of the mod {mod['name']} on curseforge")
        return self.mods
    
    def getMods(self, profile:str) -> dict:
        """get a dictionary of all the mods in the profile, return a dict of the mods names (filenames if custom) and their properties (if not custom)"""
        pass  #TODO

class addProfilePopup(Qt.QDialog):
    """popup to create a new profile"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle(lang("addProfile"))
        self.mainLayout = Qt.QVBoxLayout()
        self.setLayout(self.mainLayout)

        # profile name
        self.profileNameWidget = Qt.QWidget()
        self.profileNameLayout = Qt.QHBoxLayout()
        self.profileNameWidget.setLayout(self.profileNameLayout)
        self.mainLayout.addWidget(self.profileNameWidget)

        self.profileNameLabel = Qt.QLabel(lang("profileName"))
        self.profileNameLabel.setFont(Fonts.titleFont)
        self.profileNameLayout.addWidget(self.profileNameLabel)

        self.profileNameInput = Qt.QLineEdit()
        self.profileNameInput.setPlaceholderText(lang("profileNameHere"))
        self.profileNameInput.setFixedHeight(40)
        self.profileNameInput.setFont(Fonts.titleFont)
        self.profileNameInput.setMaxLength(64)
        self.profileNameInput.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[a-zA-Z0-9_ .-]+")))  # filter out invalid characters
        self.profileNameLayout.addWidget(self.profileNameInput)

        # minecraft version
        self.mcVersionWidget = Qt.QWidget()
        self.mcVersionLayout = Qt.QHBoxLayout()
        self.mcVersionWidget.setLayout(self.mcVersionLayout)
        self.mainLayout.addWidget(self.mcVersionWidget)

        self.mcVersionLabel = Qt.QLabel(lang("mcVersion"))
        self.mcVersionLabel.setFont(Fonts.titleFont)
        self.mcVersionLayout.addWidget(self.mcVersionLabel)
        
        self.mcVersionSelectWidget = Qt.QWidget()
        self.mcVersionSelectLayout = Qt.QVBoxLayout()
        self.mcVersionSelectWidget.setLayout(self.mcVersionSelectLayout)
        self.mcVersionLayout.addWidget(self.mcVersionSelectWidget)

        self.showReleaseCheck = Qt.QCheckBox(lang("onlyShowReleases"))
        self.showReleaseCheck.setFont(Fonts.bigTextFont)
        self.showReleaseCheck.setChecked(True)
        self.showReleaseCheck.stateChanged.connect(self.showReleaseChange)
        self.mcVersionSelectLayout.addWidget(self.showReleaseCheck)

        self.versionSelect = Qt.QComboBox()
        self.versionSelect.setFont(Fonts.titleFont)
        self.versionSelect.addItems(Methods.listMcVersions(Methods, onlyReleases=True))
        self.mcVersionSelectLayout.addWidget(self.versionSelect)

        # modloader
        self.modloaderWidget = Qt.QWidget()
        self.modloaderLayout = Qt.QHBoxLayout()
        self.modloaderWidget.setLayout(self.modloaderLayout)
        self.mainLayout.addWidget(self.modloaderWidget)

        self.modloaderLabel = Qt.QLabel(lang("modloader"))
        self.modloaderLabel.setFont(Fonts.titleFont)
        self.modloaderLayout.addWidget(self.modloaderLabel)

        self.modloaderSelect = Qt.QComboBox()
        self.modloaderSelect.setFont(Fonts.titleFont)
        self.modloaderSelect.addItems(["Fabric", "Forge", "NeoForge", "Quilt"])
        self.modloaderLayout.addWidget(self.modloaderSelect)

        self.buttonsWidget = Qt.QWidget()
        self.buttonsLayout = Qt.QHBoxLayout()
        self.buttonsWidget.setLayout(self.buttonsLayout)
        self.mainLayout.addWidget(self.buttonsWidget)

        # buttons
        self.cancelButton = Qt.QPushButton(lang("cancel"))
        self.cancelButton.setFont(Fonts.titleFont)
        self.cancelButton.setFixedHeight(50)
        self.cancelButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cancelButton.clicked.connect(self.close)
        self.buttonsLayout.addWidget(self.cancelButton)

        self.createButton = Qt.QPushButton(lang("create"))
        self.createButton.setFont(Fonts.titleFont)
        self.createButton.setFixedHeight(50)
        self.createButton.clicked.connect(self.createProfile)
        self.buttonsLayout.addWidget(self.createButton)
    
    def showReleaseChange(self):
        """change the minecraft version list to only show releases or not"""
        self.versionSelect.clear()
        if self.showReleaseCheck.isChecked():
            self.versionSelect.addItems(Methods.listMcVersions(Methods, onlyReleases=True))
        else:
            self.versionSelect.addItems(Methods.listMcVersions(Methods, onlyReleases=False))
    
    def createProfile(self):
        """create a new profile based on the user input"""
        self.profileName = self.profileNameInput.text().strip()
        if not self.profileName:
            QMessageBox.critical(self, lang("error"), lang("profileNameEmptyError"))
            return
        self.existingProfiles = [Path(item).name for item in glob.glob(str(profilesDir/"*"))]
        if self.profileName in self.existingProfiles:
            QMessageBox.critical(self, lang("error"), lang("profileNameExistsError"))
            return
        
        self.mcVersion = self.versionSelect.currentText()
        self.modloader = self.modloaderSelect.currentText()
        self.profilePath = profilesDir/self.profileName
        self.profilePath.mkdir(parents=True, exist_ok=False)
        self.profilePropertiesPath = self.profilePath/"properties.json"
        
        with open(self.profilePropertiesPath, "w") as f:
            # write the profile properties to the file
            json.dump({"name": self.profileName, "version": self.mcVersion, "modloader": self.modloader}, f, indent=4)
        
        QMessageBox.information(self, lang("success"), lang("profileCreationSuccess"))
        
        self.close()
