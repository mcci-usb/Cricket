# UI-3141-3201

## About Application

This application is designed to create simple User Interface for USB Switch 3141 and 3201 , to make the user's interaction as simple and efficient as possible.

## Required

### Development environment 
* python 3.7.6
* wxPython 4.0.7.post2
* pyserial 3.4
* pyusb 1.0.2
* libusb1 1.7.1 

#### Installation
* python 3.* (Installation steps [here](https://realpython.com/installing-python/))
* pip install wxpython
* pip install pyserial
* pip install pyusb
* pip install libusb1

#### Web link
* wxPython  (https://wxpython.org/), (https://pypi.org/project/wxPython/)
* pyserial  (https://pypi.org/project/pyserial/)
* pyusb     (https://pypi.org/project/pyusb/)
* libusb1   (https://pypi.org/project/libusb1/)

### Exe creation (Pacakaged App)
Pyinstaller bundles a Python application and all its dependencies into a single package. The user can run the pacakged app without installing a Pyhton interpreter or any modules.
Pyinstaller is distributed under GPL License 

	Installation command
	* pip install pyinstaller
	* Link - (https://pypi.org/project/PyInstaller/)

	Command to build exe
	* 'pyinstaller --onefile --windowed --icon=mcci_logo.ico main.py' .
	   This will create a executable file in the 'dist' folder.
  
### Installation setup creation
Inno Setup Compiler is a free installer application, user need to setup this application with the executable file created through Pyinstaller and other dependcies required for the UI application.
* Link - (https://jrsoftware.org/isinfo.php)
