from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Like
from posts.models import Post


# Create your views here.


@login_required
def like(request, id):
    try:
        post = Post.objects.get(pk=id)
        user = request.user

        try:
            is_liked = Like.objects.get(post=post, user=user)
            is_liked.delete()
            action = "Disliked"
        except Like.DoesNotExist:
            like_method = Like(post=post, user=user)
            like_method.save()
            action = "Liked"

        return JsonResponse({"success": f"Post {action}", "action": action})

    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
