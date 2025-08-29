from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Count
from .models import Follow
from users.models import User
from posts.models import Post


@login_required
def following_page(request):
    user = request.user
    following = Follow.objects.filter(current_user=user).values_list(
        "second_user", flat=True
    )
    posts_of_the_page = (
        Post.objects.filter(author__in=following)
        .order_by("-date")
        .annotate(num_likes=Count("likes"), num_dislikes=Count("dislikes"))
    )
    return render(
        request, "social/following.html", {"posts_of_the_page": posts_of_the_page}
    )


@login_required
def follow(request):
    if request.method == "POST":
        id = User.objects.get(username=request.POST["username"]).id
        user = request.user
        second_user = User.objects.get(pk=id)
        follow_method = Follow(current_user=user, second_user=second_user)
        follow_method.save()
        return HttpResponseRedirect(
            reverse("users:profile", kwargs={"username": second_user.username})
        )


@login_required
def unfollow(request):
    if request.method == "POST":
        id = User.objects.get(username=request.POST["username"]).id
        user = request.user
        second_user = User.objects.get(pk=id)
        follow_method = Follow.objects.get(current_user=user, second_user=second_user)
        print("current_user=", user, "second_user=", second_user)
        print(follow_method)
        follow_method.delete()
        return HttpResponseRedirect(
            reverse("users:profile", kwargs={"username": second_user.username})
        )
