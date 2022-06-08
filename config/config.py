agent_uid = "CHANGEME"
zmq_server_sub_bind_url = "tcp://*:5000"
zmq_client_pub_connect_url = "tcp://127.0.0.1:5000"
certs_dirname = "certs"
certs_name = "honeypot-cert"

export_type = "ELASTICSEARCH"

### ELASTICSEARCH ###
elasticsearch_url = "http://ip:9200"
elasticsearch_username = "elastic"
elasticsearch_password = "changeme"
elasticsearch_index = "honeypot"