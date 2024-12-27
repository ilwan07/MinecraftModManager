import customWidgets, backendMethods  # local modules
from usefulVariables import *  # local variables
import PyQt5.QtWidgets as Qt
from PyQt5 import QtCore, QtGui
from pathlib import Path
import platformdirs
import darkdetect
import logging
import markdown
import ctypes
import asyncio
import os

log = logging.getLogger(__name__)

if os.name == "nt":  # if on Windows
    appId = "ilwan.minecraftmodmanager"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appId)

Methods = backendMethods.Methods()
StartCode = backendMethods.Start()
StartCode.start()  # setup the software


class Window(Qt.QMainWindow):
    def __init__(self):
        """a class to manage the app and its main window"""
        self.currentProfile = None
        self.currentModData = {}

    def start(self):
        """launches the GUI and the app"""
        super().__init__()
        self.setWindowTitle("Minecraft Mod Manager")
        self.buildUi()
        self.setFocus()
        self.showMaximized()
        self.show()
    
    def buildUi(self):
        """builds the base UI for the main window"""
        # main layout
        self.centralAppWidget = Qt.QWidget()
        self.setCentralWidget(self.centralAppWidget)
        self.mainLayout = Qt.QHBoxLayout(self.centralAppWidget)

        # creating the 4 main parts of the window
        self.profilesListWidget = Qt.QWidget()
        self.modsListWidget = Qt.QWidget()
        self.modSearchWidget = Qt.QWidget()
        self.modInstallWidget = Qt.QWidget()

        self.profilesListLayout = Qt.QVBoxLayout()
        self.profilesListLayout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        self.modsListLayout = Qt.QVBoxLayout()
        self.modsListLayout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        self.modSearchLayout = Qt.QVBoxLayout()
        self.modSearchLayout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        self.modInstallLayout = Qt.QVBoxLayout()
        self.modInstallLayout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)

        self.profilesListWidget.setLayout(self.profilesListLayout)
        self.modsListWidget.setLayout(self.modsListLayout)
        self.modSearchWidget.setLayout(self.modSearchLayout)
        self.modInstallWidget.setLayout(self.modInstallLayout)

        # creating the splitter for these parts
        self.splitter = Qt.QSplitter(QtCore.Qt.Horizontal)
        self.mainLayout.addWidget(self.splitter)
        self.splitter.addWidget(self.profilesListWidget)
        self.splitter.addWidget(self.modsListWidget)
        self.splitter.addWidget(self.modSearchWidget)
        self.splitter.addWidget(self.modInstallWidget)
        self.splitter.setSizes([150, 250, 250, 350])

        # Add a line to make the splitter visible
        for i in range(self.splitter.count()):
            handle = self.splitter.handle(i)
            line = Qt.QFrame(handle)
            line.setFrameShape(Qt.QFrame.VLine)
            line.setFrameShadow(Qt.QFrame.Sunken)
            line.setGeometry(2, 0, 2, 2*handle.height()+1000)  # make sure it's long enough to go throught the whole screen

        # creating the two subsections for the last part
        self.modDescriptionWidget = Qt.QWidget()
        self.modVersionsWidget = Qt.QWidget()

        self.modDescriptionLayout = Qt.QVBoxLayout()
        self.modDescriptionLayout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        self.modVersionsLayout = Qt.QVBoxLayout()
        self.modVersionsLayout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)

        self.modDescriptionWidget.setLayout(self.modDescriptionLayout)
        self.modVersionsWidget.setLayout(self.modVersionsLayout)

        # creating the splitter
        self.modInstallSplitter = Qt.QSplitter(QtCore.Qt.Vertical)
        self.modInstallSplitter.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)
        self.modInstallLayout.addWidget(self.modInstallSplitter)
        self.modInstallSplitter.addWidget(self.modDescriptionWidget)
        self.modInstallSplitter.addWidget(self.modVersionsWidget)
        self.modInstallSplitter.setSizes([300, 700])

        # Add a line to make the splitter visible
        for i in range(self.modInstallSplitter.count()):
            handle = self.modInstallSplitter.handle(i)
            line = Qt.QFrame(handle)
            line.setFrameShape(Qt.QFrame.HLine)
            line.setFrameShadow(Qt.QFrame.Sunken)
            line.setGeometry(0, 1, 2*handle.width()+1000, 2)
        
        log.debug("built main compartments")
        self.buildProfilesList()
        log.debug("built profiles list compartment")
        self.buildModsList()
        log.debug("built mods list compartment")
        self.buildModSearch()
        log.debug("built mods search compartment")
        self.buildModDescription()
        log.debug("built mod description compartment")
        self.buildModVersions()
        log.debug("built mod versions compartment")
        self.setupInterface()
        log.debug("finished building and configuring the interface")
    
    def buildProfilesList(self):
        """builds the UI for profilesListWidget"""
        # settings button
        self.settingsButton = Qt.QPushButton(f" {lang("settings")}")
        self.settingsButton.setFont(Fonts.titleFont)
        self.settingsButton.setIcon(QtGui.QIcon(str(iconsAssetsDir/"settings.png")))
        self.settingsButton.setIconSize(QtCore.QSize(25, 25))
        self.settingsButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.settingsButton.setFixedHeight(60)
        self.profilesListLayout.addWidget(self.settingsButton)

        # separation line
        self.separationLine = customWidgets.SeparationLine()
        self.profilesListLayout.addWidget(self.separationLine)

        # add profile button
        self.addProfileButton = Qt.QPushButton(lang("addProfile"))
        self.addProfileButton.setFont(Fonts.titleFont)
        self.addProfileButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.addProfileButton.setFixedHeight(50)
        self.addProfileButton.clicked.connect(self.addProfile)
        self.profilesListLayout.addWidget(self.addProfileButton)

        # import profile button
        self.importProfileButton = Qt.QPushButton(lang("importProfile"))
        self.importProfileButton.setFont(Fonts.titleFont)
        self.importProfileButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.importProfileButton.setFixedHeight(50)
        self.profilesListLayout.addWidget(self.importProfileButton)

        # separation line
        self.separationLine = customWidgets.SeparationLine()
        self.profilesListLayout.addWidget(self.separationLine)

        # scroll area for the profiles
        self.profilesScroll = Qt.QScrollArea()
        self.profilesScroll.setWidgetResizable(True)
        self.profilesScroll.setFrameShape(Qt.QFrame.NoFrame)
        self.profilesScrollWidget = Qt.QWidget()
        self.profilesScrollLayout = Qt.QVBoxLayout(self.profilesScrollWidget)
        self.profilesScrollLayout.setAlignment(QtCore.Qt.AlignTop)
        self.profilesScroll.setWidget(self.profilesScrollWidget)
        self.profilesListLayout.addWidget(self.profilesScroll)
    
    def buildModsList(self):
        """builds the UI for the part that displays the mods list for the current profile"""
        # short profile description section
        self.profileLabel = Qt.QLabel()
        self.profileLabel.setFont(Fonts.bigTitleFont)
        self.profileLabel.setWordWrap(True)
        self.profileLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.modsListLayout.addWidget(self.profileLabel)

        self.profileVersionLabel = Qt.QLabel()
        self.profileVersionLabel.setFont(Fonts.subtitleFont)
        self.profileVersionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.modsListLayout.addWidget(self.profileVersionLabel)

        # launch game with profile button
        self.launchButton = Qt.QPushButton(f" {lang("launch")}")
        self.launchButton.setFont(Fonts.titleFont)
        self.launchButton.setIcon(QtGui.QIcon(str(iconsAssetsDir/"launch.png")))
        self.launchButton.setIconSize(QtCore.QSize(25, 25))
        self.launchButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.launchButton.setFixedHeight(50)
        self.modsListLayout.addWidget(self.launchButton)

        # buttons layout
        self.profileButtonsWidget = Qt.QWidget()
        self.profileButtonsLayout = Qt.QGridLayout()
        self.profileButtonsWidget.setLayout(self.profileButtonsLayout)
        self.modsListLayout.addWidget(self.profileButtonsWidget)

        # apply profile button
        self.applyProfileButton = Qt.QPushButton(lang("applyProfile"))
        self.applyProfileButton.setFont(Fonts.subtitleFont)
        self.applyProfileButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.applyProfileButton.setFixedHeight(40)
        self.profileButtonsLayout.addWidget(self.applyProfileButton, 0, 0)

        # add custom mod button
        self.addModButton = Qt.QPushButton(lang("addMod"))
        self.addModButton.setFont(Fonts.subtitleFont)
        self.addModButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.addModButton.setFixedHeight(40)
        self.profileButtonsLayout.addWidget(self.addModButton, 0, 1)

        # export profile button
        self.exportButton = Qt.QPushButton(lang("export"))
        self.exportButton.setFont(Fonts.subtitleFont)
        self.exportButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.exportButton.setFixedHeight(40)
        self.profileButtonsLayout.addWidget(self.exportButton, 1, 0)

        # configure profile button
        self.configureButton = Qt.QPushButton(lang("configure"))
        self.configureButton.setFont(Fonts.subtitleFont)
        self.configureButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.configureButton.setFixedHeight(40)
        self.profileButtonsLayout.addWidget(self.configureButton, 1, 1)

        # separation line
        self.separationLine = customWidgets.SeparationLine()
        self.modsListLayout.addWidget(self.separationLine)

        # scroll area for the mods
        self.modsScroll = Qt.QScrollArea()
        self.modsScroll.setWidgetResizable(True)
        self.modsScroll.setFrameShape(Qt.QFrame.NoFrame)
        self.modsScrollWidget = Qt.QWidget()
        self.modsScrollLayout = Qt.QVBoxLayout(self.modsScrollWidget)
        self.modsScrollLayout.setAlignment(QtCore.Qt.AlignTop)
        self.modsScroll.setWidget(self.modsScrollWidget)
        self.modsListLayout.addWidget(self.modsScroll)

        self.modsListWidget.setVisible(False)
    
    def buildModSearch(self):
        """builds the UI for the mod search part"""
        # widget for the online downloading platfor selection
        self.platformWidget = Qt.QWidget()
        self.platformLayout = Qt.QHBoxLayout()
        self.platformLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.platformWidget.setLayout(self.platformLayout)
        self.modSearchLayout.addWidget(self.platformWidget)

        # downloading platform selection
        self.platformLabel = Qt.QLabel(lang("platform"))
        self.platformLabel.setFont(Fonts.titleFont)
        self.platformLayout.addWidget(self.platformLabel)

        self.platformSelect = Qt.QComboBox()
        self.platformSelect.addItems(["Modrinth", "CurseForge"])
        self.platformSelect.setFont(Fonts.subtitleFont)
        self.platformLayout.addWidget(self.platformSelect)

        # search bar
        self.searchWidget = Qt.QWidget()
        self.searchLayout = Qt.QHBoxLayout()
        self.searchWidget.setLayout(self.searchLayout)
        self.modSearchLayout.addWidget(self.searchWidget)

        self.searchBar = Qt.QLineEdit()
        self.searchBar.setFont(Fonts.titleFont)
        self.searchBar.setFixedHeight(40)
        self.searchBar.setPlaceholderText(lang("searchQuery"))
        self.searchBar.returnPressed.connect(self.searchMod)
        self.searchLayout.addWidget(self.searchBar)

        self.searchButton = Qt.QPushButton()
        self.searchButton.setIcon(QtGui.QIcon(str(iconsAssetsDir/"search.png")))
        self.searchButton.setIconSize(QtCore.QSize(25, 25))
        self.searchButton.setFixedSize(QtCore.QSize(40, 40))
        self.searchButton.clicked.connect(self.searchMod)
        self.searchLayout.addWidget(self.searchButton)

        # only show compatible mods or not
        self.onlySearchCompatible = Qt.QCheckBox()
        self.onlySearchCompatible.setText(lang("onlySearchCompatible"))
        self.onlySearchCompatible.setFont(Fonts.bigTextFont)
        self.onlySearchCompatible.setChecked(True)
        self.modSearchLayout.addWidget(self.onlySearchCompatible)

        # results list
        self.resultsScroll = Qt.QScrollArea()
        self.resultsScroll.setWidgetResizable(True)
        self.resultsScroll.setFrameShape(Qt.QFrame.NoFrame)
        self.resultsScrollWidget = Qt.QWidget()
        self.resultsScrollLayout = Qt.QVBoxLayout(self.resultsScrollWidget)
        self.resultsScrollLayout.setAlignment(QtCore.Qt.AlignTop)
        self.resultsScroll.setWidget(self.resultsScrollWidget)
        self.modSearchLayout.addWidget(self.resultsScroll)

        self.modSearchWidget.setVisible(False)
    
    def buildModDescription(self):
        """builds the UI for the mod description part"""
        # display mod name
        self.modNameWidget = Qt.QWidget()
        self.modNameLayout = Qt.QHBoxLayout()
        self.modNameLayout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        self.modNameWidget.setLayout(self.modNameLayout)
        self.modDescriptionLayout.addWidget(self.modNameWidget, 1)

        # mod icon
        self.modDescriptionIcon = Qt.QLabel()
        self.modDescriptionIcon.setFixedSize(50, 50)
        self.modNameLayout.addWidget(self.modDescriptionIcon, 1)

        self.modNameLabel = Qt.QLabel()
        self.modNameLabel.setFont(Fonts.bigTitleFont)
        self.modNameLabel.setWordWrap(True)
        self.modNameLayout.addWidget(self.modNameLabel, 1)

        self.separationLine = customWidgets.SeparationLine()
        self.modDescriptionLayout.addWidget(self.separationLine)

        # mod description text
        self.modDescriptionScroll = Qt.QScrollArea()
        self.modDescriptionScroll.setWidgetResizable(True)
        self.modDescriptionScroll.setFrameShape(Qt.QFrame.NoFrame)
        self.modDescriptionScrollWidget = Qt.QWidget()
        self.modDescriptionScrollLayout = Qt.QVBoxLayout(self.modDescriptionScrollWidget)
        self.modDescriptionScroll.setWidget(self.modDescriptionScrollWidget)
        self.modDescriptionLayout.addWidget(self.modDescriptionScroll)

        self.modDescriptionText = Qt.QTextBrowser()
        self.modDescriptionText.setFont(Fonts.textFont)
        self.modDescriptionText.setStyleSheet("background: transparent;")
        self.modDescriptionScrollLayout.addWidget(self.modDescriptionText)

    def buildModVersions(self):
        """builds the UI for the mod versions part"""
        # filter compatible checkbox
        self.onlyShowCompatible = Qt.QCheckBox()
        self.onlyShowCompatible.setText(lang("onlyShowCompatible"))
        self.onlyShowCompatible.setFont(Fonts.bigTextFont)
        self.onlyShowCompatible.setChecked(True)
        self.modVersionsLayout.addWidget(self.onlyShowCompatible)

        # list of available versions
        self.versionsScroll = Qt.QScrollArea()
        self.versionsScroll.setWidgetResizable(True)
        self.versionsScroll.setFrameShape(Qt.QFrame.NoFrame)
        self.versionsScrollWidget = Qt.QWidget()
        self.versionsScrollLayout = Qt.QVBoxLayout(self.versionsScrollWidget)
        self.versionsScrollLayout.setAlignment(QtCore.Qt.AlignTop)
        self.versionsScroll.setWidget(self.versionsScrollWidget)
        self.modVersionsLayout.addWidget(self.versionsScroll)

        # radio buttons for each version
        self.versionsRadio = customWidgets.ModVersionRadio()
        self.onlyShowCompatible.stateChanged.connect(self.updateVersions)
        self.versionsScrollLayout.addWidget(self.versionsRadio)

        # buttons to install or remove mod
        self.installButtonsWidget = Qt.QWidget()
        self.installButtonsLayout = Qt.QHBoxLayout()
        self.installButtonsWidget.setLayout(self.installButtonsLayout)
        self.modVersionsLayout.addWidget(self.installButtonsWidget)

        self.removeModButton = Qt.QPushButton()
        self.removeModButton.setText(lang("remove"))
        self.removeModButton.setFont(Fonts.titleFont)
        self.removeModButton.setFixedHeight(50)
        self.installButtonsLayout.addWidget(self.removeModButton)

        self.installModButton = Qt.QPushButton()
        self.installModButton.setText(lang("install"))
        self.installModButton.setFont(Fonts.titleFont)
        self.installModButton.setFixedHeight(50)
        self.installButtonsLayout.addWidget(self.installModButton)

        self.modInstallWidget.setVisible(False)
    
    def setupInterface(self):
        """setup the interface after its creation"""
        self.refreshProfiles()
    
    def addProfile(self):
        """add a new modded profile"""
        self.addProfilePopup = backendMethods.addProfilePopup()
        log.info(f"opening profile creation screen")
        self.addProfilePopup.exec_()
        self.refreshProfiles()
    
    def refreshProfiles(self):
        """refresh the profiles list"""
        # remove all profiles from the list
        for i in reversed(range(self.profilesScrollLayout.count())):
            self.profilesScrollLayout.itemAt(i).widget().deleteLater()
        
        # add all profiles to the list
        self.profileWidgets = []  # list of all profile widgets objects
        for profileProperties in Methods.getProfiles().values():
            self.profileWidgets.append(customWidgets.ProfileSelect(profileProperties))
            self.profilesScrollLayout.addWidget(self.profileWidgets[-1])
            self.profileWidgets[-1].wasSelected.connect(self.selectProfile)
            if profileProperties["name"] == self.currentProfile or (not self.currentProfile and len(self.profileWidgets) == 1):
                self.profileWidgets[-1].setSelected(True)
    
    def selectProfile(self, profileName:str):
        """select a profile and deselect the others"""
        for profile in self.profileWidgets:
            if profile.name == profileName:
                if profileName != self.currentProfile:
                    self.clearSearch()
                self.currentProfile = profileName
                self.modsListWidget.setVisible(True)
                self.modSearchWidget.setVisible(True)
                self.currentProfileProperties = Methods.getProfiles()[profileName]
            else:
                profile.setSelected(False)
        
        # put the profile infos in the mods list
        self.profileLabel.setText(self.currentProfileProperties["name"])
        self.profileVersionLabel.setText(self.currentProfileProperties["version"])
    
    def searchMod(self):
        """search for a mod on the selected platform"""
        modloader = self.currentProfileProperties["modloader"]
        version = self.currentProfileProperties["version"]
        platform = self.platformSelect.currentText().lower()
        results = Methods.searchMod(self.searchBar.text(), platform, modloader, self.onlySearchCompatible.isChecked(), version)
        if platform == "modrinth":
            mods = Methods.modrinthSearchToMods(results)
        elif platform == "curseforge":
            mods = Methods.curseforgeSearchToMods(results)
        
        # remove all mods from the list
        for i in reversed(range(self.resultsScrollLayout.count())):
            self.resultsScrollLayout.itemAt(i).widget().deleteLater()
        
        # add all mods to the list
        self.modWidgets = []  # list of all mod widgets objects
        for mod in mods:
            self.modWidgets.append(customWidgets.SearchModSelect(mod))
            self.resultsScrollLayout.addWidget(self.modWidgets[-1])
            self.modWidgets[-1].wasSelected.connect(self.selectMod)
    
    def selectMod(self, modData:dict):
        """select a mod and deselect the others"""
        self.currentModData = modData
        modId = modData["id"]
        platform = modData["platform"].lower()
        for mod in self.modWidgets:
            if mod.modId == modId:
                self.currentMod = modId
                self.modInstallWidget.setVisible(True)
            else:
                mod.setSelected(False)
        
        modRequestData = Methods.getModInfos(modId, modData["platform"])
        
        # put the mod infos in the mod description
        self.modNameLabel.setText(modData["name"])
        iconCacheDir = cacheDir/"modIcons"/platform
        Methods.downloadIcon(modRequestData, platform, modId)
        if os.path.exists(iconCacheDir/f"{modId}.png"):
            self.modDescriptionIcon.setPixmap(QtGui.QPixmap(str(iconCacheDir/f"{modId}.png")).scaled(50, 50))
        else:
            self.modDescriptionIcon.setPixmap(QtGui.QPixmap(str(iconsAssetsDir/"noMedia.png")).scaled(50, 50))
        if platform == "modrinth":
            self.modDescriptionText.setHtml(Methods.cleanHtml(markdown.markdown(modRequestData["body"])))
        elif platform == "curseforge":
            self.modDescriptionText.setHtml(f"<h2>{modRequestData["data"]["summary"]}<\\h2>")
        
        # get and display the mod versions
        self.updateVersions()
    
    def updateVersions(self):
        """update the list of versions for the selected mod"""
        self.versionsInfos = asyncio.run(Methods.getVersionsInfos(self.currentMod, self.currentModData["platform"].lower(), self.currentProfileProperties["modloader"].lower(), self.onlyShowCompatible.isChecked(), self.currentProfileProperties["version"]))
        self.versionsRadio.setVersions(self.versionsInfos)
    
    def clearSearch(self):
        """clear the search section"""
        self.searchBar.clear()
        for i in reversed(range(self.resultsScrollLayout.count())):
            self.resultsScrollLayout.itemAt(i).widget().deleteLater()
        self.modInstallWidget.setVisible(False)


def setDarkMode(App:Qt.QApplication):
    """sets the app to a dark mode palette"""
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.black)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    App.setPalette(palette)
