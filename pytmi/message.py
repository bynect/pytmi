from typing import Optional, Union, Dict, Any


class Message(object):
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
        if tags is None:
            return

        tags_list = tags.split(";")
        for tag in tags_list:
            key, value = tag.split("=", 1)

            norm: Any = value

            if value.isspace() or value == "":
                norm = None

            elif value.isnumeric():
                norm = int(value)

            self.__tags[key] = norm

    @property
    def raw(self) -> Optional[str]:
        return self.__raw

    @property
    def tags(self) -> Dict[str, Any]:
        return self.__tags

    @property
    def net(self) -> Optional[str]:
        return self.__net

    @property
    def command(self) -> Optional[str]:
        return self.__command

    @property
    def left(self) -> Optional[str]:
        return self.__left

    @property
    def valid(self) -> bool:
        return self.__parsed


__all__ = ["Message"]
