import configparser
import darkdetect
import qdarktheme
import os

def checkForConfig():
    config = configparser.ConfigParser()
    if not os.path.exists("./config.ini"):
        config["App Settings"] = {
            "dark_mode": "Auto",
            "dev_mode": "True"
        }
        with open("./config.ini", "w") as configfile:
            config.write(configfile)
    else:
        config.read("./config.ini")
    return config

def checkInConfig(section, key):
    config = configparser.ConfigParser()
    config.read("./config.ini")
    try:
        return config.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return None
    
def updateInConfig(section, key, value):
    config = configparser.ConfigParser()
    config_file = "./config.ini"
    config.read("./config.ini")
    config.set(section, key, value)
    with open(config_file, 'w') as configfile:
        config.write(configfile)
        
#Higher-level functions
def updateTheme():
    checkForConfig()
    currentAppTheme = checkInConfig("App Settings", "app_theme")
    if currentAppTheme == "Auto":
        if darkdetect.isDark():
            qdarktheme.setup_theme()
        else:
            qdarktheme.setup_theme("light")
    elif currentAppTheme == "Dark":
        qdarktheme.setup_theme(currentAppTheme.lower())
    else:
        qdarktheme.setup_theme("light")
