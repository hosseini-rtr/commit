from rest_framework import serializers
from .models import Follow
from users.models import User


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal User serializer for nested relationships"""

    class Meta:
        model = User
        fields = ["id", "username"]


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for Follow model"""

    current_user = UserMinimalSerializer(read_only=True)
    second_user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ["id", "current_user", "second_user", "each_other"]
        read_only_fields = ["id", "each_other"]

    def create(self, validated_data):
        validated_data["current_user"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        # Prevent self-following
        if data.get("second_user") == self.context["request"].user:
            raise serializers.ValidationError("You cannot follow yourself.")

        # Check if already following
        if Follow.objects.filter(
            current_user=self.context["request"].user,
            second_user=data.get("second_user"),
        ).exists():
            raise serializers.ValidationError("You are already following this user.")

        return data


class FollowCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating follows (simplified)"""

    second_user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Follow
        fields = ["second_user_id"]

    def create(self, validated_data):
        from users.models import User

        second_user_id = validated_data.pop("second_user_id")
        second_user = User.objects.get(id=second_user_id)

        validated_data["current_user"] = self.context["request"].user
        validated_data["second_user"] = second_user
        return super().create(validated_data)

    def validate_second_user_id(self, value):
        from users.models import User

        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

        if value == self.context["request"].user.id:
            raise serializers.ValidationError("You cannot follow yourself.")

        return value
