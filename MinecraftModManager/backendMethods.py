import translate
import locale
from pathlib import Path
import PyQt5.QtWidgets as Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore, QtGui
import minecraft_launcher_lib
import platformdirs
import requests
import logging
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

# define some font sizes
bigTitleFont = QtGui.QFont("Arial", 24)
titleFont = QtGui.QFont("Arial", 20)
subtitleFont = QtGui.QFont("Arial", 16)
bigTextFont = QtGui.QFont("Arial", 14)
textFont = QtGui.QFont("Arial", 11)

# define some useful variables
profilesDir = appDataDir/"profiles"

class Start():
    """a class that setups the software before launching the interface"""
    def start(self):
        """code to directly execute at the start of the program"""
        profilesDir.mkdir(parents=True, exist_ok=True)


class Methods():
    """a class containing usefull methods"""
    def curseforgeRequest(endpoint, **params) -> dict:
        """make a generic request to the curseforge api via the proxy containing the api key"""
        SERVER_URL = "http://mmm.ilwan.hackclub.app/curseforge"
        url = f"{SERVER_URL}/{endpoint}"

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # check if response is valid
            if response.status_code != 200:
                log.warning(f"got status code {response.status_code} while requesting curseforge proxy\nusing endpoint '{endpoint}' with params {params}")
            return response.json()
        except requests.exceptions.RequestException as e:
            log.error(f"error while requesting to curseforge proxy : {e}\nusing endpoint '{endpoint}' with params {params}")
            return None

    def modrinthRequest(endpoint, **params):
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
    
    def listMcVersions(self, onlyReleases=True):
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
        self.profileNameLabel.setFont(titleFont)
        self.profileNameLayout.addWidget(self.profileNameLabel)

        self.profileNameInput = Qt.QLineEdit()
        self.profileNameInput.setPlaceholderText(lang("profileNameHere"))
        self.profileNameInput.setFixedHeight(40)
        self.profileNameInput.setFont(titleFont)
        self.profileNameInput.setMaxLength(64)
        self.profileNameInput.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[a-zA-Z0-9_ .-]+")))  # filter out invalid characters
        self.profileNameLayout.addWidget(self.profileNameInput)

        # minecraft version
        self.mcVersionWidget = Qt.QWidget()
        self.mcVersionLayout = Qt.QHBoxLayout()
        self.mcVersionWidget.setLayout(self.mcVersionLayout)
        self.mainLayout.addWidget(self.mcVersionWidget)

        self.mcVersionLabel = Qt.QLabel(lang("mcVersion"))
        self.mcVersionLabel.setFont(titleFont)
        self.mcVersionLayout.addWidget(self.mcVersionLabel)
        
        self.mcVersionSelectWidget = Qt.QWidget()
        self.mcVersionSelectLayout = Qt.QVBoxLayout()
        self.mcVersionSelectWidget.setLayout(self.mcVersionSelectLayout)
        self.mcVersionLayout.addWidget(self.mcVersionSelectWidget)

        self.showReleaseCheck = Qt.QCheckBox(lang("onlyShowReleases"))
        self.showReleaseCheck.setFont(bigTextFont)
        self.showReleaseCheck.setChecked(True)
        self.showReleaseCheck.stateChanged.connect(self.showReleaseChange)
        self.mcVersionSelectLayout.addWidget(self.showReleaseCheck)

        self.versionSelect = Qt.QComboBox()
        self.versionSelect.setFont(titleFont)
        self.versionSelect.addItems(Methods.listMcVersions(Methods, onlyReleases=True))
        self.mcVersionSelectLayout.addWidget(self.versionSelect)

        # modloader
        self.modloaderWidget = Qt.QWidget()
        self.modloaderLayout = Qt.QHBoxLayout()
        self.modloaderWidget.setLayout(self.modloaderLayout)
        self.mainLayout.addWidget(self.modloaderWidget)

        self.modloaderLabel = Qt.QLabel(lang("modloader"))
        self.modloaderLabel.setFont(titleFont)
        self.modloaderLayout.addWidget(self.modloaderLabel)

        self.modloaderSelect = Qt.QComboBox()
        self.modloaderSelect.setFont(titleFont)
        self.modloaderSelect.addItems(["Fabric", "Forge", "NeoForge", "Quilt"])
        self.modloaderLayout.addWidget(self.modloaderSelect)

        self.buttonsWidget = Qt.QWidget()
        self.buttonsLayout = Qt.QHBoxLayout()
        self.buttonsWidget.setLayout(self.buttonsLayout)
        self.mainLayout.addWidget(self.buttonsWidget)

        # buttons
        self.cancelButton = Qt.QPushButton(lang("cancel"))
        self.cancelButton.setFont(titleFont)
        self.cancelButton.setFixedHeight(50)
        self.cancelButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cancelButton.clicked.connect(self.close)
        self.buttonsLayout.addWidget(self.cancelButton)

        self.createButton = Qt.QPushButton(lang("create"))
        self.createButton.setFont(titleFont)
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
        self.profileName = self.profileNameInput.text()
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
