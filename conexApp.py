#==========================================================================
# (c) 2020  MCCI Interconnect Solutions
#--------------------------------------------------------------------------
# Project : UI for 3141 and 3201 interface
# File    : conexApp.py
#--------------------------------------------------------------------------
#  Main program entry point
#==========================================================================

#==========================================================================
# IMPORTS
#==========================================================================

import os
import sys
import getopt
import time

import wx


class ceMainFrame(wx.Frame):
	def __init__(self, parent, title):
		super(ceMainFrame, self).__init__(parent, title=title)
		self.Centre()
		print(wx.version())



#=========================================================================================
# MAIN PROGRAM
#=========================================================================================
def run():
	myapp = wx.App()
	myWin = ceMainFrame(None, title="MCCI-ConEx")
	myWin.Show()
	myapp.MainLoop()