from service_linker.adapter import ServiceAdapter
from service_linker.core import ServiceManager


@ServiceManager.register_service_adapter
class ElasticSearchAdapter(ServiceAdapter):
    thread_safe = True
    service_name = "elasticsearch"

    def do_get_connection(self, *args, **params):
        from elasticsearch import Elasticsearch

        es = Elasticsearch(*args, **params)
        return es

    def do_close(self, es):
        es.close()
