# -*- coding: utf-8 -*-
##############################################################################
#
# Module: configdata.py
#
# Description:
#     Configuration data management module for Cricket UI application.
#
#     Handles reading, writing, loading, and updating application
#     configuration files including:
#         • User roles and system modes
#         • Network configuration (SCC / THC)
#         • DUT configuration
#         • Batch and screen settings
#         • Portal credentials
#
#     Stores configuration in JSON format under the
#     user-specific OS data directory.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
#
##############################################################################
# Built-in imports
import os
import sys
from sys import platform
from pathlib import Path
import json
from os import getenv

# Own modules
import defaultconfig

def get_user_data_dir():
    """
    Get the user-specific data directory based on the operating system.

    Returns:
        Path: The user-specific data directory as a `Path` object.
    """
    
    if sys.platform == "win32":
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
        dir_,_ = winreg.QueryValueEx(key, "Local AppData")
        dpath = Path(dir_).resolve(strict=False)
    elif sys.platform == "darwin":
        dpath = Path('~/Library/Application Support/').expanduser()
    else:
        dpath = Path(getenv('XDG_DATA_HOME', "~/.local/lib")).expanduser()
    return dpath

def get_file_path():
    """
    Get the file path for a configuration file in the user-specific data directory.

    Returns:
        str: The full path to the configuration file.
    """
    lpath = get_user_data_dir()
    dpath = os.path.join(lpath, "MCCI", "Cricket")

    os.makedirs(dpath, exist_ok=True)
    fpath = os.path.join(dpath, "mcciconfig.json")
    return fpath

def save_config(fpath, cdata):
    """
    Save configuration data to a specified file.

    Args:
        fpath (str): The path to the file where the configuration data will be saved.
        cdata (dict): The configuration data to be saved.

    Returns:
        None
    """
    with open(fpath, "w") as out_file:
        json.dump(cdata, out_file)

def read_config(fpath):
    """
    Read configuration data from a specified file.

    Args:
        fpath (str): The path to the file from which configuration data will be read.

    Returns:
        dict: The configuration data read from the file. If the file doesn't exist or
              cannot be read, an empty dictionary is returned.
    """
    cdata = None
    try:
        with open(fpath, 'r') as open_file:
            cdata = json.load(open_file)
    except:
        cdata = {}
    return cdata


def load_default_config():
    """
    Load the default configuration data, save it to a file, and return the loaded data.

    Returns:
        dict: The default configuration data loaded and saved to a file.
    """
    cdata = defaultconfig.config_data
    fpath = get_file_path()
    save_config(fpath, cdata)
    return cdata


def read_all_config():
    """
    Read configuration data from a file. If the file doesn't exist or cannot be read,
    load the default configuration data, save it to the file, and return the loaded data.

    Returns:
        dict: The configuration data read from the file or the default configuration data
              loaded and saved to the file.
    """
    cdata = None
    fpath = get_file_path()
    try:
        with open(fpath, 'r') as open_file:
            cdata = json.load(open_file)
    except:
        cdata = load_default_config()
    return cdata

def set_sut_base_data(gdata):
    """
    Set base data for the System Under Test (SUT) in the configuration.

    Args:
        gdata (dict): The base data to be set for the SUT. The dictionary should have
                      a single key representing the SUT, and its corresponding value.

    Returns:
        None

    Raises:
        ValueError: If the provided key in `gdata` does not match any existing SUT key
                    in the configuration.
    """
    cdata = read_all_config()
    
    key = list(gdata.keys())[0]
    keys = list(cdata["dut"].keys())
    if(keys.__contains__(key)):
        cdata["dut"][key] = gdata[key]
        fpath = get_file_path()
        save_config(fpath, cdata)
    else:
        print("\nData config error!")

def set_sut_config_data(gdata):
    """
    Set configuration data for the System Under Test (SUT) in the configuration.

    Args:
        gdata (dict): The configuration data to be set for the SUT. The dictionary
                      should have a key representing the SUT, and its value should
                      be another dictionary with the configuration data.

    Returns:
        None

    Raises:
        ValueError: If the provided key in `gdata` does not match any existing SUT key
                    in the configuration.
    """
    cdata = read_all_config()
    key = list(gdata.keys())[0]
    keys = list(cdata["dut"].keys())
    nkey = list(gdata[key].keys())[0]
    if(keys.__contains__(key)):
        cdata["dut"][key][nkey] = gdata[key][nkey]
        fpath = get_file_path()
        save_config(fpath, cdata)
    else:
        print("\nData config error!")

