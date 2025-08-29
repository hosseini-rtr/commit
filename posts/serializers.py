from rest_framework import serializers
from users.models import User
from posts.models import Post
from interactions.models import Comment, Like, Dislike


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    posts_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "last_login",
            "posts_count",
            "followers_count",
            "following_count",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]

    def get_posts_count(self, obj):
        return obj.author.count()

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal User serializer for nested relationships"""

    class Meta:
        model = User
        fields = ["id", "username"]


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""

    user = UserMinimalSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "user_id", "post", "content", "date"]
        read_only_fields = ["id", "date"]

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        validated_data["user_id"] = user_id
        return super().create(validated_data)


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model"""

    author = UserMinimalSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    is_disliked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "date",
            "image_cover",
            "likes_count",
            "dislikes_count",
            "comments_count",
            "is_liked_by_user",
            "is_disliked_by_user",
            "comments",
        ]
        read_only_fields = [
            "id",
            "date",
            "likes_count",
            "dislikes_count",
            "comments_count",
            "is_liked_by_user",
            "is_disliked_by_user",
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_dislikes_count(self, obj):
        return obj.dislikes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_is_liked_by_user(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes_received.filter(user=request.user).exists()
        return False

    def get_is_disliked_by_user(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.dislikes_received.filter(user=request.user).exists()
        return False

    def create(self, validated_data):
        # Set the author to the current user
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts (without nested data)"""

    class Meta:
        model = Post
        fields = ["content", "image_cover"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class PostMinimalSerializer(serializers.ModelSerializer):
    """Minimal Post serializer to avoid circular imports"""

    author = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ["id", "author", "content", "date"]


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for Like model"""

    user = UserMinimalSerializer(read_only=True)
    post = PostMinimalSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ["id", "user", "post", "post_id"]
        read_only_fields = ["id", "user", "post"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class DislikeSerializer(serializers.ModelSerializer):
    """Serializer for Dislike model"""

    user = UserMinimalSerializer(read_only=True)
    post = PostMinimalSerializer(read_only=True)

    class Meta:
        model = Dislike
        fields = ["id", "user", "post", "post_id"]
        read_only_fields = ["id", "user", "post"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
