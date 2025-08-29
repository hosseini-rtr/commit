from django.urls import path
from . import views

app_name = "interactions"

urlpatterns = [
    path("like/<int:id>/", views.like, name="like"),
]
