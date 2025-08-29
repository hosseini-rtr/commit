from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    path("following", views.follow, name="following"),
    path("unfollowing", views.unfollow, name="unfollowing"),
    path("following_page", views.following_page, name="following_page"),
]
