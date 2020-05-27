# -*- coding: utf-8 -*-
# @Time    : 2020-05-15
# @File    : esConnector
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@gmail.com

from elasticsearch import Elasticsearch


def _generate_bulk_body(index, doc: list):
    es_body = []
    index_api = {"index": {"_index": index}}
    for item in doc:
        es_body.append(index_api)
        es_body.append(item)
    return es_body


class ESConnector:
    def __init__(self, url):
        self.es = Elasticsearch([url])

    def es_ok(self):
        return self.es.ping()

    def index_exist(self, index):
        if self.es.indices.exists(index):
            print('Info: index already exists! %s' % index)
            return True
        return False

    def index_create(self, index):
        settings = {"settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "epics_pv_analyzer": {
                        "type": "custom",
                        "tokenizer": "pv_tokenizer",
                        "filter": [
                            "lowercase"
                        ]
                    }
                },
                "tokenizer": {
                    "pv_tokenizer": {
                        "type": "char_group",
                        "tokenize_on_chars": [
                            ":",
                            "-",
                            "_",
                            " "
                        ]
                    }
                }
            }
        },
            "mappings": {
                "properties": {
                    "PVNAME": {
                        "type": "text",
                        "analyzer": "epics_pv_analyzer",
                        "search_analyzer": "epics_pv_analyzer"
                    },
                    "PVTYPE": {
                        "type": "keyword",
                        "ignore_above": 256
                    },
                    "DTYP": {
                        "type": "text"
                    },
                    "NELM": {
                        "type": "integer"
                    },
                    "PINI": {
                        "type": "keyword"
                    },
                    "FLNK": {
                        "type": "text",
                        "analyzer": "epics_pv_analyzer",
                        "search_analyzer": "epics_pv_analyzer"
                    },
                    "FTVL": {
                        "type": "keyword"
                    }
                }
            }
        }
        self.es.indices.create(index=index, ignore=400, body=settings)
        print('Created Index %s' % index)

    def insert_data(self, index, doc, ):
        """
        add data into the elastic search database
        :param index: index name
        :param doc: data
        :return: response json data from elasticsearch
        """
        body = _generate_bulk_body(index, doc)
        # add bulk API timeout value: 300 seconds
        return self.es.bulk(body=body, index=index, request_timeout=300)


if __name__ == '__main__':
    es = ESConnector("http://localhost:9200")
    # es.es.cat.indices()
    # print(es.es.ping())
