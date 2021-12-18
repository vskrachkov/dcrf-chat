from typing import Any

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from rest_framework.request import Request
from rest_framework.reverse import reverse

from .models import Room


def index(request: Request) -> HttpResponse:
    if request.method == "POST":
        name = request.POST.get("name", None)
        if name:
            room, _ = Room.objects.get_or_create(name=name, host=request.user)
            return HttpResponseRedirect(reverse("chat:room", args=[room.pk]))
    return render(request, "chat/index.html")


def room(request: Request, pk: Any) -> HttpResponse:
    room: Room = get_object_or_404(Room, pk=pk)
    return render(
        request,
        "chat/room.html",
        {
            "room": room,
        },
    )
