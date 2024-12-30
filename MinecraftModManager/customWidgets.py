from usefulVariables import *  # local variables
import PyQt5.QtWidgets as Qt
from PyQt5 import QtGui, QtCore
from pathlib import Path


class SeparationLine(Qt.QFrame):
    def __init__(self):
        """a horizontal separation line"""
        super().__init__()
        self.setFrameShape(Qt.QFrame.HLine)
        self.setFrameShadow(Qt.QFrame.Sunken)
        self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Fixed)
        self.setFixedHeight(10)

class ProfileSelect(Qt.QFrame):
    wasSelected = QtCore.pyqtSignal(str)
    def __init__(self, properties:dict):
        """a button to select the profile to launch or modify"""
        super().__init__()
        self.mainLayout = Qt.QHBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(self.mainLayout)

        self.name = properties["name"]
        self.modloader = properties["modloader"]
        self.version = properties["version"]
        self.isSelected = False

        # modloader icon
        modloaderIcon = QtGui.QIcon(str(iconsAssetsDir/f"{self.modloader.lower()}.png"))
        self.modloaderIconLabel = Qt.QLabel()
        self.modloaderIconLabel.setPixmap(modloaderIcon.pixmap(64, 64))
        self.mainLayout.addWidget(self.modloaderIconLabel)

        # widget containing the informations about the profile
        self.informationsWidget = Qt.QWidget()
        self.informationsLayout = Qt.QVBoxLayout()
        self.informationsWidget.setLayout(self.informationsLayout)
        self.mainLayout.addWidget(self.informationsWidget, 1)  # the 1 makes the widget expandable

        self.nameLabel = Qt.QLabel(self.name)
        self.nameLabel.setFont(Fonts.smallTitleFont)
        self.informationsLayout.addWidget(self.nameLabel)

        self.versionLabel = Qt.QLabel(f"{self.modloader} {self.version}")
        self.versionLabel.setFont(Fonts.textFont)
        self.informationsLayout.addWidget(self.versionLabel)

        # mouse tracking
        self.setMouseTracking(True)
        self.enterEvent = self.onEnter
        self.leaveEvent = self.onLeave

        self.mousePressEvent = self.onMousePress

    def onMousePress(self, event):
        if not self.isSelected:
            self.setSelected(True)
        event.accept()

    def onEnter(self, event):
        self.setHovered(True)
        event.accept()

    def onLeave(self, event):
        self.setHovered(False)
        event.accept()
    
    def setHovered(self, hovered:bool):
        """gray out the frame on hover"""
        if hovered:
            self.setStyleSheet("background-color: rgba(0, 0, 0, 64);")
            for widget in (self.nameLabel, self.versionLabel, self.modloaderIconLabel, self.informationsWidget):  # avoid applying shadow to inner widgets
                widget.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
        else:
            self.setStyleSheet("")

    def setSelected(self, selected:bool):
        """outline the frame if selected"""
        if selected:
            self.setFrameShape(Qt.QFrame.Box)
            self.isSelected = True
            self.wasSelected.emit(self.name)
        else:
            self.setFrameShape(Qt.QFrame.NoFrame)
            self.isSelected = False

class ModSelect(Qt.QFrame):
    wasSelected = QtCore.pyqtSignal(dict)
    def __init__(self, modData:dict):
        """a button to select the mod to view or modify"""
        super().__init__()
        self.mainLayout = Qt.QHBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.mainLayout)

        self.modData = modData
        self.name = modData["modName"]
        self.modId = modData["modId"]
        self.fileName = modData["fileName"]
        self.version = modData["versionName"]
        self.iconPath = cacheDir/"modIcons"/modData["platform"].lower()/f"{self.modId}.png"
        self.versionId = modData["versionId"]
        self.isSelected = False

        # mod icon
        self.iconLabel = Qt.QLabel()
        self.updateIcon()
        self.mainLayout.addWidget(self.iconLabel)

        self.textWidget = Qt.QWidget()
        self.textLayout = Qt.QVBoxLayout()
        self.textWidget.setLayout(self.textLayout)
        self.mainLayout.addWidget(self.textWidget, 1)

        self.nameLabel = Qt.QLabel(self.name)
        self.nameLabel.setFont(Fonts.smallTitleFont)
        self.nameLabel.setWordWrap(True)
        self.textLayout.addWidget(self.nameLabel)

        self.versionLabel = Qt.QLabel()
        if self.version:
            self.versionLabel.setText(self.version)
            self.versionLabel.setFont(Fonts.textFont)
            self.versionLabel.setWordWrap(True)
            self.textLayout.addWidget(self.versionLabel)

        # mouse tracking
        self.setMouseTracking(True)
        self.enterEvent = self.onEnter
        self.leaveEvent = self.onLeave

        self.mousePressEvent = self.onMousePress
    
    def updateIcon(self):
        """update the icon from the iconPath if it exists"""
        if os.path.exists(self.iconPath):
            self.iconLabel.setPixmap(QtGui.QPixmap(str(self.iconPath)).scaled(64, 64))
        else:
            self.iconLabel.setPixmap(QtGui.QPixmap(str(iconsAssetsDir/"noMedia.png")).scaled(64, 64))

    def onMousePress(self, event):
        if not self.isSelected:
            self.setSelected(True)
        event.accept()

    def onEnter(self, event):
        self.setHovered(True)
        event.accept()

    def onLeave(self, event):
        self.setHovered(False)
        event.accept()
    
    def setHovered(self, hovered:bool):
        """gray out the frame on hover"""
        if hovered:
            self.setStyleSheet("background-color: rgba(0, 0, 0, 64);")
            for widget in (self.textWidget, self.nameLabel, self.versionLabel, self.iconLabel):  # avoid applying shadow to inner widgets
                widget.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
        else:
            self.setStyleSheet("")

    def setSelected(self, selected:bool):
        """outline the frame if selected"""
        if selected:
            self.setFrameShape(Qt.QFrame.Box)
            self.isSelected = True
            self.wasSelected.emit(self.modData)
        else:
            self.setFrameShape(Qt.QFrame.NoFrame)
            self.isSelected = False

