# CricketUI

Simple standalone desktop application for handling MCCI USB Switches in a convenient way. it Supports MCCI USB Switch3141, 3201, 2301 and 2101 USB Connection Exerciser.

<!-- /TOC -->
[![Git release](https://img.shields.io/badge/release-v2.5.0-blue)](https://github.com/mcci-usb/COLLECTION-cricket-ui/releases/) [![Git commits](https://img.shields.io/badge/commits%20since%20v2.5.0-4-blue)](https://github.com/mcci-usb/COLLECTION-cricket-ui/compare/v2.5.0...master)
<!-- markdown-shield -->


## List of Contents

<!-- TOC depthFrom:2 updateOnSave:true -->

- [About Application](#about-application)
- [Prerequisites for running or building](#prerequisites-for-running-or-building)
- [Interpret python source](#interpret-python-source)
- [Version change process](#version-change-process)
- [GUI Preview](#gui-preview)
- [MCCI USB Switch 3201 Enhanced type-c connection exerciser](#To-know-about-MCCI-USB-Model3201)
- [MCCI USB Switch 3141 usb switch](#To-know-about-MCCI-USB-Model3141)
- [MCCI USB Switch 2101 usb connection exerciser](#To-know-about-MCCI-USB-Model2101)
- [MCCI USB Switch 2301 usb connection exerciser](#To-know-about-MCCI-USB-Model2301)
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
* matplotlib - 1.16.0
* pyinstaller - 3.6 

Download [python3.7.6](https://www.python.org/downloads/release/python-376/) and install

```shell
pip install wxpython==4.0.7.post2
pip install pyserial
pip install pyusb
pip install libusb
pip install libusb1
pip install matplotlib
pip install pyinstaller
```

<strong>On Linux OS:</strong>

Development environment

* Linux OS - Ubuntu 16.04 64 bit
* Python - 3.8.2
* Mac OS - Cataina V10.15.7 64 bit
* Python - 3.7.0
* wxpython - 4.0.7.post2
* pyserial - 3.4
* pyusb - 1.0.2
* libusb - 1.0.22b9
* libusb1 - 1.8
* matplotlib - 3.5
* pyinstaller - 4.6

```shell
sudo apt-get update
sudo apt-get install python3
sudo apt-get install python3-pip
sudo pip3 install wxpython==4.0.7.post2
sudo pip3 install pyserial
sudo pip3 install pyusb
sudo pip3 install libusb
sudo pip3 install libusb1
sudo pip3 install matplotlib
sudo pip3 install pyinstaller
```

Note:
* If the installation of wxpython is not success, perform `sudo apt-get install build-essential libgtk-3-dev`
* Some times the installation of wxpython takes longer time (>30 minutes).

<strong>On Mac OS:</strong>

Development environment

* Mac OS - Catalina 10.15.7 64 bit
* Python - 3.6.9
* wxpython - 4.0.7.post2
* pyserial - 3.4
* pyusb - 1.0.2
* libusb - 1.0.22b9
* libusb1 - 1.8
* matplotlib - 3.2.2 
* pyinstaller - 4.6
* hidapi - 0.10.1  - Only for Mac OS

```shell
sudo apt-get update
sudo apt-get install python3
sudo apt-get install python3-pip
sudo pip3 install wxpython==4.0.7.post2
sudo pip3 install pyserial
sudo pip3 install pyusb
brew install libusb
sudo pip3 install libusb1
sudo pip3 install matplotlib
sudo pip3 install pyinstaller
brew install hidapi - Only for Mac OS
```

<strong>On RaspberryPI:</strong>

Development environment

* Raspberry Pi OS - aarch64 in Ubuntu 20.04 bit
* Python - 3.6.9
* wxgtk-4.0
* pyserial - 3.5
* pyusb - 1.1.1
* libusb - 1.0.23b7
* libusb1 - 1.9
* matplotlib - 1.14.0
* pyinstaller - 4.2

```shell
sudo add-apt-repository ppa:swt-techie/wxpython4
sudo apt-get update
sudo apt-get install python3-wxgtk4.0
sudo pip3 install pyserial
sudo pip3 install pyusb
sudo pip3 install libusb
sudo pip3 install libusb1
sudo pip3 install matplotlib
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

For Linux
```shell
python3 main.py
```

For Mac
```shell
python3.6 main.py
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

## To know about MCCI USB Switch 3201

MCCI USB Switch 3201 Enhanced Type-C Connection Exerciser 

* The MCCI USB Switch 3201 Enhanced Type-C Connection Exerciser (MUTT ConnEX-C) plugs and unplugs up to 4 devices for automated testing of USB Type-C® products. Developed in conjunction with Microsoft, the 3201 is upward compatible with the MCCI Model 3101/Model 3201 Connection Exercisers and the Microsoft MUTT ConnEx-C, but has a number of significant enhancements and improvements.

 **Link:** For more information, see the product home page at [MCCI USB switch 3201 Enhanced type-c connection exerciser](https://mcci.com/usb/dev-tools/3201-enhanced-type-c-connection-exerciser/)
 
   ![Model3201-typeC](assets/Model3201.png)
   
 ## To know about MCCI USB Switch 3141

MCCI USB Switch 3141

* The MCCI® USB 3141 USB4™ Switch is a computer-controlled programmable 2:1 switch, connecting two USB Type-C receptacles to a single Type-C plug. It is compatible with USB4 hosts and devices, as well as older protocols such as Thunderbolt™ 3, USB 3.2 gen2 or gen1, USB 2.0, USB Type-C Alternate Modes, and of course Power Delivery. 
The MCCI USB Switch 3141 USB4 Switch automates connect/disconnect of one or two devices to a USB Type-C port. It can be used in stress testing, switching between peripherals (for example, a dock and a display), or any automated reconfiguration of a USB Type-C port

 **Link:** For more information, see the product home page at [MCCI USB Switch 3141 usb switch](https://mcci.com/usb/dev-tools/model-3141/).
 
  ![Model3141-typeC](assets/TypeC3141.PNG)
  
## To know about MCCI USB Switch 2101

MCCI USB Switch 2101 USB Connection Exerciser

* The MCCI USB 3.0 Connection Exerciser MCCI USB Switch 2101 automatically connects and disconnects a USB 2.0 or 3.2 gen1 host and device under push-button or software control. Connections can be single-stepped or repeated. The manual modes are useful for debugging attach/detach scenarios.  
The MCCI USB 3141 USB4 Switch automates connect/disconnect of one or two devices to a USB Type-C port. It can be used in stress testing, switching between peripherals (for example, a dock and a display), or any automated reconfiguration of a USB Type-C port

 **Link:** For more information, see the product home page at [MCCI USB Switch 2101 usb connection exerciser](https://mcci.com/usb/dev-tools/2101-usb-connection-exerciser/).
 
  ![Model3201](assets/Model2101.png)
  
  ## To know about MCCI USB Model2301

MCCI USB Switch 2301 Type-A USB 3.2 Gen2 Connection Exerciser

* The MCCI USB Switch 2301 Type-A Connection Exerciser provides a four-to-one USB switch to automate interoperability tests for systems USB 3.2 gen1 or gen2. It uses the supplied Arduino-based controller and electronic switches to electrically plug and unplug any of the four different input ports. The Gen2-capable Type-B plug can be connected to either of two Type-A receptacles, to a Standard-A receptacle (USB 2.0 only), or a Micro-B receptacle (USB 2.0 only). The Type-A Gen2 receptacles support USB 3.2 (gen 1 and gen 2) and USB 2.0 (high speed, full speed and low-speed) devices. The Standard-A receptacle supports USB 2.0 devices. . For more information, see the product home page at www.mcci.com.

 **Link:** For more information, see the product home page at [MCCI Switch 2301 usb connection exerciser](https://mcci.com/usb/dev-tools/model-2301/).

 ![Model2301](assets/Model2301.png)

 ## Release History
- HEAD has the following changes.
  - misspelling in the log window instead of Switch it was spelled as Swicth [#61](https://github.com/mcci-usb/Cricket/commit/1344384596efdfd3288ef40bea38c8149b2039f6).
- v2.5.0 is major release; it Contains the following changes
  -	Feature added – Plotting of VBUS Volt and Current `VBUS V/I Plotting` [#18 #48 #52](https://github.com/mcci-usb/Cricket/commit/eb30f3b4a2e1da2c21db470315a8489b19d7b87d).
  - USB Tree view removed and merged with Logwindow `Replaced USB Tree view window to Log Window` [#24](https://github.com/mcci-usb/Cricket/issues/24).
  - Perform device Search in advance, Device searching automatically or manually seaching the device `USB Switch Scanning` [#30](https://github.com/mcci-usb/Cricket/issues/30).
  - Auto mode improved (Port selection provided) `Port(s) selection ` [#22](https://github.com/mcci-usb/Cricket/issues/22) also with out port selection start auto popUp window appear ` PopUp window` [#Auto Popupwindow](https://github.com/mcci-usb/Cricket/commit/f44494cc7b4295b10480be373afbf4987dc6383f).
  - Linux machine IP scanning issue fixed `Scanning ip address from Linux machine ` [#20](https://github.com/mcci-usb/Cricket/issues/20).
  - The word Model replace by MCCI USB Switch `Replace MCCI USB Switch ` [#27](https://github.com/mcci-usb/Cricket/issues/27).
  - UI not responding issued fixed `UI not Responding ` [#28](https://github.com/mcci-usb/Cricket/issues/28).
  - Do not disable Manage Model>Connect when connected allow the user to directly connect to another switch `Connect menu` [#30](https://github.com/mcci-usb/Cricket/commit/d3077b5b2925553a505955d5721673705438d464). 
  - Enhancement – Highlight the name of the     Switch `Highlet Switch` [#29](https://github.com/mcci-usb/Cricket/issues/29).
  - added Finished count in Loop Mode `Finished Count ` [#23](https://github.com/mcci-usb/Cricket/issues/23).
  - Persistence of last connect `Last device connect `[#43](https://github.com/mcci-usb/Cricket/commit/2bf73805fe274e27fb775b18c4bc639828a60347)
  - Application gets hung when closing the application by using Mac Using Quit cmd `Quit Commad on Mac` [40](https://github.com/mcci-usb/Cricket/commit/2e34f30771b6dbfcf5c6bc7de9da4db7e0b7f8bb).
  - click on the settings menu, then click on the "Switch Control Computer" sub menu, this should display a dialog for searching the Computer over the network based on the port assigned for that. But dialog does not appearing `SCC and THC Setting menu search dialog not displayed - In Mac Catalian and Monterey` [#41](https://github.com/mcci-usb/Cricket/commit/e114a2bf9bb13968388f2e898b21dc2c6913edbd).
  - UI panel are not centralized `fixed UI in Central on window` [45](https://github.com/mcci-usb/Cricket/commit/755384805f0d05bce7fff4d0089f664812314f94).
  - Port selection should be disable state once the Auto mode execution get started, then the required ports are should be enabled when auto mode gets stopped `Disable the port selection when auto mode is under execution` [#50](https://github.com/mcci-usb/Cricket/commit/e45dac8e266632c75c72a7e88318fcec9a309f3c)
  - update Cricket UI Windows.spec file with One directory file `Update Cricket-Windows.spec file` [#47](https://github.com/mcci-usb/Cricket/commit/e6cfdb6fcab0714af319b37243b0895af50a4dfc).

  - Update year in the copy right info `Update copy right info in About dialog` [#53](https://github.com/mcci-usb/Cricket/commit/3530af09d231fc8ae9ffc6f47fd29bcfea5a329e)

- v2.4.0 is major release; changes are significant  to Networking protocol TcpIp.
  - Add new feature support for Three computer System and Two Computer `Two and Three Computer system through Networking ` [#14](https://github.com/mcci-usb/Cricket/pull/14/commits/931f867960b375b07b980b61e39ab32bba4dfb35).

- v2.3.0 is major release has following changes.
  - Add support for MCCI Switch 2301 USB Connection Exerciser ` MCCI USB Switch 2301 ` [#4](https://github.com/mcci-usb/Cricket/pull/4).

- v2.2.0 has following changes:

  - Python implemented to Pep8 coding standard ` MCCI USB Switch 2301 ` [#5](https://github.com/mcci-usb/Cricket/pull/5).
  - Package release for Raspberry Pi OS ubuntu18.04

- v2.0.0 has major release 

  - Interface for USB Switch 2101 added
  - Radio buttons for Port switching replaced by  image added buttons,
  - Duty parameter added in auto mode,
  - Until stopped and Port selection option added to the Loop mode and separate panel for Auto mode added, 
  - adding USB speed info, increase port switching speed.

- v1.2.0 has folloeing changes

  - Host Controller issue and Delay override

- v1.0.2 is a changes to menu option

  - Mac Menu Update 

- v1.0.0 initial release of cricket UI

  - Initial Release

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
