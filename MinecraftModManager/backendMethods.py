from pathlib import Path
import platformdirs
import logging

localPath = Path(__file__).resolve().parent
appDataDir = Path(platformdirs.user_data_dir("MinecraftModManager", appauthor="Ilwan"))  # path to the save data folder

log = logging.getLogger(__name__)