def set_sut_watch_data(gdata):
    """
    Set watch data for the System Under Test (SUT) in the configuration.

    Args:
        gdata (dict): The watch data to be set for the SUT. The dictionary should
                      have a key representing the SUT, and its value should be a
                      dictionary with watch data.

    Returns:
        None

    Raises:
        ValueError: If the provided key in `gdata` does not match any existing SUT key
                    in the configuration.
    """
    cdata = read_all_config()
    
    key = list(gdata.keys())[0]
    keys = list(cdata["dut"].keys())
    
    if(keys.__contains__(key)):
        nkey = list(gdata[key].keys())[0]
        cdata["dut"][key][nkey] = gdata[key][nkey]
        nkey = list(gdata[key].keys())[1]
        cdata["dut"][key][nkey] = gdata[key][nkey]
        fpath = get_file_path()
        save_config(fpath, cdata)

# To store Config menu, DUT selection menu

def set_base_config_data(gdata):
    """
    Set base configuration data in the configuration.

    Args:
        gdata (dict): The base configuration data to be set. The dictionary should
                      include keys 'myrole' and 'dut' with their corresponding values.

    Returns:
        None
    """
    cdata = read_all_config()
    cdata["myrole"] = gdata["myrole"]
    cdata["dut"]["nodes"] = gdata["dut"]["nodes"]
    cdata["rpanel"] = gdata["rpanel"]
    fpath = get_file_path()
    save_config(fpath, cdata)

def set_network_config(gdata):
    """
    Set network role configuration.

    Updates the system role configuration such as
    User Computer (UC), Switch Control Computer (SCC),
    and Test Host Computer (THC).

    Args:
        gdata: Dictionary containing role configuration.
               Example:
                   {
                       "uc": True,
                       "scc": True,
                       "thc": False
                   }

    Returns:
        None

    Raises:
        KeyError: If required role keys are missing.
    """
    cdata = read_all_config()
    key = list(gdata.keys())[0]
    if "myrole" in cdata:
        cdata["myrole"]["uc"]= gdata["uc"]
        cdata["myrole"]["cc"]= gdata["scc"]
        cdata["myrole"]["thc"]= gdata["thc"]
    else:
        cdata["myrole"] = {}
        cdata["myrole"]["uc"]= gdata["uc"]
        cdata["myrole"]["cc"]= gdata["scc"]
        cdata["myrole"]["thc"]= gdata["thc"]
    fpath = get_file_path()
    save_config(fpath, cdata)
    
def set_nw_scc_config(gdata):
    """
    Set Switch Control Computer (SCC) network configuration.

    Updates SCC TCP network parameters including
    IP address, port, and operating system.

    Args:
        gdata: Dictionary containing SCC network configuration.
               Example:
                   {
                       "ip": "192.168.1.10",
                       "port": "2021",
                       "os": "win32"
                   }

    Returns:
        None

    Raises:
        KeyError: If required configuration keys are missing.
    """
    cdata = read_all_config()
    nwcdata = cdata["uc"]["mynodes"]
    key = list(gdata.keys())[0]
    if "mycc" in nwcdata:
        cdata["uc"]["mynodes"]["mycc"]["tcp"]= {"ip": gdata["ip"], "port": gdata["port"]}
        cdata["uc"]["mynodes"]["mycc"]["os"]= gdata["os"]
    else:
        cdata["uc"]["mynodes"]["mycc"] = {"name": "control computer", "interface": "tcp", "serial": {}, "tcp": {}} 
        cdata["uc"]["mynodes"]["mycc"]["tcp"]= {"ip": gdata["ip"], "port": gdata["port"]}
        cdata["uc"]["mynodes"]["mycc"]["os"]= gdata["os"]
    fpath = get_file_path()
    save_config(fpath, cdata)

