# CorSense BLE
An interface for reading HR and HRV data from corSense device by EliteHRV in real-time using Bluetooth Low Energy (BLE).

## Requirements
This code is implemented using [bluePy](https://github.com/IanHarvey/bluepy) python package; thus, the current script works on Linux OS.

## HRV Real-Time Acqusition from CorSense
Artefact detection is based on a moving window of median RR values

<img src="https://github.com/Mar-iam/corSense/blob/master/corsense/images/RR.gif" width="300">
