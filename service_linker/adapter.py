import logging
from abc import ABC, abstractmethod

_logger = logging.getLogger(__name__)


class ServiceAdapter(ABC):
    """
    Abstract base class for creating service adapters.

    Attributes:
        thread_safe (bool): Indicates whether the connection is thread-safe. Must be overridden in subclasses.
        service_name (str): The name of the service associated with this adapter. Must be overridden in subclasses.
    """

    thread_safe = None
    service_name = None

    def __init_subclass__(cls, **kwargs):
        """
        Validates that subclasses override the required attributes `thread_safe` and `service_name`.

        Args:
            **kwargs: Additional arguments for subclass initialization.

        Raises:
            TypeError: If `thread_safe` or `service_name` is not overridden in the subclass.
        """
        super().__init_subclass__(**kwargs)
        if cls.thread_safe is None:
            raise TypeError(f"Class '{cls.__name__}' must override 'thread_safe'")
        if cls.service_name is None:
            raise TypeError(f"Class '{cls.__name__}' must override 'service_name'")

    def get_connection(self, **params):
        """
        Retrieves a connection by delegating to the `do_get_connection` method.

        Args:
            **params: Parameters needed to establish the connection.

        Returns:
            The established connection.
        """
        _logger.debug(f"Getting connection for service '{self.service_name}'")
        connection = self.do_get_connection(**params)
        _logger.debug(
            f"Successfully retrieved connection for service '{self.service_name}'"
        )
        return connection

    def close(self, connection):
        """
        Closes a connection by delegating to the `do_close` method.

        Args:
            connection: The connection to be closed.
        """
        _logger.debug(f"Closing connection for service '{self.service_name}'")
        self.do_close(connection)
        _logger.debug(
            f"Successfully closed connection for service '{self.service_name}'"
        )

    @abstractmethod
    def do_get_connection(self, *args, **params):
        """
        Abstract method to establish a connection. Must be implemented in subclasses.

        Args:
            *args: Parameters needed to establish the connection.
            **params: Parameters needed to establish the connection.

        Returns:
            The established connection.
        """
        pass

    @abstractmethod
    def do_close(self, connection):
        """
        Abstract method to close a connection. Must be implemented in subclasses.

        Args:
            connection: The connection to be closed.
        """
        pass
