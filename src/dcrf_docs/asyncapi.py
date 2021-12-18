import dataclasses
from typing import Any, Dict, Literal, Optional


@dataclasses.dataclass
class Info:
    title: str
    version: str


@dataclasses.dataclass
class MessageObject:
    name: str
    payload: Any


@dataclasses.dataclass
class OperationObject:
    message: "MessageObject"


ChannelName = str


@dataclasses.dataclass
class ChannelItemObject:
    description: str
    subscribe: Optional["OperationObject"]
    publish: Optional["OperationObject"]


Channels = Dict[ChannelName, ChannelItemObject]


@dataclasses.dataclass
class AsyncAPISchema:
    asyncapi: Literal["2.2.0"]
    info: "Info"
    channels: "Channels"


def cleanup_none(d: dict) -> dict:
    res = {}
    for k, v in d.items():
        if isinstance(v, dict):
            res[k] = cleanup_none(v)
        elif v is not None:
            res[k] = v
    return res
