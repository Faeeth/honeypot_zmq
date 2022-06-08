import zmq.auth
import os
import sys
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_path)
from config import config

def new_certificate(dirname,name):
    try:
        dir_url = f"{root_path}/{dirname}"
        if not os.path.isdir(dir_url):
            os.makedirs(dir_url)
        zmq.auth.create_certificates(dir_url, name)
        return True
    except Exception as e:
        return False


if __name__ == "__main__":
    print("Success.") if new_certificate(config.certs_dirname,config.certs_name) else print("Failed.")