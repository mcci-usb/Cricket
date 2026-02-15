# -*- coding: utf-8 -*-
##############################################################################
#
# Module: vbusChart.py
#
# Description:
#     VBUS Voltage and Current Monitoring Chart Module.
#
#     This module provides a real-time graphical plotting interface
#     to monitor USB VBUS electrical parameters.
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
##############################################################################
# Built-in imports
import time
import os
import threading
import wx

# Lib imports
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import numpy as np
from mpl_toolkits.axisartist.axislines import Subplot
from matplotlib.ticker import (MultipleLocator)
import matplotlib.pyplot as plt
import csv

# Own modules
from uiGlobals import *

XLIMIT = 10
XSPAN = 1
MAX_SAMPLE = 1000
DEFAULT_SAMPLE = 100
DEFAULT_YLIMIT = 6
DEFAULT_Y2LIMIT = 6
DEFAULT_SPAN = 2

YSPAN = 5

##############################################################################
# Utilities
##############################################################################
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
                           size = (680, 520) ,  
                           style= wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
        
        self.SetBackgroundColour("white")

        # Get the absolute path of the current script's directory
        base = os.path.abspath(os.path.dirname(__file__))
        iconpath = os.path.abspath(os.path.join(base, os.pardir, os.pardir))
        icon_file_path = os.path.join(iconpath, "icons", IMG_ICON)
        icon = wx.Icon(icon_file_path)
        self.SetIcon(icon)
        self.panel = wx.Panel(self)

        self.top_vbox = wx.BoxSizer(wx.VERTICAL)
        self.graph_vbox = wx.BoxSizer(wx.VERTICAL)
        self.graph_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.zoom_hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.top = top
                
        self.figure = Figure(figsize=(6, 3))
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.ax = Subplot(self.figure, 111)
        
        self.ax = self.figure.add_axes([0.130,0.22,0.72 ,0.68])

        self.cb_volts = wx.CheckBox(self.panel, -1, "Volts", size = (-1, -1))
        self.cb_amps = wx.CheckBox(self.panel, -1, "Amps", size = (-1, -1))

        self.cb_volts.SetValue(True)
        self.cb_amps.SetValue(True)
        

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

        self.vmax = 0
        self.amax = 0
        self.vref = 4

        self.xzval = 3
        self.xsindex = 0
        self.shift_flg = False
        
        self.maxsamp = DEFAULT_SAMPLE

        self.ax2 = self.ax.twinx()

        self.cal_max_samp()

        self.tc_xlim.SetValue(str(int(self.maxsamp/10)))

        self.sld = wx.Slider(self.panel, value = 4, minValue = 0, maxValue = 6,
                   style = wx.SL_VERTICAL) 
        
        self.graph_hbox.Add(self.sld, 1, wx.ALL|wx.CENTER, 0)
        self.graph_hbox.Add(self.canvas, 0, wx.ALL|wx.CENTER, 5)

        self.sldh1 = wx.Slider(self.panel,style = wx.SL_HORIZONTAL, value = 1, 
                               minValue = 0, maxValue = 100) 
        self.btnLeft = wx.Button(self.panel, -1, "<-", size =  (50,-1))
        self.btnMinus = wx.Button(self.panel, -1, "-", size =  (50,-1))
        self.btnRst = wx.Button(self.panel, -1, "Reset", size =  (70,-1))
        self.btnPlus = wx.Button(self.panel, -1, "+", size =  (50,-1))
        self.btnRight = wx.Button(self.panel, -1, "->", size =  (50,-1))

        self.zoom_hbox.Add(self.btnLeft, 0, wx.ALL|wx.CENTER, 0)
        self.zoom_hbox.Add(self.btnMinus, 0, wx.ALL|wx.CENTER, border=5)
        self.zoom_hbox.Add(self.btnRst, 0, wx.ALL|wx.CENTER, border=5)
        self.zoom_hbox.Add(self.btnPlus, 0, wx.ALL|wx.CENTER, border=5)
        self.zoom_hbox.Add(self.btnRight, 0, wx.ALL|wx.CENTER, 0)
        
        self.graph_vbox.Add(self.sldh1, 0, wx.ALL|wx.CENTER, 0)
        self.graph_vbox.Add(self.graph_hbox, 0, wx.ALL|wx.CENTER, 0)
        self.graph_vbox.Add(self.zoom_hbox, 0, wx.ALL|wx.CENTER, 0)
        
        self.hbox_btn = wx.BoxSizer(wx.HORIZONTAL)
        
        self.hbox_btn.Add(self.cb_volts, flag=wx.ALIGN_CENTER_VERTICAL | 
                            wx.LEFT , border=5)
        self.hbox_btn.Add(self.cb_amps, flag=wx.ALIGN_CENTER_VERTICAL | 
                            wx.LEFT , border=5)
        self.hbox_btn.Add(self.st_xlim, flag=wx.ALIGN_CENTER_VERTICAL | 
                            wx.LEFT , border=15)
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

        self.panel.SetSizerAndFit(self.top_vbox)
        self.Centre()

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

        self.cb_volts.Bind(wx.EVT_CHECKBOX, self.checkVolts)
        self.cb_amps.Bind(wx.EVT_CHECKBOX, self.checkAmps)
        self.sld.Bind(wx.EVT_SCROLL, self.OnSlideScroll)
        self.sldh1.Bind(wx.EVT_SCROLL, self.OnSlideMove)
        
        self.btnMinus.Bind(wx.EVT_BUTTON, self.OnXUnZoom)
        self.btnPlus.Bind(wx.EVT_BUTTON, self.OnXZoom)
        self.btnRst.Bind(wx.EVT_BUTTON, self.OnXReset)
        self.btnLeft.Bind(wx.EVT_BUTTON, self.OnLeftMove)
        self.btnRight.Bind(wx.EVT_BUTTON, self.OnRightMove)
        
        self.run_flg = True
        self.load_flg = False
        self.loadheaders = []

        self.timedf = []
        self.voltdf = []
        self.ampdf = []

        self.vchart = True
        self.achart = True

        self.timer_ud.Start(98)
        self.timer_uc.Start(250)

    def OnSlideScroll(self, evt):
        """
        Handle vertical slider scroll events to adjust chart voltage reference.

        This method is triggered when the vertical scale slider is moved.
        It updates the voltage reference scaling factor used for plotting
        the VBUS voltage waveform in the chart.

        Args:
            self: Reference to the current instance of the class.
            evt : wx.Event
                  Slider scroll event object generated by wxPython.

        Returns:
            None

        """
        sval = self.sld.GetValue()
        self.vref = 7 - sval
        if self.run_flg:
            self.update_chart()
        elif self.load_flg:
            self.plot_csv()

    def OnXUnZoom(self, evt):
        """
        Handle X-Axis Unzoom action for loaded chart data.

        This method is triggered when the user clicks the
        X-Axis Unzoom control button. It increases the zoom
        level of the X-axis when viewing previously loaded
        CSV data.
        Args:
            self: Reference to the current instance of the class.
            evt : wx.Event
                  Button click event object generated by wxPython.

        Returns:
            None
        """
        if self.load_flg:
            self.xzval = self.xzval + 1
            if self.xzval > 10:
                self.xzval = 10
            self.plot_csv()

    def OnXZoom(self, evt):
        """
        Handle X-Axis Zoom action for loaded chart data.

        This method is triggered when the user clicks the
        X-Axis Zoom control button. It decreases the zoom
        level of the X-axis when viewing previously loaded
        CSV data.

        The zoom value is reduced step-by-step to narrow
        the visible time range, allowing users to view
        data in a more detailed (zoomed-in) format.
        Args:
            self: Reference to the current instance of the class.
            evt : wx.Event
                  Button click event object generated by wxPython.

        Returns:
            None

        Raises:
            None
        """

        if self.load_flg:
            self.xzval = self.xzval - 1
            if self.xzval < 1:
                self.xzval = 1
            self.plot_csv()

    def OnLeftMove(self, evt):
        """
        Handle Left Navigation movement on the X-Axis for loaded chart data.

        This method is triggered when the user clicks the
        Left Move button in the chart zoom/navigation controls.

        It shifts the visible plotting window towards the
        left side along the X-axis timeline when CSV data
        is loaded.
        Args:
            self: Reference to the current instance of the class.
            evt : wx.Event
                  Button click event object generated by wxPython.

        Returns:
            None

        Raises:
            None
        """

        if self.load_flg:
            self.xsindex = self.xsindex - 1
            if self.xsindex < 0:
                self.xsindex = 0
            self.shift_flg = True
            self.plot_csv()
            self.sldh1.SetValue(self.xsindex)

    def OnRightMove(self, evt):
        """
        Handle Right Navigation movement on the X-Axis for loaded chart data.

        This method is triggered when the user clicks the
        Right Move button in the chart zoom/navigation controls.

        It shifts the visible plotting window towards the
        right side along the X-axis timeline when CSV data
        is loaded.

        The movement updates the starting index position
        used for chart rendering. Boundary validation is
        applied to prevent index values from exceeding
        the maximum allowed range.

        After updating the index position:

            • Shift flag is enabled
            • Chart is re-plotted
            • Horizontal slider position is synchronized

        Args:
            self: Reference to the current instance of the class.
            evt : wx.Event
                  Button click event object generated by wxPython.

        Returns:
            None

        Raises:
            None
        """
        if self.load_flg:
            self.xsindex = self.xsindex + 1
            if self.xsindex > 100:
                self.xsindex = 100
            self.shift_flg = True
            self.plot_csv()
            self.sldh1.SetValue(self.xsindex)

    def OnSlideMove(self, evt):
        """
        Handle Horizontal Slider movement for X-Axis navigation.

        This method is triggered when the user moves the
        horizontal slider control used for navigating
        through loaded CSV chart data.

        It updates the X-axis starting index based on the
        slider position, enabling smooth left/right
        navigation across the plotted dataset.

        Once the slider value is captured:

            • X-axis shift index is updated
            • Shift flag is enabled
            • Chart is re-plotted with the new view range

        This functionality is active only when CSV data
        is loaded into the chart.

        Args:
            self: Reference to the current instance of the class.
            evt : wx.Event
                  Slider movement event object generated by wxPython.

        Returns:
            None

        Raises:
            None
        """
        if self.load_flg:
            self.xsindex = self.sldh1.GetValue()
            self.shift_flg = True
            self.plot_csv()

    def OnXReset(self, evt):
        """
        Reset X-Axis Zoom and Position to Default View.

        This method is triggered when the user clicks the
        "Reset" button in the chart zoom controls.

        It restores the X-axis visualization to its
        original default settings by:

            • Resetting zoom level to default value
            • Resetting horizontal shift index
            • Re-plotting the chart data

        This ensures the full dataset becomes visible again
        from the starting position without any zoom or shift
        adjustments applied.

        Args:
            self: Reference to the current instance of the class.
            evt : wx.Event
                  Button click event object generated by wxPython.

        Returns:
            None

        Raises:
            None
        """
        self.xzval = 3
        self.xsindex = 0
        self.plot_csv()
 
    def clearax(self):
        """
        clear the ax (X axis line)
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.ax.clear()

    def DataTimer(self, e):
        """
        Loading the Volt and Current data in to buffer
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e: event handling on Load button.
        Returns:
            None
        """        
        threading.Thread(target=self.DataThread).run()
        self.timer_ud.Start()

    def ChartTimer(self, e):
        """
        Updating the Volt and Current data in to the Chart
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            e: event handling on Load button.
        Returns:
            None
        """ 
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

        self.xzval = 3
        self.xsindex = 0
        
        self.ax.clear()
        self.print_chart_lables()
        self.load_file()
        self.btnPause.SetLabel("Resume")
        self.load_flg = True

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
            self.load_flg = False
        
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
        """
        Move the volt and current data to the buffer.
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            None
        """ 
        self.push_data()

    def push_data(self):
        """
        Move the volt and current data to the buffer.
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

        self.xd.append(round(pd, 2))
        self.yd.append(voltin)
        self.y2d.append(ampsin)

        if voltin > self.vmax:
            self.vmax = voltin

        if ampsin > self.amax:
            self.amax = ampsin

    def print_chart_lables(self):
        """
        Configure and Display Chart Labels, Titles, and Axis Settings.

        This method sets up the chart’s visual labeling elements
        based on the selected display mode for Voltage and Current.

        It dynamically configures:

            • X-axis label (Time in seconds)
            • Y-axis label(s) for Volts and/or Amps
            • Axis positions (left / right)
            • Chart title
            • Reference zero line (when both plots enabled)
            • Background styling
            Args:
            self: Reference to the current instance of the class.

        Returns:
            None

        Raises:
            None
        """
        self.ax.set_xlabel("Time (sec)", fontsize=8)
        self.ax.set_facecolor('black')

        if self.vchart and self.achart:
            # LEFT axis (Volts)
            self.ax.set_ylabel("Volts (V)", fontsize=8, color='red')
            self.ax.yaxis.set_label_position("left")
            self.ax.yaxis.tick_left()

            # RIGHT axis (Amps)
            self.ax2.set_ylabel("Amps (A)", fontsize=8, color='green')
            self.ax2.yaxis.set_label_position("right")
            self.ax2.yaxis.tick_right()

            self.ax.set_title("VBUS V/I Plot", fontsize=10)

            # Only ONE zero reference line
            self.ax.axhline(0, color='yellow', linestyle='--', linewidth=0.5)

        elif self.vchart:
            self.ax.set_ylabel("Volts (V)", fontsize=8, color='red')
            self.ax.yaxis.set_label_position("left")
            self.ax.yaxis.tick_left()
            self.ax.set_title("VBUS Volt Plot", fontsize=10)

        elif self.achart:
            self.ax.set_ylabel("Amps (A)", fontsize=8, color='green')
            self.ax.yaxis.set_label_position("left")
            self.ax.yaxis.tick_left()
            self.ax.set_title("VBUS Amp Plot", fontsize=10)
  
    def ChartThread(self):
        """
        Plot volt and amp data in the Chart
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        if self.run_flg:
            if(len(self.xd) > 1):
                self.update_chart()

    def checkAmps(self, evt):
        """
        Checking the Amps event for using Check Box
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on set Check box.
        Returns:
            None
        """
        self.clearChart()

        if self.cb_amps.GetValue() == True:
            self.achart = True
        else:
            self.achart = False

        if self.run_flg:
            self.update_chart()
        elif self.load_flg:
            self.print_chart_lables()
            self.plot_csv()
            
    def checkVolts(self, e):
        """
        Checking the Volts event for using Check Box
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
            event: event handling on set Check box.
        Returns:
            None
        """
        self.clearChart()
        if self.cb_volts.GetValue() == True:
            self.vchart = True
        else:
            self.vchart = False

        if self.run_flg:
            self.update_chart()
        elif self.load_flg:
            self.print_chart_lables()
            self.plot_csv()
            
    def update_chart(self):
        """
        update the chart based on check box event, 
        single check box Volts or Amps,
        Checking for Both VandI 
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.clearChart()

        if self.vchart and self.achart:
            self.updateBoth()
        elif self.vchart:
            self.updateSingle("volt")
        elif self.achart:
            self.updateSingle("amp")
        else:
            self.clearChart()

    def updateBoth(self):
        """
        Plot volt and amp data in the Chart
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.ax.clear()
        self.ax2.clear()

        self.print_chart_lables()
                
        self.ax.set_xlim(self.xd[0], self.xd[-1])
        self.ax.yaxis.set_visible(True)
        self.ax2.yaxis.set_visible(True)

        if(len(self.xd) >= self.maxsamp):
            major_xticks = np.arange(self.xd[0], self.xd[-1]+1, self.xspan/2)
            minor_xticks = np.arange(self.xd[0], self.xd[-1]+1, self.xspan/2)
        else:
            major_xticks = np.arange(self.xd[0], (self.maxsamp+12)/10,self.xspan/2)
            minor_xticks = np.arange(self.xd[0], (self.maxsamp+12)/10, self.xspan/2)

        self.getvoltrange(self.vmax)
        self.getamprange(True, self.amax)

        self.ax.set_xticks(major_xticks)
        self.ax.set_xticks(minor_xticks, minor=True)

        self.ax.grid(which='major', linestyle = '-', 
                                    linewidth = '0.5', color = 'grey')
        self.ax2.grid(which='minor', linestyle = ':', 
                                    linewidth = '0.5', color = 'grey')

        self.ax.plot(self.xd, self.yd, linewidth = '1.5', color = 'red')
        self.ax2.plot(self.xd, self.y2d, linewidth = '1.5', color = 'green')
        
        self.canvas.draw()

    def getvoltrange(self, vmax):
        """
        Calculate and Configure Voltage Axis Range for Chart Display.

        This method dynamically determines the Y-axis range and tick
        intervals for the Voltage plot based on the maximum voltage
        value received.

        The scaling logic ensures:

            • Proper visualization of voltage variations
            • Symmetrical display around zero when required
            • Adaptive tick spacing for readability
            • Auto adjustment based on reference voltage (vref)

        Range calculation process:

            1. Compute runtime unit using reference offset.
            2. Identify expansion unit (eunit) based on vmax.
            3. Derive high range and low range limits.
            4. Apply calculated limits to Y-axis.
            5. Generate major and minor tick intervals.

        Args:
            self: Reference to the current instance of the class.
            vmax (float): Maximum voltage value observed in data.

        Returns:
            None

        Raises:
            None
        """
        lrange = 0  # always zero
        tunit = 8
        runit = tunit - self.vref
        hrange = runit

        for i in range(1, 60):
            if (i * runit) > vmax:
                eunit = i
                break

        hrange = (eunit * runit) + eunit
        lrange = 0 - (eunit * self.vref)

        self.ax.set_ylim(lrange, hrange - eunit)
        
        major_yticks = np.arange(lrange, hrange, eunit)
        minor_yticks = np.arange(lrange, hrange, eunit) 

        self.ax.set_yticks(major_yticks)
        self.ax.set_yticks(minor_yticks, minor=True)

    def getamprange(self, bothva, amax):
        """
        Calculate and Configure Current (Amps) Axis Range for Chart Display.

        This method dynamically determines the Y-axis scaling and tick
        intervals for the Current plot based on the maximum current value
        detected in the dataset.

        The scaling mechanism ensures:

            • Proper visualization of current fluctuations
            • Symmetrical scaling around zero
            • Adaptive range expansion based on peak current
            • Separate handling for single-axis or dual-axis plotting

        Functional workflow:

            1. Initialize default axis range values.
            2. Determine expansion unit (eunit) from maximum current.
            3. Calculate high and low axis limits.
            4. Configure tick intervals for visualization.
            5. Apply scaling to primary or secondary axis.

        Args:
            self: Reference to the current instance of the class.
            bothva (bool):
                Flag indicating plotting mode.
                    • True  → Dual axis plotting (Volt + Amp).
                    • False → Single axis plotting (Amp only).
            amax (float):
                Maximum current value observed in the dataset.

        Returns:
            None

        Raises:
            None
        """
        lrange = 0  # always zero
        hrange = 4
        eunit = 1
        uvalue = 4
        for i in range(1, 15):
            if (i * uvalue) > amax:
                hrange = i * uvalue
                eunit = i
                break

        lrange = 0 - hrange
        hrange = hrange + eunit

        major_yticks = np.arange(lrange, hrange, eunit)
        minor_yticks = np.arange(lrange, hrange, eunit) 

        if bothva == False:
            self.ax.set_ylim(lrange, hrange - eunit)
            self.ax.set_yticks(major_yticks)
            self.ax.set_yticks(minor_yticks, minor=True)
        else:
            self.ax2.set_ylim(lrange, hrange - eunit)
            self.ax2.set_yticks(major_yticks)
            self.ax2.set_yticks(minor_yticks, minor=True)
            
    def updateSingle(self, param):
        """
        update the chart single one Volts and Amps.
        passing the parameters for volts or amps
        single check box Volts or Amps,
        Checking for Both VandI 
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """ 
        self.ax.clear()
        self.print_chart_lables()
        
        if self.vchart:
            # clear the second subplot 
            self.ax2.clear()
            self.ax2.yaxis.set_visible(False)
        else:
            self.ax2.clear()
            self.ax2.yaxis.set_visible(False)
        
        self.ax.set_xlim(self.xd[0], self.xd[-1])

        if(len(self.xd) >= self.maxsamp):
            major_xticks = np.arange(self.xd[0], self.xd[-1]+1, self.xspan/2) #MAIN
            minor_xticks = np.arange(self.xd[0], self.xd[-1]+1, self.xspan/2) #MAIN
        else:
            major_xticks = np.arange(self.xd[0], (self.maxsamp+12)/10,self.xspan/2)
            minor_xticks = np.arange(self.xd[0], (self.maxsamp+12)/10, self.xspan/2)
                
        if self.vchart:
            self.getvoltrange(self.vmax)
        else:
            self.getamprange(False, self.amax)
            
        self.ax.set_xticks(major_xticks)
        self.ax.set_xticks(minor_xticks, minor=True)


        self.ax.grid(which='major', linestyle = '-', 
                                    linewidth = '0.5', color = 'grey')
       
        if(param == "volt"):
            self.ax.plot(self.xd, self.yd, linewidth = '1.5', color = 'red', label = 'line')
        else:
            self.ax.plot(self.xd, self.y2d, linewidth = '1.5', color = 'green')

        self.canvas.draw() 

    def clearChart(self):
        """
        clear the  chart
        Args:
            self: The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns:
            None
        """
        self.ax.clear()
        self.ax2.clear()        

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
        if self.cb_amps.GetValue() == True and \
           self.cb_volts.GetValue() == True:
            self.save_file_va()
        
        else:
            self.save_file_vora()

    def save_file_vora(self):
        """
        save the file into a selecting folder.
        Args:
            self:The self parameter is a reference to the current 
            instance of the class,and is used to access variables
            that belongs to the class.
        Returns: 
            None
        """
        volt_flg = False
        volt_flg = self.cb_volts.GetValue()
                              
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
                rows = None
                if volt_flg:
                    rows = zip(self.xd, self.yd)
                else:
                    rows = zip(self.xd, self.y2d)
                with open(filename, 'w', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    fields = None
                    if volt_flg:
                        fields = ['Time(Sec)', 'Volts']
                    else:
                        fields = ['Time(Sec)', 'Amps']
                    csvwriter.writerow(fields)
                    for row in rows:
                        csvwriter.writerow(row)
            dlg.Destroy()

        if (wx.IsBusy()):
            wx.EndBusyCursor()
        return
  
    def save_file_va(self):
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
        if 'Volts' in self.loadheaders and \
            'Amps' in self.loadheaders:
            if self.achart and self.vchart:
                self.plot_csv_va()
            elif self.achart:
                self.plot_csv_vora('Amps')
            elif self.vchart:
                self.plot_csv_vora('Volts')
        elif 'Volts' in self.loadheaders and \
               self.vchart:
                self.plot_csv_vora('Volts')
        elif 'Amps' in self.loadheaders and \
                self.achart:
                self.plot_csv_vora('Amps')
                 

    def plot_csv_vora(self, param):
        """
        volts and amps data plotting in a Chart throgh csv file.
        Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        Returns: 
        return- success for file save in directiry
        """
        self.ax.yaxis.set_visible(True)
       
        if param == 'Volts':
            self.ax2.yaxis.set_visible(False)
            self.getvoltrange(max(self.voltdf))
        else:
            # convert negative values as positive
            pamp = []
            for i in range (0, len(self.ampdf)):
                pamp.append(abs(self.ampdf[i]))

            self.ax2.yaxis.set_visible(False)
            self.getamprange(False, max(pamp))

        self.calculatexticks()

        self.ax.grid(which='major', linestyle = '-', 
                                    linewidth = '0.5', color = 'grey')
        if param == 'Volts':
            self.ax2.yaxis.set_visible(False)
            self.ax.plot(self.timedf, self.voltdf, linewidth = '1.5', color='red')
            self.ax.plot(label = 'Volts',linewidth = '1.5', color='red')
            
        else:
            self.ax2.yaxis.set_visible(False)
            self.ax.plot(self.timedf, self.ampdf, linewidth = '1.5', color='green')
            self.ax.plot(label = 'mA',linewidth = '1.5', color='green')
        self.canvas.draw()

    def calculatexticks(self):
        """
        Calculate and Configure X-Axis Tick Marks for Chart Visualization.

        This method dynamically computes the X-axis scaling, tick intervals,
        and visible plotting range based on the loaded time-series dataset.

        It supports zooming and horizontal shifting of the chart view while
        maintaining proper tick alignment for readability.
        Args:
            self: Reference to the current instance of the class.
                  Provides access to chart buffers, zoom controls,
                  and axis configuration parameters.

        Returns:
            None

        Raises:
            None
        """
        xzoom = [0.1, 0.25, 0.5, 1, 2, 4, 8, 10, 20, 30, 40]
        xunit = xzoom[self.xzval]
       
        xmin = min(self.timedf)
        xmax = max(self.timedf)
        
        xmin = round(xmin)
        if xmin > 1:
            xmin = xmin - 1

        xmax = round(xmax) + 1
        diff = xmax - xmin
        
        lrange = xmin
        if self.shift_flg:
            lrange = xmin + ((self.xsindex/10) * xunit)
            self.shift_flg = False
        
        hrange = lrange + (xunit * 10)

        self.ax.set_xlim(lrange, hrange)
        self.ax.xaxis.set_minor_locator(MultipleLocator(1))
        
        major_xticks = np.arange(lrange, hrange, xunit)   
        minor_xticks = np.arange(lrange, hrange, xunit/10)

        self.ax.set_xticks(major_xticks)
        self.ax.set_xticks(minor_xticks, minor=True)

    def plot_csv_va(self):
        """
        volts and amps data plotting in a Chart throgh csv file.
        Args:
        self:The self parameter is a reference to the current 
        instance of the class,and is used to access variables
        that belongs to the class.
        Returns: 
        return- success for file save in directiry
        """
        self.ax.yaxis.set_visible(True)
        self.ax2.yaxis.set_visible(True)

        self.calculatexticks()

        self.getvoltrange(max(self.voltdf))

        # convert negative values 
        pamp = []
        for i in range (0, len(self.ampdf)):
            pamp.append(abs(self.ampdf[i]))
        self.getamprange(True, max(pamp))

        self.ax.grid(which='major', linestyle = '-', 
                                    linewidth = '0.5', color = 'grey')
        self.ax.plot(self.timedf, self.voltdf, linewidth = '1.5', color='red')
        self.ax.plot(label = 'Volts',linewidth = '1.5', color='red')

        self.ax2.grid(which='minor', linestyle = ':', 
                                    linewidth = '0.5', color = 'grey')
        self.ax2.plot(self.timedf, self.ampdf, linewidth = '1.5', color='green')
        self.ax2.plot(label = 'Amps', linewidth = '1.5', color='green')
        self.canvas.draw()
    
    def load_file(self):
        """
        Load CSV File for VBUS Chart Data Visualization.

        This method opens a file selection dialog that allows the user
        to browse and select a CSV file containing Voltage and/or Current
        time-series data for plotting in the VBUS chart.
        Args:
            self: Reference to the current instance of the class.
                  Provides access to UI components, chart buffers,
                  and file handling utilities.

        Returns:
            None

        Raises:
            None
        """
        self.dirname=""
        dlg = wx.FileDialog(self, "Load File", self.dirname, "", "*.csv", 
                                wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        
        pathname = dlg.GetPath()
        self.loadheaders = None
        try:
            with open(pathname, "r") as file:
            # Create a CSV reader object
                csv_reader = csv.reader(file)
                # Read the first row, which contains the headers
                self.loadheaders = next(csv_reader)
        except IOError:
            wx.LogError("Can not open file '%s', " % pathname)
        try:
            with open(pathname, 'r') as csvfile:
                csvReader = csv.reader(csvfile)
                for row in csvReader:
                    try:
                        idx = 0
                        self.timedf.append(float(row[idx]))
                        if 'Volts' in self.loadheaders:
                            self.ax2.yaxis.set_visible(False)
                            idx = idx + 1
                            self.voltdf.append(float(row[idx]))
                        if 'Amps' in self.loadheaders:
                            self.ax2.yaxis.set_visible(False)
                            idx = idx + 1
                            self.ampdf.append(float(row[idx]))
                    except:
                       pass
            self.plot_csv()
        except IOError:
            wx.LogError("Can not open file '%s', " % pathname)