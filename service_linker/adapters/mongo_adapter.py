from service_linker.adapter import ServiceAdapter
from service_linker.core import ServiceManager


@ServiceManager.register_service_adapter
class MongoAdapter(ServiceAdapter):
    thread_safe = True
    service_name = "mongo"

    def do_get_connection(self, *args, **params):
        import pymongo

        client = pymongo.MongoClient(**params)
        return client

    def do_close(self, client):

        client.close()
