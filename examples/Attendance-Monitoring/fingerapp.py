import sys; sys.dont_write_bytecode = True
import logging
from pyzkfp import ZKFP2

from time import sleep
from socketio import Client
from threading import Thread

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class FingerprintScanner:
    def __init__(self):
        self.logger = logging.getLogger('fps')
        fh = logging.FileHandler('logs/logs.log')
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(fh)

        self.templates = []

        self.initialize_zkfp2()

        self.capture = None
        self.register = False
        self.fid = None

        self.keep_alive = True


    def initialize_zkfp2(self):
        self.zkfp2 = ZKFP2()
        self.zkfp2.Init()
        self.logger.info(f"{(i := self.zkfp2.GetDeviceCount())} Device{'s' if i > 1 else ''} found, Connecting to the first device.")
        self.zkfp2.OpenDevice(0)
        self.zkfp2.Light('green')


    def wait_for_socket_response(self):
        self.sio.data = None
        timer = 0
        while timer<30 and self.keep_alive:
            if self.sio.data:
                d = self.sio.data
                self.sio.data = None
                return d
            
            timer+=0.01
            sleep(0.01)
        self.logger.warning("Socket response timeout!")
        return {'state': 'cancel'}

    
    def cancel_registration(self):
        self.templates = []
        self.register = False
        self.fid = None
        self.capture = None
        self.logger.warning("Registration canceled!")


    def capture_handler(self):
        try:
            tmp, img = self.capture
            fid, score = self.zkfp2.DBIdentify(tmp)

            if fid:
                self.sio.socketio_client.emit("identified", {'fid': fid}, namespace='/fps')
                self.logger.info(f"successfully identified the user: {fid}, Score: {score}")
                self.zkfp2.Light('green')
                self.capture = None
                return


            if self.register == False:
                self.sio.data = None
                self.sio.socketio_client.emit("askForApproval", {'title': 'السماح بتسجيل بصمة العضو؟'}, namespace='/fps')
                data = self.wait_for_socket_response()
                if data['state'] == 'approved':
                    self.fid = int(data['fid'])
                    self.logger.info(f"Approval was received, user: {self.fid}")
                    self.register = True
                    sleep(0.5)


            if self.register: # handle registeration
                if len(self.templates) < 3:
                    if not self.templates or self.zkfp2.DBMatch(self.templates[-1], tmp) > 0:
                        self.zkfp2.Light('green')
                        self.templates.append(tmp)
                        message = 'تم تسجيل بصمة من اصل ثلاث' if len(self.templates)==1 else f'تم تسجيل بصمتان من اصل ثلاث' if len(self.templates)==2 else 'تم تسجيل بصمات العضو بنجاح'

                        self.logger.info(f"{3 - len(self.templates)} presses left.")

                        self.sio.data = None
                        self.sio.socketio_client.emit('registering', {
                            'id': self.fid,
                            'title': message,
                            'step': len(self.templates),
                            'image': self.zkfp2.Blob2Base64String(img)
                        }, namespace='/fps')

                        res_data = self.wait_for_socket_response()
                        if res_data['state'] == 'retry':
                            self.logger.info("Retrying...")
                            self.templates.pop()
                            self.capture = None
                            return
                        elif res_data['state'] == 'cancel':
                            self.cancel_registration()
                            return

                        if len(self.templates) == 3:
                            regTemp, regTempLen = self.zkfp2.DBMerge(*self.templates)
                            self.zkfp2.DBAdd(self.fid, regTemp)
                            # emit the regTemp to the server
                            sleep(0.3)
                            self.sio.socketio_client.emit("registered", {
                                'fid': self.fid,
                                'template': bytes(regTemp),
                            }, namespace='/fps')
                            self.logger.info("Sending the templates to the server...")
                            self.templates = []
                            self.register = False
                            self.fid = None

                    else:
                        self.zkfp2.Light('red', 1)
                        self.logger.warning("Different finger. Please enter the original finger!")
                        self.sio.data = None
                        self.sio.socketio_client.emit("deffirent_finger", {
                            "message": "البصمة غير متطابقة، رجاءً ادخل البصمة الاصلية او الغ هذه العملية"},
                            namespace="/fps")

                        res = self.wait_for_socket_response()
                        if res['state'] == 'cancel':
                            self.cancel_registration()
                            return


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
            self.sio.socketio_client.emit("error", {'message': str(e)}, namespace='/fps')
            self.capture = None


    def listenToFingerprints(self):
        self.sio = Sio(self.logger, self.zkfp2)

        try:
            while self.keep_alive:
                capture = self.zkfp2.AcquireFingerprint()
                if capture and not self.capture:
                    self.capture = capture
                    Thread(target=self._capture_handler).start()
                sleep(0.1)
        except KeyboardInterrupt:
            self.logger.info("Shutting down...")
            self.zkfp2.Terminate()
            exit(0)


class Sio:
    def __init__(self, logger, zkfp2: ZKFP2):
        self.socketio_client = Client()
        self.data = None
        
        self.membersFingerprints = None

        self.zkfp2 = zkfp2
        self.logger = logger
        sleep(7) # wait for the server to start
        self.socketio_client.connect("http://127.0.0.1:8080", namespaces=['/fps'])
        self.socketio_client.emit("init", namespace='/fps')
        self.call_backs()


    def call_backs(self):
        @self.socketio_client.on('reviewed', namespace='/fps')
        def reviewed_(data):
            self.data = data
        
        @self.socketio_client.on('membersFingerprints', namespace='/fps')
        def membersFingerprints_(data):
            if data['data']:
                for member in data['members']:
                    fid, temp = member
                    self.zkfp2.DBAdd(fid, temp)         
            self.logger.info("done adding all the members fingerprints")



if __name__ == "__main__":
    fingerprint_scanner = FingerprintScanner()
    fingerprint_scanner.listenToFingerprints()
