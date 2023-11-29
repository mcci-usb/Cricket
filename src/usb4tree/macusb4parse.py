import copy

class MacUsb4TreeParse():
    def __init__(self):
        self.idata = None
        self.ldata = None

    def parse_usb4tb_data(self, usb4data):
        """
        Parse USB4TB data and organize it into internal data structures.

        This method takes USB4TB data and organizes it into internal data structures
        for easier access and manipulation.

        Args:
            usb4data (dict): USB4TB data to be parsed.

        Returns:
            None
        """
        self.idata = None
        self.ldata = None
        mlist = self.get_item_data(usb4data)
        
        mdlist = []
        idx = 0
        for busd in mlist:
            mdlist.append(self.merge_parent_node(busd, idx))
            idx = idx + 1
        
        mdict = {}
        for busd in mdlist:
            mdict.update(busd)

        ldict = self.get_level_data(mdict)

        portdict = {}

        for level in ldict:
            for dev in ldict[level]:
                self.add_ports(level, dev, ldict, portdict)

        for dev in mdict:
            mdict[dev]["ports"] = portdict[dev]


        self.idata = copy.deepcopy(mdict)
        self.ldata = copy.deepcopy(ldict)

    def add_ports(self, glevel, gdev, gldict, gpdict):
        """
        Add port information for a device in the next level of USB hierarchy.

        This method takes the current USB hierarchy level (`glevel`), the device name (`gdev`),
        the dictionary of USB levels (`gldict`), and the dictionary of port information (`gpdict`).
        It calculates the next level index, constructs the next level key, and retrieves the list of
        devices at the next level. If devices at the next level exist, it adds port information for
        the specified device (`gdev`) to the port dictionary (`gpdict`).

        Args:
            glevel (str): Current USB hierarchy level.
            gdev (str): Device name for which ports are to be added.
            gldict (dict): Dictionary of USB levels.
            gpdict (dict): Dictionary to store port information for devices.

        Returns:
            None
        """
            
        nidx = int(glevel.split('level')[1])+1
        nlkey = 'level'+str(nidx)
        if nlkey in gldict:
            nldlist = gldict[nlkey]
            gpdict[gdev] = [int(s.split(gdev+',')[1]) for s in nldlist if s.startswith(gdev+',')]
        else:
            gpdict[gdev] = []

    # Parse the USB4 JSON to Tree buffer (customized)
    def get_item_data(self, msg):
        """
        Extract USB item data from a system profile message.

        This method takes a system profile message (`msg`) and extracts USB item data from the
        "SPThunderboltDataType" key. It iterates through the USB data, parses each USB tree, and
        collects the parsed data in a list.

        Args:
            msg (dict): System profile message containing USB data.

        Returns:
            list: A list containing parsed USB tree data for each Thunderbolt bus.
        """
        usb_data = msg["SPThunderboltDataType"]
        usbt_list = []

        for bus in usb_data:
            usbt_list.append(self.parse_usb_tree(bus, {}))
        return usbt_list
    
    # # Recursive function extract VID, PID and other properties
    def parse_usb_tree(self, node, accdict):
        """
        Parse a USB tree node and populate an accumulator dictionary.

        This method recursively traverses a USB tree node (`node`) and populates an accumulator
        dictionary (`accdict`) with information about USB devices. It looks for specific keys in
        the node to extract information such as the device name, description, vendor name, vendor ID,
        product ID, and route string.

        Args:
            node (dict): USB tree node to be parsed.
            accdict (dict): Accumulator dictionary to store information about USB devices.

        Returns:
            dict: The updated accumulator dictionary with information about USB devices.
        """
        if "_name" in node and "device_name_key" in node:
            mydict = {}
            mydict["mname"] = node['_name']
            mydict["desc"] = node['device_name_key']
            mydict['vname'] = node['vendor_name_key']
            if 'device_id_key' in node and 'vendor_id_key' in node:
                mydict['vid'] = int(node['vendor_id_key'], 16)
                mydict['pid'] = int(node['device_id_key'], 16)
            ordstr = self.convert_order(node["route_string_key"])
            # if ordstr != '0':
            accdict[ordstr] = mydict

        if "_items" in node:
            for item in node["_items"]:
                self.parse_usb_tree(item, accdict)
        return accdict
    
    # # # For Mac - In Mac Hierarchy as "route_string_key" : "30701"
    # # # Need to convert "30701" as "1,7,3"
    def convert_order(self, instr):
        """
        Convert a string of digits into a comma-separated string with reversed two-digit numbers.

        This method takes a string of digits (`instr`) and converts it into a comma-separated string
        with reversed two-digit numbers. The input string is processed in reverse order, and each pair
        of digits is converted into an integer, ignoring leading zeros. The resulting numbers are then
        reversed and joined into a comma-separated string.

        Args:
            instr (str): Input string of digits.

        Returns:
            str: Comma-separated string with reversed two-digit numbers.
        """
        conv_nums = []
        for i in range(len(instr)-2, -1, -2):
            two_digits = instr[i:i+2]
            conv_numb = int(two_digits.lstrip('0'))
            conv_nums.append(conv_numb)
        if len(instr) % 2 == 1:
            conv_nums.append(int(instr[0]))
        ordstr = ','.join(map(str, conv_nums))
        return ordstr
    
    # For Mac - In Mac root node (Ex. thunderbolt bus) is defined as "route_string_key" : "0"
    # consider if a Mac has more than one root node, then need to prefix
    # the node if of the root node with the childe nodes, to make all under one dictionary 
    # this needs unique key, so prefix the node id of the root node is required 
    def merge_parent_node(self, u4dict, idx):
        """
        Merge a parent node with its child nodes in a USB4TB data dictionary.

        This method takes a USB4TB data dictionary (`u4dict`) and merges a parent node with its
        child nodes. The merging is done by prefixing the keys of the child nodes with the index (`idx`)
        and a comma.

        Args:
            u4dict (dict): USB4TB data dictionary to be modified.
            idx (int): Index to be used for merging.

        Returns:
            dict: A new USB4TB data dictionary after merging the parent node with its child nodes.
        """
        nu4dict = {}
        for key, value in u4dict.items():
            if key != '0':
                nkey = str(idx) + ',' + key
                nu4dict[nkey] = value
            else:
                nu4dict[str(idx)] = value
        return nu4dict
    
    # Both Win and Mac
    def get_level_data(self, u4tbuf):
        """
        Group USB4TB data into levels based on comma count in keys.

        This method takes a dictionary of USB4TB data (`u4tbuf`) and groups the data into levels
        based on the number of commas in the keys.

        Args:
            u4tbuf (dict): USB4TB data to be grouped.

        Returns:
            dict: A dictionary where keys are level names ('level0', 'level1', ...) and values are
                lists of keys from the input data belonging to each level.
        """
        rkarr = list(u4tbuf.keys())
        pdict = {}
        for rkitem in rkarr:
            lcnt = rkitem.count(',')
            kl = list(pdict.keys())
            if 'level'+str(lcnt) in kl:
                pdict['level'+str(lcnt)].append(rkitem)
            else:
                pdict['level'+str(lcnt)] = [rkitem]
        return pdict