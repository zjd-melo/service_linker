from service_linker.adapter import ServiceAdapter
from service_linker.core import ServiceManager


@ServiceManager.register_service_adapter
class MySQLRawAdapter(ServiceAdapter):
    thread_safe = False
    service_name = "raw_pymysql"

    def do_get_connection(self, **params):
        import pymysql

        conn = pymysql.connect(**params)
        return conn

    def do_close(self, conn):

        conn.close()
