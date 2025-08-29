from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r"users", api_views.UserViewSet, basename="user")

# Additional URL patterns for specific endpoints
urlpatterns = [
    # Include router URLs
    path("", include(router.urls)),
    # Authentication endpoints
    path(
        "auth/register/", api_views.UserRegistrationView.as_view(), name="user-register"
    ),
    path("auth/login/", api_views.UserLoginView.as_view(), name="user-login"),
    path("auth/logout/", api_views.UserLogoutView.as_view(), name="user-logout"),
    # Additional specific endpoints
    path(
        "users/<str:username>/posts/",
        api_views.UserPostsView.as_view(),
        name="user-posts",
    ),
    path(
        "users/<str:username>/profile/",
        api_views.UserProfileView.as_view(),
        name="user-profile",
    ),
]

# The API URLs are now determined automatically by the router
# This includes:
# - /api/users/users/ (list, create)
# - /api/users/users/{id}/ (retrieve, update, delete)
# - /api/users/users/{id}/posts/ (custom action)
# - /api/users/users/{id}/followers/ (custom action)
# - /api/users/users/{id}/following/ (custom action)
# - /api/users/users/me/ (custom action)
# - /api/users/users/update_profile/ (custom action)
# - /api/users/users/change_password/ (custom action)
# - /api/users/auth/register/ (user registration)
# - /api/users/auth/login/ (user login)
# - /api/users/auth/logout/ (user logout)
# - /api/users/users/{username}/posts/ (user posts)
# - /api/users/users/{username}/profile/ (user profile)
