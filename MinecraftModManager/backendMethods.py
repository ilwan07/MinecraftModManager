from pathlib import Path
import platformdirs
import requests
import logging

localPath = Path(__file__).resolve().parent
appDataDir = Path(platformdirs.user_data_dir("MinecraftModManager", appauthor="Ilwan"))  # path to the save data folder

log = logging.getLogger(__name__)

def queryCurseforgeProxy(endpoint, params):
    """send a query to the curseforge api via the proxy"""
    proxyUrl = "http://hackclub.app:36015/curseforge"
    try:
        response = requests.get(proxyUrl, params={"endpoint": endpoint, **params})
        response.raise_for_status()
        return response.json()  # returns the response as json if no error
    except requests.exceptions.RequestException as e:
        log.error(f"error with proxy request: {e}")


endpoint = "mods/search"
params = {"gameId": 432, "searchFilter": "sodium", "pageSize": 1}
result = queryCurseforgeProxy(endpoint, params)
print(result)
