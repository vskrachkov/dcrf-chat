import logging
from typing import Any, Type, Union

from asgiref.typing import ASGI2Protocol
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.routing import ProtocolTypeRouter, URLRouter
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from rest_framework.schemas.openapi import AutoSchema

from dcrf_docs import asyncapi
from dcrf_docs.action_docs import ActionDocs

log = logging.getLogger(__name__)


def introspect_consumer(consumer: Any) -> asyncapi.Channels:
    res: asyncapi.Channels = {}

    if hasattr(consumer, "consumer_class"):
        return introspect_consumer(consumer.consumer_class)

    if hasattr(consumer, "applications"):
        for stream, consumer_class in consumer.applications.items():
            res = res | introspect_consumer(consumer_class)
        return res

    if hasattr(consumer, "available_actions"):
        for action_name, method_name in consumer.available_actions.items():
            method = getattr(consumer, method_name)
            docs = method.kwargs.get("docs", None)
            if docs:
                if not isinstance(docs, ActionDocs):
                    log.warning("docs must be an instance of ActionDocs")
                serializer = docs.serializer
                name = serializer.__class__.__name__ if serializer else ""
                payload = AutoSchema().map_serializer(serializer) if serializer else {}
                res[
                    asyncapi.ChannelName(docs.name or action_name)
                ] = asyncapi.ChannelItemObject(
                    description=docs.description or "",
                    subscribe=asyncapi.OperationObject(
                        message=asyncapi.MessageObject(name=name, payload=payload)
                    ),
                    publish=None,
                )
            else:
                log.warning(f"no docs for action: {action_name}")

    return res


def get_root_app(app: ASGI2Protocol) -> ASGI2Protocol:
    while hasattr(app, "inner"):
        app = getattr(app, "inner")
        continue
    return app


def handle__ProtocolTypeRouter(app: ProtocolTypeRouter) -> asyncapi.Channels:
    if ws := app.application_mapping.get("websocket"):
        root_app = get_root_app(ws)
        return introspect_application(root_app)
    return {}


def handle__URLRouter(app: URLRouter) -> asyncapi.Channels:
    res: asyncapi.Channels = {}
    for route in app.routes:
        if hasattr(route.callback, "consumer_class"):
            consumer = getattr(route.callback, "consumer_class")
            res = res | introspect_application(consumer)
        else:
            res = res | introspect_application(route)
    return res


def introspect_application(
    app: Union[
        ProtocolTypeRouter,
        URLRouter,
        Type[GenericAsyncAPIConsumer],
        Type[AsyncJsonWebsocketConsumer],
    ]
) -> asyncapi.Channels:
    if isinstance(app, ProtocolTypeRouter):
        return handle__ProtocolTypeRouter(app)
    if isinstance(app, URLRouter):
        return handle__URLRouter(app)
    if issubclass(app, (GenericAsyncAPIConsumer, AsyncJsonWebsocketConsumer)):
        return introspect_consumer(app)
    return {}