import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Count
from django.core.paginator import Paginator
from .models import Post
from users.models import User
from interactions.models import Like


def index(request):
    posts_of_the_page = []
    user_liked_id = []
    if request.user.is_authenticated:
        posts = (
            Post.objects.all()
            .order_by("-date")
            .annotate(
                num_likes=Count("likes"),
                num_dislikes=Count("dislikes"),
            )
        )
        # Pagination
        paginator = Paginator(posts, 10)
        page_number = request.GET.get("page")
        posts_of_the_page = paginator.get_page(page_number)

        user_liked = Like.objects.filter(user=request.user).filter(
            post__in=posts_of_the_page
        )
        user_liked_id = [like.post.id for like in user_liked]
    return render(
        request,
        "posts/index.html",
        {"posts_of_the_page": posts_of_the_page, "user_liked_id": user_liked_id},
    )


@login_required
def add_post(request):
    print("request", request)
    if request.method == "POST":
        user = request.user
        content = request.POST["content"]
        if request.FILES:
            image = request.FILES["image"]
        else:
            image = None

        post = Post(author=user, content=content, image_cover=image)
        post.save()
        return HttpResponseRedirect(reverse("posts:index"))


@login_required
def edit_post(request, id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            edit_post_ = Post.objects.get(pk=id)

            # Check if the user is the author of the post
            if edit_post_.author != request.user:
                return JsonResponse(
                    {"error": "You can only edit your own posts"}, status=403
                )

            edit_post_.content = data["content"]
            edit_post_.save()
            return JsonResponse(
                {"message": "Successes received data ", "data": data["content"]}
            )
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
