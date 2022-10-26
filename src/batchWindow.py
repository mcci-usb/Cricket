##############################################################################
# 
# Module: autoWindow.py
#
# Description:
#     autoWindow for Switch Model 3201, 3141, 2101, 2301
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
#     V2.6.0 Wed Apr 20 2022 17:00:00   Seenivasan V
#       Module created
##############################################################################
# Lib imports
import wx

from uiGlobals import *


import configdata

import os

from wx.lib.scrolledpanel import ScrolledPanel
##############################################################################
# Utilities
##############################################################################

class BatchWindow(wx.Window):
    def __init__(self, parent, top):
        wx.Window.__init__(self, parent)
        # SET BACKGROUND COLOUR TO White
        self.SetBackgroundColour("White")

        #self.SetMinSize((200,200))
        self.parent = parent
        self.top = top
        self.config = top.config_data
        
        # Oct 08 2022
        self.batch_flg = False

        self.batchopcode = {
            "switch": self.parseSwMacro,
            "main:": self.parseMain,
            "port": self.parsePort,
            "delay": self.parseDelay,
            "read": self.parseRead,
            "repeat": self.parseRepeat,
            "end": self.parseEnd
        }

        self.batchdecode = {
            "switch": self.setSwPath,
            "port": self.doPortON,
            "speed": self.setSpeed,
            "delay": self.executeDelay,
            "read": self.executeOthers,
            "repeat": self.executeRepeat
        }

        self.vbOuter = wx.BoxSizer(wx.VERTICAL)

        self.hbOuter = wx.BoxSizer(wx.HORIZONTAL)
        self.vbMid = wx.BoxSizer(wx.VERTICAL)
        self.hbSelect = wx.BoxSizer(wx.HORIZONTAL)
        self.vbSeq = wx.BoxSizer(wx.VERTICAL)
        self.hbBtn = wx.BoxSizer(wx.HORIZONTAL)

        self.cb_seqlist = self.getSeqList()

        self.mappedSw = {}
        self.reqSw = {}
        self.main_flg = False
        self.end_flg = False
        self.swpath = None
        self.repeat = 0
        self.done = 0
        self.seqIdx = 0
        self.tdelay = 500
        
        self.InitTopHbox()
        self.InitSeqBox()
        self.InitBotHbox()

        self.vbMid.AddMany([
            ((0, 20), 0, wx.EXPAND),
            (self.hbSelect, 0, wx.EXPAND),
            ((0, 20), 0, wx.EXPAND),
            (self.vbSeq, 1, wx.EXPAND),
            ((0, 20), 0, wx.EXPAND),
            (self.hbBtn, 0, wx.EXPAND),
            ((0,20), 0, wx.EXPAND),
        ])

        self.hbOuter.AddMany([
            ((-1, 0), 1, wx.EXPAND),
            (self.vbMid, 1, wx.EXPAND),
            ((-1,0), 1, wx.EXPAND),
            ])

        self.vbOuter.AddMany([
            ((0, 20), 0, wx.EXPAND),
            (self.hbOuter, 1, wx.EXPAND),
            ((0, 20), 0, wx.EXPAND),
            ])

        self.SetSizer(self.vbOuter)

        base = os.path.abspath(os.path.dirname(__file__))
        
        self.Show()
        self.Layout()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.TimerServ, self.timer)
    
    def Batch_strat_msg(self, seqName):
        """
        auto mode Start up Message for Auto Mode on logwindow.
        
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.top.print_on_log("Batch Mode start - "+seqName+"\n")

    def default(self, nodata):
        print(nodata)

    def setSwPath(self, inpath):
        self.swpath = inpath

    def doPortON(self, portNo):
        self.top.port_on(self.swpath, portNo, True)
    
    def setSpeed(self, inspeed):
        self.top.set_speed(self.swpath, inspeed)

    def executeDelay(self, indelay):
        self.tdelay = indelay
        self.top.print_on_log("Delay: "+str(indelay)+"\n")

    def executeOthers(self, incmd):
        self.top.print_on_log("Read: "+incmd+"\n")
        if incmd == "USB":
            self.top.get_usb_tree()
        else:
            self.top.read_param(self.swpath, incmd)

    def executeRepeat(self, repeat):
        self.top.print_on_log("Repeat\n")

    def getSeqList(self):
        keys = list(self.config.keys())
        if "sequenceconfig" in keys:
            cval = self.config["sequenceconfig"]
            ikeys = list(cval.keys())
            if(len(ikeys) == 0):
                return ["no sequence found"]
            else:
                return ikeys
        else:
            return ["no sequence found"]

    def InitTopHbox(self):
        self.st_seqname = wx.StaticText(self, -1, "Browse the Sequence: ")
        self.tc_bloc = wx.TextCtrl(self, -1, size=(250,-1), 
                                            style = wx.TE_CENTRE |
                                            wx.TE_PROCESS_ENTER,
                                            validator=NumericValidator())
        self.btn_load = wx.Button(self, -1, "Load", size=(60,25))

        self.hbSelect.AddMany([
            ((-1,0), 1, wx.EXPAND),
            (self.st_seqname, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER),
            ((20,0), 0, wx.EXPAND),
            (self.tc_bloc , 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER),
            ((20,0), 0, wx.EXPAND),
            (self.btn_load , 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER),
            ((-1,0), 1, wx.EXPAND)
        ])

        self.btn_load.Bind(wx.EVT_BUTTON, self.LoadBatch)

    def InitSeqBox(self):
            self.tc_seq = wx.TextCtrl(self, -1, style= wx.TE_MULTILINE, 
                                         size=(400,250))
            self.vbSeq.Add(
                self.tc_seq, 1, wx.EXPAND
            )
    
    def InitBotHbox(self):
        self.btn_start = wx.Button(self, -1, "Start", size=(60,25))
        self.btn_save = wx.Button(self, -1, "Save", size=(60,25))

        self.hbBtn.AddMany([
            ((-1,0), 1, wx.EXPAND),
            (self.btn_start, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER),
            ((20,0), 0, wx.EXPAND),
            (self.btn_save , 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER),
            ((-1,0), 1, wx.EXPAND)
        ])

        self.btn_start.Bind(wx.EVT_BUTTON, self.OnClickBatch)
        self.btn_save.Bind(wx.EVT_BUTTON, self.SaveBatch)

    def OnClickBatch(self, event):
        if self.batch_flg:
            self.StopBatch()
            self.top.print_on_log("\nBatch Mode Stopped!")
            self.timer.Stop()        
        else:
            self.StartBatch()

    def StopBatch(self):
        self.batch_flg = False
        # The Lablel to set name as Auto
        self.btn_start.SetLabel("Start")
        # The mode set as Manual Mode.
        self.top.set_mode(MODE_MANUAL)
        
    def StartBatch(self):
        self.mappedSw = {}
        self.reqSw = {}
        self.main_flg = False
        self.end_flg = False
        self.finseq = []
        self.parseBatchSeq()
        
        if self.top.createBatchPanel(self.reqSw):
            self.runBatchSeq()
        else:
            wx.MessageBox('Could not find the Switch as per sequence', 'Warning', wx.OK | wx.ICON_WARNING)
        
    def runBatchSeq(self):
        self.batch_flg = True
        self.btn_start.SetLabel("Stop")

        self.done = 0
        self.seqIdx = 0
        self.totSeq = len(self.finseq)
        self.tdelay = 500

        self.top.print_on_log("\nBatch Mode Starting!")
        self.top.print_on_log("\nRepeat Count: "+str(self.repeat))

        if(self.timer.IsRunning() == False):
            self.timer.Start(self.tdelay)

    def TimerServ(self, evt):
        self.timer.Stop()
        key = list(self.finseq[self.seqIdx])[0]
        self.batchdecode.get(key, self.defaultCmd) (self.finseq[self.seqIdx][key])
        self.seqIdx += 1
        self.timer.Start(self.tdelay)
        self.tdelay = 1
        if self.seqIdx >= len(self.finseq):
            self.seqIdx = 0
            self.done += 1
            self.top.print_on_log("\nCycle Completed: "+str(self.done))

            if self.done >= self.repeat:
                self.timer.Stop()
                self.StopBatch()
                self.top.print_on_log("\nBatch Sequence Completed!")

    def executeBatchSeq(self):
        self.done = 0
        if self.repeat == 0:
            self.repeat = 1
        self.seqIndex = 0

        self.totseq = len(self.finseq)
        
    def SaveBatch(self, event):
        content = self.tc_seq.GetValue()
        self.save_batch(content, "*.txt")

    def LoadBatch(self, event):
        self.load_file()

    def load_file(self):
        """
        click on load button open the wx.Dialog window to 
        select which is saved in a csv file
        Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        Returns: 
        return- success for file save in directiry
        """
        self.dirname=""
        dlg = wx.FileDialog(self, "Load File", self.dirname, "", "*.txt", 
                                wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        
        pathname = dlg.GetPath()
        self.tc_bloc.SetValue(pathname)
        try:
            self.tc_seq.SetValue("")
            self.mappedSw = {}
            self.main_flg = False
            self.end_flg = False
            self.finseq = []
            if os.path.exists(pathname):
                with open(pathname) as fobj:
                    for line in fobj:
                        self.tc_seq.WriteText(line)
        except IOError:
            wx.LogError("Can not open file '%s', " % pathname)

    def save_batch (self, contents, extension):
        """
        Export the LogWindow/USBTreeWindow content to a file
        Called by LogWindow and USB Tree View Window

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            return- success for file save in directiry
        """
        # Save a file
        self.dirname=""
        dlg = wx.FileDialog(self, "Save as", self.dirname, "", extension, 
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            wx.BeginBusyCursor()

            dirname = dlg.GetDirectory()
            filename = os.path.join(dirname, dlg.GetFilename())

            if (os.path.isdir(dirname) and os.access(dirname, os.X_OK | 
                                                     os.W_OK)):
                self.dirname = dirname
            try:
                f = open(filename, 'w')
                f.write(contents)
                f.close()
            except IOError:
                options = wx.OK | wx.ICON_ERROR
                dlg_error = wx.MessageDialog(self,
                                           "Error saving file\n\n" + strerror,
                                           "Error",
                                           options)
                dlg_error.ShowModal()
                dlg_error.Destroy()

        dlg.Destroy()

        if (wx.IsBusy()):
            wx.EndBusyCursor()
        return
    
    def parseSwMacro(self, oclist):
        devlist = ["3141", "3201", "2301", "2101"]
        swtype = oclist[4].replace('"','')
        swpath = oclist[3].replace('"', '')
        swpath = swpath.replace(',', '')
        if oclist[2] == "=":
            if any(swtype in s for s in devlist):
                self.mappedSw[oclist[1]] = swpath
                self.reqSw[swpath] = swtype
            else:
                print("Error in parsing Switch Mapping, not supporting USB Switch")
        else:
            print("Syntax error in mapping '='")
        
    def parseDelay(self, indata):
        if self.main_flg == True:
            try:
                delay = indata[1].replace('ms', '')
                delay = int(delay)
                self.finseq.append({"delay": delay})
            except:
                pass

        else:
            print("Main keyword should present after declaration")

    def parsePort(self, indata):
        if self.main_flg == True:
            speed = None
            try:
                if indata[2] == 'SS0' or indata[2] == 'SS1':
                    speed = indata[2]
            except:
                print("No speed info found")
            
            swcode = indata[1].split('.')   
            swname = swcode[0]
            portname = swcode[1].replace('p', '') 
            self.finseq.append({"switch": self.mappedSw[swname]})
            if speed != None:
                self.finseq.append({"speed": speed})
            self.finseq.append({"port": int(portname)})
            
        else:
            print("Main keyword should present after declaration")

    def parseRead(self, indata):
        rdlist = ["voltage", "current", "USB", ]
        try:
            if any(indata[1] in s for s in rdlist):
                self.finseq.append({"read": indata[1]})
        except:
            pass

    def parseRepeat(self, indata):
        if len(indata) == 2:
            try:
                rptcnt = int(indata[1])
                self.finseq.append({"repeat": rptcnt})
                self.repeat = rptcnt
            except:
                pass
        elif len(indata) < 2:
            wx.MessageBox('Parsing Error, expecting int to repeat, line number', 'Warning', wx.OK | wx.ICON_WARNING)
        elif len(indata) > 2:
            wx.MessageBox('Parsing Error, found more argument in repeat, line number', 'Warning', wx.OK | wx.ICON_WARNING)

    def parseMain(self, indata):
        self.main_flg = True

    def parseEnd(self, indata):
        self.end_flg = True

    def defaultCmd(self, other):
        pass

    def port_on(self, portno, stat):
        self.top.port_on(self.swkey, portno, stat)

    def parseBatchSeq(self):
        self.finseq = []
        noofline = self.tc_seq.GetNumberOfLines()
        for i in range(0, noofline):
            strdata = self.tc_seq.GetLineText(i)
            mylist = strdata.split(" ")
            self.batchopcode.get(mylist[0], self.defaultCmd)(mylist)