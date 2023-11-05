class zkfp:
    def __init__(self):
        self.hDevice: int = 0
        self.hDBCache: int = 0
        self.imageWidth: int = 0
        self.imageHeight: int = 0
        self.imageDPI: int = 0
        self.devSn: str = ""

    def AcquireFingerprint(self, imgBuffer: bytes, template: bytes, size: int) -> int:
        ...

    def AcquireFingerprintImage(self, imgBuffer: bytes) -> int:
        ...

    def AddRegTemplate(self, fid: int, regTemp: bytes) -> int:
        ...

    @staticmethod
    def Base64String2Blob(strBase64: str) -> bytes:
        ...

    @staticmethod
    def Blob2Base64String(buf: bytes, len: int) -> [str, int]:
        ...

    @staticmethod
    def ByteArray2Int(buf: bytes) -> tuple[bool, int]:
        ...

    def Clear(self) -> int:
        ...

    def CloseDevice(self) -> int:
        ...

    def DBGetParameter(self, code: int) -> tuple[int, int]:
        ...

    def DBSetParameter(self, code: int, value: int) -> int:
        ...

    def DelRegTemplate(self, fid: int) -> int:
        ...

    def ExtractFromImage(self, FileName: str, DPI: int, template: bytes) -> int:
        ...

    def Finalize(self) -> int:
        ...

    def GenerateRegTemplate(self, temp1: bytes, temp2: bytes, temp3: bytes, regTemp: bytes) -> int:
        ...

    def GetDeviceCount(self) -> int:
        ...

    def GetParameters(self, code: int, paramValue: bytes) -> tuple[int, int]:
        ...

    def Identify(self, temp: bytes) -> tuple[int, int, int]:
        ...

    def Initialize(self) -> int:
        ...

    @staticmethod
    def Int2ByteArray(value: int, buf: bytes) -> bool:
        ...

    def Match(self, temp1: bytes, temp2: bytes) -> int:
        ...

    def OpenDevice(self, index: int) -> int:
        ...

    def OutputDebugString(self, message: str) -> None:
        ...

    def SetParameters(self, code: int, pramValue: bytes, size: int) -> int:
        ...

    def VerifyByID(self, fid: int, temp: bytes) -> int:
        ...

