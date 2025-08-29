from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Follow
from posts.models import Post

User = get_user_model()


class FollowModelTest(TestCase):
    """Test Follow model"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )

    def test_follow_creation(self):
        """Test creating a follow relationship"""
        follow = Follow.objects.create(current_user=self.user1, second_user=self.user2)
        self.assertEqual(follow.current_user, self.user1)
        self.assertEqual(follow.second_user, self.user2)
        self.assertFalse(follow.each_other)

    def test_follow_each_other(self):
        """Test mutual follow relationship"""
        # User1 follows User2
        Follow.objects.create(current_user=self.user1, second_user=self.user2)
        # User2 follows User1
        Follow.objects.create(current_user=self.user2, second_user=self.user1)

        # Check that each_other is set to True
        follow1 = Follow.objects.get(current_user=self.user1, second_user=self.user2)
        follow2 = Follow.objects.get(current_user=self.user2, second_user=self.user1)

        self.assertTrue(follow1.each_other)
        self.assertTrue(follow2.each_other)


class FollowAPITest(APITestCase):
    """Test Follow API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )
        self.follow = Follow.objects.create(
            current_user=self.user1, second_user=self.user2
        )

    def test_list_follows_authenticated(self):
        """Test listing follows when authenticated"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("follow-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["current_user"]["username"], "user1"
        )
        self.assertEqual(
            response.data["results"][0]["second_user"]["username"], "user2"
        )

    def test_list_follows_unauthenticated(self):
        """Test listing follows when not authenticated"""
        url = reverse("follow-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_follow(self):
        """Test creating a follow relationship"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("follow-list")
        data = {"second_user_id": self.user2.id}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Follow.objects.count(), 2)  # Including the one from setUp

    def test_create_follow_self(self):
        """Test creating a follow relationship with self"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("follow-list")
        data = {"second_user_id": self.user1.id}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_follow_already_following(self):
        """Test creating a follow relationship when already following"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("follow-list")
        data = {"second_user_id": self.user2.id}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_follow_nonexistent_user(self):
        """Test creating a follow relationship with nonexistent user"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("follow-list")
        data = {"second_user_id": 999}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_follows_by_current_user(self):
        """Test filtering follows by current user"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("follow-list")
        response = self.client.get(url, {"current_user": "user1"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["current_user"]["username"], "user1"
        )

    def test_filter_follows_by_second_user(self):
        """Test filtering follows by second user"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("follow-list")
        response = self.client.get(url, {"second_user": "user2"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["second_user"]["username"], "user2"
        )


class FollowCustomActionsAPITest(APITestCase):
    """Test Follow custom actions"""

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )
        self.follow = Follow.objects.create(
            current_user=self.user1, second_user=self.user2
        )

    def test_my_following(self):
        """Test getting users that current user follows"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("follow-my_following")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["second_user"]["username"], "user2")

    def test_my_followers(self):
        """Test getting users who follow current user"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("follow-my_followers")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["current_user"]["username"], "user1")

    def test_unfollow(self):
        """Test unfollowing a user"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("follow-unfollow", args=[self.follow.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "unfollowed")
        self.assertEqual(Follow.objects.count(), 0)

    def test_unfollow_wrong_user(self):
        """Test unfollowing by wrong user"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("follow-unfollow", args=[self.follow.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Follow.objects.count(), 1)

    def test_follow_user_by_username(self):
        """Test following a user by username"""
        user3 = User.objects.create_user(
            username="user3", email="user3@example.com", password="testpass123"
        )

        self.client.force_authenticate(user=self.user1)
        url = reverse("follow-follow_user")
        data = {"username": "user3"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Follow.objects.count(), 2)

    def test_follow_user_nonexistent(self):
        """Test following a nonexistent user"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("follow-follow_user")
        data = {"username": "nonexistent"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_follow_user_self(self):
        """Test following self"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("follow-follow_user")
        data = {"username": "user1"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_follow_user_already_following(self):
        """Test following a user already being followed"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("follow-follow_user")
        data = {"username": "user2"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FollowingPostsAPITest(APITestCase):
    """Test Following Posts API"""

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )
        self.follow = Follow.objects.create(
            current_user=self.user1, second_user=self.user2
        )
        self.post = Post.objects.create(
            author=self.user2, content="Post from followed user"
        )

    def test_following_posts_authenticated(self):
        """Test getting posts from followed users when authenticated"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("following-posts")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["content"], "Post from followed user"
        )

    def test_following_posts_unauthenticated(self):
        """Test getting posts from followed users when not authenticated"""
        url = reverse("following-posts")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_following_posts_no_follows(self):
        """Test getting posts when not following anyone"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("following-posts")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)


class UserFollowStatsAPITest(APITestCase):
    """Test User Follow Stats API"""

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )
        self.user3 = User.objects.create_user(
            username="user3", email="user3@example.com", password="testpass123"
        )

        # User1 follows User2
        Follow.objects.create(current_user=self.user1, second_user=self.user2)
        # User3 follows User1
        Follow.objects.create(current_user=self.user3, second_user=self.user1)

    def test_user_follow_stats(self):
        """Test getting user follow statistics"""
        url = reverse("user-follow-stats", args=[self.user1.username])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["username"], "user1")
        self.assertEqual(response.data["following_count"], 1)  # Following user2
        self.assertEqual(response.data["followers_count"], 1)  # Followed by user3

    def test_user_follow_stats_nonexistent_user(self):
        """Test getting follow stats for nonexistent user"""
        url = reverse("user-follow-stats", args=["nonexistent"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
