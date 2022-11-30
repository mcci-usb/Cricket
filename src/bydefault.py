config_data = {"computer": ["uc", "cc", "thc"],
 "uc": {"cc": [{"type": "tcp", "port": "2021", "ip": "192.168.0.21"}], 
        "thc": {"type": "tcp", "port": "2022", "ip": "192.168.0.22"}, 
        "DUT": [{"name":"DUT Log Window-1", "type": "serial", 
                 "settings": {"comPort": "None", "baudRate": "9600", "dataBits": "8", "parity": "None", 
                 "stopBits": "1", "parityErrChk": "(ignore)"}, 
                 "faultMsg": ["None"], "action": "None"}, 
                 {"name":"DUT Log Window-2", "type": "serial", 
                 "settings": {"comPort": "None", "baudRate": "9600", "dataBits": "8", "parity": "None", 
                 "stopBits": "1", "parityErrChk": "(ignore)"}, 
                 "faultMsg": ["None"], "action": "None"}]
        },
 "cc": {"type": "tcp", "port": "2021"},
 "thc": {"type": "tcp", "port": "2022"}}