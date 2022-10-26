config_data = {"computer": ["uc", "cc", "thc"],
 "uc": {"cc": [{"type": "tcp", "port": "2021", "ip": "192.168.0.34"}, {"type": "tcp", "port": "2021", "ip": "192.168.0.112"}], 
        "thc": {"type": "tcp", "port": "2022", "ip": "192.168.0.95"}, 
        "SUT": [{"name":"Alpha Serial Log", "type": "serial", 
                 "settings": {"comPort": "COM13", "baudRate": "9600", "dataBits": "8", "parity": "None", 
                 "stopBits": "1", "parityErrChk": "(ignore)"}, 
                 "faultMsg": ["Non-secure Usage Fault", "FATAL ERROR: Secure Fault", "osTimerNew() failed"]}, 
                 {"name":"Beta Serial Log", "type": "serial", 
                 "settings": {"comPort": "COM15", "baudRate": "9600", "dataBits": "8", "parity": "None", 
                 "stopBits": "1", "parityErrChk": "(ignore)"}, 
                 "faultMsg": ["Non-secure Usage Fault", "FATAL ERROR: Secure Fault", "osTimerNew() failed"]}]
        },
 "cc": {"type": "tcp", "port": "2021"},
 "thc": {"type": "tcp", "port": "2022"}}