from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import Post
from .serializers import (
    PostSerializer,
    PostCreateSerializer,
    UserSerializer,
    CommentSerializer,
    LikeSerializer,
    DislikeSerializer,
)
from users.models import User
from interactions.models import Comment, Like, Dislike


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Post model with full CRUD operations
    """

    queryset = Post.objects.all().order_by("-date")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "create":
            return PostCreateSerializer
        return PostSerializer

    def get_queryset(self):
        queryset = Post.objects.all().order_by("-date")

        # Filter by author if provided
        author = self.request.query_params.get("author", None)
        if author:
            queryset = queryset.filter(author__username=author)

        # Filter by content search
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(content__icontains=search)

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # Only allow the author to update their own posts
        if serializer.instance.author != self.request.user:
            raise PermissionDenied("You can only edit your own posts.")
        serializer.save()

    def perform_destroy(self, instance):
        # Only allow the author to delete their own posts
        if instance.author != self.request.user:
            raise PermissionDenied("You can only delete your own posts.")
        instance.delete()

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def like(self, request, pk=None):
        """Like or unlike a post"""
        post = self.get_object()
        user = request.user

        try:
            like = Like.objects.get(post=post, user=user)
            like.delete()
            return Response({"status": "unliked"})
        except Like.DoesNotExist:
            Like.objects.create(post=post, user=user)
            return Response({"status": "liked"})

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def dislike(self, request, pk=None):
        """Dislike or undislike a post"""
        post = self.get_object()
        user = request.user

        try:
            dislike = Dislike.objects.get(post=post, user=user)
            dislike.delete()
            return Response({"status": "undisliked"})
        except Dislike.DoesNotExist:
            Dislike.objects.create(post=post, user=user)
            return Response({"status": "disliked"})

    @action(detail=True, methods=["get"])
    def comments(self, request, pk=None):
        """Get comments for a specific post"""
        post = self.get_object()
        comments = post.comments.all().order_by("-date")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def add_comment(self, request, pk=None):
        """Add a comment to a post"""
        post = self.get_object()
        data = request.data.copy()
        data["user_id"] = request.user.id
        data["post"] = post.id
        serializer = CommentSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for User model (read-only)
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = User.objects.all()

        # Filter by username if provided
        username = self.request.query_params.get("username", None)
        if username:
            queryset = queryset.filter(username__icontains=username)

        return queryset

    @action(detail=True, methods=["get"])
    def posts(self, request, pk=None):
        """Get posts by a specific user"""
        user = self.get_object()
        posts = user.author.all().order_by("-date")
        serializer = PostSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def followers(self, request, pk=None):
        """Get followers of a user"""
        user = self.get_object()
        followers = user.followers.all()
        serializer = UserSerializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def following(self, request, pk=None):
        """Get users that this user follows"""
        user = self.get_object()
        following = user.following.all()
        serializer = UserSerializer(following, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Comment model
    """

    queryset = Comment.objects.all().order_by("-date")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LikeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Like model
    """

    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DislikeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Dislike model
    """

    queryset = Dislike.objects.all()
    serializer_class = DislikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Additional API endpoints for specific functionality
class PostListCreateView(generics.ListCreateAPIView):
    """
    List all posts or create a new post
    """

    queryset = Post.objects.all().order_by("-date")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostCreateSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a post
    """

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        # Only allow the author to update their own posts
        if serializer.instance.author != self.request.user:
            raise PermissionDenied("You can only edit your own posts.")
        serializer.save()

    def perform_destroy(self, instance):
        # Only allow the author to delete their own posts
        if instance.author != self.request.user:
            raise PermissionDenied("You can only delete your own posts.")
        instance.delete()


class UserPostsView(generics.ListAPIView):
    """
    Get all posts by a specific user
    """

    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        username = self.kwargs["username"]
        return Post.objects.filter(author__username=username).order_by("-date")
