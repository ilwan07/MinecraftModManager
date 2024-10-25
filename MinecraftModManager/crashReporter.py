import PyQt5.QtWidgets as Qt
from PyQt5 import QtCore
import webbrowser
import pyperclip


class Reporter(Qt.QMainWindow):
    def __init__(self, exception:Exception, logPath:str, reportLink:str):
        """a crash reporter window"""
        super().__init__()
        self.reportLink = reportLink
        self.setWindowTitle("Crash reporter")
        
        self.centralWidget = Qt.QWidget()
        self.layout:Qt.QLayout = Qt.QVBoxLayout()
        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)
        
        self.explainLabel = Qt.QLabel(f"The app encountered an unexpected error and crashed.\nThe following exception happened: {str(exception)}.\nSee log for more information:")
        self.explainLabel.setWordWrap(True)
        self.layout.addWidget(self.explainLabel)
        
        self.textZone = Qt.QTextEdit()
        self.textZone.setReadOnly(True)
        with open(logPath, "r", encoding="utf-8") as logFile:
            self.logContent = logFile.read()
        self.textZone.setText(self.logContent)
        self.layout.addWidget(self.textZone)
        
        self.sendLabel1 = Qt.QLabel("Please open a new issue on")
        self.sendLabel1.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.sendLabel1)
        
        self.linkLabel = Qt.QPushButton(self.reportLink)
        self.linkLabel.setFlat(True)
        self.linkLabel.setStyleSheet("text-decoration: underline; color: blue;")
        self.linkLabel.clicked.connect(lambda: webbrowser.open(self.reportLink))
        self.layout.addWidget(self.linkLabel)
        
        self.sendLabel2 = Qt.QLabel("explaining how the crash happened and providing the log to help the developpers fix the app.")
        self.sendLabel2.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.sendLabel2)
        
        self.buttonsWidget = Qt.QWidget()
        self.buttonsLayout = Qt.QHBoxLayout()
        self.buttonsWidget.setLayout(self.buttonsLayout)
        
        self.copyButton = Qt.QPushButton("Copy log")
        self.copyButton.clicked.connect(lambda: self.copyLog(self.logContent))
        self.buttonsLayout.addWidget(self.copyButton)
        
        self.exportButton = Qt.QPushButton("Export log file")
        self.exportButton.clicked.connect(lambda: self.exportLog(self.logContent))
        self.buttonsLayout.addWidget(self.exportButton)
        
        self.quitButton = Qt.QPushButton("Quit")
        self.quitButton.clicked.connect(self.close)
        self.buttonsLayout.addWidget(self.quitButton)
        
        self.layout.addWidget(self.buttonsWidget)

        self.show()
    
    def copyLog(self, logStr:str):
        """copy the log and confirms"""
        pyperclip.copy(logStr)
        Qt.QMessageBox.information(self, "Log copied", f"The log has been copied to the clipboard.")

    def exportLog(self, logStr:str):
        """export the log file"""
        filePath, _ = Qt.QFileDialog.getSaveFileName(self, "Save crash log", "crashlog.log", "Log Files (*.log);;Text Files (*.txt)")
        if filePath:
            try:
                with open(filePath, "w") as logFile:
                    logFile.write(logStr)
                Qt.QMessageBox.information(self, "Log exported", f"The log has been exported to {filePath}.")
            except Exception as e:
                Qt.QMessageBox.critical(self, "Export error", f"Failed to export log: {str(e)}.")
