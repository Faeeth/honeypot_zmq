import zmq
import zmq.auth
import asyncio
import zmq.asyncio
import zlib
from config import config
import os
import sys
import json


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

    sender = set_sender("elasticsearch")

    while True:
        data = await socket.recv()
        try:
            decompressed_data = zlib.decompress(data).decode("utf-8")
            if isinstance(decompressed_data,str):
                topic, true_data = parse_data_received(decompressed_data)
                print(topic)
                print(true_data)
                if str(topic).lower() == "honeypot_logs":
                    if str(config.export_type).lower() == "elasticsearch":
                        sender.send(true_data)
        except Exception as e:
            print("error : ", e)


def set_sender(type):
    if str(type).lower() == "elasticsearch":
        from export_modules.export_elasticsearch import my_elasticsearch
        sender = my_elasticsearch(url=config.elasticsearch_url, username=config.elasticsearch_username,
                                  password=config.elasticsearch_password, index=config.elasticsearch_index)
        return sender


def parse_data_received(data):
    try:
        topic = False
        true_data = False
        if len(data) >= 2:
            if data[0] == "(":
                data = data[1:]
            if data[-1:] == ")":
                data = data[:-1]
            splited_by_simple_quote = data.split("'")
            if len(splited_by_simple_quote) >= 2:
                topic = splited_by_simple_quote[1]
            true_data = data[len(topic) + 2:]
            if true_data[0] == ",":
                true_data = true_data[1:]
            if true_data[0] == " ":
                true_data = true_data[1:]
            return (topic, true_data.replace("'",'"'))
        else:
            return (False, False)
    except Exception as e:
        print(e)
        return (False,False)


if __name__ == "__main__":
    ctx = zmq.asyncio.Context()
    asyncio.run(sub(ctx))
