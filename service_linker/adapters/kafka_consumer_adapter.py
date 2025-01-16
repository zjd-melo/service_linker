from service_linker.adapter import ServiceAdapter
from service_linker.core import ServiceManager


@ServiceManager.register_service_adapter
class KafkaConsumerAdapter(ServiceAdapter):
    thread_safe = False
    service_name = "kafka_python_consumer"

    def do_get_connection(self, *args, **params):
        from kafka import KafkaConsumer

        consumer = KafkaConsumer(*args, **params)
        return consumer

    def do_close(self, consumer):
        consumer.close()
