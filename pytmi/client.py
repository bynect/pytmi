import asyncio
import ssl
import logging
from typing import Optional, Union, cast

from pytmi.common import *
from pytmi.stream import *
from pytmi.message import Message


logger = logging.getLogger(__name__)


class Client(object):
    def __init__(
        self,
        use_ssl: bool = True,
        stream: LineStream = None,
    ) -> None:
        if stream is None:
            stream = DefaultLineStream()

        self.__stream: LineStream = stream
        self.__use_ssl: bool = use_ssl

        self.__logged: bool = False
        self.__joined: Optional[str] = None

    async def login_oauth(
        self, token: str, nick: str, retry: int = CLIENT_MAX_RETRY
    ) -> None:
        if self.__logged:
            raise ValueError("Alredy logged in")

        token = normalize_token(token)
        nick = normalize_nick(nick)

        backoff = 0
        _retry = max(1, retry)
        errs = []

        while _retry > 0:
            logger.debug(
                "Trying to login %i of %i (backoff time %f)",
                retry - _retry,
                retry,
                backoff / 1.5,
            )

            try:
                if not self.__stream.connected:
                    await self.__connect()

                await self.__login(token, nick)
                return
            except Exception as e:
                # TODO: Fixme, maybe this can be dealt with better
                if isinstance(e, (ConnectionResetError, ConnectionRefusedError)):
                    raise

                errs.append(e)
                logger.debug("While trying to login got exception", exc_info=1)

            if backoff <= 1:
                backoff += 1
            else:
                backoff *= 2

            await asyncio.sleep(backoff / 1.5)
            _retry -= 1

        raise LoginError(retry, errs)

    async def login_anonymous(self, retry: int = CLIENT_MAX_RETRY) -> None:
        await self.login_oauth(*make_anonymous_creds(), retry=retry)

    async def __connect(self) -> None:
        if self.__use_ssl:
            await self.__stream.connect(
                TMI_SERVER, TMI_SERVER_SSLPORT, ssl_ctx=ssl.create_default_context()
            )
        else:
            await self.__stream.connect(TMI_SERVER, TMI_SERVER_PORT)

    async def __login(self, token: str, nick: str) -> None:
        # Authentication
        pass_command = "PASS " + token + "\r\n"
        await self.__stream.write(pass_command.encode())

        nick_command = "NICK " + nick + "\r\n"
        await self.__stream.write(nick_command.encode())

        # Acknowledgement/test connection
        welcome1 = f":tmi.twitch.tv 001 {nick} :Welcome, GLHF!\r\n"
        assert await self.__stream.read() == welcome1.encode()

        welcome2 = f":tmi.twitch.tv 002 {nick} :Your host is tmi.twitch.tv\r\n"
        assert await self.__stream.read() == welcome2.encode()

        welcome3 = f":tmi.twitch.tv 003 {nick} :This server is rather new\r\n"
        assert await self.__stream.read() == welcome3.encode()

        welcome4 = f":tmi.twitch.tv 004 {nick} :-\r\n"
        assert await self.__stream.read() == welcome4.encode()

        welcome5 = f":tmi.twitch.tv 375 {nick} :-\r\n"
        assert await self.__stream.read() == welcome5.encode()

        welcome6 = f":tmi.twitch.tv 372 {nick} :You are in a maze of twisty passages, all alike.\r\n"
        assert await self.__stream.read() == welcome6.encode()

        welcome7 = f":tmi.twitch.tv 376 {nick} :>\r\n"
        assert await self.__stream.read() == welcome7.encode()

        # Capabilities
        for req, ack in TMI_CAPS:
            await self.__stream.write(req)
            assert await self.__stream.read() == ack

        self.__logged = True
        logger.info("Logged in")

    async def logout(self) -> None:
        if not self.__logged:
            raise ValueError("Not logged in")

        if self.__joined is not None:
            await self.part(self.__joined)

        await self.__stream.disconnect()

        self.__logged = False
        logger.info("Logged out")

    async def join(self, channel: str) -> None:
        if not self.__logged:
            raise ValueError("Not logged in")

        channel = normalize_channel(channel)
        command = "JOIN " + channel + "\r\n"
        await self.__stream.write(command.encode())

        self.__joined = channel
        logger.info("Joined channel %s", channel)

    async def part(self, channel: Optional[str] = None) -> None:
        if not self.__logged:
            raise ValueError("Not logged in")

        if channel is None:
            channel = self.__joined
            if channel is None:
                raise AttributeError("Unspecified channel to part")

        assert channel is not None
        channel = cast(str, normalize_channel(channel))

        command = "PART " + channel + "\r\n"
        await self.__stream.write(command.encode())
        self.__joined = None

        logger.info("Parted channel %s", channel)

    async def privmsg(self, message: str, channel: Optional[str] = None) -> None:
        if not self.__logged:
            raise AttributeError("Not logged in")

        if channel is None:
            channel = self.__joined

        assert channel is not None
        channel = cast(str, normalize_channel(channel))

        await self.__stream.write(make_privmsg(channel, message))
        logger.debug("Sent a privmsg to channel %s", channel)

    async def get_message(self) -> Message:
        message = await self.get_message_raw()
        return Message(message)

    async def get_message_raw(self) -> bytes:
        if not self.__logged:
            raise AttributeError("Not logged in")

        line = await self.__stream.read()

        if line == TMI_PING_MESSAGE:
            await self.__stream.write(TMI_PONG_MESSAGE)
            line = await self.__stream.read()

        return line

    @property
    def logged(self) -> bool:
        return self.__logged

    @property
    def joined(self) -> Optional[str]:
        return self.__joined


__all__ = ["Client"]
