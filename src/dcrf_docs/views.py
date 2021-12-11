import dataclasses
import logging
from typing import Type, Iterable, Tuple, List

from django.shortcuts import render
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from rest_framework.schemas.openapi import AutoSchema

from dcrf_docs import asyncapi
from dcrf_docs.action_docs import ActionDocs

log = logging.getLogger(__name__)


def cleanup_none(d: dict) -> dict:
    res = {}
    for k, v in d.items():
        if isinstance(v, dict):
            res[k] = cleanup_none(v)
        elif v is not None:
            res[k] = v
    return res


def introspect_consumer(
    consumer: Type[GenericAsyncAPIConsumer],
) -> Iterable[Tuple[asyncapi.ChannelName, asyncapi.ChannelItemObject]]:
    res: List[Tuple[asyncapi.ChannelName, asyncapi.ChannelItemObject]] = []
    for action_name, method_name in consumer.available_actions.items():
        method = getattr(consumer, method_name)
        docs = method.kwargs.get("docs", None)
        if docs:
            if not isinstance(docs, ActionDocs):
                log.warning("docs must be an instance of ActionDocs")
            serializer = docs.serializer
            name = serializer.__class__.__name__ if serializer else ""
            payload = AutoSchema().map_serializer(serializer) if serializer else {}
            res.append(
                (
                    asyncapi.ChannelName(docs.name or action_name),
                    asyncapi.ChannelItemObject(
                        description=docs.description or "",
                        subscribe=asyncapi.OperationObject(
                            message=asyncapi.MessageObject(name=name, payload=payload)
                        ),
                        publish=None,
                    ),
                )
            )
        else:
            log.warning(f"no docs for action: {action_name}")
    return res


def async_docs(request):
    info = asyncapi.Info(title="Hello world application", version="1.1.2")
    from chat import consumers

    channels: asyncapi.Channels = {
        channel_name: channel_item_obj
        for channel_name, channel_item_obj in introspect_consumer(consumers.RoomConsumer)
    }
    schema = asyncapi.AsyncAPISchema(
        asyncapi="2.2.0",
        info=info,
        channels=channels,
    )

    return render(
        request,
        "dcrf_docs/index.html",
        {"schema": cleanup_none(dataclasses.asdict(schema))},
    )
