import socket
import abc
from typing import Optional


# Twitch IRC server `https://dev.twitch.tv/docs/irc/guide#connecting-to-twitch-irc`
TMI_SERVER = "irc.chat.twitch.tv"
TMI_SERVER_PORT = 6667
TMI_SERVER_SSLPORT = 6697


# Default connection limits
# Note that `MAX_MSGSIZE` is not an arbitrary value but is the lenght indicated by the IRC standard `RFC 1459`
MAX_MSGSIZE = 512
MAX_BUFSIZE = 1024


class TmiBaseConnection(abc.ABC):
    """Base class for the TMI protocol connection."""

    @abc.abstractmethod
    def connect(self, host: str, port: int) -> bool:
        """Create a connection to the server represented by `host` and `port`.
        When a new connection is created `bytes_sent` and `bytes_recvd` should be set to zero.

        Return `True` if the operation succeeded, `False` otherwise.
        In case another connection is alredy in place, this method should return `False`.
        """

    @abc.abstractmethod
    def disconnect(self) -> bool:
        """Terminate the connection with the server.

        Return `True` if the operation succeeded, `False` otherwise.
        In case no connection is in place, this method should return `False`.
        """

    @abc.abstractmethod
    def send(self, message: bytes) -> None:
        """Send to the server a message of `bytes` of maximum size `MAX_MSGSIZE`."""

    @abc.abstractmethod
    def recv(self) -> bytes:
        """Receive from the server a message of `bytes` of maximum size `MAX_MSGSIZE`."""

    @abc.abstractproperty
    def bytes_sent(self) -> int:
        """Return the number of `bytes` sent to the server.

        This property will be set to zero when the `connect` method is called.
        """

    @abc.abstractproperty
    def bytes_recvd(self) -> int:
        """Return the number of `bytes` received from the server.

        This property will be set to zero when the `connect` method is called.
        """

    @abc.abstractproperty
    def connected(self) -> bool:
        """Return `True` if there is a connection in place, `False` otherwise."""


class TmiConnection(TmiBaseConnection):
    """Class for the TMI protocol connection without SSL."""

    def __init__(self):
        self.__sent: int = 0
        self.__recvd: int = 0

        self.__connected: bool = False
        self.__sock: Optional[socket.socket] = None

    def connect(self, host: str = TMI_SERVER, port: int = TMI_SERVER_PORT) -> bool:
        if self.__connected or self.__sock != None:
            return False

        try:
            sock = socket.socket()
            sock.connect((host, port))

            self.__sent = 0
            self.__recvd = 0

            self.__sock = sock
            self.__connected = True
        finally:
            return self.__connected

    def disconnect(self) -> bool:
        if not self.__connected or self.__sock == None:
            return False
        try:
            self.__sock.close()
            self.__connected = False
            self.__sock = None
        except:
            return False

        return True

    def send(self, message: bytes) -> None:
        if not self.__connected or self.__sock == None:
            raise AttributeError("Connection not initiated")

        self.__sent += self.__sock.send(message)

    def recv(self) -> bytes:
        if not self.__connected or self.__sock == None:
            raise AttributeError("Connection not initiated")

        message = self.__sock.recv(MAX_BUFSIZE)
        self.__recvd += len(message)

        return message

    @property
    def bytes_sent(self) -> int:
        return self.__sent

    @property
    def bytes_recvd(self) -> int:
        return self.__recvd

    @property
    def connected(self) -> bool:
        return self.__connected


class TmiSslConnection(TmiBaseConnection):
    """Class for the TMI protocol connection over SSL."""
    ### TODO ###


__all__ = [
    "TmiBaseConnection",
    "TmiConnection",
    "TmiSslConnection",
    "MAX_MSGSIZE",
    "MAX_BUFSIZE"
]
