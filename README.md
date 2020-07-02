# UI-3141-3201

## About Application

This application is designed to create simple User Interface for USB Switch 3141 and 3201 , to make the user's interaction as simple and efficient as possible.

## Prerequisites for running or building

### Windows

* python 3.* (Installation steps [here](https://realpython.com/installing-python/))
* pip install wxpython==4.0.7.post2
* pip install pyserial
* pip install pyusb
* pip install libusb
* pip install libusb1
* pip install pyinstaller

### Linux and Mac

* python 3
* sudo apt-get install pip3
* sudo pip3 install wxpython==4.0.7.post2
* sudo pip3 install pyserial
* sudo pip3 install pyusb
* sudo pip3 install libusb
* sudo pip3 install libusb1
* sudo pip3 install pyinstaller

## Build and Package creation
Pyinstaller -  Interprets the python script, bundles the application with its dependencies and provide a stand-alone executable.

### Windows and Linux
* 'pyinstaller --distpath ./exeout/ --workpath ./exeout/build/ -F -w -i=./icons/mcci_logo.ico main.py -n UI3141-3201' .

### Mac
* 'pyinstaller --distpath ./exeout/ --workpath ./exeout/build/ -F -w -i=./icons/mcci_logo.icns main.py -n UI3141-3201' .

*  This will create a executable file 'UI3141-3201' in the 'exeout' folder.

## Installer setup
### Windows
Inno Setup - Installer which creates single exe to install the application in the OS.

* Install Inno Setup compiler-6.0.5 (Download stable release [here](https://jrsoftware.org/isdl.php#stable)
* Run the iss script file 'UI3141-Installer-Windows'

The Inno setup script takes the application exe 'UI3141-3201' from 'exeout' folder and leavs the installtion exe 'UI3141-3201-Windows' in the 'AppInstaller' folder	

### Mac
Packages - Installer which repackages altogether in the PKG format


