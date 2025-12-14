from rest_framework import serializers
from logs.models import ActionLog

class ActionLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Return username string

    class Meta:
        model = ActionLog
        fields = ['id', 'user', 'action', 'details', 'timestamp']
