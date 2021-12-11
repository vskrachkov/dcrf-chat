import dataclasses
import logging
from typing import Type, Dict, Callable

from asgiref.typing import ASGI2Protocol
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf import settings
from django.shortcuts import render
from django.utils.module_loading import import_string
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
) -> asyncapi.Channels:
    res: asyncapi.Channels = {}
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


def handle__URLRouter(app: URLRouter) -> asyncapi.Channels:
    res: asyncapi.Channels = {}
    for route in app.routes:
        if hasattr(route.callback, "consumer_class"):
            consumer = getattr(route.callback, "consumer_class")
            res = res | introspect_consumer(consumer)
    return res


ASGIIntrospectionHandler = Callable[[ASGI2Protocol], asyncapi.Channels]


def introspect_application(app: ASGI2Protocol) -> asyncapi.Channels:
    handlers: Dict[ASGI2Protocol, ASGIIntrospectionHandler] = {
        ProtocolTypeRouter: handle__ProtocolTypeRouter,
        URLRouter: handle__URLRouter,
    }
    if handler := handlers.get(type(app), None):
        return handler(app)
    return {}


def async_docs(request):
    info = asyncapi.Info(title="Hello world application", version="1.1.2")
    asgi_app = import_string(settings.ASGI_APPLICATION)
    channels: asyncapi.Channels = introspect_application(asgi_app)
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
