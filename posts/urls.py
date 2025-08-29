from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
    path("", views.index, name="index"),
    path("post", views.add_post, name="post"),
    path("edit_post/<str:id>/", views.edit_post, name="edit_post"),
]
