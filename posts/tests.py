from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Post
from interactions.models import Comment, Like, Dislike

User = get_user_model()


class PostModelTest(TestCase):
    """Test Post model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_post_creation(self):
        """Test creating a post"""
        post = Post.objects.create(author=self.user, content="Test post content")
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.content, "Test post content")
        self.assertIsNotNone(post.date)

    def test_post_str_representation(self):
        """Test post string representation"""
        post = Post.objects.create(author=self.user, content="Test post content")
        self.assertIn("Post", str(post))
        self.assertIn(self.user.username, str(post))
        self.assertIn("made by", str(post))


class PostAPITest(APITestCase):
    """Test Post API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.post = Post.objects.create(author=self.user, content="Test post content")

    def test_list_posts_authenticated(self):
        """Test listing posts when authenticated"""
        self.client.force_authenticate(user=self.user)
        url = reverse("post-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["content"], "Test post content")

    def test_list_posts_unauthenticated(self):
        """Test listing posts when not authenticated"""
        url = reverse("post-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_post_authenticated(self):
        """Test creating a post when authenticated"""
        self.client.force_authenticate(user=self.user)
        url = reverse("post-list")
        data = {"content": "New test post"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(response.data["content"], "New test post")

    def test_create_post_unauthenticated(self):
        """Test creating a post when not authenticated"""
        url = reverse("post-list")
        data = {"content": "New test post"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_post(self):
        """Test retrieving a specific post"""
        url = reverse("post-detail", args=[self.post.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "Test post content")

    def test_update_post_author(self):
        """Test updating a post by its author"""
        self.client.force_authenticate(user=self.user)
        url = reverse("post-detail", args=[self.post.id])
        data = {"content": "Updated content"}
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "Updated content")

    def test_update_post_not_author(self):
        """Test updating a post by non-author"""
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=other_user)
        url = reverse("post-detail", args=[self.post.id])
        data = {"content": "Updated content"}
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_author(self):
        """Test deleting a post by its author"""
        self.client.force_authenticate(user=self.user)
        url = reverse("post-detail", args=[self.post.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)

    def test_delete_post_not_author(self):
        """Test deleting a post by non-author"""
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=other_user)
        url = reverse("post-detail", args=[self.post.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 1)

    def test_filter_posts_by_author(self):
        """Test filtering posts by author"""
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        Post.objects.create(author=other_user, content="Other user post")

        url = reverse("post-list")
        response = self.client.get(url, {"author": "testuser"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["author"]["username"], "testuser")

    def test_search_posts(self):
        """Test searching posts by content"""
        Post.objects.create(author=self.user, content="Another test post")

        url = reverse("post-list")
        response = self.client.get(url, {"search": "Another"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertIn("Another", response.data["results"][0]["content"])


class PostLikeAPITest(APITestCase):
    """Test Post like/unlike functionality"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.post = Post.objects.create(author=self.user, content="Test post content")

    def test_like_post(self):
        """Test liking a post"""
        self.client.force_authenticate(user=self.user)
        url = reverse("post-like", args=[self.post.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "liked")
        self.assertTrue(Like.objects.filter(post=self.post, user=self.user).exists())

    def test_unlike_post(self):
        """Test unliking a post"""
        Like.objects.create(post=self.post, user=self.user)
        self.client.force_authenticate(user=self.user)
        url = reverse("post-like", args=[self.post.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "unliked")
        self.assertFalse(Like.objects.filter(post=self.post, user=self.user).exists())

    def test_like_post_unauthenticated(self):
        """Test liking a post when not authenticated"""
        url = reverse("post-like", args=[self.post.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PostDislikeAPITest(APITestCase):
    """Test Post dislike/undislike functionality"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.post = Post.objects.create(author=self.user, content="Test post content")

    def test_dislike_post(self):
        """Test disliking a post"""
        self.client.force_authenticate(user=self.user)
        url = reverse("post-dislike", args=[self.post.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "disliked")
        self.assertTrue(Dislike.objects.filter(post=self.post, user=self.user).exists())

    def test_undislike_post(self):
        """Test undisliking a post"""
        Dislike.objects.create(post=self.post, user=self.user)
        self.client.force_authenticate(user=self.user)
        url = reverse("post-dislike", args=[self.post.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "undisliked")
        self.assertFalse(
            Dislike.objects.filter(post=self.post, user=self.user).exists()
        )


class PostCommentAPITest(APITestCase):
    """Test Post comment functionality"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.post = Post.objects.create(author=self.user, content="Test post content")

    def test_get_post_comments(self):
        """Test getting comments for a post"""
        Comment.objects.create(user=self.user, post=self.post, content="Test comment")

        url = reverse("post-comments", args=[self.post.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["content"], "Test comment")

    def test_add_comment_to_post(self):
        """Test adding a comment to a post"""
        self.client.force_authenticate(user=self.user)
        url = f"/api/posts/{self.post.id}/add_comment/"
        data = {"content": "New comment"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(response.data["content"], "New comment")

    def test_add_comment_unauthenticated(self):
        """Test adding a comment when not authenticated"""
        url = f"/api/posts/{self.post.id}/add_comment/"
        data = {"content": "New comment"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
