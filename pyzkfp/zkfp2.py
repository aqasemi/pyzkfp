from threading import Thread
from time import sleep

import clr

from .errors_handler import *
from ._construct.zkfp import *

try:
    from PIL import Image
except ImportError:
    pass

from io import BytesIO
from base64 import b64encode

clr.AddReference("libzkfpcsharp")
clr.AddReference("System")

from System import Array, Byte # ignore the warning

from libzkfpcsharp import * # here too


class ZKFP2:
    """
    Python wrapper for ZKFinger Reader SDK in C#.
    """

    def __init__(self):
        """
        Initialize the ZKFP2 class and load the DLL.
        """
        self.zkfp2 = zkfp2()
        self.devHandle: int = None
        self.dbHandle: int = None
        self.Width = None
        self.Height = None


    def _handle_error(self, err_code):
        error_mapping = {
            -25: (DeviceAlreadyConnectedError, "The device is already connected"),
            -24: (DeviceNotInitializedError, "The device is not initialized"),
            -23: (DeviceNotStartedError, "The device is not started"),
            -22: (FailedToCombineTemplatesError, "Failed to combine the registered fingerprint templates"),
            -20: (FingerprintComparisonFailedError, "Fingerprint comparison failed"),
            -18: (CaptureCancelledError, "Capture cancelled"),
            -17: (OperationFailedError, "Operation failed"),
            -14: (FailedToDeleteTemplateError, "Failed to delete the fingerprint template"),
            -13: (FailedToAddTemplateError, "Failed to add the fingerprint template"),
            -12: (FingerprintCapturedError, "The fingerprint is being captured"),
            -11: (InsufficientMemoryError, "Insufficient memory"),
            -10: (AbortedError, "Aborted"),
            -9: (FailedToExtractTemplateError, "Failed to extract the fingerprint template"),
            -8: (FailedToCaptureImageError, "Failed to capture the image"),
            -7: (InvalidHandleError, "Invalid Handle"),
            -6: (FailedToStartDeviceError, "Failed to start the device"),
            -5: (InvalidParameterError, "Invalid parameter"),
            -4: (NotSupportedError, "Not supported by the interface"),
            -3: (NoDeviceConnectedError, "No device connected"),
            -2: (CaptureLibraryInitializationError, "Failed to initialize the capture library"),
            -1: (AlgorithmLibraryInitializationError, "Failed to initialize the algorithm library"),
        }

        if err_code in error_mapping:
            error_class, error_message = error_mapping[err_code]
            raise error_class(error_message)


    def Init(self) -> None:
        """
        Initialize the device.
        """
        ret = self.zkfp2.Init()
        self._handle_error(ret)


    def Terminate(self) -> None:
        """
        Release library resources.
        """
        ret = self.zkfp2.Terminate()
        self._handle_error(ret)


    def GetDeviceCount(self) -> int:
        """
        Acquire the number of connected devices.

        Returns:
            int: The device count.
        """
        return self.zkfp2.GetDeviceCount()


    def OpenDevice(self, index: int = 0) -> int:
        """
        Connect to a device.

        Args:
            `index` (int): Device index.

        Returns:
            `devHandle`: Device handle.
        """
        self.devHandle = self.zkfp2.OpenDevice(index)
        self.DBInit()
        # Get image width and height
        paramValue = self.GetParameters(1)
        self.Width = self.ByteArray2Int(paramValue)

        paramValue = self.GetParameters(2)
        self.Height = self.ByteArray2Int(paramValue)


        return self.devHandle


    def CloseDevice(self) -> None:
        """
        Shut down a device.
        """
        if self.devHandle is None:
            raise DeviceNotInitializedError("Device not initialized.")

        ret = self.zkfp2.CloseDevice(self.devHandle)
        self._handle_error(ret)


    def SetParameters(self, code: int, paramValue: Array[Byte] | bytes = bytes([1, 0, 0, 0]), size: int = 4) -> None:
        """
        Set a parameter.

        Args:
            `code` (int): Parameter code.
            `paramValue` (bytes): Parameter value.
            `size` (int): Parameter data length.
        """
        if self.devHandle is None:
            raise DeviceNotInitializedError("Device not initialized.")
        
        ret = self.zkfp2.SetParameters(self.devHandle, code, paramValue, len(paramValue))
        self._handle_error(ret)
        return paramValue


    def GetParameters(self, code: int) -> int:
        """
        Acquire a parameter.

        Args:
            `code` (int): Parameter code.

        Returns:
            int: `paramValue` if succeeded.
        """
        if self.devHandle is None:
            raise DeviceNotInitializedError("Device not initialized.")

        paramValue = self.Int2ByteArray(0)
        ret, size = self.zkfp2.GetParameters(self.devHandle, code, paramValue, 4)
        self._handle_error(ret)
        return paramValue


    def AcquireFingerprint(self) -> tuple[Array[Byte], bytes]:
        """
        Capture a fingerprint image and template.

        Args:
            `size` (int): Template array length.

        Returns:
            if result == 0:
                bytes: Template data.
                bytes: Image data.
            else: None.
        """
        if self.devHandle is None:
            raise DeviceNotInitializedError("Device not initialized.")

        imgBuffer = Array[Byte](self.Width * self.Height)
        template = Array[Byte](1024*2)  
        size = template.Length

        ret, size = self.zkfp2.AcquireFingerprint(self.devHandle, imgBuffer, template, size)
        if ret == 0: # only return when ther is a fingerprint captured
            return template, bytes(imgBuffer)
            # i'm the biggest bird

        if ret != -8: 
            self._handle_error(ret) # something went wrong => raise error


    def AcquireFingerprintImage(self) -> bytes:
        """
        Capture a fingerprint image.

        Args:
            imgBuffer (bytes): Returned image.
        
        Returns:
            bytes: Image data.
        """
        imgBuffer = Array[Byte](self.Width * self.Height)

        if self.devHandle is None:
            raise DeviceNotInitializedError("Device not initialized.")

        ret = self.zkfp2.AcquireFingerprintImage(self.devHandle, imgBuffer)

        if ret == 0: # only return when there is a fingerprint captured
            return bytes(imgBuffer)
            # i'm the biggest bird

        if ret != -8: 
            self._handle_error(ret) # something went wrong => raise error


    def DBInit(self) -> int:
        """
        Create an algorithm cache.

        Returns:
            dbHandle: CacheDB handle.
        """
        self.dbHandle = self.zkfp2.DBInit()
        return self.dbHandle


    def DBFree(self) -> None:
        """
        Release an algorithm cache.
        """
        if not self.dbHandle:
            raise DeviceNotInitializedError("Cache not initialized.")

        ret = self.zkfp2.DBFree(self.dbHandle)
        self._handle_error(ret)


    def DBMerge(self, temp1: Array[Byte], temp2: Array[Byte], temp3: Array[Byte]) -> tuple[Array[Byte], int]:
        """
        Combine three pre-registered fingerprint templates as one registered fingerprint template.

        Args:
            temp1 (bytes): Pre-registered fingerprint template 1.
            temp2 (bytes): Pre-registered fingerprint template 2.
            temp3 (bytes): Pre-registered fingerprint template 3.
        
        Returns:
            regTemp (bytes): Returned registered template.
            regTempLen (int): Template array length.
        """
        if not self.dbHandle:
            raise DeviceNotInitializedError("Cache not initialized.")

        regTemp = Array[Byte](1024*2)
        regTempLen = len(regTemp)
        ret = self.zkfp2.DBMerge(self.dbHandle, temp1, temp2, temp3, regTemp, regTempLen)
        self._handle_error(ret)
        return regTemp, regTempLen


    def DBAdd(self, fid: int, regTemp: bytes) -> None:
        """
        Add a registered template to the memory.

        Args:
            fid (int): Fingerprint ID.
            regTemp (bytes): Registered template.
        """
        if not self.dbHandle:
            raise DeviceNotInitializedError("Cache not initialized.")

        ret = self.zkfp2.DBAdd(self.dbHandle, fid, regTemp)
        self._handle_error(ret)


    def DBDel(self, fid: int) -> None:
        """
        Delete a registered fingerprint template from the memory.

        Args:
            fid (int): Fingerprint ID.
        """
        if not self.dbHandle:
            raise DeviceNotInitializedError("Cache not initialized.")

        ret = self.zkfp2.DBDel(self.dbHandle, fid)
        self._handle_error(ret)


    def DBClear(self) -> None:
        """
        Clear all fingerprint templates in the memory.
        """
        return self.zkfp2.DBClear(self.dbHandle)


    def DBIdentify(self, temp: bytes) -> list[int, int]:
        """
        Conduct 1:N comparison.

        Args:
            temp (bytes): Template used for comparison.
        
        Returns:
            fid (int): Fingerprint ID if succeeded.
            score (int): Comparison score if succeeded.
        """
        if not self.dbHandle:
            raise DeviceNotInitializedError("Cache not initialized.")

        fid = 0
        score = 0

        ret, fid, score = self.zkfp2.DBIdentify(self.dbHandle, temp, fid, score)
        if ret not in [0, -17]:
            self._handle_error(ret)
        return fid, score


    def DBMatch(self, temp1: bytes, temp2: bytes) -> int:
        """
        Conduct 1:1 comparison on two fingerprint templates.

        Args:
            temp1 (bytes): Template 1 used for comparison.
            temp2 (bytes): Template 2 used for comparison.

        Returns:
            int: Comparison score if succeeded.
        """
        score_result = self.zkfp2.DBMatch(self.dbHandle, temp1, temp2)
        
        if score_result < 0: self._handle_error(score_result)
        
        return score_result


    def Blob2Base64String(self, buf: bytes | Array[Byte]) -> str:
        """
        Convert a byte[] array into a Base64 string.

        Args:
            buf (bytes): BLOB data.
            len (int): Length.

        Returns:
            str: Base64 string.
        """
        # the sdk's function wasn't really working for me, so i made my own with PIL

        # SKD's function
        # strBase64 = String.Empty

        # ret, result = zkfp.Blob2Base64String(buf, len(buf) if isinstance(buf, bytes) else buf.Length, strBase64)
        # self._handle_error(ret)
        # return result

        # my function
        if not isinstance(buf, bytes):
            buf = bytes(buf)

        bf = BytesIO()
        image = Image.frombytes("L", (self.Width, self.Height), buf)
        image.save(bf, format="PNG")
        return b64encode(bf.getvalue()).decode("utf-8")


    def Base64String2Blob(self, strBase64: str) -> bytes:
        """
        Convert a Base64 string into a byte[] array.

        Args:
            strBase64 (str): Base64 string.

        Returns:
            bytes: the `blob` Byte[] array.
        """

        blob = zkfp2.Base64String2Blob(strBase64)
        return blob


    def ByteArray2Int(self, buf: bytes) -> int:
        """
        Convert a 4-byte array into an integer.

        Args:
            buf (bytes): Byte array.

        Returns:
            int: Converted integer if succeeded, None otherwise.
        """
        str_len, value = self.zkfp2.ByteArray2Int(buf, 0)
        return value


    def Int2ByteArray(self, value: int) -> bytes:
        """
        Convert an integer into a 4-byte array.

        Args:
            value (int): Data.

        Returns:
            bytes: Byte array.
        """
        buf = Array[Byte](4)
        result = self.zkfp2.Int2ByteArray(value, buf)
        if result:
            return buf


    def ExtractFromImage(self, FileName: str, DPI: int) -> int:
        """
        Extract a template from a BMP or JPG file.

        Args:
            FileName (str): Full path of a file.
            DPI (int): Image DPI.
        """
        if not self.dbHandle:
            raise DeviceNotInitializedError("Cache not initialized.")

        template = Array[Byte](1024*2)
        size = template.Length
        ret = self.zkfp2.ExtractFromImage(self.dbHandle, FileName, DPI, template, size)
        self._handle_error(ret)
        return template


    def Light(self, c, duration=0.5):
        def light_thread():
            code = {"white": 101, "green": 102, "red": 103}
            if c not in code:
                raise ValueError(f"Invalid color: {c}")

            self.SetParameters(code[c])
            sleep(duration)
            self.SetParameters(code[c], self.Int2ByteArray(0)) 
            # !NOTE: for some reason, the light doesn't turn off when set to 0. I haven't tested it on other devices besides the SLK20R. If you have a solution, please open a PR.

        Thread(target=light_thread).start()

