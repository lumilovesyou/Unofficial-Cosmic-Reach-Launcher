import os
import sys
import json
import configparser
import platform
import subprocess
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import *
            
def checkOs():
    if platform.system() == 'Darwin':
        return True
    elif platform.system() == 'Windows':
        return False
    else:
        return ("Unknown")
    
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

def checkDirValidity(file_to_check):
    if not os.path.exists("./" + file_to_check + "/"):
        os.mkdir("./" + file_to_check)
        print("Created " + file_to_check)
    else:
        print(file_to_check + " already exists!")

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

def openDialog(name, type, self):
    file_path, _ = QFileDialog.getOpenFileName(self, name, "", type)
    return file_path, _

def createFolder(location, overwrite=False):
    if not os.path.exists(location) or overwrite:
            os.makedirs(location)

def checkForVersion(version):
    file = f"meta/versions/{version}/about.json"
    print(file)
    print(os.path.exists(file))
    try:
        with open(file, "r") as f:
            file_loaded = json.load(f)
        if file_loaded.get("version") == version:
            return True
        else:
            return f"Couldn't locate correct version in {file}"
    except:
        return f"Couldn't locate file {file}"

def loadEnvironmentVars(file_path):
    with open(file_path, "r") as file:
            env_vars = json.load(file)
    env = os.environ.copy()
    env.update(env_vars["keys"])
    return env

def runVersion (version, keys, type, instance_ID):
    json_file = f"meta/versions/{version}/about.json"
    jar_file = f"meta/versions/{version}/Cosmic-Reach-{version}.jar"
    
    env = loadEnvironmentVars(json_file)
    
    process = subprocess.Popen(
        ["java", "-jar", str(jar_file)],
        env=env
    )
    
    print(f"Subprocess started with PID {process.pid}")
    return(process.pid)