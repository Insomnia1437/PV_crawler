# -*- coding: utf-8 -*-
# @Time    : 2020-05-15
# @File    : esConnector
# @Software: PyCharm
# @Author  : Di Wang(KEK Linac)
# @Email   : sdcswd@gmail.com

from elasticsearch import Elasticsearch


class ESConnector:
    def __init__(self, url):
        self.es = Elasticsearch([url])

    def es_ok(self):
        return self.es.ping()

    def _generate_bulk_body(self, index, doc: list):
        es_body = []
        index_api = {"index": {"_index": index}}
        for item in doc:
            es_body.append(index_api)
            es_body.append(item)
        return es_body

    def insert_pv(self, index, db_doc, ):
        body = self._generate_bulk_body(index, db_doc)
        return self.es.bulk(body=body, index=index)

    def insert_ioc(self, index, ioc_doc):
        """
        send ioc info to ES
        :param index: ES index
        :param ioc_doc: example:
        [{'IOCNAME': name,'IOCHOST': host,'IOCPORT': port,'IOCPATH': path}]
        :return: ES response
        """
        body = self._generate_bulk_body(index, ioc_doc)
        return self.es.bulk(body=body, index=index)


if __name__ == '__main__':
    es = ESConnector("http://localhost:9200")
    # es.es.cat.indices()
    # print(es.es.ping())
