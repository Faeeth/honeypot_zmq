### ZMQ ###
zmq_server_sub_bind_url = "tcp://*:5000"
zmq_client_pub_connect_url = "tcp://127.0.0.1:5000"
certs_dirname = "certs"
certs_name = "honeypot-cert"

### HONEYPOT CONFIG
agent_uid = "CHANGEME"
port_config_filename = "port_config.json"
export_type = "ELASTICSEARCH"
ipinfo_access_token = "CHANGEME"
ip_country_list = []

### ELASTICSEARCH ###
elasticsearch_url = "http://CHANGEME:9200"
elasticsearch_username = "elastic"
elasticsearch_password = "CHANGEME"
elasticsearch_index = "honeypot"