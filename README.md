# pyzkfp


[![PyPI version](https://badge.fury.io/py/pyzkfp.svg)](https://badge.fury.io/py/pyzkfp)

## Overview
This is a python wrapper library of the ZKTeco SDK.

## Compatibility
This library can connect to `SLK20R` and ZK series, including `ZK9500`, `ZK6500`, `ZK8500R` devices.
 
## Installation
On linux and MacOS: A .NET (or Mono) runtime is required. Windows is equipped with one by default
- You have to first install the ZKFinger SDK from the offical website [here](https://www.zkteco.com/en/Biometrics_Module_SDK/) 
- Then install this library:
    ```bash
    pip install pyzkfp
    ```

## Features
- Initialize and interact with ZKFinger Reader devices.
- Capture fingerprint images.
- Perform fingerprint 1:1 comparisons.
- Perform fingerprint 1:N comparisons.
- Show captured fingerprints (reuqires Pillow).
- Register/Delete fingerprints to and from the device's DB.
- Identify users' fingerprints.
- Light & Beep control functions.

## Note
This repo doesn't follow the naming conventions of Python. This repo doesn't implmenet or add any extra functionalties. It's just a binding to the C# executable. 
This library is fully compatible with zkteco's documentation (found inside the SDK zip file), you can read them to learn more. 

## Usage
Here's a simple example of how to use this library:

#### Initialize the ZKFP2 class and open the device
```python
from pyzkfp import ZKFP2


zkfp2 = ZKFP2()
zkfp2.Init() # Initialize the ZKFP2 class

# Get device count and open first device
device_count = zkfp2.GetDeviceCount()
print(f"{device_count} devices found")
zkfp2.OpenDevice(0) # connect to the first device
```

### Capture a fingerprint
```python
while True:
    capture = zkfp2.AcquireFingerprint()
    if capture:
        # Implement your logic here
        break
```

### Perform a 1:N comparison
```python
tmp, img = capture
fingerprint_id, score = zkfp2.DBIdentify(tmp)
```

### Perform a 1:1 comparison
Usually used to make sure the same finger is scanned throughout the fingerprint registration process. 
```python
res = zkfp2.DBMatch(template1, template2) # returns 1 if match, 0 if not
```

### Register a fingerprint
In order to register a fingerprint, we must collect a bunch of (ideally 3) fingerprints of the same finger. And then we can merge them into one template and store it in the device's database.
```python
templates = []
for i in range(3):
    while True:
        capture = zkfp2.AcquireFingerprint()
        if capture:
            print('fingerprint captured')
            tmp, img = capture
            templates.append(tmp)
            break
regTemp, regTempLen = zkfp2.DBMerge(*templates)

# Store the template in the device's database
finger_id = 1 # The id of the finger to be registered
zkfp2.DBAdd(finger_id, regTemp)
```

### Storing and Loading Templates from an External Database for Future Use

Given that the device's memory clears upon shutdown, this step is crucial for preserving data. You have the option to store `regTemp` (the final result of the the three merged templates) in your preferred database to retrieve them for later use. The segment of code responsible for loading the registered templates from the database to the device's memory should be run after the device's initialization. Here is a simple way to do it.

```python

members = ... # load members' regTemp and their corresponding fingerprint_id from your database.

for member in members:
    fid, temp = member
    zkfp2.DBAdd(fid, temp)
    ...  
```

### Display a fingerprint
```python
tmp, img = capture
zkfp2.show_image(img) # requires Pillow lib
```

### Turn on/off the light
```python
zkfp2.Light('green') # green/red/white
```

### Terminate the device and release resources
```python
zkfp2.Terminate()
```

For more detailed usage instructions, please refer to the example folder (WIP).

