from enum import StrEnum


class Decision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    FORBIDDEN = "forbidden"