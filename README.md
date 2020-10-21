# apis-emulator

## Introduction
Emulatorは蓄電池や電力融通用DC/DC Converter等を含んだハードウェア環境をコンピュータ上で再現し、
日射量と住宅の消費電力量情報を読み込み、複数の住宅の発電と消費、蓄電池の充放電等の電力の流れを
エミュレーションすることが可能である。さらにブラウザからEmulatorにアクセスすることで再現された
ハードウェア環境のパラメータを容易に変更することができるため、リアルタイムに条件を変えて
エミュレーションを実施することが可能である。また、apis-mainとの通信機能も有しており、
apis-mainはコンピュータ上で再現されたハードウェア環境から蓄電池の情報を読み取ったり
DC/DC Converterを操作したりして電力融通のエミュレーションを行うことが可能である。

![apis-emulator](https://user-images.githubusercontent.com/71874910/94903858-60973700-04d5-11eb-8d60-c0bdbbec9b4a.PNG)

![apis-emulator2](https://user-images.githubusercontent.com/71874910/94904048-ace27700-04d5-11eb-9dec-f144644dbf44.PNG)


## Installation
Here is how to install apis-emulator individually.  
This software runs in Python2.7.

```bash
$ git clone https://github.com/SonyCSL/apis-emulator.git
$ cd apis-emulator
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Running
Here is how to run apis-emulator individually.  

```bash
$ cd apis-emulator
$ source venv/bin/activate
$ python startEmul.py 4
　(The last number is the number of hardware you want to emulate.)
```

## Documentation
&emsp;[apis-emulator_specification(JP)](https://github.com/SonyCSL/apis-emulator/blob/master/doc/jp/apis-emulator_specification.md)


## License
&emsp;[Apache License Version 2.0](https://github.com/oes-github/apis-emulator/blob/master/LICENSE)

## Notice
&emsp;[Notice](https://github.com/oes-github/apis-emulator/blob/master/NOTICE.md)
