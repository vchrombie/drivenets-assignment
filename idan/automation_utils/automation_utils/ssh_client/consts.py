import re

# Remove ANSI escape
# Refer to
#  1 https://stackoverflow.com/questions/36279015/what-does-x1bb-do
#  2 https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
from enum import Enum

ansi_regex = (
    r"\x1b("
    r"(\[\??\d+[hl])|"
    r"([=<>a-kzNM78])|"
    r"([\(\)][a-b0-2])|"
    r"(\[\d{0,2}[ma-dgkjqi])|"
    r"(\[\d+;\d+[hfy]?)|"
    r"(\[;?[hf])|"
    r"(#[3-68])|"
    r"([01356]n)|"
    r"(O[mlnp-z]?)|"
    r"(/Z)|"
    r"(\d+)|"
    r"(\[\?\d;\d0c)|"
    r"(\d;\dR))"
)

remove_regex = r"\r([ ]+)?"

ANSI_ESCAPE = re.compile(ansi_regex, flags=re.IGNORECASE)
REMOVE_CHARS = re.compile(remove_regex, flags=re.IGNORECASE)

DEFAULT_DEVICE_PROMPT_REGEX = r"(.*)[$#>] ?$"

MAX_BUFFER = 65535

NO_OUTPUT_EXCEPTION_MSG = "Expected output from command, received none."


class KeySequence(Enum):
    CTRL_C = "\x03"
    CTRL_D = "\x04"
    CTRL_Z = "\x1A"
    TAB = "\x09"
    SPACE = "\x20"
    BACKSPACE = "\x08"
