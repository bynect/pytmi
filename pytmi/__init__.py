__version__ = "0.2.1"

from .stream import *
from .message import *
from .client import *


# Default client limits
# These are arbitrary value
MAX_RETRY = 8
MAX_LENGTH = 128
