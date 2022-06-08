from elasticsearch import Elasticsearch
import sys


class my_elasticsearch:
    def __init__(self, url, username, password, index):
        self.url = url
        self.username = username
        self.password = password
        self.index = index
        self._es = self.connect()
        if not self._es:
            sys.exit("Impossible d'établir la connexion avec Elasticsearch.")

    def connect(self):
        self._es = Elasticsearch(self.url, basic_auth=(self.username, self.password))
        if self._es.ping():
            print("-- ELASTICSEARCH CONNECTED SUCCESSFULLY --")
            return self._es
        else:
            print("-- ELASTICSEARCH NOT CONNECTED --")
            return False

    def send(self, data):
        try:
            print(self._es.index(index=self.index,body=data))
        except Exception as e:
            print(f"Erreur lors de l'importation vers elasticsearch : {e}")
