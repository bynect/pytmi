import collections
import abc
from typing import Deque


class TmiBaseBuffer(abc.ABC):
    """Abstract buffer for TMI messages."""

    @abc.abstractmethod
    def append(self, message: str) -> None:
        """Append a message to the buffer."""

    @abc.abstractmethod
    def pop(self) -> str:
        """Pop the first message from the buffer.

        If no elements are present, raises an IndexError.
        """

    @abc.abstractmethod
    def peek(self) -> str:
        """Peek the first message in the buffer.

        If no elements are present, raises an IndexError.
        """

    @abc.abstractmethod
    def empty(self) -> bool:
        """Check if the buffer is empty."""


class TmiBuffer(TmiBaseBuffer):
    """Circular buffer for TMI messages."""

    def __init__(self, maxlen: int) -> None:
        self.__buf: Deque[str] = collections.deque(maxlen=maxlen)

    def append(self, message: str) -> None:
        """Append a message to the circular buffer.

        If the max size is reached the last element is overriden.
        """
        self.__buf.append(message)

    def pop(self) -> str:
        return self.__buf.pop()

    def peek(self) -> str:
        return self.__buf[-1]

    def empty(self) -> bool:
        return len(self.__buf) == 0
