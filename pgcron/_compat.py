from __future__ import annotations

import enum
import sys

if sys.version_info < (3, 11):

    class StrEnum(str, enum.Enum): ...

else:
    from enum import StrEnum  # type: ignore # noqa
