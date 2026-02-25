# -*- coding: utf-8 -*-
##############################################################################
# 
# Module: autoWindow.py
#
# Description:
#     autoWindow for Switch Model 3201, 3141, 2101, 2301
#
# Author:
#     Vinay N, MCCI Corporation Feb 2026
#
# Revision history:
#     V4.7.0 Mon Feb 16 2026 17:00:00   Vinay N
#         Module created
##############################################################################
# Lib imports
import wx
from uiGlobals import *
import os
import re  
from wx.lib.scrolledpanel import ScrolledPanel
# ---- Extract model ----
# import re

import configdata

MODEL_PORT_MAP = {
    "3141": ["p1", "p2"],
    "3142": ["p1", "p2"],
    "2101": ["p1", "p2"],
    "3201": ["p1", "p2", "p3", "p4"],
    "2301": ["p1", "p2", "p3", "p4"],
}

##############################################################################
# Utilities
##############################################################################
class BatchWindow(wx.Window):
    """
    Batch Execution Window.

    Description:
        Provides a graphical interface to execute batch scripts
        for automated switch and port control operations.

        This window enables users to run predefined macro commands
        that control device switching, port toggling, serial
        communication, delays, and repeat sequences.
        Inheritance:
        wx.Window → Provides GUI container functionality.
    """
    def __init__(self, parent, top):
        """
        Initialize Batch Execution Window.

        Detailed Description:
            This constructor initializes the BatchWindow UI container
            and prepares internal execution states, opcode mappings,
            and command decoding handlers required for batch script
            processing.

            It sets up:

                • Parent UI reference
                • Top controller reference
                • Batch execution flags
                • Opcode parser mappings
                • Execution decoder mappings
                Args:
            self:
                Reference to the current BatchWindow instance.

            parent:
                Parent UI container that owns this window.

            top:
                Main controller reference used for device control,
                logging, and command execution.

        Returns:
            None

        Raises:
            None
        """
        wx.Window.__init__(self, parent)
        # SET BACKGROUND COLOUR TO White
        self.SetBackgroundColour("White")

        #self.SetMinSize((200,200))
        self.parent = parent
        self.top = top
        
        self.batch_flg = False
        self.mapping_error = False

        self.batchopcode = {
            "switch": self.parseSwMacro,
            "main:": self.parseMain,
            "port": self.parsePort,
            "delay": self.parseDelay,
            "read": self.parseRead,
            "repeat": self.parseRepeat,
            "serial": self.parseSerial,
            "end": self.parseEnd
        }

        self.batchdecode = {
            "switch": self.setSwPath,
            "port": self.doPortON,
            "speed": self.setSpeed,
            "delay": self.executeDelay,
            "read": self.executeOthers,
            "serial": self.executeSerial,
            "repeat": self.executeRepeat
        }

        self.vbOuter = wx.BoxSizer(wx.VERTICAL)
        self.hbOuter = wx.BoxSizer(wx.HORIZONTAL)
        self.vbMid = wx.BoxSizer(wx.VERTICAL)
        self.hbSelect = wx.BoxSizer(wx.HORIZONTAL)
        self.vbSeq = wx.BoxSizer(wx.VERTICAL)
        self.hbBtn = wx.BoxSizer(wx.HORIZONTAL)

        self.mappedSw = {}
        self.reqSw = {}
        self.main_flg = False
        self.end_flg = False
        self.swpath = None
        self.repeat = 0
        self.seqIdx = 0
        self.tdelay = 500

        self.done = 0
        self.cdpass = 0
        self.cdfail = 0
        
        # self.InitTopHbox()
        self.InitSeqBox()
        self.InitBotHbox()

        self.vbMid.AddMany([
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
        pass

    def setSwPath(self, inpath):
        """
        Set Switch Path for Batch Execution.

        Detailed Description:
            This function stores the switch path identifier parsed
            from the batch script and assigns it to the current
            execution context.

            The switch path is used in subsequent batch operations
            such as port control, switching actions, and device
            routing.

            It acts as the active target switch reference for all
            upcoming commands within the batch execution cycle.

        Args:
            self:
                Reference to the current BatchWindow instance.

            inpath:
                Switch path identifier parsed from the batch script.
                Typically represents the switch device key or route.

        Returns:
            None

        Raises:
            None
        """
        self.swpath = inpath

    def doPortON(self, portNo):
        """
        Execute Port ON Operation.

        Detailed Description:
            This function triggers a port ON command on the selected
            switch device during batch execution.

            It uses the previously configured switch path and sends
            a control command to enable (turn ON) the specified port.

            The command is forwarded to the top controller, which
            communicates with the physical switch hardware.
            Args:
            self:
                Reference to the current BatchWindow instance.

            portNo:
                Port number to be turned ON.
                Expected to be an integer representing the physical
                port index on the switch device.

        Returns:
            None

        Raises:
            None
        """
        self.top.port_on(self.swpath, portNo, True)
    
    def setSpeed(self, inspeed):
        """
        Set the speed of the switch.

        Parameters:
            inspeed (str): The desired speed value.

        """
        self.top.set_speed(self.swpath, inspeed)

    def executeDelay(self, indelay):
        """
        executing the based on the set delay on log

        Parameters:
            indelay (str): The desired delay value.

        """
        self.tdelay = indelay
        self.top.print_on_log("Delay: "+str(indelay)+"\n")

    def executeOthers(self, incmd):
        """
        Execute Generic Read Operations from Batch Script.

        Detailed Description:
            This function processes and executes generic READ commands
            parsed from the batch script during batch execution.

            It logs the read request into the DUT / Switch log window
            and routes the command to the appropriate handler based
            on the command type.
            Args:
            self:
                Reference to the current BatchWindow instance.

            incmd:
                Incoming read command string parsed from the
                batch script.

                Examples:
                    "USB"
                    "VBUS"
                    "Current"
                    "Voltage"

        Returns:
            None

        Raises:
            None
        """
        self.top.print_on_log("Read: "+incmd+"\n")
        if incmd == "USB":
            self.top.get_usb_tree()
        else:
            self.top.read_param(self.swpath, incmd)

    def executeSerial(self, incmd):
        """
        Execute Serial Communication Commands from Batch Script.

        Detailed Description:
            This function processes serial communication instructions
            parsed from the batch execution script and routes them to
            the appropriate serial interface handlers.

            The incoming command dictionary contains a single key
            representing the serial operation type along with its
            associated parameters.

            Supported serial operations include:

            • open
                Opens the configured serial COM port using the
                provided serial settings.

            • write
                Sends data to the serial device over the active
                COM port connection.

            • read
                Reads data from the serial device and validates
                the response.

                Based on the validation result:
                    - Pass counter is incremented on success.
                    - Fail counter is incremented on mismatch.

            This mechanism is primarily used for automated DUT
            communication validation during batch execution.

        Args:
            self:
                Reference to the current BatchWindow instance.

            incmd:
                Dictionary containing serial command and parameters.

                Example formats:

                    {"open":  {"port": "COM3", "baud": 9600}}
                    {"write": "AT+RST"}
                    {"read":  "OK"}

        Returns:
            None

        Raises:
            None
        """
        skey = list(incmd.keys())[0]
        #   self.top.print_on_log("Serial: "+incmd+"\n")
        if skey == "open":
            self.top.open_com_port(incmd[skey])
        elif skey == "write":
            self.top.write_serial(incmd[skey])
        elif skey == "read":
            res = self.top.read_serial(incmd[skey])
            if res == True:
                self.cdpass = self.cdpass + 1
            else:
                self.cdfail = self.cdfail + 1

    def executeRepeat(self, repeat):
        """
        executing the repeated times

        Parameters:
           repeat: set the paramaeter
        """
        self.top.print_on_log("Repeat\n")
        
    def InitSeqBox(self):
        """
        Initialize Batch Sequence Script Editor UI.

        Detailed Description:
            This function creates and configures the multi-line text
            control used for entering batch execution scripts.

            The sequence editor allows users to define automated
            switch and DUT operation commands such as:

            • Model / Port selection
            • Delay intervals
            • Repeat cycle count

            A default template script is preloaded into the editor
            to guide users in writing valid batch sequences.

            The initialized text control is then added to the
            parent sequence layout container.

        Args:
            self:
                Reference to the current BatchWindow instance.

        Returns:
            None

        Raises:
            None
        """

        self.tc_seq = wx.TextCtrl(
            self,
            -1,
            style=wx.TE_MULTILINE,
            size=(400,250)
        )

        default_script = (
            "model = 3141, p1\n"
            "delay = 1000\n"
            "repeat = 10\n"
        )


        self.tc_seq.SetValue(default_script)

        self.vbSeq.Add(
            self.tc_seq, 1, wx.EXPAND
        )


    def InitBotHbox(self):
        """
        Initialize Batch Control Button Layout.

        Detailed Description:
            This function creates and arranges the bottom control
            buttons used for batch script operations within the
            Batch Window interface.

            The control section provides user actions to manage
            batch execution workflows including:

            • Script generation
            • Script revert/reset
            • Batch execution start
            • Script saving

            Buttons are aligned horizontally using a box sizer
            layout to maintain consistent UI spacing and alignment.

            Event bindings are also configured to connect each
            button with its respective handler function.

        Buttons Created:
            Generate Script :
                Builds or auto-generates batch command scripts.

            Revert :
                Restores the script editor to its previous/default state.

            Start :
                Initiates batch execution sequence.

            Save :
                Saves the current batch script to file/storage.

        Args:
            self:
                Reference to the current BatchWindow instance.

        Returns:
            None
        """
        self.btn_generate = wx.Button(self, -1, "Generate Script", size=(100,25))
        self.btn_revert = wx.Button(self, -1, "Revert", size=(70,25))
        self.btn_start = wx.Button(self, -1, "Start", size=(60,25))
        self.btn_save = wx.Button(self, -1, "Save", size=(60,25))
        
        self.hbBtn.AddMany([
            ((-1,0), 1, wx.EXPAND),
            (self.btn_generate, 0, wx.ALIGN_CENTER),
            ((20,0), 0, wx.EXPAND),
            (self.btn_revert, 0, wx.ALIGN_CENTER),
            ((20,0), 0, wx.EXPAND),
            (self.btn_start, 0, wx.ALIGN_CENTER),
            ((20,0), 0, wx.EXPAND),
            (self.btn_save , 0, wx.ALIGN_CENTER),
            ((-1,0), 1, wx.EXPAND)
        ])

        self.btn_start.Bind(wx.EVT_BUTTON, self.OnClickBatch)
        self.btn_save.Bind(wx.EVT_BUTTON, self.SaveBatch)
        self.btn_generate.Bind(wx.EVT_BUTTON, self.OnGenerateScript)
        self.btn_revert.Bind(wx.EVT_BUTTON, self.OnRevertScript)
        self.btn_start.Disable()
    
    def OnGenerateScript(self, event):
        """
        Generate Batch Script from User Input.

        Detailed Description:
            This function parses the user-entered batch configuration
            script from the sequence text control and automatically
            generates a fully structured execution script.

            The generated script includes:

                • Switch mapping definitions
                • Port switching sequence
                • Delay intervals
                • Repeat execution block

            It validates user inputs such as model names and port
            selections before script generation to ensure compatibility
            with supported hardware configurations.

        Processing Flow:
            1. Read raw script text from the editor.
            2. Parse configuration parameters:
                - Model(s)
                - Port(s)
                - Delay
                - Repeat count
            3. Validate model support using MODEL_PORT_MAP.
            4. Validate selected ports (if provided).
            5. Auto-generate formatted batch script.
            6. Load generated script back into editor.
            7. Enable batch execution (Start button).

        Supported Input Format Example:
            model = 3141, p1, p2
            delay = 1000
            repeat = 10

        Args:
            self:
                Reference to the current BatchWindow instance.

            event:
                wxPython button click event triggered when
                the "Generate Script" button is pressed.

        Returns:
            None
        """
        text = self.tc_seq.GetValue()

        models = {}   # ← model : [ports]
        delay = 1000
        repeat = 1

        for line in text.splitlines():

            if "=" not in line:
                continue
            key, value = [x.strip() for x in line.split("=")]
            if key.lower() == "model":

                parts = value.replace(" ", "").split(",")

                model = parts[0]
                ports = parts[1:] if len(parts) > 1 else []

                # remove p0 if user typed
                ports = [p for p in ports if p != "p0"]

                models[model] = ports

            elif key.lower() == "delay":
                delay = int(value)
            elif key.lower() == "repeat":
                repeat = int(value)

        # ---- Validation ----
        if not models:
            wx.MessageBox(
                "No model defined in script.",
                "Input Error",
                wx.OK | wx.ICON_ERROR
            )
            return
        script = ""
        # ---- Switch Mapping ----
        for model in models:

            if model not in MODEL_PORT_MAP:
                wx.MessageBox(
                    f"Unsupported model: {model}",
                    "Model Error",
                    wx.OK | wx.ICON_ERROR
                )
                return

            script += f'switch my{model} = "COMX", "{model}"\n'

        script += "\nmain:\n"

        # ---- Generate Ports ----
        for model, user_ports in models.items():

            available_ports = MODEL_PORT_MAP[model]

            # ---- If user specified ports ----
            if user_ports:

                invalid = [p for p in user_ports if p not in available_ports]

                if invalid:
                    wx.MessageBox(
                        f"{model} → Invalid port(s): {', '.join(invalid)}",
                        "Port Error",
                        wx.OK | wx.ICON_ERROR
                    )
                    return

                ports_to_use = user_ports

            else:
                ports_to_use = available_ports  # all ports

            # ---- Generate Sequence ----
            for p in ports_to_use:

                script += f"port my{model}.{p}\n"
                script += f"delay {delay}ms\n"
                script += f"port my{model}.p0\n"
                script += f"delay {delay}ms\n"

            script += "\n"

        script += f"repeat {repeat}\nend\n"

        self.tc_seq.SetValue(script)
        self.btn_start.Enable()

    def OnRevertScript(self, event):
        """
        Revert Generated Batch Script to Simple Template Format.

        Detailed Description:
            This function converts an auto-generated batch execution
            script back into a simplified user-editable template.

            It is primarily used when users want to modify parameters
            such as:

                • Model number
                • Selected port
                • Delay interval
                • Repeat count

            The function performs pattern extraction from the generated
            script and rebuilds a minimal configuration script.

        Processing Flow:
            1. Read the current script from the editor.
            2. Check whether the script is already in simple format.
            3. If simple → reload default template.
            4. If generated → extract:
                • Model ID
                • Delay value
                • Repeat count
                • First active port
            5. Rebuild simplified script.
            6. Load template back into editor.

        Default Template Format:
            model = 3141, p1
            delay = 1000
            repeat = 10

        Args:
            self:
                Reference to the current BatchWindow instance.

            event:
                wxPython button click event triggered when
                the "Revert" button is pressed.

        Returns:
            None

        Raises:
            None
                Parsing failures fall back to default values.
        """
        text = self.tc_seq.GetValue()
        # ---- If already simple → reload template ----
        if "switch my" not in text:

            default_script = (
                "model = 3141, p1\n"
                "delay = 1000\n"
                "repeat = 10\n"
            )


            self.tc_seq.SetValue(default_script)
            return

        # ---- Extract model ----
        model_match = re.search(r"switch my(\d+)", text)
        model = model_match.group(1) if model_match else "3141"

        # ---- Extract delay ----
        delay_match = re.search(r"delay (\d+)ms", text)
        delay = delay_match.group(1) if delay_match else "1000"

        # ---- Extract repeat ----
        repeat_match = re.search(r"repeat (\d+)", text)
        repeat = repeat_match.group(1) if repeat_match else "10"

        # ---- Extract port (FIRST ON port only) ----
        port_match = re.search(r"port my\d+\.(p\d+)", text)

        if port_match:
            port = port_match.group(1)
        else:
            port = "p1"   # default fallback

        # ---- Build simple script ----
        # ---- Build simple script ----
        simple_script = (
            f"model = {model}, {port}\n"
            f"delay = {delay}\n"
            f"repeat = {repeat}\n"
        )

        self.tc_seq.SetValue(simple_script)

    def OnClickBatch(self, event):
        """
        Handle the event triggered by clicking on the batch button.

        Description:
            - If batch mode is active, stop the batch, print a message, and stop the timer.
            - If batch mode is not active, start the batch.

        Parameters:
            event (wx.Event): The event object representing the button click.

        """
        if self.batch_flg:
            self.StopBatch()
            self.top.print_on_log("\nBatch Mode Stopped!")
            self.timer.Stop()        
        else:
            self.StartBatch()
    
    def StopBatch(self):
        """
        Stop Batch Execution Mode.

        Detailed Description:
            This function terminates the currently running Batch Mode
            execution process.

            It performs the following operations:

                • Resets the internal batch execution flag.
                • Updates the Start/Stop button label back to "Start".
                • Switches the application operating mode to Manual.
                Args:
        self:
            Reference to the current BatchWindow instance.

        Returns:
            None

        Raises:
            None
        """
        self.batch_flg = False
        # The Lablel to set name as Auto
        self.btn_start.SetLabel("Start")
        # The mode set as Manual Mode.
        self.top.set_mode(MODE_MANUAL)

    def check_each_sw(self, swseq):
        """
        Validate and extract Switch Sequence Parameters.

        Detailed Description:
            This function parses each switch operation entry from the
            provided switch sequence list and categorizes the commands
            based on operation type.

            It inspects every item in the sequence and identifies whether
            the operation corresponds to:

                • Port switching command
                • Delay execution command
        Args:
            self :
                Reference to the current BatchWindow instance.

            swseq (list of dict) :
                Parsed switch execution sequence containing
                port and delay command dictionaries.

                Example:
                    [
                        {'port': 'p1'},
                        {'delay': 1000},
                        {'port': 'p0'}
                    ]

        Returns:
            None

        Raises:
            None
        """
        
        dlist = []
        klist = []
        plist = []
        for item in swseq:
            if 'port' in item:
                klist.append('port')
                plist.append(item['port'])
            elif 'delay' in item:
                klist.append('delay')
                dlist.append(item['delay'])

        mindly = min(dlist)
        maxdly = max(dlist)
        if mindly <= 999 or maxdly <= 999:
            return {"result": "error", "message": "minumum delay should be 1000 msec"}
        
        for i in range(len(klist)-1):
            if klist[i] == "port":
                if klist[i+1] == "delay" and klist[i-1] == "delay":
                    continue
                else:
                    return {"result": "error", "message": "port switching not surrounded with delay"}

        for i in range(len(plist)-1):
            if plist[i] != 0:
                if (plist[i+1] == 0 or plist[i+1] == plist[i]) and (plist[i-1] == 0 or plist[i-1] == plist[i]):
                    continue
                else:
                    return {"result": "error", "message": "Port ON not surrounded with Port OFF"}
        return {"result": "success"}

    def checkSafeSwitching(self):
        """
        Validate Safe Port Switching Sequence in Batch Execution.

        Detailed Description:
            This function verifies whether the generated or user-defined
            batch switching sequence follows safe device switching rules.

            It performs multi-stage validation to ensure that:

                • Only relevant switching commands are processed.
                • Consecutive delay commands are merged.
                • Switching sequences are grouped per device.
                • Port ON/OFF timing is validated for safety compliance.

            The primary objective is to prevent unsafe switching patterns
            that could damage connected DUT devices.

        Args:
            self :
                Reference to the current BatchWindow instance.

        Returns:
            bool :

                True  →
                    Safe to proceed with batch execution
                    OR user overrides warning.

                False →
                    Unsafe switching detected and user
                    chose to abort execution.
        """
        # Filterout switch, port, delay
        mykilist = ["switch", "port", "delay"]
        mynewlist = []
        
        for item in self.finseq:
            ikey = list(item.keys())[0]
            if ikey in mykilist:
                mynewlist.append(item)
        
        # adding of consecutive delay in the list
        myanlist = []
        for item in mynewlist:
            # nkey = list(item.keys())[0]
            if "delay" in item.keys():
                if "delay" in myanlist[-1].keys():
                    myanlist[-1]["delay"] += item["delay"]
                else:
                    myanlist.append(item)
            else:
                myanlist.append(item)
        
        # converting list as dict
        myndict = {}

        for item in myanlist:
            if "switch" in item.keys():
                kval = item["switch"]
                myndict[kval] = []

        lsw = None
        for item in myanlist:
            if "switch" in item.keys():
                kval = item["switch"] 
                lsw = kval
            elif "port" in item.keys():
                myndict[lsw].append(item)
            else:
                for mk in myndict.keys():
                    myndict[mk].append(item)
        
        # Check each dict element for
        resdict = None
        for item in myndict:
            resdict = self.check_each_sw(myndict[item])
            if resdict["result" ] == "error":
                break
        
        if resdict["result"] == "success":
            return True
        else:
            title = ("Port ON/OFF time warning! For Device safety")
            msg = ("Batch script warning! - \n"
                       + resdict["message"] +
                       "\nClick Yes if you wish to continue"
                       "\nClick No to exit the batch mode")
            dlg = wx.MessageDialog(self, msg, title, wx.NO|wx.YES|wx.ICON_WARNING)
            if(dlg.ShowModal() == wx.ID_YES):
                return True
            else:
                return False
    
    def StartBatch(self):
        """
        Initialize and Execute Batch Mode Sequence.

        Detailed Description:
            This function is responsible for starting the Batch Execution Mode.

            It performs complete initialization, parsing, validation,
            safety verification, and execution of the batch script
            entered by the user.

            The batch execution workflow includes:

                • Resetting previous batch states
                • Parsing batch script sequence
                • Validating switch mapping
                • Performing safety switching checks
                • Creating batch execution UI panel
                • Running the batch sequence

        Args:
            self :
                Reference to the current BatchWindow instance.

        Returns:
            None

        """
        self.mappedSw = {}
        self.reqSw = {}
        self.main_flg = False
        self.end_flg = False
        self.finseq = []
        self.mapping_error = False

        self.parseBatchSeq()

        # ---- Mapping Parse Error ----
        if self.mapping_error:

            msg = (
                "Batch Script Parsing Error\n\n"
                "Switch mapping could not be parsed correctly.\n\n"
                "Possible reasons:\n"
                " • Extra spaces in switch line\n"
                " • Incorrect switch syntax\n"
                " • Unsupported switch model\n\n"
                "Example correct format:\n"
                ' switch my3141 = "COM6", "3141"\n\n'
                "Please correct the script and try again."
            )

            wx.MessageBox(
                msg,
                "Parsing Error",
                wx.OK | wx.ICON_ERROR
            )
            return

        # ---- Safety Check ----
        if self.checkSafeSwitching():

            if self.top.createBatchPanel(self.reqSw):
                self.runBatchSeq()

            else:
                missing_switches = ", ".join(self.reqSw.keys())

                msg = (
                    "Switch mapping not found for the batch sequence.\n\n"
                    f"Requested Switch(es): {missing_switches}\n\n"
                    "Please verify the following:\n"
                    " • Please check whether the Switch Model is correct\n"
                    " • The switch device or model is connected and powered ON\n"
                    " • The correct Serial COM Port is assigned (e.g., COM1)\n"
                )

                wx.MessageBox(
                    msg,
                    "Switch Detection Warning",
                    wx.OK | wx.ICON_WARNING
                )

    def runBatchSeq(self):
        """
        Start Batch Sequence Execution.

        Detailed Description:
            This function initializes and starts the batch execution engine.

            It prepares runtime counters, resets execution indexes,
            prints batch start logs, and activates the execution timer
            to begin processing the batch sequence.
        
        Args:
        self :
            Reference to the current BatchWindow instance.

        Returns:
            None

        Raises:
            None
        """

        self.batch_flg = True
        self.btn_start.SetLabel("Stop")

        self.done = 0
        self.cdpass = 0
        self.cdfail = 0

        self.seqIdx = 0
        self.totSeq = len(self.finseq)
        self.tdelay = 500

        self.top.print_on_log("\n######################################")
        self.top.print_on_log("\nBatch Mode Starting!")
        self.top.print_on_log("\nRepeat Count: "+str(self.repeat))
        self.top.print_on_log("\n######################################\n\n")

        if(self.timer.IsRunning() == False):
            self.timer.Start(self.tdelay)

    def TimerServ(self, evt):
        """
        Handle the timer event for batch processing.

        Description:
            - Stop the timer.
            - Get the command key from the current sequence index.
            - Execute the command associated with the key using batchdecode dictionary.
            - Increment the sequence index.
            - Start the timer with a delay.
            - Check if the sequence index exceeds the length of the sequence.
            - If the sequence is completed, reset the index, increment the cycle count, and print results.
            - Stop the timer if the desired number of cycles is reached.

        Parameters:
            evt (wx.Event): The timer event triggering the function.

        """
        self.timer.Stop()
        key = list(self.finseq[self.seqIdx])[0]
        self.batchdecode.get(key, self.defaultCmd) (self.finseq[self.seqIdx][key])
        self.seqIdx += 1
        self.timer.Start(self.tdelay)
        self.tdelay = 1
        if self.seqIdx >= len(self.finseq):
            self.seqIdx = 0
            self.done += 1
            resstr = "Cycle Completed: "+str(self.done)+";   Pass: "\
                     +str(self.cdpass)+";   Fail: "+str(self.cdfail)+"\n\n"
            # self.top.print_on_log("Cycle Completed: "+str(self.done)+"\n")
            self.top.print_on_log(resstr)

            if self.done >= self.repeat:
                self.timer.Stop()
                self.StopBatch()
                self.top.print_on_log("Batch Sequence Completed!")
                self.top.print_on_log("\n######################################\n\n")

    def executeBatchSeq(self):
        """
        Execute Parsed Batch Script Sequence.

        Detailed Description:
            This function initializes the execution parameters required
            to start processing the parsed batch script.

            It prepares runtime counters, validates repeat count,
            resets the sequence index pointer, and calculates the
            total number of commands available in the final sequence.

        Execution Responsibilities:

            • Reset completed cycle counter
            • Validate repeat count (minimum = 1)
            • Initialize sequence index pointer
            • Calculate total sequence length
            Args:
            self :
                Reference to the current BatchWindow instance.

            Returns:
                None
            """
        self.done = 0
        if self.repeat == 0:
            self.repeat = 1
        self.seqIndex = 0

        self.totseq = len(self.finseq)
        
    def SaveBatch(self, event):
        """
        Save Batch Script Content.

        Detailed Description:
            This function retrieves the batch script content
            from the sequence text control and saves it
            into a text file using the batch save handler.

        Execution Responsibilities:

            • Read batch script from UI text control
            • Invoke save handler with file filter
            • Store script as a .txt file

        Args:
            self :
                Reference to the current BatchWindow instance.

            event :
                Button click event triggering the save action.

        Returns:
            None
        """
        content = self.tc_seq.GetValue()
        self.save_batch(content, "*.txt")

    def updateBatchLocation(self, pathname):
        """
        Update Batch Script Location Path.

        Detailed Description:
            This function updates the stored batch script
            file location path in the application configuration.

            It ensures the latest selected batch script
            directory or file path is saved for future access.

        Execution Responsibilities:

            • Receive batch script path input
            • Update configuration storage
            • Maintain last used batch location reference

        Args:
            self :
                Reference to the current BatchWindow instance.

            pathname :
                Absolute path of the selected batch script file
                or directory location.

        Returns:
            None
        """
        configdata.updt_batch_location(pathname)

    def LoadBatch(self, event):
        """
        Load Batch Script From Local Path.

        Detailed Description:
            This function handles loading an existing batch
            script file from the user’s local system.

            It opens the file selection dialog, retrieves the
            selected batch script path, and updates the stored
            batch location for future reference.

        Execution Responsibilities:

            • Open batch file selection dialog
            • Retrieve selected file path
            • Update batch script location in configuration

        Args:
            self :
                Reference to the current BatchWindow instance.

            event :
                Event object triggered by Load button action.

        Returns:
            None
        """
        pathname = self.load_file()
        self.updateBatchLocation(pathname)


    def load_last_file(self):
        """
        Load Last Used Batch Script File.

        Detailed Description:
            This function loads the previously used batch
            script file from the stored batch location.

            It validates the saved file path, reads the script
            content, and populates the batch sequence editor.
            If the file is unavailable or invalid, execution
            controls are disabled.

        Execution Responsibilities:

            • Validate stored batch file path
            • Clear existing batch editor content
            • Reset parsed sequence data
            • Read and load script into editor
            • Enable batch execution if load succeeds
            • Handle file access errors safely

        Args:
            self :
                Reference to the current BatchWindow instance.

        Returns:
            None
        """
        if self.bloc == None:
            self.btn_start.Disable()
            return
        
        self.tc_bloc.SetValue(self.bloc)
        try:
            self.tc_seq.SetValue("")
            self.mappedSw = {}
            self.main_flg = False
            self.end_flg = False
            self.finseq = []
            if os.path.exists(self.bloc):
                with open(self.bloc) as fobj:
                    for line in fobj:
                        self.tc_seq.WriteText(line)
                self.btn_start.Enable()
        except IOError:
            wx.LogError("Can not open file '%s', " % self.bloc)
            self.btn_start.Disable()

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
                self.btn_start.Enable()
        except IOError:
            wx.LogError("Can not open file '%s', " % pathname)
            self.btn_start.Disable()
        return pathname

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
        """
        Parse Switch Mapping Macro from Batch Script.

        Detailed Description:
            This function parses the switch mapping definition
            from the batch script sequence.

            It extracts the switch alias, communication path,
            and switch model type from the tokenized command list.
            The parsed mapping is validated against the supported
            device model list before registering it for execution.

        Execution Responsibilities:

            • Extract switch communication path
            • Extract switch model type
            • Validate mapping syntax ('=' operator)
            • Verify supported device model
            • Store alias → COM path mapping
            • Register required switch model list
            • Log parsing errors if validation fails

        Args:
            self :
                Reference to the current BatchWindow instance.

            oclist :
                Tokenized command list containing switch
                mapping elements parsed from script.

        Returns:
            None
        """
        devlist = ["3141","3142", "3201", "2301", "2101"]
        
        swpath = oclist[3].replace(',', '').strip()
        swpath = swpath[1:-1].strip()
        swtype = oclist[4][1:-1].strip()


        if oclist[2] == "=":
            if swtype in devlist:
                self.mappedSw[oclist[1]] = swpath
                self.reqSw[swpath] = swtype
            else:
                self.top.print_on_log("\nError in parsing Switch Mapping")
        else:
            self.top.print_on_log("Syntax error in mapping '='")
        
    def parseDelay(self, indata):
        """
        Parse Delay Command from Batch Script.

        Detailed Description:
            This function parses the delay instruction defined
            inside the batch script main execution block.

            It validates whether the parser is currently inside
            the 'main' execution section. If valid, it extracts
            the delay value (in milliseconds), converts it into
            integer format, and appends it to the final execution
            sequence list.
        Args:
            self :
                Reference to the current BatchWindow instance.

            indata :
                Tokenized delay command list parsed
                from the batch script.

        Returns:
            None
        """
        if self.main_flg == True:
            try:
                delay = indata[1].replace('ms', '')
                delay = int(delay)
                self.finseq.append({"delay": delay})
            except:
                pass

        else:
            # self.top.print_on_log("Main keyword should present after declaration")
            pass
    
    def parsePort(self, indata):
        """
        Parse Port Command from Batch Script.

        Detailed Description:
            This function parses the port switching instruction
            defined inside the batch script main execution block.

            It extracts the switch identifier, port number, and
            optional speed parameter from the parsed command tokens.

            The function validates whether the referenced switch
            is already mapped. If mapping is missing or syntax is
            invalid, it raises a parsing error and stops execution.

            When valid, the function appends the corresponding
            switch path, optional speed, and port number into the
            final execution sequence list.
        Args:
            self :
                Reference to the current BatchWindow instance.

            indata :
                Tokenized port command list parsed
                from the batch script.

        Returns:
            None
        """

        if self.main_flg == True:

            speed = None

            # ---- Detect speed ----
            try:
                if indata[2] in ['SS0', 'SS1']:
                    speed = indata[2]
            except:
                pass

            # ---- Parse switch & port ----
            try:
                swcode = indata[1].split('.')
                swname = swcode[0]
                portname = swcode[1].replace('p', '')
            except:
                self.mapping_error = True

                wx.MessageBox(
                    "Invalid port syntax detected.\n\n"
                    "Example:\n"
                    " port my3141.p1",
                    "Parsing Error",
                    wx.OK | wx.ICON_ERROR
                )
                return

            # ---- Mapping validation ----
            if swname not in self.mappedSw:

                self.mapping_error = True

                msg = (
                    "Batch Script Parsing Error\n\n"
                    f"Switch '{swname}' is not mapped.\n\n"
                    "Possible reasons:\n"
                    " • Switch declaration missing\n"
                    " • Incorrect switch name in port line\n"
                    " • Extra spaces or syntax issue\n\n"
                    "Example:\n"
                    ' switch my3141 = "COM6", "3141"\n'
                    " port my3141.p1\n"
                )

                wx.MessageBox(
                    msg,
                    "Mapping Error",
                    wx.OK | wx.ICON_ERROR
                )
                return

            # ---- Append switch ----
            self.finseq.append({"switch": self.mappedSw[swname]})

            # ---- Append speed if exists ----
            if speed is not None:
                self.finseq.append({"speed": speed})

            # ---- Append port (ALWAYS) ----
            self.finseq.append({"port": int(portname)})

        else:
            pass

    def parseRead(self, indata):
        """
        Parse Read Command from Batch Script.

        Detailed Description:
            This function parses the read instruction defined
            in the batch script. It validates whether the
            requested read parameter is supported and, if valid,
            appends it to the final execution sequence.

        Execution Responsibilities:

            • Validate read parameter support
            • Accept voltage / current / USB commands
            • Append read operation to final sequence list

        Args:
            self :
                Reference to the current BatchWindow instance.

            indata :
                Tokenized read command list parsed
                from the batch script.

        Returns:
            None
        """
        rdlist = ["voltage", "current", "USB", ]
        try:
            if any(indata[1] in s for s in rdlist):
                self.finseq.append({"read": indata[1]})
        except:
            pass

    def parseSerial(self, indata):
        """
        Parse serial commands and add them to the batch sequence.

        Description:
            - Check if the second element in indata is one of the 
              allowed values ("open", "write", "read").
            - If yes, extract the serial settings from the third element in indata.
            - Replace double quotes from the serial settings.
            - Add the serial command to the batch sequence.

        Parameters:
            indata (list): List containing serial command details.

        """
        
        rdlist = ["open", "write", "read"]
        try:
            if any(indata[1] in s for s in rdlist):

                serset = indata[2].replace('"', '')

                self.finseq.append({"serial": {indata[1]: serset}})
        except:
            pass
        
    def parseRepeat(self, indata):
        """
        Parse repeat command and add it to the batch sequence.

        Description:
            - Check the length of indata.
            - If the length is 2, try to convert the second element to an integer (rptcnt).
            - Add the repeat command with rptcnt to the batch sequence.
            - Update the repeat attribute with rptcnt.
            - Handle parsing errors with wx.MessageBox.

        Parameters:
            indata (list): List containing repeat command details.

        """
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
        """
        Set the main flag to True.

        Description:
            - Set the main flag to True.

        Parameters:
            indata (list): List containing main command details.

        """
        self.main_flg = True

    def parseEnd(self, indata):
        """
        Set the end flag to True.

        Description:
            - Set the end flag to True.

        Parameters:
            indata (list): List containing end command details.

        """
        self.end_flg = True

    def defaultCmd(self, other):
        pass

    def port_on(self, portno, stat):
        """
        Trigger the port_on method in the top level.

        Description:
            - Trigger the `port_on` method in the top level with the provided `portno` and `stat` parameters.

        Parameters:
            portno (str): Port number.
            stat (bool): Port status.

        """
        self.top.port_on(self.swkey, portno, stat)

    def parseBatchSeq(self):
        """
        Parse the batch sequence.

        Description:
            - Initialize an empty list (`finseq`) to store the parsed batch sequence.
            - Retrieve the number of lines in the text control (`tc_seq`).
            - Iterate through each line in the text control.
            - Split each line into a list of strings.
            - Use the `batchopcode` dictionary to call the corresponding command method with the parsed list.
        
        """
        self.finseq = []
        noofline = self.tc_seq.GetNumberOfLines()
        for i in range(0, noofline):
            strdata = self.tc_seq.GetLineText(i)
            mylist = strdata.split(" ")
            self.batchopcode.get(mylist[0], self.defaultCmd)(mylist)