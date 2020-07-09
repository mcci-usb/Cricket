# UI-3141-3201

## About Application

This application is designed to create simple User Interface for USB Switch 3141 and 3201 , to make the user's interaction as simple and efficient as possible.

It is a cross platform GUI application developed by using WxPython.

## Prerequisites for running or building

<strong>On Windows:</strong>

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

```shell
sudo apt-get install python3
sudo apt-get install pip3
sudo pip3 install wxpython==4.0.7.post2
sudo pip3 install pyserial
sudo pip3 install pyusb
sudo pip3 install libusb
sudo pip3 install libusb1
sudo pip3 install pyinstaller
```

## Interpret python source

Traverse to 'src' folder

Run the below command

For Windows 
```shell
'python main.py'  
```

For Linux and Mac
```shell
'python3 main.py'
```

## GUI Preview

![UI Preview](assets/UI-3141_3201.png)