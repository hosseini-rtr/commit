from django.db import models
from users.models import User
from posts.models import Post


class Like(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='likes_given')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes_received")


class Dislike(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='dislikes_given')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="dislikes_received")


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Comment {self.id} made by {self.user} on {self.post.id} at {self.date.strftime('%d %b %Y %H:%M:%S')}"
