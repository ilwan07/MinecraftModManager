from pathlib import Path
import PyQt5.QtWidgets as Qt
from PyQt5.QtWidgets import QMessageBox
from PyQt5 import QtCore, QtGui
import platformdirs
import requests
import logging

localPath = Path(__file__).resolve().parent  # path of the software folder
appDataDir = Path(platformdirs.user_data_dir("MinecraftModManager", appauthor="Ilwan"))  # path to the save data folder

log = logging.getLogger(__name__)

class Start():
    """a class that setups the software before launching the interface"""
    def start(self):
        """code to directly execute at the start of the program"""
        self.profilesDir = appDataDir/"profiles"
        self.profilesDir.mkdir(parents=True, exist_ok=True)


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
    
    def addProfile(self):
        """create a new modded profile"""
        pass

class addProfilePopup():
    """popup to create a new profile"""
    pass
