import asyncio
import random
import ssl
import collections
from typing import Optional, Union

def _token(token: str) -> str:
    assert token.find("\r\n") == -1
    if token.startswith("oauth:"):
        return token
    self = "oauth:" + token

def _nick(nick: str) -> str:
    assert nick.find("\r\n") == -1
    return nick.lower()

def _channel(channel: str) -> str:
    assert channel.find("\r\n") == -1
    if channel.startswith("#"):
        return channel
    return "#" + channel.lower()

class Deque(asyncio.Queue):
    def _init(self, maxsize):
        self._queue = collections.deque(maxlen=maxsize)

class Client(object):
    def __init__(self, message_buffer_size: int = 1024, use_ssl: bool = False):
        self.__reader: Optional[asyncio.StreamReader] = None
        self.__writer: Optional[asyncio.StreamWriter] = None
        self.__ssl: bool = use_ssl
        self.__task: Optional[asyncio.Task] = None
        self.__buffer: Deque = Deque(message_buffer_size)
        self.__logged: bool = False
        self.__channel: Optional[str] = None

    async def login_oauth(self, token: str, nick: str, retry: int = 8, raise_connection_error: bool = False):
        assert not self.__logged
        assert retry >= 0

        token = _token(token)
        nick = _nick(nick)

        backoff = 0
        for t in range(retry + 1):
            try:
                #print("Backoff=", backoff, "Try_n=", t, "Retry=", retry)
                if self.__writer is None:
                    await self.__connect()

                self.__task = asyncio.create_task(self.__worker(), name="Client __worker")
                await self.__login(token, nick)
                return
            except Exception as e:
                if raise_connection_error or not isinstance(e, (ConnectionResetError, ConnectionRefusedError)):
                    raise

            if backoff <= 1:
                backoff += 1
            else:
                backoff *= 2

            await asyncio.sleep(backoff / 1.5)

    async def login_anonymous(self, retry: int = 8, raise_connection_error: bool = False):
        token = "random_string"
        # NOTE: There is a very small possibility that the random username has already been taken by someone
        nick = "justinfan" + str(random.randint(12345, 67890))
        await self.login_oauth(token, nick, retry, raise_connection_error)

    async def __connect(self):
        host = "irc.chat.twitch.tv"
        port = 6667
        ssl_port = 6697
        if self.__ssl:
            self.__reader, self.__writer = await asyncio.open_connection(
                host, ssl_port, ssl=ssl.create_default_context()
            )
        else:
            self.__reader, self.__writer = await asyncio.open_connection(host, port)
        self.__logged = True

    async def __login(self, token, nick):
        pass_command = f"PASS {token}\r\n"
        nick_command = f"NICK {nick}\r\n"

        self.__writer.write(pass_command.encode())
        self.__writer.write(nick_command.encode())
        await self.__writer.drain()

        # Acknowledgement/test connection
        welcome1 = f":tmi.twitch.tv 001 {nick} :Welcome, GLHF!\r\n"
        assert await self.__message() == welcome1.encode()

        welcome2 = f":tmi.twitch.tv 002 {nick} :Your host is tmi.twitch.tv\r\n"
        assert await self.__message() == welcome2.encode()

        welcome3 = f":tmi.twitch.tv 003 {nick} :This server is rather new\r\n"
        assert await self.__message() == welcome3.encode()

        welcome4 = f":tmi.twitch.tv 004 {nick} :-\r\n"
        assert await self.__message() == welcome4.encode()

        welcome5 = f":tmi.twitch.tv 375 {nick} :-\r\n"
        assert await self.__message() == welcome5.encode()

        welcome6 = f":tmi.twitch.tv 372 {nick} :You are in a maze of twisty passages, all alike.\r\n"
        assert await self.__message() == welcome6.encode()

        welcome7 = f":tmi.twitch.tv 376 {nick} :>\r\n"
        assert await self.__message() == welcome7.encode()

        # Capabilities
        req = "CAP REQ :twitch.tv/membership twitch.tv/tags twitch.tv/commands\r\n".encode()
        ack = ":tmi.twitch.tv CAP * ACK :twitch.tv/membership twitch.tv/tags twitch.tv/commands\r\n".encode()

        await self.__write(req)
        assert await self.__message() == ack

    async def __write(self, it):
        self.__writer.write(it)
        await self.__writer.drain()

    async def __message(self):
        message = await self.__buffer.get()
        self.__buffer.task_done()
        return message

    async def __worker(self):
        ping = b"PING :tmi.twitch.tv\r\n"
        pong = b"PONG :tmi.twitch.tv\r\n"

        while True:
            message = await self.__reader.readuntil(b"\r\n")
            if message == ping:
                await self.__write(pong)
            else:
                self.__buffer.put_nowait(message)

    async def join(self, channel: str):
        assert self.__logged
        command = f"JOIN {_channel(channel)}\r\n"
        await self.__write(command.encode())
        self.__channel = channel

    async def leave(self, channel: Optional[str] = None):
        assert self.__logged
        channel = channel if channel is not None else self.__channel
        assert channel is not None

        command = f"PART {_channel(channel)}\r\n"
        await self.__write(command.encode())
        self.__channel = None

    async def logout(self):
        assert self.__logged

        if self.__channel is not None:
            await self.part()

        self.__task.cancel()
        self.__writer.close()
        await self.__writer.wait_closed()

        self.__logged = False
        self.__task = None

    async def get_message(self, raw: bool = False) -> Union[str, bytes]:
        assert self.__logged
        assert self.__channel is not None
        if raw:
            return await self.__message()

        return (await self.__message()).decode()

    async def send_message(self, message: str, channel: Optional[str] = None):
        assert self.__logged
        channel = channel if channel is not None else self.__channel
        assert channel is not None

        assert len(message) <= 500
        command = f"PRIVMSG {_channel(channel)} : {message}\r\n"
        await self.__write(command.encode())

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.logout()

    @property
    def logged(self) -> bool:
        return self.__logged

    @property
    def channel(self) -> Optional[str]:
        return self.__channel

__all__ = ["Client"]
