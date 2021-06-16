# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: thServer.py
#
# Description:
#     Server socket module, which listens for the client
#     Based on the command from Clinet, control device which is connected
#     Send the response back to Clinet in JSON format (JSON Object)
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
#     Seenivasan V, MCCI Corporation June 2021
#
# Revision history:
#     V2.4.0-2 Wed June 14 2021 18:50:10 seenivasan
#       Module created
##############################################################################
# Built-in imports

import socket
import threading
import time
import wx
import json
import usbDev

keywords = {'Python',
            'wxpython',
            'SocketProgramming'
            }

class ServerHc:
    def __init__(self, host='', port: int = 5567):
        self.IP = ""
        self.PORT = 5567
        self.ADDR = ((self.IP, self.PORT))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
        print('Test Host Server Listeneing port: ' + host + ':' + str(port))
        self.bind_addr = host + ':' + str(port)
        self.conn_socket = None
        self.addr = None

    def close(self):
        self.socket.close()
        

class StayAccept(threading.Thread):
    def __init__(self, parent):
        super(StayAccept, self).__init__()
        self.window = parent
        self.wait = True
        self.rs = None
    
    def run(self) -> None:
        print("\nTHC Server waiting for connections")
        while self.wait:
            try:
                self.window.hcserver.conn_socket, self.window.hcserver.addr = self.window.hcserver.socket.accept()
                new_conn_info = '\nnew connection: ' + str(self.window.hcserver.addr)
                self.rs = RequestSync(self.window)
                self.rs.start()
            except:
                pass

    def close_connection(self):
        print("\nTHC Server close connections")
        self.wait = False

   
class RequestSync(threading.Thread):
    def __init__(self, parent):
        super(RequestSync, self).__init__()
        self.window = parent
        self._running = True
    
    def terminate(self):
        print("THC Server closing a client")
        self._running = False

    def run(self) -> None:
        # This message sent to client, when it gets connected with this server
        print("THC Server accepting a client")
        while self._running:
            try:
                data = self.window.hcserver.conn_socket.recv(1024).decode('utf-8')
            except ConnectionResetError:
                self.window.hcserver.conn_socket.close()
                disconnect_info = str(self.window.hcserver.addr) + ' socket\n'
                wx.CallAfter(self.window.panel.PrintLog, "\n P2: "+disconnect_info)
                break
            if data == 'exit':
                self.window.hcserver.conn_socket.sendall('exit'.encode('utf-8'))
                self.window.hcserver.conn_socket.close()
                disconnect_info = str(self.window.hcserver.addr) + ' ipadd\n'
                wx.CallAfter(self.window.panel.PrintLog, "\n"+disconnect_info)
                break
            if data == 'force_exit':
                self.window.hcserver.conn_socket.close()
                disconnect_info = str(self.window.hcserver.addr) + ' ipadd\n'
                wx.CallAfter(self.window.panel.PrintLog, "\n P4: "+disconnect_info)
                break
            if data:
                msg = 'ClientIPAddr '+str(self.window.hcserver.addr)+' '+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+' Time: '+data
                print("THC Command received: ", data)
                result = self.verify_command(data)
                data= json.dumps(result)
                self.window.hcserver.conn_socket.sendall(data.encode('utf-8'))
                self.terminate()
                
    
    def verify_command(self, nwdata):
        nwd = nwdata.split(",")
        msg = nwd[0]
        if(msg == "usb"):
            print("Server Cmd Read USB")
            result = usbDev.get_usb_tree()
            #print("USB Result: ", result)
            wx.CallAfter(self.window.panel.PrintLog, nwd[1])
            rdict = {}
            rdict["data"] = result
            #print("\nDictionary: ")
            #print(rdict)
            return rdict
        else:
            errMsg = "command not valid"
            return errMsg