def set_nw_thc_config(gdata):
    """
    Set Test Host Computer (THC) network configuration.

    Updates THC TCP network parameters including
    IP address, port, and operating system.

    Args:
        gdata: Dictionary containing THC network configuration.
               Example:
                   {
                       "ip": "192.168.1.20",
                       "port": "2022",
                       "os": "linux"
                   }

    Returns:
        None

    Raises:
        KeyError: If required configuration keys are missing.
    """
    cdata = read_all_config()
    nwcdata = cdata["uc"]["mynodes"]
    key = list(gdata.keys())[0]
    if "mythc" in nwcdata:
        cdata["uc"]["mynodes"]["mythc"]["tcp"]= {"ip": gdata["ip"], "port": gdata["port"]}
        cdata["uc"]["mynodes"]["mythc"]["os"]= gdata["os"]
    else:
        cdata["uc"]["mynodes"]["mythc"] = {"name": "control computer", "interface": "tcp", "serial": {}, "tcp": {}} 
        cdata["uc"]["mynodes"]["mythc"]["tcp"]= {"ip": gdata["ip"], "port": gdata["port"]}
        cdata["uc"]["mynodes"]["mythc"]["os"]= gdata["os"]
    fpath = get_file_path()
    save_config(fpath, cdata)

def set_scc_config(gdata):
    """
    Set SCC interface configuration.

    Updates SCC communication interface settings
    such as TCP network parameters.

    Args:
        gdata: Dictionary containing SCC interface configuration.
               Example:
                   {
                       "type": "tcp",
                       "ip": "192.168.1.10",
                       "port": "2021"
                   }

    Returns:
        None

    Raises:
        KeyError: If required configuration keys are missing.
    """
    cdata = read_all_config()
    scdata = cdata["cc"]
    
    key = list(gdata.keys())[0]
    cdata["cc"][gdata["type"]] = {"ip": gdata["ip"], "port": gdata["port"]}
    fpath = get_file_path()
    save_config(fpath, cdata)

def set_thc_config(gdata):
    """
    Set THC interface configuration.

    Updates THC communication interface settings
    such as TCP network parameters.

    Args:
        gdata: Dictionary containing THC interface configuration.
               Example:
                   {
                       "type": "tcp",
                       "ip": "192.168.1.20",
                       "port": "2022"
                   }

    Returns:
        None

    Raises:
        KeyError: If required configuration keys are missing.
    """
    cdata = read_all_config()
    scdata = cdata["thc"]
    
    key = list(gdata.keys())[0]
    cdata["thc"][gdata["type"]] = {"ip": gdata["ip"], "port": gdata["port"]}
    fpath = get_file_path()
    save_config(fpath, cdata)

def set_switch_config(gdata):
    """
    Set switch configuration data in the configuration.

    Args:
        gdata (dict): The switch configuration data to be set. The dictionary should
                      have a key representing the switch, and its value should be the
                      configuration data for that switch.

    Returns:
        None
    """
    cdata = read_all_config()
    # cdata["swconfig"] = gdata
    key = list(gdata.keys())[0]
    if "switchconfig" in cdata:
        cdata["switchconfig"][key]= gdata[key]
    else:
        cdata["switchconfig"] = {}
        cdata["switchconfig"][key]= gdata[key]
    fpath = get_file_path()
    save_config(fpath, cdata)

def updt_batch_location(bloc):
    """
    Update the batch location in the configuration.

    Args:
        bloc (str): The new batch location to be set.

    Returns:
        None
    """
    cdata = read_all_config()
    cdata["batch"]["location"] = bloc
    fpath = get_file_path()
    save_config(fpath, cdata)

def updt_screen_size(gdata):
    """
    Update the screen size configuration in the global configuration.

    Args:
        gdata (dict): The new screen size configuration.

    Returns:
        None
    """
    cdata = read_all_config()
    cdata["screen"] = gdata["screen"]
    fpath = get_file_path()
    save_config(fpath, cdata)

def updt_warning_dialog(gdata):
    """
    Update the warning dialog configuration in the global configuration.

    Args:
        gdata (dict): The new warning dialog configuration.

    Returns:
        None
    """
    cdata = read_all_config()
    cdata["wdialog"] = gdata["wdialog"]
    fpath = get_file_path()
    save_config(fpath, cdata)

def updt_portal_credentials(gdata):
    """
    Update the portal credentials configuration in the global configuration.

    Args:
        gdata (dict): The new portal credentials configuration.

    Returns:
        None
    """
    cdata = read_all_config()
    cdata["msudp"] = gdata["msudp"]
    fpath = get_file_path()
    save_config(fpath, cdata)

def read_msudp_config():
    """
    Read the portal credentials configuration from the global configuration.

    Returns:
        dict: The portal credentials configuration.
    """
    cdata = None
    fpath = get_file_path()
    try:
        with open(fpath, 'r') as open_file:
            cdata = json.load(open_file)
    except:
        cdata = load_default_config()
    return cdata["msudp"]
