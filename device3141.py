import os
import sys
import serial
import threading
from threading import Timer




class SerialTimer():
    def __init__(self, ti, tfunction):
        self.flag = True
        self.ti = ti
        self.tfunction = tfunction
        self.thread = Timer(self.ti, self.thandler)

    def thandler(self):
        self.tfunction()
        if(self.flag):
            self.thread = Timer(self.ti, self.thandler)
            self.thread.start()

    def kickstart(self):
        self.thread.start()

    def cancel(self):
        self.flag = False
        



class McciSerial():
    def __init__(self):
        self.sp = None;
        self.pn = None

    def setCom(self,pname):
        self.pn = pname

    def openCom(self):
        try:
            print("Opening Serial Port ...>>>")
            self.sp = serial.Serial(port=self.pn, baudrate=9600, bytesize=serial.EIGHTBITS,
                                    parity=serial.PARITY_NONE, timeout=1, stopbits=serial.STOPBITS_ONE)
        except:
            print("Port Open Failed")

    def writeCom(self,str):
        self.sp.write(str)

    def readCom(self):
        rstr = self.sp.readline().decode('utf-8')
        return rstr


    

def isPortUsable(pname):
    try:
        ser = serial.Serial(pname)
        return True
    except:
        return False



def validCom(pname):
    if(len(pname) <= 6 and len(pname) >= 4):
        cname = pname[:3]
        cnum = pname[3:]
        if(cname.upper() == "COM"):
            if(cnum.isdigit()):
                pn = int(cnum)
                if(pn >= 1 and pn <= 255):
                    return True
    return False



def validPort(ststr):
    if(ststr.lower() == "port"):
        return True
    else:
        return False


def validPn(ststr):
    if(ststr.isdigit()):
        pn = int(ststr)
        if(pn >= 1 and pn <= 2):
            return True
        else:
            return False
    else:
        return False

def validOpr(strpn, stropr):
    if(stropr.lower() == "on"):
        return strpn
    elif(stropr.lower() == "off"):
        return "0"
    else:
        return ""


def validStatus(ststr):
    if(ststr.lower() == "status"):
        return True
    else:
        return False


def validSn(ststr):
    if(ststr.lower() == "sn"):
        return True
    else:
        return False


def sendPortCmd(pname,cmd):
    sc.setCom(pname)
    sc.openCom()
    sc.writeCom(cmd.encode())
    rstr = sc.readCom()
    print(rstr)
    


def sendStatCmd(pname):
    sc.setCom(pname)
    sc.openCom()
    sc.writeCom(b'status\r\n')
    st.kickstart()
    
def sendSnCmd(pname):
    sc.setCom(pname)
    sc.openCom()
    sc.writeCom(b'sn\r\n')
    rstr = sc.readCom()
    print(rstr)
    


def readComT():
    rstr = sc.readCom()
    #print(len(rstr))
    if(len(rstr) == 0):
        st.cancel()
    else:
        print(rstr)

     

if __name__ == '__main__':
    sp = None
    sc = McciSerial()
    st = SerialTimer(0.05, readComT)
    cnt = 0;
    bname = None

    nags = len(sys.argv)
    if(nags <= 2 or nags >=6):
        print("Invalid command format !!!")
        sys.exit()
    elif(nags == 3):
        if(validCom(sys.argv[1])):
            if(validStatus(sys.argv[2])):
                sendStatCmd(sys.argv[1])
                sys.exit()
            elif(validSn(sys.argv[2])):
                sendSnCmd(sys.argv[1])
                sys.exit()
    elif(nags == 4):
        validCom(sys.argv[1])
    elif(nags == 5):
        if(validCom(sys.argv[1])):
            if(validPort(sys.argv[2])):
                if(validPn(sys.argv[3])):
                    rstr=validOpr(sys.argv[3], sys.argv[4])
                    if(rstr):
                        cmd = 'port'+' '+rstr+'\r\n'
                        sendPortCmd(sys.argv[1], cmd)
                    
                        
                
            
   
