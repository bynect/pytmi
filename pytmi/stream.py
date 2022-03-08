import asyncio
import ssl
import abc
import logging
from typing import Union, Optional


logger = logging.getLogger(__name__)


class LineStream(abc.ABC):
    @abc.abstractmethod
    async def connect(
        self, host: str, port: Union[int, str], ssl_ctx: Optional[ssl.SSLContext] = None
    ) -> None:
        pass

    @abc.abstractmethod
    async def disconnect(self) -> None:
        pass

    @abc.abstractmethod
    async def write(self, data: bytes) -> None:
        pass

    @abc.abstractmethod
    async def read(self) -> bytes:
        pass

    @abc.abstractproperty
    def connected(self) -> bool:
        pass


class DefaultLineStream(LineStream):
    def __init__(self) -> None:
        self.__writer: Optional[asyncio.StreamWriter] = None
        self.__reader: Optional[asyncio.StreamReader] = None

        self.__connected: bool = False
        self.__buffer: bytes = b""

    async def connect(
        self, host: str, port: Union[int, str], ssl_ctx: Optional[ssl.SSLContext] = None
    ) -> None:
        assert self.__reader is None and self.__writer is None
        logger.debug(
            "Trying to connect to %s:%s (ssl=%s)", host, port, ssl_ctx is not None
        )

        self.__reader, self.__writer = await asyncio.open_connection(
            host, port, ssl=ssl_ctx
        )
        self.__connected = True

    async def disconnect(self) -> None:
        assert self.connected and self.__writer is not None

        self.__writer.close()
        await self.__writer.wait_closed()

        DefaultLineStream.__init__(self)

    async def write(self, data: bytes) -> None:
        assert self.__writer

        self.__buffer += data
        newline = self.__buffer.find(b"\r\n")

        if newline != -1:
            newline += 2
            self.__writer.write(self.__buffer[:newline])
            await self.__writer.drain()
            self.__buffer = self.__buffer[newline:]

    async def read(self) -> bytes:
        assert self.__reader
        return await self.__reader.readuntil(b"\r\n")

    @property
    def connected(self) -> bool:
        return self.__connected


__all__ = ["LineStream", "DefaultLineStream"]
