from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source="user.id")
    username = serializers.ReadOnlyField(source="user.username")
    email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = Profile
        fields = ["user_id", "username", "email", "main_goal", "routine_time", "routine_days", "created_at", "updated_at"]
        read_only_fields = ["user_id", "username", "email", "created_at", "updated_at"]
