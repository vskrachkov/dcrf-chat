from rest_framework import serializers

from .models import Message, Room, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password"]


class MessageSerializer(serializers.ModelSerializer):
    created_at_formatted = serializers.SerializerMethodField()
    user = UserSerializer()

    class Meta:
        model = Message
        fields = "__all__"
        depth = 1

    @staticmethod
    def get_created_at_formatted(obj: Message) -> str:
        return obj.created_at.strftime("%d-%m-%Y %H:%M:%S")


class RoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ["pk", "name", "host", "messages", "current_users", "last_message"]
        depth = 1
        read_only_fields = ["messages", "last_message"]

    @staticmethod
    def get_last_message(obj: Room) -> dict:
        return MessageSerializer(obj.messages.order_by("created_at").last()).data


class JoinRoomActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["join_room"])
    request_id = serializers.IntegerField()
    pk = serializers.IntegerField()


class LeaveRoomActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["leave_room"])
    request_id = serializers.IntegerField()
    pk = serializers.IntegerField()


class SubscribeToMessageInRoomSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["subscribe_to_messages_in_room"])
    request_id = serializers.IntegerField()
    pk = serializers.IntegerField()


class CreateMessageActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["create_message"])
    request_id = serializers.IntegerField()
    message = serializers.CharField()
