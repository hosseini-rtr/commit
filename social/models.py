from django.db import models
from users.models import User


class Follow(models.Model):
    current_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')
    second_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers')
    each_other = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Check if the users follow each other
        if self.current_user.following.filter(id=self.second_user.id).exists() and \
                self.second_user.following.filter(id=self.current_user.id).exists():
            self.each_other = True
        else:
            self.each_other = False

        super().save(*args, **kwargs)
