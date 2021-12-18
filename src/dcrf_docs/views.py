import dataclasses

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.module_loading import import_string
from rest_framework.request import Request

from . import asyncapi, introspect


def asyncapi_docs(request: Request) -> HttpResponse:
    app = import_string(settings.ASGI_APPLICATION)
    return render(
        request,
        "dcrf_docs/index.html",
        dict(
            schema=asyncapi.cleanup_none(
                dataclasses.asdict(
                    asyncapi.AsyncAPISchema(
                        asyncapi="2.2.0",
                        info=dict(
                            title="Hello world application",
                            version="1.1.2",
                        ),
                        channels=introspect.introspect_application(app),
                    )
                )
            )
        ),
    )
