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
        if hasattr(es, "close"):  # version >= 7.14.0
            es.close()
        else:  # version < 7.14.0
            es.transport.close()
