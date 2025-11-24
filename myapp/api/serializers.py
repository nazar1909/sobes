from rest_framework import serializers
from myapp.models import AD,ChatRoom,ChatMessage

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = AD
        fields = '__all__'








from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'content', 'created_at']


class ChatRoomSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'participants', 'messages', 'updated_at']