class SearchModSelect(Qt.QFrame):
    wasSelected = QtCore.pyqtSignal(dict)
    def __init__(self, modData:dict):
        """a button to select the mod to view and install"""
        super().__init__()
        self.mainLayout = Qt.QHBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(self.mainLayout)

        self.modData = modData
        self.name = modData["name"]
        self.author = modData["author"]
        self.iconPath = modData["icon"]
        self.modId = modData["id"]
        self.platform = modData["platform"]
        self.isSelected = False

        # mod icon
        self.iconLabel = Qt.QLabel()
        self.updateIcon()
        self.mainLayout.addWidget(self.iconLabel)

        # widget containing the informations about the mod
        self.textWidget = Qt.QWidget()
        self.textLayout = Qt.QVBoxLayout()
        self.textWidget.setLayout(self.textLayout)
        self.mainLayout.addWidget(self.textWidget, 1)  # the 1 makes the widget expandable

        self.nameLabel = Qt.QLabel(self.name)
        self.nameLabel.setFont(Fonts.smallTitleFont)
        self.nameLabel.setWordWrap(True)
        self.textLayout.addWidget(self.nameLabel)

        self.authorLabel = Qt.QLabel(f"by {self.author}")
        self.authorLabel.setFont(Fonts.textFont)
        self.authorLabel.setWordWrap(True)
        self.textLayout.addWidget(self.authorLabel)

        # mouse tracking
        self.setMouseTracking(True)
        self.enterEvent = self.onEnter
        self.leaveEvent = self.onLeave

        self.mousePressEvent = self.onMousePress
    
    def updateIcon(self):
        """update the icon from the iconPath if it exists"""
        if os.path.exists(self.iconPath):
            self.iconLabel.setPixmap(QtGui.QPixmap(str(self.iconPath)).scaled(64, 64))
        else:
            self.iconLabel.setPixmap(QtGui.QPixmap(str(iconsAssetsDir/"noMedia.png")).scaled(64, 64))

    def onMousePress(self, event):
        if not self.isSelected:
            self.setSelected(True)
        event.accept()

    def onEnter(self, event):
        self.setHovered(True)
        event.accept()

    def onLeave(self, event):
        self.setHovered(False)
        event.accept()
    
    def setHovered(self, hovered:bool):
        """gray out the frame on hover"""
        if hovered:
            self.setStyleSheet("background-color: rgba(0, 0, 0, 64);")
            for widget in (self.textWidget, self.nameLabel, self.iconLabel):  # avoid applying shadow to inner widgets
                widget.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
        else:
            self.setStyleSheet("")

    def setSelected(self, selected:bool):
        """outline the frame if selected"""
        if selected:
            self.setFrameShape(Qt.QFrame.Box)
            self.isSelected = True
            self.wasSelected.emit(self.modData)
        else:
            self.setFrameShape(Qt.QFrame.NoFrame)
            self.isSelected = False

class ModVersionRadio(Qt.QWidget):
    def __init__(self):
        """a serie of radio buttons to select the mod version, given a list of versions with their properties"""
        super().__init__()
        self.versions = {}
        self.radioButtons = []
        self.mainLayout = Qt.QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.radioGroup = Qt.QButtonGroup(self)
    
    def setVersions(self, versions:dict, gameVersion:str):
        """update the radio buttons with the new versions"""
        self.versions = versions
        # clear previous radio buttons
        for radioButton in self.radioButtons:
            self.radioGroup.removeButton(radioButton)
        self.radioButtons = []
        for i in reversed(range(self.mainLayout.count())):
            self.mainLayout.itemAt(i).widget().deleteLater()
        
        # create new radio buttons
        foundRecommended = False
        isFirst = True
        for version, properties in self.versions.items():
            text = f"{properties['releaseType']} - {version}"
            if isFirst:
                text = f"(latest) {text}"
            if not foundRecommended and properties['releaseType'] == "release" and gameVersion in properties['mcVersions']:
                text = f"(recommended) {text}"
                foundRecommended = True
            radioButton = Qt.QRadioButton(text)
            radioButton.setFont(Fonts.subtitleFont)
            self.radioGroup.addButton(radioButton)
            self.radioButtons.append(radioButton)
            self.mainLayout.addWidget(radioButton)
            isFirst = False
        
    def getSelectionData(self) -> dict:
        """return the version data of the selected radio button"""
        for radioButton in self.radioButtons:
            if radioButton.isChecked():
                version = radioButton.text()
                cleanVersion = version
                for prefix in ["(latest) ", "(recommended) ", "release - ", "beta - ", "alpha - "]:
                    cleanVersion = cleanVersion.replace(prefix, "", 1)  # remove the prefix
                return self.versions[cleanVersion]
        return None  # if no version selected
    
    def getCheckedVersion(self):
        """return the version data of the checked radio button"""
        for radioButton in self.radioGroup.buttons():
            if radioButton.isChecked():
                version = radioButton.text()
                return version, self.versions[version]
        return None
