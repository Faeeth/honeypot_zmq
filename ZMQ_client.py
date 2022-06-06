import time

import zmq
import zmq.auth
import zlib

certs_dirname = "certs"
certs_name = "honeypot-cert"
url = "tcp://127.0.0.1:5000"

def auth_service():
    auth = zmq.auth.Authenticator(ctx)
    auth.start()
    auth.configure_curve(location=f"./{certs_dirname}")

def pub(ctx):
    print("-- PUBLISHER CLIENT --")
    socket = ctx.socket(zmq.PUB)

    # Load client keys.
    public_key, secret_key = zmq.auth.load_certificate(f"./{certs_dirname}/{certs_name}.key_secret")
    socket.curve_publickey = public_key
    socket.curve_secretkey = secret_key

    # Load server public key.
    server_public_key, _ = zmq.auth.load_certificate(f"./{certs_dirname}/{certs_name}.key")
    socket.curve_serverkey = server_public_key

    socket.connect(url)
    while True:
        socket.send(zlib.compress(bytes(f"test",encoding="utf-8")))
        time.sleep(1)

if __name__ == "__main__":
    ctx = zmq.asyncio.Context()
    pub(ctx)