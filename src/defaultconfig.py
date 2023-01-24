##############################################################################
# 
# Module: defaultconfig.py
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
#    V3.0.0 Wed Oct 12 2022 17:00:00   Seenivasan V
#       Module created
################################################################################

config_data = {
       "name": "Cricket", 
       "version": "1.0.0", 
       "myrole": {"uc": True, "cc": True, "thc": True }, 
       "uc": {"interfaces": ["serial", "tcp"], 
              "mynodes": {"mycc": [{"name": "control computer", 
                                    "interface": "tcp", 
                                    "serial": {}, 
                                    "tcp": {}}], 
                          "mythc": {"name": "test host computer",
                                    "ineterface": "tcp", 
                                    "serial": {}, "tcp": {}}}, 
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
       "wdialog": False
}
