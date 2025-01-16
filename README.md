# Service Linker Library

## Overview

The **Service Linker** library provides a unified and extensible way to manage connections to various services like databases, message brokers, and search engines. It simplifies connection management by ensuring proper lifecycle handling, thread-safety, and flexibility for different service requirements.

The core functionality includes:

- Registering service adapters for various services.
- Managing both thread-safe and non-thread-safe connections.
- Providing context management for connections.

## Key Features

1. **Extensibility**: Easily register new services by creating adapters.
2. **Thread-Safety**: Handle both thread-safe and non-thread-safe connections.
3. **Connection Lifecycle Management**: Automatically close all connections at program exit.
4. **Context Management**: Simplify connection handling using Python’s `with` statement.

## Components

### `core.py`

The `core.py` module provides the main `ServiceManager` class, which handles connection registration, retrieval, and cleanup.

#### Key Classes

1. **`ServiceManager`**
   - Manages connections and ensures proper lifecycle handling.
   - Supports both global and thread-local connection storage.
   - Provides methods to register adapters, retrieve connections, and close connections.

2. **`ConnectionWrapper`**
   - Wraps individual connections to provide additional management capabilities.
   - Delegates attribute and method access to the underlying connection object.

### `adapter.py`

The `adapter.py` module defines the abstract base class `ServiceAdapter`, which must be implemented for each new service. It ensures consistency and enforces the implementation of methods to establish and close connections.

#### Key Methods

- `do_get_connection`: Establishes a connection.
- `do_close`: Closes a connection.

### Adapters

The library includes several pre-built adapters for popular services:

1. **Elasticsearch** (`adapters/elasticsearch_adapter.py`)
   - Adapter: `ElasticSearchAdapter`
   - Thread-Safe: Yes

2. **Kafka Consumer** (`adapters/kafka_consumer_adapter.py`)
   - Adapter: `KafkaConsumerAdapter`
   - Thread-Safe: No

3. **Kafka Producer** (`adapters/kafka_producer_adapter.py`)
   - Adapter: `KafkaProducerAdapter`
   - Thread-Safe: Yes

4. **MongoDB** (`adapters/mongo_adapter.py`)
   - Adapter: `MongoAdapter`
   - Thread-Safe: Yes

5. **MySQL (Raw)** (`adapters/mysql_raw_adapter.py`)
   - Adapter: `MySQLRawAdapter`
   - Thread-Safe: No

## Usage

### 1. Registering an Adapter

Adapters are registered automatically using the `@ServiceManager.register_service_adapter` decorator.

### 2. Retrieving a Connection

```python
from service_linker.core import ServiceManager

connection = ServiceManager.get_connection("elasticsearch", hosts=["http://localhost:9200"])
```

### 3. Using Context Management

```python
from service_linker.core import ServiceManager

with ServiceManager.connection_context("mongo", host="localhost", port=27017) as conn:
    db = conn.my_database
    print(db.list_collection_names())
```

### 4. Closing Connections

```python
from service_linker.core import ServiceManager

ServiceManager.close_connection("elasticsearch", hosts=["http://localhost:9200"])
```

### 5. Closing All Connections

All connections are automatically closed when the program exits, but you can manually invoke it:

```python
from service_linker.core import ServiceManager

ServiceManager.close_all_connections()
```

## Extending the Library

To add support for a new service, create a new adapter by subclassing `ServiceAdapter`:

```python
from service_linker.adapter import ServiceAdapter
from service_linker.core import ServiceManager

@ServiceManager.register_service_adapter
class MyServiceAdapter(ServiceAdapter):
    thread_safe = True
    service_name = "my_service"

    def do_get_connection(self, **params):
        # Logic to establish a connection
        return connection

    def do_close(self, connection):
        # Logic to close the connection
        pass
```

## Installation

Clone the repository and install dependencies:

```bash
pip install service_linker
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.
