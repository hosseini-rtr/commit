from django.contrib import admin
from .models import Like, Dislike, Comment


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "post_content_preview")
    list_filter = ("user", "post__date")
    search_fields = ("user__username", "post__content")

    def post_content_preview(self, obj):
        return (
            obj.post.content[:50] + "..."
            if len(obj.post.content) > 50
            else obj.post.content
        )

    post_content_preview.short_description = "Post Content"


@admin.register(Dislike)
class DislikeAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "post_content_preview")
    list_filter = ("user", "post__date")
    search_fields = ("user__username", "post__content")

    def post_content_preview(self, obj):
        return (
            obj.post.content[:50] + "..."
            if len(obj.post.content) > 50
            else obj.post.content
        )

    post_content_preview.short_description = "Post Content"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "content", "date")
    list_filter = ("date", "user", "post__date")
    search_fields = ("content", "user__username", "post__content")
    date_hierarchy = "date"
