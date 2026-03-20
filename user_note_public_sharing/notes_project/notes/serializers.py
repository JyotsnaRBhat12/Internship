from rest_framework import serializers
from .models import Note, SharedLink


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'


class SharedLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedLink
        fields = '__all__'


class ShareLinkCreateSerializer(serializers.Serializer):
    expiry_date = serializers.DateTimeField(required=False, allow_null=True)
