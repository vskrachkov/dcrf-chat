import typing_extensions
from django.contrib.auth.models import AbstractUser
from django.db import models

if typing_extensions.TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class User(AbstractUser):
    if typing_extensions.TYPE_CHECKING:
        current_rooms: RelatedManager["Room"]


class Room(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms")
    current_users = models.ManyToManyField(
        User, related_name="current_rooms", blank=True
    )
    if typing_extensions.TYPE_CHECKING:
        messages: RelatedManager["Message"]

    def __str__(self) -> str:
        return f"Room({self.name} {self.host})"


class Message(models.Model):
    room = models.ForeignKey(
        "chat.Room", on_delete=models.CASCADE, related_name="messages"
    )
    text = models.TextField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Message({self.user} {self.room})"
