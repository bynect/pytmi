import time
import random
import abc
from typing import Type, Optional, List

from pytmi.connection import *
from pytmi.message import *


# Twitch IRC extensions `https://dev.twitch.tv/docs/irc/guide#twitch-irc-capabilities`
TMI_REQMEMBERSHIP = b"CAP REQ :twitch.tv/membership\r\n"
TMI_REQTAGS = b"CAP REQ :twitch.tv/tags\r\n"
TMI_REQCOMMANDS = b"CAP REQ :twitch.tv/commands\r\n"

TMI_REQACK = "CAP * ACK"


# Every 5 minutes the server send a PING and expect a PONG
PING_MESSAGE = "PING :tmi.twitch.tv\r\n"
PONG_MESSAGE = "PONG :tmi.twitch.tv\r\n"


# Default client limits
# Those are arbitrary value
MAX_RETRY = 8


class TmiBaseClient(abc.ABC):
    """Base client for TMI connection."""


class TmiClient(TmiBaseClient):
    """Client for TMI connection."""

    def __init__(self, ssl: bool = False, connection: Optional[Type[TmiBaseConnection]] = None):
        self.__ssl: bool = ssl

        if connection == None:
            connection_class = TmiSslConnection if ssl else TmiConnection
        else:
            connection_class = connection

        self.__connection = connection_class()

        self.__joined_channel: Optional[str] = None

        self.__message_buffer: List[str] = []

        if ssl:
            raise NotImplementedError("SSL is currently not implemented.")

    def login_oauth(self, token: str, nick: str, retry: int = MAX_RETRY) -> bool:
        """Create a connection to Twitch and authenticate you using the oauth tokens.

        `token` is the oauth token of your Twitch account.
        `nick` is your Twitch username.

        If you prefer an anonymous login you can use the `login_anonymous` method.

        Return `True` if the operation succeeded, `False` otherwise.
        If the login fail, it will be reattempted `retry` times before returning.
        """

        if self.__connection.connected:
            return False

        if not token.startswith("oauth:"):
            token = "oauth:" + token

        nick = nick.lower()

        if retry < 0:
            retry = -retry

        backoff = 0
        for r in range(retry):
            try:
                if self.__login(token, nick):
                    return True
            except Exception as e:
                if isinstance(e, OSError):
                    raise

            if backoff <= 1:
                backoff += 1
            else:
                backoff *= 2
                time.sleep(backoff / 1.5)

        return False

    def login_anonymous(self) -> bool:
        """Create a connection to Twitch without authentication."""

        if self.__connection.connected:
            return False

        for r in range(MAX_RETRY):
            token = "random_string"
            nick = "justinfan" + str(r) + str(random.randint(123, 456))

            if self.login_oauth(token, nick):
                return True

        return False

    def __login(self, token: str, nick: str) -> bool:
        """Internal login method, use `login_oauth` or `login_anonymous`."""

        if not self.__connection.connect():
            return False

        # Authenticate using oauth token and nick
        token = "PASS " + token + "\r\n"
        nick = "NICK " + nick.lower() + "\r\n"

        self.__connection.send(token.encode())
        self.__connection.send(nick.encode())

        if self.__connection.bytes_sent <= 0:
            return False

        buf = self.__connection.recv()

        if not buf.decode().find(":Welcome, GLHF!"):
            return False

        # Enables TMI extensions over the IRC protocol
        self.__connection.send(TMI_REQMEMBERSHIP)
        self.__connection.send(TMI_REQTAGS)
        self.__connection.send(TMI_REQCOMMANDS)

        buf = self.__connection.recv()

        if not buf.decode().find(TMI_REQACK):
            return False

        self.__message_buffer.clear()

        return True

    def logout(self) -> bool:
        """Terminate the established connection to Twitch and logout.

        Send the PART command if called when a JOIN was used.
        """

        if not self.__connection.connected:
            return False

        if self.__joined_channel != None:
            self.part()

        return self.__connection.disconnect()

    def __del__(self) -> None:
        """Logout automatically when TmiClient is disposed."""

        try:
            self.logout()
        except:
            pass

    def get_string(self) -> Optional[str]:
        """Get the current buffered message as a string."""

        ### XXX ###

        if not self.__connection.connected:
            return

        if len(self.__message_buffer) == 0:
            buf = self.__connection.recv()

            try:
                buf = buf.decode()
            except:
                return

            if PING_MESSAGE in buf:
                self.__connection.send(PONG_MESSAGE.encode())
                buf = buf.replace(PING_MESSAGE, "")

            message_list = buf.split("\r\n")
            message_list = [m for m in message_list if TMI_REQACK not in m]

            self.__message_buffer.extend(message_list)

            if len(self.__message_buffer) == 0:
                return self.get()

        return self.__message_buffer.pop(0)

    def get_message(self) -> Optional[TmiMessage]:
        """Get the current buffered message as a parsed TmiMessage instance."""

        if not self.__connection.connected:
            return

        message = self.get_string()

        if message == None or message == "":
            return

        return TmiMessage(message)

    def join(self, channel: str) -> bool:
        """Send the JOIN command to the server to join `channel`."""

        if not self.__connection.connected:
            return False

        if not channel.startswith("#"):
            channel = "#" + channel

        self.__joined_channel = channel

        command = "JOIN " + channel + "\r\n"
        self.__connection.send(command.encode())

        return True

    def part(self, channel: Optional[str] = None) -> bool:
        """Send the PART command to the server to leave `channel`."""

        if not self.__connection.connected:
            return False

        if channel == None:
            channel = self.__joined_channel

        if not channel.startswith("#"):
            channel = "#" + channel

        self.__joined_channel = None

        command = "PART " + channel + "\r\n"
        self.__connection.send(command.encode())

        return True

    def privmsg(self, message: str, channel: Optional[str] = None) -> None:
        """Send the PRIVMSG command to the server to send `message` in `channel`."""

        if not self.__connection.connected:
            return False

        if channel == None:
            channel = self.__joined_channel

        if not channel.startswith("#"):
            channel = "#" + channel

        command = "PRIVMSG " + channel + " :" + message + "\r\n"
        self.__connection.send(command.encode())


__all__ = [
    "TmiBaseClient",
    "TmiClient",
]
