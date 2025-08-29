from django.contrib import admin
from .models import Follow


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("current_user", "second_user", "each_other")
    list_filter = ("each_other", "current_user", "second_user")
    search_fields = ("current_user__username", "second_user__username")
