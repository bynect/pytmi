from typing import Optional, Union, Dict, Any


class TmiMessage(object):
    """Message abstraction for IRC messages with TMI tags."""

    def __init__(self, message: Union[str, bytes]) -> None:
        if isinstance(message, bytes):
            message = message.decode()

        message = message.strip()

        self.__tags: Dict[str, Any] = {}

        self.__net: Optional[str] = None
        self.__command: Optional[str] = None

        self.__raw: str = message
        self.__left: Optional[str] = None

        self.__parsed: bool = False

        try:
            self.__parse_raw()
        except:
            self.__left = self.__raw

    def __parse_raw(self) -> None:
        """Parse the raw message and populate the `tags`, `net` and `command` properties."""

        raw = self.__raw
        if raw.startswith("@"):
            raw = raw[1:]
            tags, raw = raw.split(" :", 1)
            self.__parse_tags(tags)

        self.__net, raw = raw.split(" ", 1)

        temp = raw.split("\r\n", 1)
        if len(temp) > 1:
            self.__left = temp[1]

        self.__command = temp[0].lstrip()

        self.__parsed = True

    def __parse_tags(self, tags: str) -> None:
        """Parse the given tags populating the `tags` property with a key-value dict."""

        if tags == None:
            return

        tags_list = tags.split(";")

        for tag in tags_list:
            key, value = tag.split("=", 1)

            norm = value

            if value.isspace() or value == "":
                norm = None

            elif value.isnumeric():
                norm = int(value)

            self.__tags[key] = norm

    @property
    def raw(self) -> Optional[str]:
        """Return the raw message string, aka the original input string."""
        return self.__raw

    @property
    def tags(self) -> Dict[str, Any]:
        """Return a dict populated with the message tags key-value."""
        return self.__tags

    @property
    def net(self) -> Optional[str]:
        """Return a string containing the address part of the message."""
        return self.__net

    @property
    def command(self) -> Optional[str]:
        """Return a string containing the command part of the message."""
        return self.__command

    @property
    def left(self) -> Optional[str]:
        """Return a string containing the unparsed part of the message."""
        return self.__left

    @property
    def parsed(self) -> bool:
        """Return `True` if the message was parsed correctly, otherwise `False`."""
        return self.__parsed


__all__ = [
    "TmiMessage",
]
