from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "content", "date", "image_cover")
    list_filter = ("date", "author")
    search_fields = ("content", "author__username")
    date_hierarchy = "date"
