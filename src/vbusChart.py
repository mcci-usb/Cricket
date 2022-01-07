##############################################################################
# 
# Module: vbusChart.py
#
# Description:
#     Monitoring the Voltage and Current data updated in V/I Plot.
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
#     V2.5.0 Fri Jan 07 2022 17:40:05   Seenivasan V
#       Module created
##############################################################################
# # Built-in imports
import time
import os
import threading
import wx
# Lip imports
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import numpy as np
from mpl_toolkits.axisartist.axislines import Subplot
from matplotlib.ticker import (MultipleLocator)
import csv
#from pylab import figure, show, legend, ylabel
# Own modules
from uiGlobals import *

XLIMIT = 10
XSPAN = 1
MAX_SAMPLE = 500
DEFAULT_SAMPLE = 100
DEFAULT_YLIMIT = 6
DEFAULT_Y2LIMIT = 0.1
DEFAULT_SPAN = 2



class VbusChart(wx.Frame):
    """
    A class Pltamps with init method

    The Pltamps navigate to Volts and Amps Panel in same Frame 
    
    """
    def __init__(self, parent, top):
        """
        VBUS plot chart  with in a init  method.
        Args:
            self: The self parameter is a reference to the current 
                instance of the class,and is used to access variables
                that belongs to the class.
                parent: Pointer to a parent window.
                top: creates an object
            Returns:
                None
        """
        wx.Frame.__init__(self, parent = None, title = "USB VBUS VI Chart Plot",
                           size = (680, 380) ,  
                           style= wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
        
        self.SetBackgroundColour("white")
        self.panel = wx.Panel(self)

        self.top_vbox = wx.BoxSizer(wx.VERTICAL)
        self.graph_vbox = wx.BoxSizer(wx.VERTICAL)
        self.graph_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.top = top
                
        self.figure = Figure(figsize=(6, 2))
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.ax = Subplot(self.figure, 111)
        
        self.ax = self.figure.add_axes([0.130,0.22,0.72 ,0.68])
        
        self.st_xlim = wx.StaticText(self.panel, -1, "X_Width", size  = (-1,-1))
        self.tc_xlim = wx.TextCtrl(self.panel, -1, size=(50,-1), 
                                            style = wx.TE_CENTRE |
                                            wx.TE_PROCESS_ENTER,
                                            validator=NumericValidator())

        self.tc_xlim.SetMaxLength(3)
        
        self.btnSet = wx.Button(self.panel, -1, "Set", size =  (50,-1))
        self.btnPause = wx.Button(self.panel, -1, "Pause", size =  (70,-1))
        self.btnLoad = wx.Button(self.panel, -1, 'Load', size =  (50,-1))
        self.btnSave = wx.Button(self.panel, -1, 'Save', size =  (50,-1))

        # Init variables for Chart
        self.xd = []
        self.yd = []
        self.y2d = []
        self.ylim = DEFAULT_YLIMIT
        self.y2lim = DEFAULT_Y2LIMIT
        
        self.maxsamp = DEFAULT_SAMPLE
        
        # Create Y axis for Current at Right side of the Chart
        self.ax2 = self.ax.twinx()
        self.ax2.set_ylabel('Current (A)', color='tab:blue')

        self.cal_max_samp()

        self.tc_xlim.SetValue(str(int(self.maxsamp/10)))
        
        self.graph_hbox.Add(self.canvas, 0, wx.ALL|wx.CENTER, 5)

        self.graph_vbox.Add(self.graph_hbox, 0, wx.ALL|wx.CENTER, 10)
        
        self.hbox_btn = wx.BoxSizer(wx.HORIZONTAL)

        self.hbox_btn.Add(self.st_xlim, flag=wx.ALIGN_CENTER_VERTICAL | 
                            wx.LEFT , border=5)
        self.hbox_btn.Add(self.tc_xlim, flag=wx.ALIGN_CENTER_VERTICAL | 
                            wx.LEFT , border=5)
        self.hbox_btn.Add(self.btnSet, flag=wx.ALIGN_CENTER_VERTICAL | 
                            wx.LEFT , border=5)
        
        self.hbox_btn.Add(self.btnPause, flag=wx.ALIGN_CENTER_VERTICAL | 
                            wx.LEFT , border=35)
        self.hbox_btn.Add(self.btnLoad, flag=wx.ALIGN_CENTER_VERTICAL | 
                            wx.LEFT , border=5)
        self.hbox_btn.Add(self.btnSave, flag=wx.ALIGN_CENTER_VERTICAL | 
                            wx.LEFT , border=5)

        self.top_vbox.Add(self.graph_vbox,0, wx.ALL|wx.CENTER, 5)
        self.top_vbox.Add(self.hbox_btn, 0, wx.ALL|wx.CENTER, 10)

        self.panel.SetSizer(self.top_vbox)
        self.Centre()
        self.panel.Fit()

        # Timer for Data update
        self.timer_ud = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.DataTimer, self.timer_ud)
        
        # Timer for Chart update
        self.timer_uc = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.ChartTimer, self.timer_uc)
        
        self.btnLoad.Bind(wx.EVT_BUTTON, self.OnLoad)
        self.btnSave.Bind(wx.EVT_BUTTON, self.OnSave)
        self.btnPause.Bind(wx.EVT_BUTTON, self.OnPause)
        self.btnSet.Bind(wx.EVT_BUTTON, self.OnSet)
        
        self.Bind(wx.EVT_CLOSE, self.OnClose) 

        self.run_flg = True

        self.timedf = []
        self.voltdf = []
        self.ampdf = []

        self.timer_ud.Start(98)
        self.timer_uc.Start(250)
        
    
    def DataTimer(self, e):
        threading.Thread(target=self.DataThread).run()
        self.timer_ud.Start()

    def ChartTimer(self, e):
        threading.Thread(target=self.ChartThread).run()
        self.timer_uc.Start()

    def OnLoad(self, e):
        """
        Loading the data in to a plot chart
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on Load button.
        Returns:
            None
        """
        self.run_flg = False
        
        del self.timedf[:]
        del self.voltdf[:]
        del self.ampdf[:]
        
        self.ax.clear()
        self.ax2.clear()

        self.print_chart_lables()
        self.load_file()
        self.btnPause.SetLabel("Resume")

    def OnSave(self, e):
        """
        Save the Chart data for volts and amps,
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on Save button.
        Returns:
            None
        """
        self.save_file()
     
    def OnPause(self, e):
        """
        The Running Plot activity will be paused for a moment.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on pause button.
        Returns:
            None
        """
        if self.run_flg:
            self.run_flg = False
            self.btnPause.SetLabel('Resume')
        else:
            self.run_flg = True
            self.btnPause.SetLabel('Pause')
        
    def OnSet(self, e):
        """
        set the samples which are given the samples.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on set button.
        Returns:
            None
        """
        self.run_flg = False
        xmax = self.tc_xlim.GetValue()
        if int(xmax) > MAX_SAMPLE:
            xmax = str(MAX_SAMPLE)
            self.tc_xlim.SetValue(str(MAX_SAMPLE))

        self.maxsamp = int(xmax) * 10
        del self.xd[:]
        del self.yd[:]
        del self.y2d[:]

        self.cal_max_samp()
        
        self.ax.clear()
        self.ax2.clear()
        self.ax.grid(True, which='both')
        self.run_flg = True

    def cal_max_samp(self):
        """
        calculate max samples
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        if self.maxsamp >= 200:
            self.xspan = int(self.maxsamp/100)
        elif self.maxsamp >= 100:
            self.xspan = int(self.maxsamp/50)
        else: # self.maxsamp < 100:
            self.xspan = 1

    def DataThread(self):
        # if self.run_flg:
        self.push_data()


    def push_data(self):
        """
        the particular data will pushed into a buffer.
        Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        Returns: 
        None
        """    
        voltin = self.top.vdata
        ampsin = self.top.adata

        if(voltin == None):
            voltin = 0
        if(ampsin == None):
            ampsin = 0

        xlen = len(self.xd)
        if(xlen >= self.maxsamp):
            self.xd.pop(0)
            self.yd.pop(0)
            self.y2d.pop(0)
    
        if(len(self.xd) == 0):
            pd = 0
        else:
            pd = self.xd[-1] + 0.1

        #self.xd.append(round(pd+0.1, 2)) # after point two digits only printed
        self.xd.append(round(pd, 2))
        self.yd.append(voltin)
        self.y2d.append(ampsin)

        if voltin > self.ylim:
            self.ylim = voltin + 1
    
        if ampsin > self.y2lim:
            self.y2lim = ampsin + 0.5
     
    def print_chart_lables(self):
        """
        here chart labels (X and Y)axes, title name. facecolor print on chart.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on voltas and Amps start.
        Returns:
            None
        """
        self.ax.set_xlabel(r"Time (sec)",fontsize=8 )
        self.ax.set_ylabel(r"Volts (V)", fontsize=8, color='tab:red')
        self.ax.set_title("VBUS V/I Plot", fontsize=10)
        self.ax2.set_ylabel('Amps (A)', fontsize=8, color='tab:green')
        self.ax.set_facecolor('black')

    def ChartThread(self):
        if self.run_flg:
            if(len(self.xd) > 1):
                self.update_chart()

    def update_chart(self): # Data receive here voltin 
        """
        OnPlotting volts and amps data is chart updated.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on voltas and Amps start.
        Returns:
            None
        """
        self.ax.clear()
        self.ax2.clear()

        self.print_chart_lables()
        
        self.ax.set_ylim(0.0, self.ylim)
        self.ax2.set_ylim(0.0, self.y2lim)

        self.ax.set_xlim(self.xd[0], self.xd[-1])

        if(len(self.xd) >= self.maxsamp):
            major_xticks = np.arange(self.xd[0], self.xd[-1]+1, self.xspan)
            minor_xticks = np.arange(self.xd[0], self.xd[-1]+1, self.xspan/2)
        else:
            major_xticks = np.arange(self.xd[0], (self.maxsamp+10)/10,self.xspan)
            minor_xticks = np.arange(self.xd[0], (self.maxsamp+10)/10, 
                                                    self.xspan/2)

        major_yticks = np.arange(0, self.ylim, self.ylim/5)
        minor_yticks = np.arange(0, self.ylim, self.ylim/10)

        self.ax.set_xticks(major_xticks)
        self.ax.set_xticks(minor_xticks, minor=True)
        self.ax.set_yticks(major_yticks)
        self.ax.set_yticks(minor_yticks, minor=True)

        major_y2ticks = np.arange(0, self.y2lim, self.y2lim/5)
        minor_y2ticks = np.arange(0, self.y2lim, self.y2lim/10)

        self.ax2.set_yticks(major_y2ticks)
        self.ax2.set_yticks(minor_y2ticks, minor=True)

        self.ax.grid(which='major', linestyle = '-', 
                                    linewidth = '0.5', color = 'grey')
        self.ax2.grid(which='minor', linestyle = ':', 
                                    linewidth = '0.5', color = 'grey')

        self.ax.plot(self.xd, self.yd, linewidth = '1.5', color = 'red')
        self.ax2.plot(self.xd, self.y2d, linewidth = '1.5', color = 'green')
        self.canvas.draw()
 
    def OnClose(self, event):
        """
        closing menu frame.
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling for closing frame
        Returns:
            None
        """
        
        self.top.vgraph = False
        self.top.agraph = False
        self.timer_ud.Stop()
        self.timer_uc.Stop()
        self.Destroy()

    def save_file(self):
        """
        save the file into a selecting folder.

        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            None
        """
        # Save a file
        self.dirname=""
        dlg = wx.FileDialog(self, "Save as", self.dirname, "", "*.csv", 
                            wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        if dlg.ShowModal() == wx.ID_OK:
            wx.BeginBusyCursor()

            dirname = dlg.GetDirectory()
            filename = os.path.join(dirname, dlg.GetFilename())

            if (os.path.isdir(dirname) and os.access(dirname, os.X_OK | 
                                                    os.W_OK)):
                self.dirname = dirname
                rows = zip(self.xd, self.yd, self.y2d)
                with open(filename, 'w', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    fields = ['Time(Sec)', 'Volts', 'Amps']
                    csvwriter.writerow(fields)
                    for row in rows:
                        csvwriter.writerow(row)
            dlg.Destroy()

        if (wx.IsBusy()):
            wx.EndBusyCursor()
        return

    def plot_csv(self):
        """
        volts and amps data plotting in a Chart throgh csv file.
        Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        Returns: 
        return- success for file save in directiry
        """
        cvmin = min(self.voltdf)
        cvmax = max(self.voltdf)

        camin = min(self.ampdf)
        camax = max(self.ampdf)

        self.ax.set_ylim(0, cvmax+1)
        self.ax2.set_ylim(0, camax+0.05)

        xmin = min(self.timedf)
        xmax = max(self.timedf)

        xmin = int(xmin - 1)
        if(xmin < 0):
            xmin = 0
        
        xmax = int(xmax + 1)

        self.ax.set_xlim(xmin, xmax)

        self.ax.xaxis.set_minor_locator(MultipleLocator(1))
        major_xticks = np.arange(xmin, xmax, 2)
        minor_xticks = np.arange(xmin, xmax, 1)
        
        major_yticks = np.arange(cvmin, cvmax+1, (cvmax+1)/5)
        minor_yticks = np.arange(cvmin, cvmax+1, (cvmax+1)/10)

        major_y2ticks = np.arange(camin, camax+0.05, (camax+0.05)/5)
        minor_y2ticks = np.arange(camin, camax+0.05, (camax+0.05)/10)

        self.ax.set_xticks(major_xticks)
        self.ax.set_xticks(minor_xticks, minor=True)

        self.ax.set_yticks(major_yticks)
        self.ax.set_yticks(minor_yticks, minor=True)

        self.ax2.set_yticks(major_y2ticks)
        self.ax2.set_yticks(minor_y2ticks, minor=True)

        self.ax.grid(which='major', linestyle = '-', 
                                    linewidth = '0.5', color = 'grey')
        self.ax2.grid(which='minor', linestyle = ':', 
                                    linewidth = '0.5', color = 'grey')

        self.ax.plot(self.timedf, self.voltdf, linewidth = '1.5', color='red')
        self.ax2.plot(self.timedf, self.ampdf, linewidth = '1.5', color='green')

        self.canvas.draw()
 
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
        dlg = wx.FileDialog(self, "Load File", self.dirname, "", "*.csv", 
                                wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        
        pathname = dlg.GetPath()
        #print("File Path: ", pathname)
        try:
            with open(pathname, 'r') as csvfile:
                csvReader = csv.reader(csvfile)
                for row in csvReader:
                    try:
                        self.timedf.append(float(row[0]))
                        self.voltdf.append(float(row[1]))
                        self.ampdf.append(float(row[2]))
                    except:
                       pass
            self.plot_csv()
        except IOError:
            wx.LogError("Can not open file '%s', " % pathname)