import atexit
import hashlib
import threading
import weakref
from contextlib import contextmanager

from .adapter import ServiceAdapter


class ServiceManager:
    """
    ServiceManager manages connections to various services using adapters.
    It supports both thread-safe and non-thread-safe connections.

    Attributes:
        _adapters (dict): A dictionary to store registered service adapters.
        _connections (weakref.WeakValueDictionary): A global dictionary for storing connections.
        _thread_local (threading.local): Thread-local storage for non-thread-safe connections.
        _lock (threading.Lock): A lock to ensure thread-safe access to global connections.
    """

    _adapters = {}
    _connections = (
        weakref.WeakValueDictionary()
    )  # Use WeakValueDictionary to avoid memory leaks
    _thread_local = threading.local()
    _lock = threading.Lock()  # Ensure thread safety for global connections

    @classmethod
    def register_service_adapter(cls, adapter):
        """
        Registers a service adapter.

        Args:
            adapter (ServiceAdapter): The adapter to register. Must implement `do_get_connection` and `do_close` methods.

        Raises:
            TypeError: If the adapter does not subclass `ServiceAdapter`.
        """
        service_name = adapter.service_name
        if not issubclass(adapter, ServiceAdapter):
            e = f"{service_name} adapter must implement ServiceAdapter protocol"
            raise TypeError(e)
        if service_name in cls._adapters:
            raise ValueError(
                f"Service '{service_name}' has already been registered."
                "Duplicate registration is not allowed."
            )
        cls._adapters[service_name] = adapter()

    @classmethod
    def _generate_connection_key(cls, service_name, **params):
        """
        Generates a unique connection key based on the service name and parameters.

        Args:
            service_name (str): The name of the service.
            params: Additional parameters for the service.

        Returns:
            str: A hashed string representing the connection key.
        """
        key = f"{service_name}_" + "_".join(
            [f"{k}={v}" for k, v in sorted(params.items())]
        )
        return hashlib.md5(key.encode("utf-8")).hexdigest()

    @classmethod
    def get_connection(cls, service_name, *args, **params):
        """
        Retrieves a connection for the specified service and parameters.

        Args:
            service_name (str): The name of the service.
            *args: Positional parameters for the service.
            **params: Additional parameters for the service.

        Returns:
            ConnectionWrapper: A wrapper around the connection object.

        Raises:
            ValueError: If no adapter is found for the service.
        """
        adapter = cls._adapters.get(service_name)
        if not adapter:
            services = ", ".join(cls._adapters.keys())
            raise ValueError(
                f"Not found {service_name} adapter, currently support: {services}!"
            )

        connection_key = cls._generate_connection_key(service_name, **params)

        if adapter.thread_safe:
            with cls._lock:  # Ensure thread-safe access to global connections
                if connection_key not in cls._connections:
                    conn = adapter.get_connection(*args, **params)
                    wrapper = ConnectionWrapper(conn, cls, service_name, params)
                    cls._connections[connection_key] = wrapper
                return cls._connections[connection_key]
        else:
            if not hasattr(cls._thread_local, "connections"):
                cls._thread_local.connections = weakref.WeakValueDictionary()
            if connection_key not in cls._thread_local.connections:
                conn = adapter.get_connection(*args, **params)
                wrapper = ConnectionWrapper(conn, cls, service_name, params)
                cls._thread_local.connections[connection_key] = wrapper
            return cls._thread_local.connections[connection_key]

    @classmethod
    def close_connection(cls, service_name, **params):
        """
        Closes the connection for the specified service and parameters.

        Args:
            service_name (str): The name of the service.
            **params: Additional parameters for the service.
        """
        connection_key = cls._generate_connection_key(service_name, **params)

        # Close global connection
        with cls._lock:
            if connection_key in cls._connections:
                wrapper = cls._connections.pop(connection_key)
                adapter = cls._adapters.get(service_name)
                adapter.close(wrapper._connection)

        # Close thread-local connection
        if (
            hasattr(cls._thread_local, "connections")
            and connection_key in cls._thread_local.connections
        ):
            wrapper = cls._thread_local.connections.pop(connection_key)
            adapter = cls._adapters.get(service_name)
            adapter.close(wrapper._connection)

    @classmethod
    @contextmanager
    def connection_context(cls, service_name, **params):
        """
        Provides a context manager for a connection.

        Args:
            service_name (str): The name of the service.
            **params: Additional parameters for the service.

        Yields:
            ConnectionWrapper: A wrapper around the connection object.
        """
        connection = cls.get_connection(service_name, **params)
        try:
            yield connection
        finally:
            cls.close_connection(service_name, **params)

    @classmethod
    def close_all_connections(cls):
        """
        Closes all global and thread-local connections during program exit.
        """
        # Close global connections
        with cls._lock:
            for _, wrapper in list(cls._connections.items()):
                adapter = cls._adapters.get(wrapper._service_name)
                if adapter:
                    adapter.close(wrapper._connection)
            cls._connections.clear()

        # Close thread-local connections
        if hasattr(cls._thread_local, "connections"):
            for _, wrapper in list(cls._thread_local.connections.items()):
                adapter = cls._adapters.get(wrapper._service_name)
                if adapter:
                    adapter.close(wrapper._connection)
            cls._thread_local.connections.clear()

    def __repr__(self):
        """
        Returns a string representation of the ServiceManager's status.

        Returns:
            str: A summary of registered adapters and active connections.
        """
        registered_adapters = ", ".join(self._adapters.keys()) or "None"

        global_connections = len(self._connections)

        thread_local_connections = (
            len(getattr(self._thread_local, "connections", {}))
            if hasattr(self._thread_local, "connections")
            else 0
        )

        return (
            f"ServiceManager Status:\n"
            f"Registered Adapters: {registered_adapters}\n"
            f"Global Connections: {global_connections}\n"
            f"Thread-Local Connections: {thread_local_connections}"
        )


class ConnectionWrapper:
    """
    A wrapper for managing individual service connections.

    Attributes:
        _connection: The actual connection object.
        _manager (ServiceManager): The ServiceManager instance managing this connection.
        _service_name (str): The name of the service.
        _params (dict): The parameters used to create the connection.
    """

    def __init__(self, connection, manager, service_name, params):
        self._connection = connection
        self._manager = manager
        self._service_name = service_name
        self._params = params
        self._closed = False

    def __getattr__(self, name):
        """
        Delegates attribute access to the underlying connection object.

        Args:
            name (str): The attribute name.

        Returns:
            Any: The value of the requested attribute from the connection object.
        """
        return getattr(self._connection, name)

    def __getitem__(self, key):
        """
        Delegates subscript access to the underlying connection object.

        Args:
            key (Any): The key to access.

        Returns:
            Any: The value of the requested key from the connection object.
        """
        return self._connection[key]

    def __iter__(self):
        """
        Delegates iteration to the underlying connection object.

        Returns:
            Iterator: An iterator from the connection object.
        """
        return iter(self._connection)

    def close(self):
        """
        Closes the connection by delegating to the ServiceManager.
        """
        if not self._closed:
            self._manager.close_connection(self._service_name, **self._params)
            self._closed = True

    def __repr__(self):
        """
        Returns a string representation of the ConnectionWrapper.

        Returns:
            str: A summary of the connection's details.
        """
        return (
            f"ConnectionWrapper(\n"
            f"  Service Name: {self._service_name},\n"
            f"  Connection Object: {self._connection}\n"
            f")"
        )


atexit.register(ServiceManager.close_all_connections)
