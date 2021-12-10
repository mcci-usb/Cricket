# CricketUI

Simple standalone desktop application for handling MCCI USB Switches in a convenient way. it Supports MCCI USB Switch3141, 3201, 2301 and 2101 USB Connection Exerciser.

<!-- /TOC -->
[![Git release](https://img.shields.io/badge/release-v2.4.0-blue)](https://github.com/mcci-usb/COLLECTION-cricket-ui/releases/) [![Git commits]<!-- markdown-shield -->


## List of Contents

<!-- TOC depthFrom:2 updateOnSave:true -->

- [About Application](#about-application)
- [Prerequisites for running or building](#prerequisites-for-running-or-building)
- [Interpret python source](#interpret-python-source)
- [Version change process](#version-change-process)
- [GUI Preview](#gui-preview)
- [3201 Enhanced type-c connection exerciser](#To-know-about-MCCI-USB-Model3201)
- [model 3141 usb switch](#To-know-about-MCCI-USB-Model3141)
- [model 2101 usb connection exerciser](#To-know-about-MCCI-USB-Model2101)
- [model 2301 usb connection exerciser](#To-know-about-MCCI-USB-Model2301)
- [Release History](#release-history)
- [Meta](#meta)
  - [Copyright and License](#Copyright-and-License)
  - [Support Open Source Hardware and Software](#support-open-source-hardware-and-software)
  - [Trademarks](#trademarks)

<!-- /TOC -->

## About Application

This application is designed to create simple User Interface for USB Switch 3141 3201, 2101 and 2301 to make the user's interaction as simple and efficient as possible.

It is a cross platform GUI application developed by using WxPython.

## Prerequisites for running or building

<strong>On Windows:</strong>

Development environment

* OS - Windows 10 64 bit
* Python - 3.7.6
* wxpython - 4.0.7.post2
* pyserial - 3.4
* pyusb - 1.0.2
* libusb - 1.0.22b9
* libusb1 - 1.8
* pyinstaller - 3.6 

Download [python3.7.6](https://www.python.org/downloads/release/python-376/) and install

```shell
pip install wxpython==4.0.7.post2
pip install pyserial
pip install pyusb
pip install libusb
pip install libusb1
pip install pyinstaller
```

<strong>On Linux and Mac:</strong>

Development environment

* Linux OS - Ubuntu 20.04 64 bit
* Python - 3.8.2
* Mac OS - High Sierra 10.13.6 64 bit
* Python - 3.7.0
* wxpython - 4.0.7.post2
* pyserial - 3.4
* pyusb - 1.0.2
* libusb - 1.0.22b9
* libusb1 - 1.8
* pyinstaller - 3.6  
* hidapi - 0.10.1  - Only for Mac OS

```shell
sudo apt-get update
sudo apt-get install python3
sudo apt-get install python3-pip
sudo pip3 install wxpython==4.0.7.post2
sudo pip3 install pyserial
sudo pip3 install pyusb
sudo pip3 install libusb
sudo pip3 install libusb1
sudo pip3 install pyinstaller
brew install hidapi - Only for Mac OS
```

Note:
* If the installation of wxpython is not success, perform `sudo apt-get install build-essential libgtk-3-dev`
* Some times the installation of wxpython takes longer time (>30 minutes).

<strong>On RaspberryPI:</strong>

Development environment

* Raspberry Pi OS - aarch64 in Ubuntu 20.04 bit
* Python - 3.6.9
* wxgtk-4.0
* pyserial - 3.5
* pyusb - 1.1.1
* libusb - 1.0.23b7
* libusb1 - 1.9
* pyinstaller - 4.2

```shell
sudo add-apt-repository ppa:swt-techie/wxpython4
sudo apt-get update
sudo apt-get install python3-wxgtk4.0
sudo pip3 install pyserial
sudo pip3 install pyusb
sudo pip3 install libusb
sudo pip3 install libusb1
sudo pip3 install pyinstaller
```

Note:
* If the installation of wxpython is not success, perform `sudo apt-get install build-essential libgtk-3-dev`

## Interpret python source

Move to the directory `destdir/src/`

Run the below command

For Windows 
```shell
python main.py  
```

For Linux and Mac
```shell
python3 main.py
```

For RaspberryPi
```shell
python3 main.py
```

## Version change process

To update the version for each release

* Move to the directory `destdir/src/`
* Open the file `uiGlobals.py`
* Update the value of the String Macro `APP_VERSION`
* Update the VERSION.md `destdir/VERSION.md`

## GUI Preview

![UI Preview](assets/CricketUI.png)

## To know about MCCI USB Model3201

MCCI Model 3201 Enhanced Type-C Connection Exerciser 

* The MCCI Model 3201 Enhanced Type-C Connection Exerciser (MUTT ConnEX-C) plugs and unplugs up to 4 devices for automated testing of USB Type-C® products. Developed in conjunction with Microsoft, the 3201 is upward compatible with the MCCI Model 3101/Model 3201 Connection Exercisers and the Microsoft MUTT ConnEx-C, but has a number of significant enhancements and improvements.

 **Link:** For more information, see the product home page at [3201 Enhanced type-c connection exerciser](https://mcci.com/usb/dev-tools/3201-enhanced-type-c-connection-exerciser/)
 
   ![Model3201-typeC](assets/Model3201.png)
   
 ## To know about MCCI USB Model3141

MCCI Model 3141 USB Switch

* The MCCI® Model 3141 USB4™ Switch is a computer-controlled programmable 2:1 switch, connecting two USB Type-C receptacles to a single Type-C plug. It is compatible with USB4 hosts and devices, as well as older protocols such as Thunderbolt™ 3, USB 3.2 gen2 or gen1, USB 2.0, USB Type-C Alternate Modes, and of course Power Delivery. 
The Model 3141 USB4 Switch automates connect/disconnect of one or two devices to a USB Type-C port. It can be used in stress testing, switching between peripherals (for example, a dock and a display), or any automated reconfiguration of a USB Type-C port

 **Link:** For more information, see the product home page at [model 3141 usb switch](https://mcci.com/usb/dev-tools/model-3141/).
 
  ![Model3141-typeC](assets/TypeC3141.PNG)
  
## To know about MCCI USB Model2101

MCCI Model 2101 USB Connection Exerciser

* The MCCI USB 3.0 Connection Exerciser Model 2101 automatically connects and disconnects a USB 2.0 or 3.2 gen1 host and device under push-button or software control. Connections can be single-stepped or repeated. The manual modes are useful for debugging attach/detach scenarios.  
The Model 3141 USB4 Switch automates connect/disconnect of one or two devices to a USB Type-C port. It can be used in stress testing, switching between peripherals (for example, a dock and a display), or any automated reconfiguration of a USB Type-C port

 **Link:** For more information, see the product home page at [model 2101 usb connection exerciser](https://mcci.com/usb/dev-tools/2101-usb-connection-exerciser/).
 
  ![Model3201](assets/Model2101.png)
  
  ## To know about MCCI USB Model2301

MCCI Model 2301 Type-A USB 3.2 Gen2 Connection Exerciser

* The MCCI Model 2301 Type-A Connection Exerciser provides a four-to-one USB switch to automate interoperability tests for systems USB 3.2 gen1 or gen2. It uses the supplied Arduino-based controller and electronic switches to electrically plug and unplug any of the four different input ports. The Gen2-capable Type-B plug can be connected to either of two Type-A receptacles, to a Standard-A receptacle (USB 2.0 only), or a Micro-B receptacle (USB 2.0 only). The Type-A Gen2 receptacles support USB 3.2 (gen 1 and gen 2) and USB 2.0 (high speed, full speed and low-speed) devices. The Standard-A receptacle supports USB 2.0 devices. . For more information, see the product home page at www.mcci.com.

 **Link:** For more information, see the product home page at [model 2301 usb connection exerciser](https://mcci.com/usb/dev-tools/model-2301/).

 ![Model2301](assets/Model2301.png)

 ## Release History

 - v1.0.0 Initial Release

 - v1.0.2 Mac Menu Update

 - v1.2.0 Host Controller issue and Delay override

 - v2.0.0 Interface for USB Switch 2101 added, Radio buttons for Port switching replaced by  image added buttons, Duty parameter added in auto mode, Until stopped and Port selection option added to the Loop mode and separate panel for Auto mode added, adding USB speed info, increase port switching speed.

 - v2.2.0 Python implemented to Pep8 coding standard.
 Package release for Raspberry Pi OS ubuntu18.04

 - v2.3.0 Add support for Model 2301 USB Connection Exerciser 

 - v2.4.0 Add new feature support for Three computer System and Two Computer System


 ## Meta

### Copyright and License

Except as explicitly noted, content created by MCCI in this repository tree is copyright (C) 2021, MCCI Corporation.

The Cricket UI is released under the terms of the attached [GNU General Public License, version 2](./LICENSE.md). `LICENSE.md` is taken directly from the [FSF website](http://www.gnu.org/licenses/old-licenses/gpl-2.0.md).

Commercial licenses and commercial support are available from MCCI Corporation.

Git submodules are subject to their own copyrights and licenses; however overall collection is a combined work, and is copyrighted and subject to the overall license.

### Support Open Source Hardware and Software

MCCI invests time and resources providing this open source code, please support MCCI and open-source hardware by purchasing products from MCCI and other open-source hardware/software vendors!

For information about MCCI's products, please visit [store.mcci.com](https://store.mcci.com/).

### Trademarks

MCCI and MCCI Catena are registered trademarks of MCCI Corporation. All other marks are the property of their respective owners.
