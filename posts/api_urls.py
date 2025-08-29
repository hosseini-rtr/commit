from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r"posts", api_views.PostViewSet, basename="post")
router.register(r"users", api_views.UserViewSet, basename="user")
router.register(r"comments", api_views.CommentViewSet, basename="comment")
router.register(r"likes", api_views.LikeViewSet, basename="like")
router.register(r"dislikes", api_views.DislikeViewSet, basename="dislike")

# Additional URL patterns for specific endpoints
urlpatterns = [
    # Include router URLs
    path("", include(router.urls)),
    # Additional specific endpoints
    path("posts/", api_views.PostListCreateView.as_view(), name="post-list-create"),
    path("posts/<int:pk>/", api_views.PostDetailView.as_view(), name="post-detail"),
    path(
        "users/<str:username>/posts/",
        api_views.UserPostsView.as_view(),
        name="user-posts",
    ),
]

# The API URLs are now determined automatically by the router
# This includes:
# - /api/posts/ (list, create)
# - /api/posts/{id}/ (retrieve, update, delete)
# - /api/posts/{id}/like/ (custom action)
# - /api/posts/{id}/dislike/ (custom action)
# - /api/posts/{id}/comments/ (custom action)
# - /api/posts/{id}/add_comment/ (custom action)
# - /api/users/ (list)
# - /api/users/{id}/ (retrieve)
# - /api/users/{id}/posts/ (custom action)
# - /api/users/{id}/followers/ (custom action)
# - /api/users/{id}/following/ (custom action)
# - /api/comments/ (list, create)
# - /api/comments/{id}/ (retrieve, update, delete)
# - /api/likes/ (list, create)
# - /api/likes/{id}/ (retrieve, update, delete)
# - /api/dislikes/ (list, create)
# - /api/dislikes/{id}/ (retrieve, update, delete)
