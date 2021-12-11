import dataclasses
from typing import Any, Dict, Literal, Union, Optional


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
