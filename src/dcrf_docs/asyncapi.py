import dataclasses
from typing import Dict, Literal, Optional, TypedDict

ChannelName = str


class ChannelItemObject(TypedDict):
    description: str
    subscribe: Optional[dict]
    publish: Optional[dict]


Channels = Dict[ChannelName, ChannelItemObject]


@dataclasses.dataclass
class AsyncAPISchema:
    asyncapi: Literal["2.2.0"]
    info: dict
    channels: "Channels"


def cleanup_none(d: dict) -> dict:
    res = {}
    for k, v in d.items():
        if isinstance(v, dict):
            res[k] = cleanup_none(v)
        elif v is not None:
            res[k] = v
    return res
