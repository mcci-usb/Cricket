# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: devServer.py
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
import search
import control2101 as d2101

keywords = {'Python',
            'wxpython',
            'SocketProgramming'
            }

class ServerCc:
    def __init__(self, host='', port: int = 5566):
        self.IP = ""
        self.PORT = 5566
        self.ADDR = ((self.IP, self.PORT))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
        print('Server Listeneing port: ' + host + ':' + str(port))
        self.bind_addr = host + ':' + str(port)
        self.conn_socket = None
        self.addr = None

    def close(self):
        self.socket.close()
        
keywords = {'Python',
            'wxpython',
            'SocketProgramming'
            }

class StayAccept(threading.Thread):
    def __init__(self, parent):
        super(StayAccept, self).__init__()
        self.window = parent
        self.wait = True
        self.rs = None
    
    def run(self) -> None:
        print("\nServer waiting for connections")
        while self.wait:
            try:
                self.window.ccserver.conn_socket, self.window.ccserver.addr = self.window.ccserver.socket.accept()
                new_conn_info = '\nnew connection: ' + str(self.window.ccserver.addr)
                self.rs = RequestSync(self.window)
                self.rs.start()
            except:
                pass

    def close_connection(self):
        print("\nServer close connections")
        self.wait = False

   
class RequestSync(threading.Thread):
    def __init__(self, parent):
        super(RequestSync, self).__init__()
        self.window = parent
        self._running = True
    
    def terminate(self):
        print("Server closing a client")
        self._running = False

    def run(self) -> None:
        # This message sent to client, when it gets connected with this server
        print("Server accepting a client")
        while self._running:
            try:
                data = self.window.ccserver.conn_socket.recv(1024).decode('utf-8')
            except ConnectionResetError:
                self.window.ccserver.conn_socket.close()
                disconnect_info = str(self.window.ccserver.addr) + ' socket\n'
                wx.CallAfter(self.window.panel.PrintLog, "\n P2: "+disconnect_info)
                break
            if data == 'exit':
                self.window.ccserver.conn_socket.sendall('exit'.encode('utf-8'))
                self.window.ccserver.conn_socket.close()
                disconnect_info = str(self.window.ccserver.addr) + ' ipadd\n'
                wx.CallAfter(self.window.panel.PrintLog, "\n"+disconnect_info)
                break
            if data == 'force_exit':
                self.window.ccserver.conn_socket.close()
                disconnect_info = str(self.window.ccserver.addr) + ' ipadd\n'
                wx.CallAfter(self.window.panel.PrintLog, "\n P4: "+disconnect_info)
                break
            if data:
                msg = 'ClientIPAddr '+str(self.window.ccserver.addr)+' '+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+' Time: '+data
                
                result = self.verify_command(data)
                data= json.dumps(result)
                self.window.ccserver.conn_socket.sendall(data.encode('utf-8'))
                self.terminate()
                
    
    def verify_command(self, nwdata):
        nwd = nwdata.split(",")
        msg = nwd[0]
        if(msg == "open"):
            result = self.window.devHand.open_serial_device(nwd[1], int(nwd[2]))
            rdict = {}
            if result:
                rdict["data"] = "success"
            else:
                rdict["data"] = "fail"
            wx.CallAfter(self.window.panel.PrintLog, "\nPort Open: "+rdict["data"]+"\n")
            return rdict
        if(msg == "close"):
            result = self.window.devHand.close()
            rdict = {}
            if result:
                rdict["data"] = "success"
            else:
                rdict["data"] = "fail"
            wx.CallAfter(self.window.panel.PrintLog, "\nPort Close: "+rdict["data"]+"\n")
            return rdict
        elif msg == "port":
            result = self.window.devHand.send_port_cmd(nwd[1])
            wx.CallAfter(self.window.panel.PrintLog, nwd[1])
            rdict = {}
            rdict["data"] = result
            return rdict
        elif msg == "read":
            result = self.window.devHand.read_port_cmd()
            rdict = {}
            rdict["data"] = result
            return rdict
        elif(msg == "status"):
            result = self.window.devHand.send_status_cmd()
            rdict = {}
            rdict["data"] = result
            return rdict
        elif(msg == "volts"):
            result = self.window.devHand.send_volts_cmd()
            rdict = {}
            rdict["data"] = result
            wx.CallAfter(self.window.panel.PrintLog, "\nVolts")
            return rdict
        elif(msg == "amps"):
            result = self.window.devHand.send_amps_cmd()
            rdict = {}
            rdict["data"] = result
            wx.CallAfter(self.window.panel.PrintLog, "\nAmps")
            return rdict
        elif(msg == "c2101"):
            result = d2101.control_port(nwd[1], int(nwd[2]))
            rdict = {}
            rdict["data"] = str(result)
            wx.CallAfter(self.window.panel.PrintLog, "\n2101 Port: "+rdict["data"]+"\n")
            return rdict

        elif(msg == "device"):
            result = search.search_port()
            wx.CallAfter(self.window.panel.PrintLog, "\nDevice Search")
            return result
        elif (msg == "on"):
            sCmd = "port 1" + "\r\n"
            result = self.write_serial(sCmd)
            return result
        elif (msg == "off"):
            sCmd = "port 1" + "0" + "\r\n"
            result = self.write_serial(sCmd)
            return result
        elif (msg == "on2"):
            sCmd = "port 2" + "\r\n"
            result = self.write_serial(sCmd)
            return result
        elif (msg == "off2"):
            sCmd = "port 2" + "0" + "\r\n"
            result = self.write_serial(sCmd)
            return result
        elif (msg == "on3"):
            sCmd = "port 3" + "\r\n"
            result = self.write_serial(sCmd)
            return result
        elif (msg == "off3"):
            sCmd = "port 3" + "0" + "\r\n"
            result = self.write_serial(sCmd)
            return result
        elif (msg == "on4"):
            sCmd = "port 4" + "\r\n"
            result = self.write_serial(sCmd)
            return result
        elif (msg == "off4"):
            sCmd = "port 4" + "0" + "\r\n"
            result = self.write_serial(sCmd)
            return result
        elif (msg == "volts"):
            sCmd = "volts" + "\r\n"
            result = self.write_serial(sCmd)
            return result

        elif(msg.startswith("port:")):
            rSplitPort = msg.split(":")
            rPort = rSplitPort[-1]
            resp = self.open_serial(rPort)
            return resp
        else:
            errMsg = "command not valid"
            return errMsg