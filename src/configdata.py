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
#    V2.6.0 Wed Apr 20 2022 17:00:00   Seenivasan V
#       Module created
################################################################################

import os
import sys
from sys import platform
from pathlib import Path
import json

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
        fpath = os.path.join(dpath, "Cricketconfig.json")
        return fpath

def save_config(fpath, cdata):
    with open(fpath, "w") as out_file:
        json.dump(cdata, out_file)

# def push_default_value(self):
#     cdata = {"comPort": "COM0", }

def read_config(fpath):
    cdata = None
    try:
        with open(fpath, 'r') as open_file:
            cdata = json.load(open_file)
    except:
        cdata = {}
    return cdata


def get_new_file_path():
    lpath = get_user_data_dir()
    dpath = os.path.join(lpath, "MCCI", "Cricket")

    os.makedirs(dpath, exist_ok=True)
    fpath = os.path.join(dpath, "config.json")
    return fpath


def read_all_config():
    cdata = None
    fpath = get_new_file_path()
    print("File Path: ", fpath)
    try:
        with open(fpath, 'r') as open_file:
            cdata = json.load(open_file)
            print("Open the file")
    except:
        print("can not open file")
        cdata = defaultconfig.config_data
        save_config(fpath, cdata)
    return cdata

def set_sut_base_data(gdata):
    cdata = read_all_config()
    # print("Existing: ", cdata)
    # print("New : ",gdata)
    
    key = list(gdata.keys())[0]
    keys = list(cdata["sut"].keys())
    print("Keys: ", keys)
    print("Key: ", key)
    if(keys.__contains__(key)):
        cdata["sut"][key] = gdata[key]
        fpath = get_new_file_path()
        save_config(fpath, cdata)
    else:
        print("\nData matching error!!!")


def set_sut_config_data(gdata):
    cdata = read_all_config()
    key = list(gdata.keys())[0]
    keys = list(cdata["sut"].keys())
    nkey = list(gdata[key].keys())[0]
    print("Keys: ", keys)
    print("Key: ", key)
    print("Nkey: ", nkey)
    if(keys.__contains__(key)):
        print("Proceed to save data")
        cdata["sut"][key][nkey] = gdata[key][nkey]
        fpath = get_new_file_path()
        save_config(fpath, cdata)
    else:
        print("\nData matching error!!!")


def set_sut_watch_data(gdata):
    cdata = read_all_config()
    
    key = list(gdata.keys())[0]
    keys = list(cdata["sut"].keys())
    print("Keys: ", keys)
    print("Key: ", key)

    print(gdata[key])

    if(keys.__contains__(key)):
        print("Proceed to save data")
        nkey = list(gdata[key].keys())[0]
        cdata["sut"][key][nkey] = gdata[key][nkey]
        fpath = get_new_file_path()
        save_config(fpath, cdata)

# To store Config menu, SUT selection menu
# Myrole and SUT nodes
# {"myrole": {"uc": true, "cc": false, "thc": false}, "sut": {"nodes": {"sut1": true, "sut2": false}}}
def set_base_config_data(gdata):
    cdata = read_all_config()
    print("Store base config data: ", gdata)
    cdata["myrole"] = gdata["myrole"]
    cdata["sut"]["nodes"] = gdata["sut"]["nodes"]
    fpath = get_new_file_path()
    save_config(fpath, cdata)