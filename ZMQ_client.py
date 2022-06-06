import time
import zmq
import zmq.auth
import zlib
import config

class zmq_pub():
    def __init__(self):
        self.ctx = zmq.asyncio.Context()
        self.launch()


    def auth_service(self):
        self.auth = zmq.auth.Authenticator(self.ctx)
        self.auth.start()
        self.auth.configure_curve(location=f"./{config.certs_dirname}")

    def launch(self):
        self.auth_service()
        print("-- PUBLISHER CLIENT --")
        self.socket = self.ctx.socket(zmq.PUB)

        # Load client keys.
        public_key, secret_key = zmq.auth.load_certificate(f"./{config.certs_dirname}/{config.certs_name}.key_secret")
        self.socket.curve_publickey = public_key
        self.socket.curve_secretkey = secret_key

        # Load server public key.
        server_public_key, _ = zmq.auth.load_certificate(f"./{config.certs_dirname}/{config.certs_name}.key")
        self.socket.curve_serverkey = server_public_key

        # Connect to server
        self.socket.connect(config.url)

    def send(self,data):
        try:
            self.socket.send(zlib.compress(bytes(f"{data}", encoding="utf-8")))
        except Exception as e:
            print(f"[Error] : {e}")
