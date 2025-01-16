from service_linker.adapter import ServiceAdapter
from service_linker.core import ServiceManager


@ServiceManager.register_service_adapter
class KafkaProducerAdapter(ServiceAdapter):
    thread_safe = True
    service_name = "kafka_python_producer"

    def do_get_connection(self, *args, **params):
        from kafka import KafkaProducer

        producer = KafkaProducer(*args, **params)
        return producer

    def do_close(self, producer):
        producer.flush()
        producer.close()
