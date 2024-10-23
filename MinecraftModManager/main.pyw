import interface, crashReporter  # local modules
import PyQt5.QtWidgets as Qt
from pathlib import Path
import logging as log
import platformdirs
import darkdetect
import traceback
import sys


appDataDir = Path(platformdirs.user_data_dir("MinecraftModManager", appauthor=False))  # path to the save data folder
logDir = appDataDir/"logs"
# create folders if missing
appDataDir.mkdir(parents=True, exist_ok=True)
logDir.mkdir(parents=True, exist_ok=True)

log.basicConfig(level=log.DEBUG, filename=appDataDir/"logs"/"latest.log", filemode="w", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

log.info("running and launching the app directly")
App = Qt.QApplication(sys.argv)
App.setStyle("fusion")
if darkdetect.isDark():  # if using dark mode
    interface.setDarkMode(App)
log.info("applied theme")
MainWindow = interface.Window()  # initializing window
try:
    log.info("starting the app")
    MainWindow.start()  # start the GUI
    App.exec_()
except Exception as e:  # crash handling
    log.critical(f"app crashed with the following exception: {e}\nsee traceback for more details:\n\n{traceback.format_exc()}")
    MainWindow.close()
    ReportApp = Qt.QApplication(sys.argv)
    ReportWindow = crashReporter.Reporter(e, logDir/"latest.log", "IGaming73/MinecraftModManager")
    ReportApp.exec_()
