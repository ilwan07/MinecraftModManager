from pathlib import Path
import platformdirs
import requests
import logging

localPath = Path(__file__).resolve().parent
appDataDir = Path(platformdirs.user_data_dir("MinecraftModManager", appauthor="Ilwan"))  # path to the save data folder

log = logging.getLogger(__name__)


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
