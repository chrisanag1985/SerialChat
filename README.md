# SerialChat

Python Multithreading Chat over Serial Port with Qt interface and Encryption

---
## Description
The purpose of this project is to provide a **multi-threading** chat application with a friendly qt interface. 

The idea behind *serialChat* is **half-duplex** communication over radio through serial port.

The *serialChat* is use **Python 2.7**

---
## Dependencies
The *serialChat* depends on *pyside* project which is available on:


pip:
```bash
pip2 install pyside
```

the *pyserial* project:

__github__:
https://github.com/pyserial/pyserial


**For compatibility issues with WIN_XP it uses pyserial v2.7**

**It doesn't work with higher versions of pyserial.**


__pip__ :



```bash
pip2 install pyserial==2.7
```

the *playsound*:

**pip**:

```bash
pip2 install playlinux
```


and the *pycrypto* :

__pip__:

```bash
pip2 install pycrypto
```
**SOS** to install pycrypto on windows XP it required to install first the Microsoft Visual C++ 9 for Python 2.7 from the internet

**OR just:**
 
```bash
pip2 install -r requirements.txt
```

---


## Installation
There is no need for installation process.

Just clone the project to your computer and run the **serialChat.py**
```bash
python2.7 serialChat.py
```

**Tested on:**
 
* WIN_XP
* WIN7
* WIN10 
* Linux

---

## Create Executable File ( OneFile ) 

```bash
pip install pyinstaller
```
Inside the folder of SerialChat enter the command

```bash
pyinstaller --noconsole --onefile --icon resources\icons\chat.ico serialChat.py
```
Now put the **serialChat.exe** from the folder **dist** in the same folder with the folders **config** and **resources** and then you will able to run the serialChat by clicking on the **serialChat.exe**

---

## Usage


After you start the application, you can go to the *settings* menu item and configure the *serialChat* with your specific configuration.

1. Choose your serial port from the dropdown list.
2. Change the serial port configuration to your needs.
3. Enable ACP-127 text based protocol (optional).
4. Enable AES-CBC encryption (optional).
5. Enter your nickname.
6. Change the path with one that you wish the incoming files to be saved. 


Then you're ready to GO...

