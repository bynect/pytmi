"""Module containing stream related abstractions."""

import asyncio
import ssl
import abc
from typing import Union, Optional


class TmiBaseStream(abc.ABC):
    """Asynchronous stream base class for the IRC-TMI protocol."""

    @abc.abstractmethod
    async def connect(
        self, host: str, port: Union[int, str], ssl_ctx: Optional[ssl.SSLContext] = None
    ) -> None:
        """Create a connection to the server represented by `host` and `port`.
        If `ssl_ctx` is not `None` initiates an SSL connection.

        Must raise `AttributeError` if a connection is alredy in place.
        May raise `OSError` exceptions.
        """

    @abc.abstractmethod
    async def disconnect(self) -> None:
        """Terminate the connection with the server.

        Must raise `AttributeError` if no connection is in place.
        May raise `OSError` exceptions.
        """

    @abc.abstractmethod
    async def write_buf(self, data: bytes) -> None:
        """Write to a buffer and when the delimiter `\\r\\n` is found flushes it.

        Must raise `AttributeError` if no connection is in place.
        May raise `OSError` exceptions.
        """

    @abc.abstractmethod
    async def read_buf(self) -> bytes:
        """Read from a buffered stream until the delimiter `\\r\\n` or EOF.

        Must raise `AttributeError` if no connection is in place.
        May raise `OSError` exceptions.
        """

    @abc.abstractproperty
    def connected(self) -> bool:
        """Return `True` if there is a connection in place, otherwise `False`."""

    @abc.abstractproperty
    def use_ssl(self) -> bool:
        """Return `True` if a `ssl_ctx` was given in the current connection.

        If there is no connection in place or no `ssl_ctx` was given return `False`.
        """


class TmiStream(TmiBaseStream):
    """Stream class for the IRC-TMI protocol which provides SSL support."""

    def __init__(self) -> None:
        self.__writer: Optional[asyncio.StreamWriter] = None
        self.__reader: Optional[asyncio.StreamReader] = None
        self.__use_ssl: bool = False

        self.__connected: bool = False
        self.__buffer: bytes = b""

    async def connect(
        self, host: str, port: Union[int, str], ssl_ctx: Optional[ssl.SSLContext] = None
    ) -> None:
        assert self.__reader is None
        assert self.__writer is None

        if ssl_ctx is not None:
            self.__reader, self.__writer = await asyncio.open_connection(
                host, port, ssl=ssl_ctx
            )
        else:
            self.__reader, self.__writer = await asyncio.open_connection(host, port)

        self.__use_ssl = ssl_ctx is not None
        self.__connected = True

    async def disconnect(self):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return

        assert self.connected

        self.__writer.close()
        await self.__writer.wait_closed()

        self.__reset()

    def __reset(self):
        self.__writer = None
        self.__reader = None
        self.__use_ssl = False
        self.__connected = False

    async def write_buf(self, data: bytes) -> None:
        assert self.__writer

        self.__buffer += data
        newline = self.__buffer.find(b"\r\n")

        if newline != -1:
            newline += 2
            self.__writer.write(self.__buffer[:newline])
            await self.__writer.drain()
            self.__buffer = self.__buffer[newline:]

    async def read_buf(self) -> bytes:
        assert self.__reader
        return await self.__reader.readuntil(b"\r\n")

    @property
    def connected(self):
        if self.__connected:
            assert self.__writer is not None
            closing = self.__writer.is_closing()
            if closing == True:
                self.__reset()
            return True

        return False

    @property
    def use_ssl(self):
        assert self.connected
        return self.__use_ssl


__all__ = [
    "TmiBaseStream",
    "TmiStream",
]
