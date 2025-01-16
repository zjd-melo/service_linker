import json

from service_linker.adapters.elasticsearch_adapter import ElasticSearchAdapter
from service_linker.adapters.kafka_consumer_adapter import KafkaConsumerAdapter
from service_linker.adapters.kafka_producer_adapter import KafkaProducerAdapter
from service_linker.adapters.mongo_adapter import MongoAdapter
from service_linker.adapters.mysql_raw_adapter import MySQLRawAdapter
from service_linker.adapters.redis_adapter import RedisAdapter


def json_encode(v):
    return json.dumps(v).encode("utf-8")


def json_decode(v):
    if v is not None:
        return json.loads(v.decode("utf-8"))
    return None
