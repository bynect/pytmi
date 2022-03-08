from typing import List, Tuple
import random


# Twitch IRC server `https://dev.twitch.tv/docs/irc/guide#connecting-to-twitch-irc`
TMI_SERVER = "irc.chat.twitch.tv"
TMI_SERVER_PORT = 6667
TMI_SERVER_SSLPORT = 6697

TMI_PING_MESSAGE = b"PING :tmi.twitch.tv\r\n"
TMI_PONG_MESSAGE = b"PONG :tmi.twitch.tv\r\n"

TMI_CAPS = [
    (
        f"CAP REQ :twitch.tv/{cap}\r\n".encode(),
        f":tmi.twitch.tv CAP * ACK :twitch.tv/{cap}\r\n".encode(),
    )
    for cap in ["membership", "tags", "commands"]
]


# Default client limits
# These are arbitrary values
CLIENT_MAX_RETRY = 8
CLIENT_MAX_BUFFER_SIZE = 128
CLIENT_MESSAGE_INTERVAL = 0.5


class LoginError(Exception):
    def __init__(
        self,
        tried: int,
        errs: List[Exception],
        message: str = "Unable to complete login",
    ) -> None:
        self.message = message
        self.tried = tried
        self.errs = errs
        super().__init__(message)

    def __str__(self) -> str:
        string = (
            f"{self.message}\nTried {self.tried} times, got {len(self.errs)} errors:\n"
        )
        for err in self.errs:
            string += str(err)
            string += "\n"
        return string


def make_anonymous_creds() -> Tuple[str, str]:
    token = "random_string"
    nick = "justinfan" + str(random.randint(12345, 67890))
    return (token, nick)


def make_privmsg(channel: str, message: str) -> bytes:
    assert len(message) <= 500
    return "PRIVMSG {} : {}\r\n".format(
        channel if channel.startswith("#") else "#" + channel, message
    ).encode()


def normalize_token(token: str) -> str:
    assert token.find("\r\n") == -1
    if token.startswith("oauth:"):
        return token
    return "oauth:" + token


def normalize_nick(nick: str) -> str:
    assert nick.find("\r\n") == -1
    return nick.lower()


def normalize_channel(channel: str) -> str:
    assert channel.find("\r\n") == -1
    if channel.startswith("#"):
        return channel
    return "#" + channel
