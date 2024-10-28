import translate
import PyQt5.QtWidgets as Qt
from PyQt5 import QtCore, QtGui
from pathlib import Path
import logging
import locale
import ctypes
import os

log = logging.getLogger(__name__)

langLocale, _ = locale.getlocale()
if langLocale: userLanguage = langLocale.split("_")[0]
else:
    langLocale = os.environ.get("LANG")
    if langLocale: userLanguage = langLocale.split("_")[0]
    else: userLanguage = "en"
Language = translate.Translator(Path(__file__).resolve().parent/"locales", userLanguage)
lang = Language.translate

if os.name == "nt":  # if on Windows
    appId = u'ilwan.minecraftmodmanager'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appId)

class QSeparationLine(Qt.QFrame):
    def __init__(self):
        """A horizontal separation line"""
        super().__init__()
        self.setFrameShape(Qt.QFrame.HLine)
        self.setFrameShadow(Qt.QFrame.Sunken)
        self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.setFixedHeight(10)

class Window(Qt.QMainWindow):
    def __init__(self):
        """a class to manage the app and its main window"""
        pass

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
        # some ressources
        self.bigTitleFont = QtGui.QFont("Arial", 24)
        self.titleFont = QtGui.QFont("Arial", 20)
        self.subtitleFont = QtGui.QFont("Arial", 16)
        self.textFont = QtGui.QFont("Arial", 11)

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
        self.modSearchLayout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.modInstallLayout = Qt.QVBoxLayout()
        self.modInstallLayout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

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
            line.setGeometry(2, 0, 2, 2*handle.height()+100)  # make sure it's long enough to go throught the whole screen
        
        log.debug("built main compartments")
        self.buildProfilesList()
    
    def buildProfilesList(self):
        """builds the UI for profilesListWidget"""
        # settings button
        self.settingsButton = Qt.QPushButton(lang("settings"))
        self.settingsButton.setFont(self.titleFont)
        self.settingsButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.settingsButton.setFixedHeight(60)
        self.profilesListLayout.addWidget(self.settingsButton)

        # separation line
        self.separationLine = QSeparationLine()
        self.profilesListLayout.addWidget(self.separationLine)

        # add profile button
        self.addProfileButton = Qt.QPushButton(lang("addProfile"))
        self.addProfileButton.setFont(self.titleFont)
        self.addProfileButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.addProfileButton.setFixedHeight(50)
        self.profilesListLayout.addWidget(self.addProfileButton)

        # import profile button
        self.importProfileButton = Qt.QPushButton(lang("importProfile"))
        self.importProfileButton.setFont(self.titleFont)
        self.importProfileButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.importProfileButton.setFixedHeight(50)
        self.profilesListLayout.addWidget(self.importProfileButton)

        # separation line
        self.separationLine = QSeparationLine()
        self.profilesListLayout.addWidget(self.separationLine)

        # scroll area for the profiles
        self.profilesScroll = Qt.QScrollArea()
        self.profilesScroll.setWidgetResizable(True)
        self.profilesScroll.setFrameShape(Qt.QFrame.NoFrame)
        self.profilesScrollWidget = Qt.QWidget()
        self.profilesScrollLayout = Qt.QVBoxLayout(self.profilesScrollWidget)
        self.profilesScroll.setWidget(self.profilesScrollWidget)
        self.profilesListLayout.addWidget(self.profilesScroll)

        self.buildModsList()
    
    def buildModsList(self):
        """builds the UI for the part that displays the mods list for the current profile"""
        # short profile description section
        self.profileLabel = Qt.QLabel("Profile 1")  #TODO: placeholder text
        self.profileLabel.setFont(self.bigTitleFont)
        self.profileLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.modsListLayout.addWidget(self.profileLabel)

        self.profileVersionLabel = Qt.QLabel("Fabric 1.21")  #TODO: placeholder text
        self.profileVersionLabel.setFont(self.subtitleFont)
        self.profileVersionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.modsListLayout.addWidget(self.profileVersionLabel)

        # buttons layout
        self.profileButtonsWidget = Qt.QWidget()
        self.profileButtonsLayout = Qt.QGridLayout()
        self.profileButtonsWidget.setLayout(self.profileButtonsLayout)
        self.modsListLayout.addWidget(self.profileButtonsWidget)

        # launch game with profile button
        self.launchButton = Qt.QPushButton(lang("launch"))
        self.launchButton.setFont(self.subtitleFont)
        self.launchButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.launchButton.setFixedHeight(40)
        self.profileButtonsLayout.addWidget(self.launchButton, 0, 0)

        # apply profile button
        self.applyProfileButton = Qt.QPushButton(lang("applyProfile"))
        self.applyProfileButton.setFont(self.subtitleFont)
        self.applyProfileButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.applyProfileButton.setFixedHeight(40)
        self.profileButtonsLayout.addWidget(self.applyProfileButton, 0, 1)

        # export profile button
        self.exportButton = Qt.QPushButton(lang("export"))
        self.exportButton.setFont(self.subtitleFont)
        self.exportButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.exportButton.setFixedHeight(40)
        self.profileButtonsLayout.addWidget(self.exportButton, 1, 0)

        # configure profile button
        self.configureButton = Qt.QPushButton(lang("configure"))
        self.configureButton.setFont(self.subtitleFont)
        self.configureButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.configureButton.setFixedHeight(40)
        self.profileButtonsLayout.addWidget(self.configureButton, 1, 1)

        # separation line
        self.separationLine = QSeparationLine()
        self.modsListLayout.addWidget(self.separationLine)

        # scroll area for the mods
        self.modsScroll = Qt.QScrollArea()
        self.modsScroll.setWidgetResizable(True)
        self.modsScroll.setFrameShape(Qt.QFrame.NoFrame)
        self.modsScrollWidget = Qt.QWidget()
        self.modsScrollLayout = Qt.QVBoxLayout(self.modsScrollWidget)
        self.modsScroll.setWidget(self.modsScrollWidget)
        self.modsListLayout.addWidget(self.modsScroll)

        self.buildModSearch()
    
    def buildModSearch(self):
        """builds the UI for the mod search part"""
        pass


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
