from importlib.resources import contents
import wx

from serialLogWindow import SerialLogWindow

class RightPanel(wx.Panel):
    def __init__(self, parent):
        super(RightPanel, self).__init__(parent)

        self.SetBackgroundColour('White')

        # self.SetMaxSize((400, -1))
        # self.SetSize((300, 700))

        # self.slogPan = SerialLogWindow(self, parent)
        # self.slogPan2 = SerialLogWindow(self, parent)
        self.parent =  parent

        self.slobj = []

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        # for number in range(5):
        #     btn = wx.Button(self, label='Button {}'.format(number))
        #     main_sizer.Add(btn, 0, wx.ALL, 5)


        # self.main_sizer.Add(0, 10, 0)
        # self.main_sizer.Add(self.slogPan, 1, wx.EXPAND)
        # self.main_sizer.Add(0, 10, 0)
        # self.main_sizer.Add(self.slogPan2, 1, wx.EXPAND)
        # self.main_sizer.Add(0, 10, 0)

        self.SetSizer(self.main_sizer)

        # self.SetSizer(self.vb_outer)
        
        # Setting Layouts
        # self.SetAutoLayout(True)
        self.main_sizer.Fit(self)
        self.Layout()

    def update_slog_panel(self, cnt):
        print("I am in right panel: ",cnt)

        if(len(self.slobj) > 0):
            self.main_sizer.Clear(True)

        self.slobj.clear()

        for idx in range(0, cnt):
            self.slobj.append(SerialLogWindow(self, self.parent))

        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        for slobj in self.slobj:
            self.main_sizer.Add(slobj, 1, wx.ALL, 5)
            self.main_sizer.Add((0,10), 1, wx.EXPAND)
            
        self.main_sizer.Add((0,20), 0, wx.EXPAND)
        self.Layout()


    def Hide_SL1(self):
        self.slogPan.Hide()
        self.Layout()

    def Hide_SL2(self):
        self.slogPan2.Hide()
        self.Layout()

    def Show_SL1(self):
        self.slogPan.Show()
        self.Layout()

    def Show_SL2(self):
        self.slogPan2.Show()
        self.Layout()

    def add_switches(self, swlist):
        for idx in range(1,len(swlist)):
            print(idx, swlist[idx])
        pass