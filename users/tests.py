from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from posts.models import Post

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model"""

    def test_user_creation(self):
        """Test creating a user"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))

    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.assertEqual(str(user), "testuser")


class UserAPITest(APITestCase):
    """Test User API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_list_users_authenticated(self):
        """Test listing users when authenticated"""
        self.client.force_authenticate(user=self.user)
        url = "/api/users/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["username"], "testuser")

    def test_list_users_unauthenticated(self):
        """Test listing users when not authenticated"""
        url = "/api/users/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_user(self):
        """Test retrieving a specific user"""
        url = f"/api/users/{self.user.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")

    def test_filter_users_by_username(self):
        """Test filtering users by username"""
        User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )

        url = "/api/users/"
        response = self.client.get(url, {"username": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["username"], "testuser")


class UserRegistrationAPITest(APITestCase):
    """Test User registration API"""

    def setUp(self):
        self.client = APIClient()

    def test_user_registration_success(self):
        """Test successful user registration"""
        url = reverse("user-register")
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data["user"]["username"], "newuser")

    def test_user_registration_password_mismatch(self):
        """Test user registration with password mismatch"""
        url = "/api/users/auth/register/"
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123",
            "password_confirm": "differentpass",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_user_registration_duplicate_username(self):
        """Test user registration with duplicate username"""
        User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="testpass123",
        )

        url = "/api/users/auth/register/"
        data = {
            "username": "existinguser",
            "email": "new@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)


class UserLoginAPITest(APITestCase):
    """Test User login API"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_user_login_success(self):
        """Test successful user login"""
        url = "/api/users/auth/login/"
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["username"], "testuser")

    def test_user_login_invalid_credentials(self):
        """Test user login with invalid credentials"""
        url = "/api/users/auth/login/"
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_nonexistent_user(self):
        """Test user login with nonexistent user"""
        url = "/api/users/auth/login/"
        data = {"username": "nonexistent", "password": "testpass123"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLogoutAPITest(APITestCase):
    """Test User logout API"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_user_logout_authenticated(self):
        """Test user logout when authenticated"""
        self.client.force_authenticate(user=self.user)
        url = "/api/users/auth/logout/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Logout successful.")

    def test_user_logout_unauthenticated(self):
        """Test user logout when not authenticated"""
        url = "/api/users/auth/logout/"
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserProfileAPITest(APITestCase):
    """Test User profile API"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_get_current_user_profile(self):
        """Test getting current user's profile"""
        self.client.force_authenticate(user=self.user)
        url = "/api/users/me/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["first_name"], "Test")
        self.assertEqual(response.data["last_name"], "User")

    def test_update_current_user_profile(self):
        """Test updating current user's profile"""
        self.client.force_authenticate(user=self.user)
        url = "/api/users/update_profile/"
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com",
        }
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Updated")
        self.assertEqual(response.data["last_name"], "Name")
        self.assertEqual(response.data["email"], "updated@example.com")

    def test_change_password_success(self):
        """Test successful password change"""
        self.client.force_authenticate(user=self.user)
        url = "/api/users/change_password/"
        data = {
            "old_password": "testpass123",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Password changed successfully.")

        # Verify password was actually changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass123"))

    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password"""
        self.client.force_authenticate(user=self.user)
        url = "/api/users/change_password/"
        data = {
            "old_password": "wrongpassword",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_mismatch(self):
        """Test password change with password mismatch"""
        self.client.force_authenticate(user=self.user)
        url = "/api/users/change_password/"
        data = {
            "old_password": "testpass123",
            "new_password": "newpass123",
            "new_password_confirm": "differentpass",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserPostsAPITest(APITestCase):
    """Test User posts API"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.post = Post.objects.create(author=self.user, content="Test post content")

    def test_get_user_posts(self):
        """Test getting posts by a specific user"""
        url = f"/api/users/{self.user.username}/posts/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["content"], "Test post content")

    def test_get_user_posts_nonexistent_user(self):
        """Test getting posts for nonexistent user"""
        url = "/api/users/nonexistent/posts/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)


class UserProfileViewAPITest(APITestCase):
    """Test User profile view API"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )

    def test_get_user_profile(self):
        """Test getting user profile by username"""
        url = f"/api/users/{self.user.username}/profile/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["first_name"], "Test")
        self.assertEqual(response.data["last_name"], "User")

    def test_get_user_profile_nonexistent(self):
        """Test getting profile for nonexistent user"""
        url = "/api/users/nonexistent/profile/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
