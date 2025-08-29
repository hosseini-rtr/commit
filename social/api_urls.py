from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r"follows", api_views.FollowViewSet, basename="follow")

# Additional URL patterns for specific endpoints
urlpatterns = [
    # Include router URLs
    path("", include(router.urls)),
    # Additional specific endpoints
    path(
        "following-posts/",
        api_views.FollowingPostsView.as_view(),
        name="following-posts",
    ),
    path(
        "users/<str:username>/follow-stats/",
        api_views.UserFollowStatsView.as_view(),
        name="user-follow-stats",
    ),
]

# The API URLs are now determined automatically by the router
# This includes:
# - /api/social/follows/ (list, create)
# - /api/social/follows/{id}/ (retrieve, update, delete)
# - /api/social/follows/my_following/ (custom action)
# - /api/social/follows/my_followers/ (custom action)
# - /api/social/follows/{id}/unfollow/ (custom action)
# - /api/social/follows/follow_user/ (custom action)
# - /api/social/following-posts/ (posts from followed users)
# - /api/social/users/{username}/follow-stats/ (user follow statistics)
