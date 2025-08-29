from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Follow
from .serializers import FollowSerializer, FollowCreateSerializer
from users.models import User
from posts.models import Post
from posts.serializers import PostSerializer


class FollowViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Follow model
    """

    queryset = Follow.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return FollowCreateSerializer
        return FollowSerializer

    def get_queryset(self):
        queryset = Follow.objects.all()

        # Filter by current user if provided
        current_user = self.request.query_params.get("current_user", None)
        if current_user:
            queryset = queryset.filter(current_user__username=current_user)

        # Filter by second user if provided
        second_user = self.request.query_params.get("second_user", None)
        if second_user:
            queryset = queryset.filter(second_user__username=second_user)

        return queryset

    @action(detail=False, methods=["get"])
    def my_following(self, request):
        """Get users that the current user follows"""
        following = Follow.objects.filter(current_user=request.user)
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_followers(self, request):
        """Get users who follow the current user"""
        followers = Follow.objects.filter(second_user=request.user)
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def unfollow(self, request, pk=None):
        """Unfollow a user"""
        follow = self.get_object()

        # Check if the current user is the one who created this follow relationship
        if follow.current_user != request.user:
            return Response(
                {"error": "You can only unfollow users you are following."},
                status=status.HTTP_403_FORBIDDEN,
            )

        follow.delete()
        return Response({"status": "unfollowed"})

    @action(detail=False, methods=["post"])
    def follow_user(self, request):
        """Follow a user by username"""
        username = request.data.get("username")
        if not username:
            return Response(
                {"error": "Username is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_to_follow = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if user_to_follow == request.user:
            return Response(
                {"error": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if already following
        if Follow.objects.filter(
            current_user=request.user, second_user=user_to_follow
        ).exists():
            return Response(
                {"error": "You are already following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow = Follow.objects.create(
            current_user=request.user, second_user=user_to_follow
        )
        serializer = self.get_serializer(follow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FollowingPostsView(generics.ListAPIView):
    """
    Get posts from users that the current user follows
    """

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Get users that the current user follows
        following_users = Follow.objects.filter(
            current_user=self.request.user
        ).values_list("second_user", flat=True)

        # Get posts from those users
        return Post.objects.filter(author__in=following_users).order_by("-date")


class UserFollowStatsView(generics.RetrieveAPIView):
    """
    Get follow statistics for a user
    """

    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        username = self.kwargs["username"]
        user = get_object_or_404(User, username=username)

        # Return follow statistics
        following_count = Follow.objects.filter(current_user=user).count()
        followers_count = Follow.objects.filter(second_user=user).count()

        return {
            "user": user,
            "following_count": following_count,
            "followers_count": followers_count,
        }

    def retrieve(self, request, *args, **kwargs):
        stats = self.get_object()
        return Response(
            {
                "user": {"id": stats["user"].id, "username": stats["user"].username},
                "following_count": stats["following_count"],
                "followers_count": stats["followers_count"],
            }
        )
