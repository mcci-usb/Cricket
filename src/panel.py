import wx
 
 
class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(None, *args, **kwargs)
        self.Title = 'Wx App'
        screen_width, screen_height = wx.GetDisplaySize()
        win_width = min(screen_width, 1280)
        win_height = min(screen_height, 800)
        self.Size = (win_width, win_height)
 
        self.panel = MainPanel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.panel)
        self.SetSizer(sizer)

        # self.st = wx.StaticText(self, -1, "Hello")
        self.Center()
        self.Show()
 
 
class MainPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
 
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        self.st = wx.StaticText(self, -1, "Hello")
        self.Show()
 
 
if __name__ == '__main__':
    wx_app = wx.App()
    MainFrame()
    wx_app.MainLoop()