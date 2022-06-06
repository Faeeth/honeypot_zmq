import zmq
import zmq.auth
import os
import config

def new_certificate(dirname,name):
    try:
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        zmq.auth.create_certificates(f"./{dirname}", f"{name}-cert")
        return True
    except Exception as e:
        return False


if __name__ == "__main__":
    print("Success.") if new_certificate(config.certs_dirname,config.certs_name) else print("Failed.")