from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Count
from .models import User
from posts.models import Post
from social.models import Follow


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('posts:index'))

    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("posts:index"))
        else:
            return render(request, "users/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "users/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("posts:index"))


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('posts:index'))

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "users/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "users/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("posts:index"))
    else:
        return render(request, "users/register.html")


@login_required
def profile(request, username):
    user = User.objects.get(username=username)
    posts = Post.objects.filter(author=user).order_by('-date').annotate(
        num_likes=Count('likes'),
        num_dislikes=Count('dislikes')
    )
    following = Follow.objects.filter(current_user=user)
    followers = Follow.objects.filter(second_user=user)
    user_profile = user
    checkFollow = Follow.objects.filter(current_user=user, second_user=user)
    print(checkFollow)
    checkFollow = Follow.objects.filter(
        current_user=request.user, second_user=user)
    isFollowing = True if len(checkFollow) != 0 else False

    return render(request, "users/profile.html", {
        "posts_of_the_page": posts,
        'username': user.username,
        "following": following,
        "followers": followers,
        "isFollowing": isFollowing,
        "user_profile": user_profile
    })
