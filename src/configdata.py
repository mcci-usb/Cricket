##############################################################################
# 
# Module: configdata.py
#
# Description:
#     Scan the USB bus and get the list of devices attached
#
# Copyright notice:
#     This file copyright (c) 2020 by
#
#         MCCI Corporation
#         3520 Krums Corners Road
#         Ithaca, NY  14850
#
#     Released under the MCCI Corporation.
#
# Author:
#     Seenivasan V, MCCI Corporation Mar 2020
#
# Revision history:
#    V4.0.0 Wed May 25 2023 17:00:00   Seenivasan V
#       Module created
################################################################################

import os
import sys
from sys import platform
from pathlib import Path
import json
from os import getenv
import defaultconfig

def get_user_data_dir():
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
    lpath = get_user_data_dir()
    dpath = os.path.join(lpath, "MCCI", "Cricket")

    os.makedirs(dpath, exist_ok=True)
    fpath = os.path.join(dpath, "config.json")
    return fpath


def save_config(fpath, cdata):
    with open(fpath, "w") as out_file:
        json.dump(cdata, out_file)

def read_config(fpath):
    cdata = None
    try:
        with open(fpath, 'r') as open_file:
            cdata = json.load(open_file)
    except:
        cdata = {}
    return cdata


def load_default_config():
    cdata = defaultconfig.config_data
    fpath = get_file_path()
    save_config(fpath, cdata)
    return cdata


def read_all_config():
    cdata = None
    fpath = get_file_path()
    try:
        with open(fpath, 'r') as open_file:
            cdata = json.load(open_file)
    except:
        cdata = load_default_config()
    return cdata

def set_sut_base_data(gdata):
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
    cdata = read_all_config()
    cdata["myrole"] = gdata["myrole"]
    cdata["dut"]["nodes"] = gdata["dut"]["nodes"]
    fpath = get_file_path()
    save_config(fpath, cdata)

def set_switch_config(gdata):
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
    cdata = read_all_config()
    cdata["batch"]["location"] = bloc
    fpath = get_file_path()
    save_config(fpath, cdata)

def updt_screen_size(gdata):
    cdata = read_all_config()
    cdata["screen"] = gdata["screen"]
    fpath = get_file_path()
    save_config(fpath, cdata)

def updt_warning_dialog(gdata):
    cdata = read_all_config()
    cdata["wdialog"] = gdata["wdialog"]
    fpath = get_file_path()
    save_config(fpath, cdata)
