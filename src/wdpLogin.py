import wx
import configdata

# from main import Mywin

class LoginFrame(wx.Dialog):
    def __init__(self, parent, top):
        super(LoginFrame, self).__init__(parent, title="Login Window", size=(350, 280))
        self.panel = wx.Panel(self)
        self.top = top

        self.username_label = wx.StaticText(self.panel, label="Username")
        self.username_text = wx.TextCtrl(self.panel, size=(150, -1))
        # self.username_text = wx.TextCtrl(self.panel, wx.ID_ANY, "mcci", size=(150, -1))

        self.password_label = wx.StaticText(self.panel, label="Password")
        self.password_text = wx.TextCtrl(self.panel, style=wx.TE_PASSWORD, size=(150, -1))
        # self.password_text = wx.TextCtrl(self.panel, wx.ID_ANY, "mcci", size=(150, -1))

        self.login_button = wx.Button(self.panel, label="Save")
        self.login_button.Bind(wx.EVT_BUTTON, self.on_save)

        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.username_text.SetFont(font)
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.password_text.SetFont(font)

        self.username = None
        self.password = None

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.username_label, 0, wx.ALL, 10)
        sizer.Add(self.username_text, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add(self.password_label, 0, wx.ALL, 10)
        sizer.Add(self.password_text, 0, wx.ALL | wx.EXPAND, 10)
        sizer.Add(self.login_button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 20)

        self.panel.SetSizer(sizer)

    def on_save(self, event):
        self.username = self.username_text.GetValue()
        self.password = self.password_text.GetValue()
        if self.username.strip() == '' or self.password.strip() == '':
            wx.MessageBox("Please enter the user credentials")
        
        udict = {"msudp": {"uname": self.username, "pwd": self.password}}
        configdata.updt_portal_credentials(udict)

        # self.top.set_user_credentials(self.username, self.password)  # Use self.top here
        self.Close()