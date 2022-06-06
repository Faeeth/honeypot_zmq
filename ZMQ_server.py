import zmq
import zmq.auth
import asyncio
import zmq.asyncio
import zlib
import config

def auth_service():
    auth = zmq.auth.Authenticator(ctx)
    auth.start()
    auth.configure_curve(location=f"./{config.certs_dirname}")

async def sub(ctx):
    auth_service()
    print("-- SUBSCRIBER SERVER --")
    socket = ctx.socket(zmq.SUB)

    # Subscribe on all topics.
    socket.setsockopt(zmq.SUBSCRIBE, b"")

    # Load server keys.
    public_key, secret_key = zmq.auth.load_certificate(f"./{config.certs_dirname}/{config.certs_name}.key_secret")

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