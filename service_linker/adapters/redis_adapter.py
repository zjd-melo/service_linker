from service_linker.adapter import ServiceAdapter
from service_linker.core import ServiceManager


@ServiceManager.register_service_adapter
class RedisAdapter(ServiceAdapter):
    thread_safe = False
    service_name = "redis"

    def do_get_connection(self, *args, **params):
        import redis

        rc = redis.Redis(**params)
        return rc

    def do_close(self, rc):

        rc.close()
