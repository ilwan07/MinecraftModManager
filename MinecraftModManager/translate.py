from pathlib import Path
import logging
import yaml
import os


log = logging.getLogger(__name__)

class Translator():
    def __init__(self, folderPath:Path, language:str="en"):
        """a class to translate strings from a set of translation files to the given language"""
        if not os.path.exists(folderPath):
            raise FileNotFoundError(f"Folder not found: {folderPath}")
        self.language = language
        self.folderPath = folderPath

        if self.language:
            try:
                with open(self.folderPath/f"{self.language}.yaml", "r", encoding="utf-8") as f:
                    self.translations = yaml.safe_load(f)
                log.debug(f"loaded the {self.language} language successfully")
            except FileNotFoundError:  # use english if the requested language isn't available
                self.language = "en"
                with open(self.folderPath/"en.yaml", "r", encoding="utf-8") as f:
                    self.translations = yaml.safe_load(f)
                log.warning(f"unable to load the {self.language} language, defaulting to english")

    def translate(self, id:str, language:str=None) -> str:
        """translate the string from the id in the given language, or in the default language"""
        if not language:
            language = self.language
            translations = self.translations
        else:
            try:
                with open(self.folderPath/f"{language}.yaml", "r", encoding="utf-8") as f:
                    translations = yaml.safe_load(f)
            except FileNotFoundError:  # use english if the requested language isn't available
                language = "en"
                with open(self.folderPath/"en.yaml", "r", encoding="utf-8") as f:
                    translations = yaml.safe_load(f)
                log.warning(f"unable to load the {language} language, defaulting to english")
        if not translations:
            translations = {}
        translation = translations.get(id)
        if translation:
            return translation
        else:
            with open(self.folderPath/"en.yaml", "r", encoding="utf-8") as f:
                    translations = yaml.safe_load(f)
            if not translations:
                translations = {}
            translation = translations.get(id)
            if translation:
                log.warning(f"can't find translation for [{id}] in the language {language}")
                return translation
            else:
                log.warning(f"can't find translation for [{id}] neither in the language {language} or in english, returning back the id")
                return f"[{id}]"
