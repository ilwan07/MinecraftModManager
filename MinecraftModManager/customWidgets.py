import backendMethods
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
    wasSelected = QtCore.pyqtSignal()
    def __init__(self, name:str, modloader:str, version:str):
        """a button to select the profile to launch or modify"""
        super().__init__()
        self.mainLayout = Qt.QVBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.mainLayout)

        self.name = name
        self.modloader = modloader
        self.version = version
        self.isSelected = False

        self.nameLabel = Qt.QLabel(self.name)
        self.nameLabel.setFont(QtGui.QFont("Arial", 20))
        self.mainLayout.addWidget(self.nameLabel)

        self.versionLabel = Qt.QLabel(f"{self.modloader} {self.version}")
        self.versionLabel.setFont(QtGui.QFont("Arial", 14))
        self.mainLayout.addWidget(self.versionLabel)

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
            for widget in (self.nameLabel, self.versionLabel):  # avoid applying shadow to inner widgets
                widget.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
        else:
            self.setStyleSheet("")

    def setSelected(self, selected:bool):
        """outline the frame if selected"""
        if selected:
            self.setFrameShape(Qt.QFrame.Box)
            self.isSelected = True
            self.wasSelected.emit()
        else:
            self.setFrameShape(Qt.QFrame.NoFrame)
            self.isSelected = False

class ModSelect(Qt.QFrame):
    wasSelected = QtCore.pyqtSignal()
    def __init__(self, name:str, fileName:str, modId:str=None, version:str=None, iconPath:Path=None):
        """a button to select the mod to view or modify"""
        super().__init__()
        self.mainLayout = Qt.QHBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.mainLayout)

        self.name = name
        self.fileName = fileName
        self.version = version
        self.iconPath = iconPath
        self.modId = modId
        self.isSelected = False

        #TODO: mod icon

        self.textWidget = Qt.QWidget()
        self.textLayout = Qt.QVBoxLayout()
        self.textWidget.setLayout(self.textLayout)
        self.mainLayout.addWidget(self.textWidget)

        self.nameLabel = Qt.QLabel(self.name)
        self.nameLabel.setFont(QtGui.QFont("Arial", 18))
        self.textLayout.addWidget(self.nameLabel)

        self.versionLabel = Qt.QLabel()
        if self.version:
            self.versionLabel.setText(self.version)
            self.versionLabel.setFont(QtGui.QFont("Arial", 12))
            self.textLayout.addWidget(self.versionLabel)

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
            for widget in (self.textWidget, self.nameLabel, self.versionLabel):  # avoid applying shadow to inner widgets
                widget.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
        else:
            self.setStyleSheet("")

    def setSelected(self, selected:bool):
        """outline the frame if selected"""
        if selected:
            self.setFrameShape(Qt.QFrame.Box)
            self.isSelected = True
            self.wasSelected.emit()
        else:
            self.setFrameShape(Qt.QFrame.NoFrame)
            self.isSelected = False

class SearchModSelect(Qt.QFrame):
    wasSelected = QtCore.pyqtSignal()
    def __init__(self, name:str, modId:str, iconPath:Path=None):
        """a button to select the mod to view and install"""
        super().__init__()
        self.mainLayout = Qt.QHBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.mainLayout)

        self.name = name
        self.iconPath = iconPath
        self.modId = modId
        self.isSelected = False

        #TODO: mod icon

        self.textWidget = Qt.QWidget()
        self.textLayout = Qt.QVBoxLayout()
        self.textWidget.setLayout(self.textLayout)
        self.mainLayout.addWidget(self.textWidget)

        self.nameLabel = Qt.QLabel(self.name)
        self.nameLabel.setFont(QtGui.QFont("Arial", 18))
        self.textLayout.addWidget(self.nameLabel)

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
            for widget in (self.textWidget, self.nameLabel):  # avoid applying shadow to inner widgets
                widget.setStyleSheet("background-color: rgba(0, 0, 0, 0)")
        else:
            self.setStyleSheet("")

    def setSelected(self, selected:bool):
        """outline the frame if selected"""
        if selected:
            self.setFrameShape(Qt.QFrame.Box)
            self.isSelected = True
            self.wasSelected.emit()
        else:
            self.setFrameShape(Qt.QFrame.NoFrame)
            self.isSelected = False
