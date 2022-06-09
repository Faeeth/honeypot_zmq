import zmq
import zmq.auth
import asyncio
import zmq.asyncio
import zlib
import sys
import os
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_path)
from config import config
import ipinfo
import json

def auth_service(certs_url):
    if not os.path.isdir(certs_url):
        sys.exit(f"[Error] : {certs_url} folder not found.")
    auth = zmq.auth.Authenticator(ctx)
    auth.start()
    auth.configure_curve(location=certs_url)


async def sub(ctx):
    certs_url = f"{root_path}/{config.certs_dirname}"
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

    sender = set_sender(config.export_type)

    while True:
        data = await socket.recv()
        try:
            decompressed_data = zlib.decompress(data).decode("utf-8")
            if isinstance(decompressed_data,str):
                print(decompressed_data)
                topic, true_data = parse_data_received(decompressed_data)
                true_data["country"], true_data["hostname"], true_data["longitude"], true_data["latitude"] = country_ip("90.114.230.113")
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
            return topic, json.loads(true_data.replace("'", '"'), strict=False)
        else:
            return (False, False)
    except Exception as e:
        print(e)
        return (False,False)

def country_ip(ip):
    h = [x for x in config.ip_country_list if x[0] == str(ip)]
    if len(h) > 0:
        return (str(h[0][1]),str(h[0][2]),str(h[0][3]),str(h[0][4]))
    else:
        try:
            handler = ipinfo.getHandler(config.ipinfo_access_token)
            details = handler.getDetails(ip)
            config.ip_country_list.append([f"{str(ip)}", details.country, details.hostname, details.longitude, details.latitude])
            return (details.country, details.hostname, details.longitude, details.latitude)
        except Exception as e:
            print(f"Error : {e}")
            return ("","","","")


if __name__ == "__main__":
    ctx = zmq.asyncio.Context()
    asyncio.run(sub(ctx))
