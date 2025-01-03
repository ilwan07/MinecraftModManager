import crashReporter  # local modules
from usefulVariables import *  # local variables
import PyQt5.QtWidgets as Qt
from PyQt5 import QtGui, QtCore
from pathlib import Path
import logging as log
import darkdetect
import traceback
import atexit
import shutil
import glob
import sys


# create folders if missing
appDataDir.mkdir(parents=True, exist_ok=True)
logDir.mkdir(parents=True, exist_ok=True)
if cacheDir.exists():
    shutil.rmtree(cacheDir)
cacheDir.mkdir(parents=True, exist_ok=True)


log.basicConfig(level=log.DEBUG, filename=appDataDir/"logs"/"latest.log", filemode="w", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

class ErrorHandlerApp(Qt.QApplication):
    def notify(self, receiver, event):
        try:
            return super().notify(receiver, event)
        except Exception as e:
            handleException(e)
            return False  # re-raise the exception here


def handleException(exception):
    """handle uncaught exceptions"""
    try:
        MainWindow.close()
    except Exception as ex:
        log.error(f"unable to close main window after crash because of this exception: {ex}")
    log.critical(f"app crashed with the following exception: {exception}\nsee traceback for more details:\n\n{traceback.format_exc()}")
    ReportApp = Qt.QApplication(sys.argv)
    ReportWindow = crashReporter.Reporter(exception, logDir/"latest.log", "https://github.com/IGaming73/SimpleCrashReporter/issues")
    ReportApp.exec_()

def handle_exit():
    """handle uncaught exceptions at exit"""
    if sys.exc_info() != (None, None, None):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        handleException(exc_value)

# set the exception hook and the exit hook to catch uncaught exceptions
sys.excepthook = handleException
atexit.register(handle_exit)

try:
    import interface
    log.info("running and launching the app directly")
    if sys.platform == "darwin":  # if on MacOS
        try:
            from Foundation import NSBundle
            bundle = NSBundle.mainBundle()
            if bundle:
                app_info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
                if app_info:
                    app_info["CFBundleName"] = "Minecraft Mod Manager"
        except ImportError:
            pass
    App = ErrorHandlerApp(sys.argv)
    appIcon = QtGui.QIcon()
    for iconPath in glob.glob(f"{str(localPath/'assets'/'icons'/'logo'/'res')}/*.png"):
        res = int(Path(iconPath).name.split(".")[0])
        appIcon.addFile(iconPath, QtCore.QSize(res, res))
    App.setWindowIcon(appIcon)
    App.setApplicationName("Minecraft Mod Manager")
    App.setStyle("fusion")
    if darkdetect.isDark():  # if using dark mode
        interface.setDarkMode(App)
    log.info("applied theme")
    MainWindow = interface.Window()  # initializing window
    log.info("starting the app")
    MainWindow.start()  # start the GUI
    App.exec_()
except Exception as e:  # crash handling
    handleException(e)
