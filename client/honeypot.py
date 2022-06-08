#!/usr/bin/env python3
import socket
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
from datetime import datetime
from config import config
import ZMQ_client

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("1.1.1.1", 53))
        return str(s.getsockname()[0])
    except Exception as e:
        sys.exit(f"Impossible de définir l'adresse IP local à utiliser\n Error : {e}")

class SocketThread(threading.Thread):
    def __init__(self, threadID, ip, port, name, localport, protocol, minute_limit, hour_limit, socket_message):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.ip = ip
        self.port = port
        self.name = name
        self.local_port = localport
        self.protocol = protocol
        self.minute_limit = minute_limit
        self.hour_limit = hour_limit
        self.socket_message = socket_message

    def run(self):
        listen_port(self.ip, self.local_port, self.port, self.name, self.protocol, self.minute_limit, self.hour_limit, self.socket_message)

def parse_data(ip, port_client, port_honeypot, data_content):
    try:
        data = {
            "agent_uid" : config.agent_uid,
            "ip" : str(ip),
            "timestamp" : int(str(datetime.now().timestamp()).split('.')[0]),
            "port_client" : str(port_client),
            "port_honeypot" : str(port_honeypot),
            "data" : data_content.decode("utf-8").replace('"','\\"')
        }
        return data
    except:
        return False

def listen_port(host, localport, port, portname, protocol,minute_limit,hour_limit,socket_message):
    try:
        if protocol == "UDP":
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        elif protocol == "TCP":
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        else:
            return print(f"Error Protocol {portname}")
        if "linux" in sys.platform:
            os.system(f'echo yes | freeport {localport} 2>/dev/null 1>&2 && sleep 1')
        s.bind((host, localport))
        if protocol == "TCP":
            s.listen(65536)
        print('Honey Port capture sur le port %s -> local (%s)' % (portname,localport))
        while True:
            try:
                if protocol == "TCP":
                    (insock, address) = s.accept()
                    print('Tentative de connexion de %s:%d sur le port %s (%s)' % (address[0], address[1], portname, protocol))
                    data_content = insock.recv(1024)
                    insock.send(socket_message.encode())
                    insock.close()
                    # LOGGING
                    parsed_data = parse_data(address[0], address[1], portname, data_content)
                    if parsed_data:
                        pub_socket.send(("honeypot_logs",parsed_data))
                if protocol == "UDP":
                    data_content, address = s.recvfrom(4096)
                    continue
                    # TO DO
            except socket.error:
                pass
    except Exception as e:
        print(f"[Error] : {e}")


if __name__ == '__main__':
    try:
        pub_socket = ZMQ_client.zmq_pub()
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/{config.port_config_filename}") as json_file:
            data = json.load(json_file)
            if len(data) == 0:
                sys.exit('Veuillez renseigner au moins 1 port dans port_config.json\nPar exemple :\n{\n"22":{\n    "port" : 22,\n    "name" : "Ssh (22)",\n    "local_port" : 2222,\n    "protocol": "TCP",\n    "minute_limit" : 3,\n    "hour_limit" : 20\n}\n}')
            else:
                thread_data = []
                ip = get_local_ip()
                for key, value in data.items():
                    thread_data.append(value)
                for i in range(0,len(thread_data)):
                    t = SocketThread(i+1, ip, thread_data[i]["port"], thread_data[i]["name"], thread_data[i]["local_port"], thread_data[i]["protocol"], thread_data[i]["minute_limit"], thread_data[i]["hour_limit"],thread_data[i]["socket_message"])
                    t.start()
    except Exception as e:
        sys.exit(e)