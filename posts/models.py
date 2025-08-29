from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from users.models import User


def validate_image_size(value):
    limit = 3 * 1024 * 1024  # 3MB limit
    if value.size > limit:
        raise ValidationError(f"File size exceeds the limit of 3MB.")


class Post(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='author')
    content = models.CharField(max_length=140)
    date = models.DateTimeField(auto_now_add=True)
    image_cover = models.ImageField(upload_to='img/', null=True, validators=[
                                    FileExtensionValidator(['jpg', 'jpeg', 'png']), validate_image_size])
    likes = models.ManyToManyField(
        User, through='interactions.Like', related_name='liked_posts')
    dislikes = models.ManyToManyField(
        User, through='interactions.Dislike', related_name='disliked_posts')

    def __str__(self) -> str:
        return f"Post {self.id} made by {self.author} on {self.date.strftime('%d %b %Y %H:%M:%S')}"
