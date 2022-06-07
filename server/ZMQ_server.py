import zmq
import zmq.auth
import asyncio
import zmq.asyncio
import zlib
from config import config
import os
import sys

def auth_service(certs_url):
    if not os.path.isdir(certs_url):
        sys.exit(f"[Error] : {certs_url} folder not found.")
    auth = zmq.auth.Authenticator(ctx)
    auth.start()
    auth.configure_curve(location=certs_url)

async def sub(ctx):
    certs_url = f"../{config.certs_dirname}"
    auth_service(certs_url)
    print("-- SUBSCRIBER SERVER --")
    socket = ctx.socket(zmq.SUB)

    # Subscribe on all topics.
    socket.setsockopt(zmq.SUBSCRIBE, b"")

    # Load server keys.
    public_key, secret_key = zmq.auth.load_certificate(f"{certs_url}/{config.certs_name}.key_secret")

    socket.curve_publickey = public_key
    socket.curve_secretkey = secret_key
    socket.curve_server = True

    socket.bind(config.zmq_server_sub_bind_url)

    while True:
        data = await socket.recv()
        try:
            decompressed_data = zlib.decompress(data).decode("utf-8")
            print(decompressed_data)
            # PARSE AND SAVE DATA
        except Exception as e:
            print("error : ", e)

if __name__ == "__main__":
    ctx = zmq.asyncio.Context()
    asyncio.run(sub(ctx))