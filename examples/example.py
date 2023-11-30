import sys; sys.dont_write_bytecode = True # don't create __pycache__
import logging
from pyzkfp import ZKFP2

from time import sleep
from threading import Thread

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class FingerprintScanner:
    def __init__(self):
        self.logger = logging.getLogger('fps')
        fh = logging.FileHandler('logs.log')
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(fh)

        self.templates = []

        self.initialize_zkfp2()

        self.capture = None
        self.register = False
        self.fid = 1

        self.keep_alive = True


    def initialize_zkfp2(self):
        self.zkfp2 = ZKFP2()
        self.zkfp2.Init()
        self.logger.info(f"{(i := self.zkfp2.GetDeviceCount())} Devices found. Connecting to the first device.")
        self.zkfp2.OpenDevice(0)
        self.zkfp2.Light("green")


    def capture_handler(self):
        try:
            tmp, img = self.capture
            fid, score = self.zkfp2.DBIdentify(tmp)

            if fid:
                self.logger.info(f"successfully identified the user: {fid}, Score: {score}")
                self.zkfp2.Light('green')
                self.capture = None
                return


            if self.register == False:
                self.register = input("Do you want to register a new user? [y/n]: ").lower() == 'y'


            if self.register: # registeration logic
                if len(self.templates) < 3:
                    if not self.templates or self.zkfp2.DBMatch(self.templates[-1], tmp) > 0: # check if the finger is the same
                        self.zkfp2.Light('green')
                        self.templates.append(tmp)

                        message = f"Finger {len(self.templates)} registered successfully! " + (f"{3-len(self.templates)} presses left." if 3-len(self.templates) > 0 else '')
                        self.logger.info(message)

                        # blob_image = self.zkfp2.Blob2Base64String(img) # convert the image to base64 string

                        if len(self.templates) == 3:
                            regTemp, regTempLen = self.zkfp2.DBMerge(*self.templates)
                            self.zkfp2.DBAdd(self.fid, regTemp)

                            self.templates.clear()
                            self.register = False
                            self.fid += 1

                    else:
                        self.zkfp2.Light('red', 1)
                        self.logger.warning("Different finger. Please enter the original finger!")


        except KeyboardInterrupt:
            self.logger.info("Shutting down...")
            self.zkfp2.Terminate()
            exit(0)

        # release the capture
        self.capture = None


    def _capture_handler(self):
        try:
            self.capture_handler()
        except Exception as e:
            self.logger.error(e)
            self.capture = None


    def listenToFingerprints(self):
        try:
            while self.keep_alive:
                capture = self.zkfp2.AcquireFingerprint()
                if capture and not self.capture:
                    self.capture = capture
                    Thread(target=self._capture_handler, daemon=True).start()
                sleep(0.1)
        except KeyboardInterrupt:
            self.logger.info("Shutting down...")
            self.zkfp2.Terminate()
            exit(0)


if __name__ == "__main__":
    fingerprint_scanner = FingerprintScanner()
    fingerprint_scanner.listenToFingerprints()
