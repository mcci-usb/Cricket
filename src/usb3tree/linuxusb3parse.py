
##############################################################################
# 
# Module: linuxusb3parse.py
#
# Description:
#     parsing the USB3 Tree view data in Linux 
#
# Author:
#     Vinay N, MCCI Corporation Mar 2024
#
# Revision history:
#      V4.3.1 Mon Apr 15 2024 17:00:00   Seenivasan V 
#       Module created
##############################################################################
class LinuxUsb4TreeParse():
    def __init__(self):
        self.idata = None
        self.ldata = None
    
    def parse_usb3tb_data(self, usb3data):
        """
        Parse USB3 data and organize it into internal data structures.

        This method takes USB3 data and organizes it into internal data structures
        for easier access and manipulation.

        Args:
            usb4data (dict): USB4TB data to be parsed.

        Returns:
            None
        """
        self.idata = self.get_item_data(usb3data)
        self.ldata = self.get_level_data(self.idata)
        # if self.idata is not None:
        #     self.ldata = self.get_level_data(self.idata)
        # else:
        #     print("Error: idata is None")

    def get_item_data(self, msg):
        """
        Parse USB 3.0 data from a list of dictionaries containing USB device information.

        Args:
            msg (list): A list of dictionaries containing USB device information.

        Returns:
            dict: A dictionary containing parsed USB 3.0 data with keys formatted as 'vid,pid,bus,speed'.
                Each value is a dictionary containing details such as type, vid, pid, bus, speed, ifc,
                and optionally mport and port if available.
            None: If the input 'msg' is not a list or if there are missing required fields in any item.
        """
        if not isinstance(msg, list):
            print("Error: usb3data is not a list")
            return None
        
        parsed_usb3 = {}
        for item in msg:
            if isinstance(item, dict):
                vid = item.get('vid')
                pid = item.get('pid')
                bus = item.get('bus')
                speed = item.get('speed')
                ifc = item.get('ifc')
                mport = item.get('mport')
                port = item.get('port')

                if vid is not None and pid is not None and bus is not None and speed is not None and ifc is not None:
                    key = f"{vid},{pid},{bus},{speed}"
                    parsed_item = {
                        'type': 'usb3',
                        'vid': vid,
                        'pid': pid,
                        'bus': bus,
                        'speed': speed,
                        'ifc': ifc
                    }
                    if mport is not None:
                        parsed_item['mport'] = mport
                        parsed_item['port'] = port
                    parsed_usb3[key] = parsed_item
                else:
                    print("Error: Missing required fields in item")
            else:
                print("Error: Item is not a dictionary")
        
        return parsed_usb3

    def get_level_data(self, u3tbuf):
        """
        Organize USB 3.0 data into levels based on the count of comma-separated keys.

        Args:
            u3tbuf (dict): A dictionary containing USB 3.0 data where keys are formatted as 'vid,pid,bus,speed'.

        Returns:
            dict: A dictionary organizing USB 3.0 data into levels based on the count of comma-separated keys.
                Keys are formatted as 'levelX' where X is the count of commas in the keys of u3tbuf.
                Values are lists containing keys from u3tbuf that match the respective level.
            None: If the input 'u3tbuf' is not a dictionary.
        """
        if not isinstance(u3tbuf, dict):
            print("Error: u3tbuf is not a dictionary")
            return None

        pdict = {}
        for rkitem in u3tbuf.keys():
            lcnt = rkitem.count(',')
            kl = list(pdict.keys())
            if 'level'+str(lcnt) in kl:
                pdict['level'+str(lcnt)].append(rkitem)
            else:
                pdict['level'+str(lcnt)] = [rkitem]
        return pdict
