from matplotlib.pyplot import switch_backend
import wx

from wx.lib.scrolledpanel import ScrolledPanel

from dev2101Window import Dev2101Window
from dev3141Window import Dev3141Window
from dev3201Window import Dev3201Window
from dev2301Window import Dev2301Window

class LeftPanel(ScrolledPanel):
    def __init__(self, parent):
        super(LeftPanel, self).__init__(parent)

        self.SetBackgroundColour('White')

        self.SetupScrolling()

        self.parent = parent

        # self.SetSize((300, 720))

        self.SetMinSize((320, 720))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.swobj = []

        # self.sw1 = Dev3201Window(self, parent)
        # self.sw2 = Dev3201Window(self, parent)
        # self.sw3 = Dev3201Window(self, parent)
        # self.sw4 = Dev3201Window(self, parent)
        # self.sw5 = Dev3201Window(self, parent)

        # self.main_sizer.Add(self.sw1, 0, wx.ALL, 5)
        # self.main_sizer.Add(self.sw2, 0, wx.ALL, 5)
        # self.main_sizer.Add(self.sw3, 0, wx.ALL, 5)
        # self.main_sizer.Add(self.sw4, 0, wx.ALL, 5)
        # self.main_sizer.Add(self.sw5, 0, wx.ALL, 5)



        # for number in range(5):
        #     # btn = wx.Button(self, label='Button {}'.format(number))
        #     main_sizer.Add(Dev3201Window, 0, wx.ALL, 5)

        self.SetSizer(self.main_sizer)

        # self.SetSizer(self.vb_outer)
        
        # Setting Layouts
        self.SetAutoLayout(True)
        self.main_sizer.Fit(self)
        self.Layout()

    def add_switches(self, swlist):
        print("I am Left Panel, now adding switches one by one")
        nswlist = []
        for idx in range(len(swlist)):
            nswlist.append(swlist[idx].split('(')[0])
        
        # for swobj in self.swobj:
        #     self.main_sizer.
        if(len(self.swobj) > 0):
            self.main_sizer.Clear(True)
            
        self.swobj.clear()

        for idx in range(len(nswlist)):
            if(nswlist[idx] == '3141'):
                self.swobj.append(Dev3141Window(self, self.parent))
            elif(nswlist[idx] == '3201'):
                self.swobj.append(Dev3201Window(self, self.parent))
            elif(nswlist[idx] == '2101'):
                self.swobj.append(Dev2101Window(self, self.parent))
            elif(nswlist[idx] == '2301'):
                self.swobj.append(Dev2301Window(self, self.parent))

        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        for swobj in self.swobj:
            self.main_sizer.Add(swobj, 0, wx.ALL, 5)
            self.main_sizer.Add((0,10), 0, wx.EXPAND)
            
        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        self.Layout()
        

