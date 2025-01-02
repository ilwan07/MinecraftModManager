import translate
from PyQt5 import QtGui
from pathlib import Path
import minecraft_launcher_lib
import platformdirs
import darkdetect
import locale
import os

langLocale, _ = locale.getlocale()
if langLocale: userLanguage = langLocale.split("_")[0]
else:
    langLocale = os.environ.get("LANG")
    if langLocale: userLanguage = langLocale.split("_")[0]
    else: userLanguage = "en"
Language = translate.Translator(Path(__file__).resolve().parent/"locales", userLanguage)
lang = Language.translate

localPath = Path(__file__).resolve().parent
appDataDir = Path(platformdirs.user_data_dir("MinecraftModManager", appauthor="Ilwan"))  # path to the save data folder

iconsAssetsDir = localPath/"assets"/"icons"/"dark" if darkdetect.isDark() else localPath/"assets"/"icons"/"light"  # assets path depending on color mode
profilesDir = appDataDir/"profiles"  # path to the profiles folder
cacheDir = appDataDir/"cache"  # path to the cache folder
logDir = appDataDir/"logs"  # path to the logs folder

minecraftAppdataPath = Path(minecraft_launcher_lib.utils.get_minecraft_directory())
minecraftModsPath = minecraftAppdataPath/"mods"

modrinthApi = "https://api.modrinth.com/v2"
curseForgeApi = "http://mmm.ilwan.hackclub.app/curseforge"

availablePlatforms = ["modrinth", "curseforge"]

appVersion = "0.1.0"

class Fonts():
    """a class containing useful fonts"""
    bigTitleFont = QtGui.QFont("Arial", 24)
    titleFont = QtGui.QFont("Arial", 20)
    smallTitleFont = QtGui.QFont("Arial", 18)
    subtitleFont = QtGui.QFont("Arial", 16)
    bigTextFont = QtGui.QFont("Arial", 14)
    textFont = QtGui.QFont("Arial", 11)
