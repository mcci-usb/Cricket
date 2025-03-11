import wx
from features.dut import dutLogWindow
from usb4tree import usb4TreeWindow
from usb4tree import usb3TreeWindow

class RightPanel(wx.Panel):
    def __init__(self, parent):
        super(RightPanel, self).__init__(parent)
        
        self.SetBackgroundColour('White')
        self.parent = parent

        # Create USB4 and USB3 Tree Notebook (Top Section)
        self.usb_notebook = wx.Notebook(self)
        
        # Create DUT Notebook (Bottom Section)
        self.dut_notebook = wx.Notebook(self)

        # Layout Sizers
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.top_sizer.Add(self.usb_notebook, 1, wx.EXPAND)
        self.bottom_sizer.Add(self.dut_notebook, 1, wx.EXPAND)

        self.main_sizer.Add(self.top_sizer, 1, wx.EXPAND | wx.ALL, 5)   # Top Section
        self.main_sizer.Add(self.bottom_sizer, 1, wx.EXPAND | wx.ALL, 5) # Bottom Section

        self.SetSizer(self.main_sizer)
        self.Layout()

    def init_my_panel(self, pdict):
        rpdict = pdict["rpanel"]
        dutdict = pdict["dut"]
        
        # Clear Notebooks
        self.usb_notebook.DeleteAllPages()
        self.dut_notebook.DeleteAllPages()

        # usb4_selected = rpdict.get("u4tree", False)
        # usb3_selected = rpdict.get("u3tree", False)
        usb4_selected = True  # Always show USB4 Tree
        usb3_selected = True  # Always show USB3 Tree

        dut_selected = any(rpdict.get(dut, False) for dut in dutdict.keys())

        # Populate USB4 and USB3 Tree Notebook
        if usb4_selected:
            usb4_page = usb4TreeWindow.Usb4TreeWindow(self.usb_notebook, self.parent)
            self.usb_notebook.AddPage(usb4_page, "USB4 Tree Window")
        
        if usb3_selected:
            usb3_page = usb3TreeWindow.Usb3TreeWindow(self.usb_notebook, self.parent)
            self.usb_notebook.AddPage(usb3_page, "USB3 Tree Window")

        # Populate DUT Notebook
        if dut_selected:
            for dut in dutdict.keys():
                if rpdict.get(dut, False):
                    dut_page = dutLogWindow.DutLogWindow(self.dut_notebook, self.parent, {dut: dutdict[dut]})
                    self.dut_notebook.AddPage(dut_page, dut.upper())

        # Adjust layout dynamically
        self.main_sizer.Show(self.top_sizer, usb4_selected or usb3_selected)
        self.main_sizer.Show(self.bottom_sizer, dut_selected)

        if dut_selected and not (usb4_selected or usb3_selected):
            self.main_sizer.SetItemMinSize(self.bottom_sizer, -1, -1)  # Expand DUT section fully
        else:
            self.main_sizer.SetItemMinSize(self.bottom_sizer, -1, 100)  # Reset DUT section size

        self.Layout()

    def update_my_panel(self, pdict):
        self.init_my_panel(pdict)  # Refresh the layout

    # def update_usb4_tree(self, msusb4):
    #     for i in range(self.usb_notebook.GetPageCount()):
    #         page = self.usb_notebook.GetPage(i)
    #         # if isinstance(page, (usb4TreeWindow.Usb4TreeWindow, usb3TreeWindow.Usb3TreeWindow)):
    #         if isinstance(page, usb4TreeWindow.Usb4TreeWindow):
    #             page.update_usb4_tree(msusb4)
    #         # elif isinstance(page, usb3TreeWindow.Usb3TreeWindow):
    #         #      page.update_usb3_tree(msusb)  # Update USB3 Tree
    #             break
    
    def update_usb4_tree(self, msusb4):
        # print("msusb4-->:", msusb4)
        for i in range(self.usb_notebook.GetPageCount()):
            page = self.usb_notebook.GetPage(i)
            if isinstance(page, usb4TreeWindow.Usb4TreeWindow):
                page.update_usb4_tree(msusb4)
                break  # Stop after finding the first USB4 page
        # pass

    def update_usb3_tree(self, msusb3):
        for i in range(self.usb_notebook.GetPageCount()):
            page = self.usb_notebook.GetPage(i)
            if isinstance(page, usb3TreeWindow.Usb3TreeWindow):
                page.update_usb3_tree(msusb3)
                break  # Stop after finding the first USB3 page

    # def update_usb3_tree(self, msusb3):
    #     self.update_usb3_tree(msusb3)
    
    def print_on_log(self, data):
        pass
