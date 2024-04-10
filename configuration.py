from pathlib import Path
from configparser import ConfigParser

MAIN_CONFIG_FILE = "settings.ini"

DB_SECTION = "Database"
DB_NAME_KEY = "name"
DB_HOST_KEY = "host"
DB_USER_KEY = "user"
DB_PWD_F_KEY = "password_file"
DB_PWD_SAMPLE = "sample_pwd"


class MainAppConfiguration:
    """ The class to operate with the application settings stored in INI-file in the same directory """

    def __init__(self):
        """ Reads defined configuration file by the standard ConfigParser """
        if Path(MAIN_CONFIG_FILE).is_file():
            self.__config = ConfigParser()
            self.__config.read(MAIN_CONFIG_FILE)
        else:
            raise FileNotFoundError(f"{MAIN_CONFIG_FILE} configuration file not found.")

    def __get_setting(self, section, key) -> str:
        """ Returns any defined setting value by the section/key from the configuration file """
        config_setting = self.__config[section][key].strip()
        if config_setting == "":
            raise ValueError(f"'{section} > {key}' setting undefined in {MAIN_CONFIG_FILE} file.")
        return config_setting

    def get_db_name(self) -> str:
        """ Returns configured database name """
        return self.__get_setting(DB_SECTION, DB_NAME_KEY)

    def get_db_host(self) -> str:
        """ Returns configured DB Server hostname/ip-address """
        return self.__get_setting(DB_SECTION, DB_HOST_KEY)

    def get_db_user(self) -> str:
        """ Returns configured DB Server login """
        return self.__get_setting(DB_SECTION, DB_USER_KEY)

    def get_db_password(self) -> str:
        """
        Returns configured DB Server password from the separate text file defined in the application settings.
        Creates default separate text file with sample password, if not found, which should be updated by the user.
        """
        pwd_value = ""
        pwd_filename = self.__get_setting(DB_SECTION, DB_PWD_F_KEY)

        if Path(pwd_filename).is_file():
            # Any decryption method can be applied here to store encrypted password in the file
            with open(pwd_filename, encoding='ascii') as pwd_file:
                pwd_value = pwd_file.readline().strip()
        else:
            with open(pwd_filename, 'a', encoding='ascii') as pwd_file:
                pwd_file.write(DB_PWD_SAMPLE)

        if pwd_value in ("", DB_PWD_SAMPLE):
            raise ValueError(f"{self.get_db_name()} DB password undefined in {pwd_filename} file.")

        return pwd_value
