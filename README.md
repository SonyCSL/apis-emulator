# apis-emulator

## Introduction
The Emulator runs a computer emulation that reproduces the hardware system for energy sharing, including the battery system and the DC/DC converter, etc. The Emulator reads in data on the amount of solar radiation and the power consumption of residences and emulates the flow of energy such as the power generated and consumed by multiple residences, and battery system charging and discharging. The emulation conditions can be changed in real time by using a Web browser to access and change the hardware parameters. There is also a function for communication with apis-main, which reads storage battery data from the hardware emulation on the computer and operates the DC/DC converter to emulate energy sharing.

Refer to the [apis-emulator_specification](#anchor1)  for more information.

![apis-emulator](https://user-images.githubusercontent.com/71874910/94903858-60973700-04d5-11eb-8d60-c0bdbbec9b4a.PNG)

![apis-emulator2](https://user-images.githubusercontent.com/71874910/94904048-ace27700-04d5-11eb-9dec-f144644dbf44.PNG)


## Installation
Here is how to install apis-emulator individually.  

```bash
$ git clone https://github.com/SonyCSL/apis-emulator.git
$ cd apis-emulator
$ python3 -m venv venv 
$ . venv/bin/activate
$ pip install --upgrade pip
$ pip install -r requirements.txt
$ deactivate
```

## Running
Here is how to run apis-emulator individually.  

```bash
$ cd apis-emulator
$ . venv/bin/activate
$ python3 startEmul.py 4
　(The last number is the number of hardware you want to emulate.)
```

## Stopping
Here is how to stop apis-emulator individually.  

```bash
$ bash stop.sh
$ deactivate
```
<a id="anchor1"></a>
## Documentation
&emsp;[apis-emulator_specification(EN)](https://github.com/SonyCSL/apis-emulator/blob/master/doc/en/apis-emulator_specification_en.md)  
&emsp;[apis-emulator_specification(JP)](https://github.com/SonyCSL/apis-emulator/blob/master/doc/jp/apis-emulator_specification.md)


## License
&emsp;[Apache License Version 2.0](https://github.com/oes-github/apis-emulator/blob/master/LICENSE)

## Notice
&emsp;[Notice](https://github.com/oes-github/apis-emulator/blob/master/NOTICE.md)
