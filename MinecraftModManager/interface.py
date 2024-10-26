import translate
import PyQt5.QtWidgets as Qt
from PyQt5 import QtCore, QtGui
from pathlib import Path
import logging
import locale
import os


log = logging.getLogger(__name__)
localPath = Path(__file__).resolve().parent

langLocale, _ = locale.getlocale()
if langLocale: userLanguage = langLocale.split("_")[0]
else:
    langLocale = os.environ.get("LANG")
    if langLocale: userLanguage = langLocale.split("_")[0]
    else: userLanguage = "en"
Language = translate.Translator(Path(__file__).resolve().parent/"locales", userLanguage)
lang = Language.translate

class Window(Qt.QMainWindow):
    def __init__(self):
        """a class to manage the app and its main window"""
        pass

    def start(self):
        """launches the GUI and the app"""
        super().__init__()
        self.setWindowTitle("Minecraft Mod Manager")
        self.setWindowIcon(QtGui.QIcon(str(localPath/"assets"/"icon.png")))
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
        self.modDescriptionWidget = Qt.QWidget()
        self.modVersionWidget = Qt.QWidget()

        self.profilesListLayout = Qt.QVBoxLayout()
        self.profilesListLayout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        self.modsListLayout = Qt.QVBoxLayout()
        self.modsListLayout.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignTop)
        self.modDescriptionLayout = Qt.QVBoxLayout()
        self.modDescriptionLayout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.modVersionLayout = Qt.QVBoxLayout()
        self.modVersionLayout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.profilesListWidget.setLayout(self.profilesListLayout)
        self.modsListWidget.setLayout(self.modsListLayout)
        self.modDescriptionWidget.setLayout(self.modDescriptionLayout)
        self.modVersionWidget.setLayout(self.modVersionLayout)

        # creating the splitter for these parts
        self.splitter = Qt.QSplitter(QtCore.Qt.Horizontal)
        self.mainLayout.addWidget(self.splitter)
        self.splitter.addWidget(self.profilesListWidget)
        self.splitter.addWidget(self.modsListWidget)
        self.splitter.addWidget(self.modDescriptionWidget)
        self.splitter.addWidget(self.modVersionWidget)
        self.splitter.setSizes([150, 250, 250, 350])
        log.debug("built main compartments")
        
        self.buildProfilesList()
    
    def buildProfilesList(self):
        """builds the UI for profilesListWidget"""
        # settings button
        self.settingsButton = Qt.QPushButton(lang("settings"))
        self.settingsButton.setFont(QtGui.QFont("Arial", 24))
        self.settingsButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.settingsButton.setFixedHeight(60)
        self.profilesListLayout.addWidget(self.settingsButton)

        # separation line
        self.separationLine = Qt.QFrame()
        self.separationLine.setFrameShape(Qt.QFrame.HLine)
        self.separationLine.setFrameShadow(Qt.QFrame.Sunken)
        self.separationLine.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.separationLine.setFixedHeight(20)
        self.profilesListLayout.addWidget(self.separationLine)

        # add profile button
        self.addProfileButton = Qt.QPushButton(lang("addProfile"))
        self.addProfileButton.setFont(QtGui.QFont("Arial", 20))
        self.addProfileButton.setFlat(True)
        self.addProfileButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.addProfileButton.setFixedHeight(50)
        self.profilesListLayout.addWidget(self.addProfileButton)

        # import profile button
        self.importProfileButton = Qt.QPushButton(lang("importProfile"))
        self.importProfileButton.setFont(QtGui.QFont("Arial", 20))
        self.importProfileButton.setFlat(True)
        self.importProfileButton.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.importProfileButton.setFixedHeight(50)
        self.profilesListLayout.addWidget(self.importProfileButton)

        # separation line
        self.separationLine = Qt.QFrame()
        self.separationLine.setFrameShape(Qt.QFrame.HLine)
        self.separationLine.setFrameShadow(Qt.QFrame.Sunken)
        self.separationLine.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.separationLine.setFixedHeight(20)
        self.profilesListLayout.addWidget(self.separationLine)

        # scroll area for the profiles
        self.profilesScroll = Qt.QScrollArea()
        self.profilesScroll.setWidgetResizable(True)
        self.profilesScroll.setFrameShape(Qt.QFrame.NoFrame)
        self.profilesScrollWidget = Qt.QWidget()
        self.profilesScrollLayout = Qt.QVBoxLayout(self.profilesScrollWidget)
        self.profilesScroll.setWidget(self.profilesScrollWidget)
        self.profilesListLayout.addWidget(self.profilesScroll)


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
