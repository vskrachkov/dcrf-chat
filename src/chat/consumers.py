import json
from typing import Any, Iterable, Optional

from channels.db import database_sync_to_async
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer import generics, model_observer
from djangochannelsrestframework.observer.model_observer import Action
from djangochannelsrestframework.permissions import IsAuthenticated

from dcrf_docs.action_docs import ActionDocs

from .models import Message, Room, User
from .serializers import (
    CreateMessageActionSerializer,
    JoinRoomActionSerializer,
    LeaveRoomActionSerializer,
    MessageSerializer,
    RoomSerializer,
    SubscribeToMessageInRoomSerializer,
    UserSerializer,
)


class RoomConsumer(generics.ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = "pk"
    room_subscribe: Any
    permission_classes = [IsAuthenticated]

    async def disconnect(self, code: int) -> None:
        if hasattr(self, "room_subscribe"):
            await self.remove_user_from_room(self.room_subscribe)
            await self.notify_users()
        await super().disconnect(code)

    @generics.action(docs=ActionDocs(serializer=JoinRoomActionSerializer()))  # type: ignore
    async def join_room(self, pk: Any, **kwargs: Any) -> None:
        self.room_subscribe = pk
        await self.add_user_to_room(pk)
        await self.notify_users()

    @generics.action(docs=ActionDocs(serializer=LeaveRoomActionSerializer()))  # type: ignore
    async def leave_room(self, pk: Any, **kwargs: Any) -> None:
        await self.remove_user_from_room(pk)

    @generics.action(docs=ActionDocs(serializer=CreateMessageActionSerializer()))  # type: ignore
    async def create_message(self, message: str, **kwargs: Any) -> None:
        room: Room = await self.get_room(pk=self.room_subscribe)
        await database_sync_to_async(Message.objects.create)(
            room=room, user=self.scope["user"], text=message
        )

    @generics.action(docs=ActionDocs(serializer=SubscribeToMessageInRoomSerializer()))  # type: ignore
    async def subscribe_to_messages_in_room(self, pk: Any, **kwargs: Any) -> None:
        await self.message_activity.subscribe(room=pk)  # type: ignore

    @model_observer(Message)
    async def message_activity(self, message: Message, **kwargs: Any) -> None:
        await self.send_json(message)

    @message_activity.groups_for_signal  # type: ignore
    def message_activity(self, instance: Message, **kwargs: Any) -> Iterable[str]:
        yield "room__{instance.room_id}"
        yield f"pk__{instance.pk}"

    @message_activity.groups_for_consumer  # type: ignore
    def message_activity(self, room=None, **kwargs: Any) -> Optional[Iterable[str]]:
        if room is not None:
            yield f"room__{room}"

    @message_activity.serializer  # type: ignore
    def message_activiy(self, instance: Message, action: Action, **kwargs: Any) -> dict:
        return dict(
            data=MessageSerializer(instance).data, action=action.value, pk=instance.pk
        )

    async def notify_users(self) -> None:
        room: Room = await self.get_room(self.room_subscribe)
        for group in self.groups:
            await self.channel_layer.group_send(
                group,
                {"type": "update_users", "usuarios": await self.current_users(room)},
            )

    async def update_users(self, event: dict) -> None:
        await self.send(text_data=json.dumps({"usuarios": event["usuarios"]}))

    @staticmethod
    @database_sync_to_async  # type: ignore
    def get_room(pk: int) -> Room:
        return Room.objects.get(pk=pk)

    @staticmethod
    @database_sync_to_async  # type: ignore
    def current_users(room: Room) -> Iterable[dict]:
        return [UserSerializer(user).data for user in room.current_users.all()]

    @database_sync_to_async  # type: ignore
    def remove_user_from_room(self, room: Room) -> None:
        user: User = self.scope["user"]
        user.current_rooms.remove(room)

    @database_sync_to_async  # type: ignore
    def add_user_to_room(self, pk: Any) -> None:
        user: User = self.scope["user"]
        if not user.current_rooms.filter(pk=self.room_subscribe).exists():
            user.current_rooms.add(Room.objects.get(pk=pk))