class zkfp2:
    def __init__(self) -> None:
        pass

    @staticmethod
    def AcquireFingerprint(devHandle: int, imgBuffer: bytes, template: bytes, size: int) -> int:
        ...

    @staticmethod
    def AcquireFingerprintImage(devHandle: int, imgbuf: bytes) -> int:
        ...

    @staticmethod
    def Base64ToBlob(base64Str: str) -> bytes:
        ...

    @staticmethod
    def BlobToBase64(blob: bytes, nDataLen: int) -> str:
        ...

    @staticmethod
    def ByteArray2Int(buf: bytes, value: int) -> bool:
        ...

    @staticmethod
    def CloseDevice(devHandle: int) -> int:
        ...

    @staticmethod
    def DBAdd(dbHandle: int, fid: int, regTemp: bytes) -> int:
        ...

    @staticmethod
    def DBClear(dbHandle: int) -> int:
        ...

    @staticmethod
    def DBCount(dbHandle: int) -> int:
        ...

    @staticmethod
    def DBDel(dbHandle: int, fid: int) -> int:
        ...

    @staticmethod
    def DBFree(dbHandle: int) -> int:
        ...

    @staticmethod
    def DBGetParameter(dbHandle: int, code: int, value: int) -> int:
        ...

    @staticmethod
    def DBIdentify(dbHandle: int, temp: bytes, fid: int, score: int) -> int:
        ...

    @staticmethod
    def DBInit() -> int:
        ...

    @staticmethod
    def DBMatch(dbHandle: int, temp1: bytes, temp2: bytes) -> int:
        ...

    @staticmethod
    def DBMerge(dbHandle: int, temp1: bytes, temp2: bytes, temp3: bytes, regTemp: bytes, regTempLen: int) -> int:
        ...

    @staticmethod
    def DBSetParameter(dbHandle: int, code: int, value: int) -> int:
        ...

    @staticmethod
    def ExtractFromImage(dbHandle: int, FileName: str, DPI: int, template: bytes, size: int) -> int:
        ...

    @staticmethod
    def GetDeviceCount() -> int:
        ...

    @staticmethod
    def GetParameters(devHandle: int, code: int, paramValue: bytes, size: int) -> int:
        ...

    @staticmethod
    def Init() -> int:
        ...

    @staticmethod
    def Int2ByteArray(value: int, buf: bytes) -> bool:
        ...

    @staticmethod
    def OpenDevice(index: int) -> int:
        ...

    @staticmethod
    def OutputDebugString(message: str) -> None:
        ...

    @staticmethod
    def SetParameters(devHandle: int, code: int, pramValue: bytes, size: int) -> int:
        ...

    @staticmethod
    def Terminate() -> int:
        ...

    @staticmethod
    def WriteLog(text: str) -> None:
        ...

    @staticmethod
    def ZKFPM_AcquireFingerprint(handle: int, fpImage: bytes, cbFPImage: int, fpTemplate: bytes, cbTemplate: int) -> int:
        ...

    @staticmethod
    def ZKFPM_AcquireFingerprintImage(hDBCache: int, fpImage: bytes, cbFPImage: int) -> int:
        ...

    @staticmethod
    def ZKFPM_AddRegTemplateToDBCache(hDBCache: int, fid: int, fpTemplate: bytes, cbTemplate: int) -> int:
        ...

    @staticmethod
    def ZKFPM_Base64ToBlob(src: str, blob: int, cbBlob: int) -> int:
        ...

    @staticmethod
    def ZKFPM_BlobToBase64(src: int, cbSrc: int, dst, cbDst: int) -> int:
        ...

    @staticmethod
    def ZKFPM_ClearDBCache(hDBCache: int) -> int:
        ...

    @staticmethod
    def ZKFPM_CloseDBCache(hDBCache: int) -> int:
        ...

    @staticmethod
    def ZKFPM_CloseDevice(handle: int) -> int:
        ...

    @staticmethod
    def ZKFPM_CreateDBCache() -> int:
        ...

    @staticmethod
    def ZKFPM_DBGetParameter(handle: int, nParamCode: int, paramValue: int) -> int:
        ...

    @staticmethod
    def ZKFPM_DBSetParameter(handle: int, nParamCode: int, paramValue: int) -> int:
        ...

    @staticmethod
    def ZKFPM_DelRegTemplateFromDBCache(hDBCache: int, fid: int) -> int:
        ...

    @staticmethod
    def ZKFPM_ExtractFromImage(hDBCache: int, FilePathName: str, DPI: int, fpTemplate: bytes, cbTemplate: int) -> int:
        ...

    @staticmethod
    def ZKFPM_GenRegTemplate(hDBCache: int, temp1: bytes, temp2: bytes, temp3: bytes, regTemp: bytes, cbRegTemp: int) -> int:
        ...

    @staticmethod
    def ZKFPM_GetCaptureParamsEx(handle: int, width: int, height: int, dpi: int) -> int:
        ...

    @staticmethod
    def ZKFPM_GetDBCacheCount(hDBCache: int, count: int) -> int:
        ...

    @staticmethod
    def ZKFPM_GetDeviceCount() -> int:
        ...

    @staticmethod
    def ZKFPM_GetParameters(handle: int, nParamCode: int, paramValue: bytes, cbParamValue: int) -> int:
        ...

    @staticmethod
    def ZKFPM_Identify(hDBCache: int, fpTemplate: bytes, cbTemplate: int, FID: int, score: int) -> int:
        ...

    @staticmethod
    def ZKFPM_Init() -> int:
        ...

    @staticmethod
    def ZKFPM_MatchFinger(hDBCache: int, fpTemplate1: bytes, cbTemplate1: int, fpTemplate2: bytes, cbTemplate2: int) -> int:
        ...

    @staticmethod
    def ZKFPM_OpenDevice(index: int) -> int:
        ...

    @staticmethod
    def ZKFPM_SetParameters(handle: int, nParamCode: int, paramValue: bytes, cbParamValue: int) -> int:
        ...

    @staticmethod
    def ZKFPM_Terminate() -> int:
        ...

    @staticmethod
    def ZKFPM_VerifyByID(hDBCache: int, fid: int, fpTemplate: bytes, cbTemplate: int) -> int:
        ...

class zkfperrdef:
    ZKFP_ERR_ALREADY_INIT:int = 1
    ZKFP_ERR_OK:int = 0
    ZKFP_ERR_INITLIB:int = -1
    ZKFP_ERR_INIT:int = -2
    ZKFP_ERR_NO_DEVICE:int = -3
    ZKFP_ERR_NOT_SUPPORT:int = -4
    ZKFP_ERR_INVALID_PARAM:int = -5
    ZKFP_ERR_OPEN:int = -6
    ZKFP_ERR_INVALID_HANDLE:int = -7
    ZKFP_ERR_CAPTURE:int = -8
    ZKFP_ERR_EXTRACT_FP:int = -9
    ZKFP_ERR_ABSORT:int = -10
    ZKFP_ERR_MEMORY_NOT_ENOUGH:int = -11
    ZKFP_ERR_BUSY:int = -12
    ZKFP_ERR_ADD_FINGER:int = -13
    ZKFP_ERR_DEL_FINGER:int = -14
    ZKFP_ERR_FAIL:int = -17
    ZKFP_ERR_CANCEL:int = -18
    ZKFP_ERR_VERIFY_FP:int = -20
    ZKFP_ERR_MERGE:int = -22
    ZKFP_ERR_NOT_OPENED:int = -23
    ZKFP_ERR_NOT_INIT:int = -24
    ZKFP_ERR_ALREADY_OPENED:int = -25
    ZKFP_ERR_LOADIMAGE:int = -26
    ZKFP_ERR_ANALYSE_IMG:int = -27
    ZKFP_ERR_TIMEOUT:int = -28
