config_data = {
       "name": "Cricket UI", 
       "version": "1.0.0", 
       "myrole": {
              "uc": True, 
              "cc": True, 
              "thc": True
              }, 
              
              "uc": {
                     "interfaces": ["serial", "tcp"], 
                     "mynodes": {
                            "mycc": [{
                                   "name": "alpha machine", 
                                   "interface": "tcp", 
                                   "serial": {}, 
                                   "tcp": {
                                          "ip": "192.168.0.176", 
                                          "port": "2021"}}], 
                                          "mythc": {
                                                 "name": "alpha test host", 
                                                 "ineterface": "tcp", 
                                                 "serial": {}, "tcp": {}}}, "default": {"mycc": {"tcp": {"ip": "192.168.0.23", "port": "2021"}}, "mythc": {"tcp": {"ip": "192.168.0.31", "port": "2022"}}}}, "cc": {"interface": "tcp", "serial": {}, "tcp": {"ip": "192.168.0.34", "port": "2021"}}, "thc": {"interface": "tcp", "serial": {}, "tcp": {"ip": "192.168.0.34", "port": "2022"}}, "features": ["auto", "loop"], "plugins": ["sut", "batch"], "sut": {"nodes": {"sut1": True, "sut2": False}, "interfaces": ["serial", "tcp"], "sut1": {"name": "TI - Serial Log Window", "faultseq": ["MCCI-TEST"], "action": "count match", "interface": "serial", "serial": {"port": "COM21", "baud": "115200", "databits": "8", "parity": "none", "stopbits": "1", "parerrcheck": "ignore"}, "tcp": {}, "default": {"serial": {"port": "COM1", "baud": "9600", "parity": "none", "databits": 8, "stopbits": "1", "parerrcheck": "ignore"}, "tcp": {}}}, "sut2": {"name": "DUT Log Window - 2", "faultseq": ["mybeta fault-1", "mybeta fault-2", "mybeta fault-3"], "action": "count match", "interface": "serial", "serial": {"port": "COM11", "baud": "115200", "databits": "8", "parity": "none", "stopbits": "1", "parerrcheck": "ignore"}, "tcp": {}, "default": {"serial": {"port": "COM1", "baud": "9600", "parity": "none", "databits": 8, "stopbits": "1", "parerrcheck": "ignore"}, "tcp": {}}}}}
