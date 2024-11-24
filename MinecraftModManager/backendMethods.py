from pathlib import Path
import platformdirs
import requests
import logging

localPath = Path(__file__).resolve().parent
appDataDir = Path(platformdirs.user_data_dir("MinecraftModManager", appauthor="Ilwan"))  # path to the save data folder

log = logging.getLogger(__name__)


def curseforgeRequest(endpoint, params=None):
    """make a generic request to the curseforge api via the proxy containing the api key"""
    SERVER_URL = "http://hackclub.app:36015/curseforge"
    url = f"{SERVER_URL}/{endpoint}"

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # check if response is valid
        return response.json()
    except requests.exceptions.RequestException as e:
        log.error(f"error while requesting to curseforge proxy : {e}\nusing endpoint '{endpoint}' with params {params}'")
        return None

