##############################################################################
# 
# Module: defaultconfig.py
#
# Description:
#     Scan the USB bus and get the list of devices attached
#
# Author:
#     Seenivasan V, MCCI Corporation Mar 2020
#
# Revision history:
#    V4.3.1 Mon Apr 15 2024 17:00:00   Seenivasan V 
#       Module created
################################################################################

config_data = {
       "name": "Cricket", 
       "version": "1.0.0", 
       "myrole": {"uc": True, "cc": True, "thc": True }, 
       "uc": {"interfaces": ["serial", "tcp"], 
              "mynodes": {"mycc": {"name": "control computer",
                                   "os":"win32",
                                    "interface": "tcp", 
                                    "serial": {}, 
                                    "tcp": {"ip": "0.0.0.0", "port": "2021"}}, 
                          "mythc": {"name": "test host computer",
                                    "os":"win32",
                                    "ineterface": "tcp", 
                                    "serial": {}, "tcp": {"ip": "0.0.0.0", "port": "2022"}}}, 
              "default": {"mycc": {"tcp": {"ip": "0.0.0.0", "port": "2021"}}, 
                          "mythc": {"tcp": {"ip": "0.0.0.0", "port": "2022"}}}}, 
       "cc": {"interface": "tcp", "serial": {}, "tcp": {"ip": "0.0.0.0", "port": "2021"}}, 
       "thc": {"interface": "tcp", "serial": {}, "tcp": {"ip": "0.0.0.0", "port": "2022"}}, 
       "features": ["auto", "loop"], "plugins": ["dut", "batch"], 
       "dut": {"nodes": {"dut1": False, "dut2": False}, "interfaces": ["serial", "tcp"], 
              "dut1": {"name": "DUT Log Window-1", "faultseq": [], 
                       "action": "None", "interface": "serial", 
                       "serial": {"port": "None", "baud": "9600", "databits": "8", 
                                  "parity": "none", "stopbits": "1", "parerrcheck": "ignore"}, 
                       "tcp": {}, 
                       "default": {"serial": {"port": "None", "baud": "9600", "parity": "none", 
                                              "databits": 8, "stopbits": "1", "parerrcheck": "ignore"}, 
                                   "tcp": {}}}, 
              "dut2": {"name": "DUT Log Window-2", "faultseq": [], 
                       "action": "None", "interface": "serial", 
                       "serial": {"port": "None", "baud": "9600", "databits": "8", "parity": "none", 
                                  "stopbits": "1", "parerrcheck": "ignore"}, 
                       "tcp": {}, 
                       "default": {"serial": {"port": "None", "baud": "9600", "parity": "none", 
                                              "databits": 8, "stopbits": "1", "parerrcheck": "ignore"}, 
                                   "tcp": {}}}
       },
       "batch" : {"location": ""},
       "screen": {"pos": [], "size": []},
       "wdialog": False,
       "msudp": {"uname": None, "pwd": None},
       "rpanel": {"dut1": True, "dut2": True, "u4tree": True}
}
