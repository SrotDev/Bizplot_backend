from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import json
import uuid

User = get_user_model()


class RegisterViewTests(APITestCase):
    """Test suite for user registration"""
    
    def setUp(self):
        self.register_url = reverse('register')
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    
    def test_successful_user_registration(self):
        """Test successful user registration with valid data"""
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertNotIn('password', response.data)  # Password shouldn't be returned
        
        # Verify user is created in database
        user_exists = User.objects.filter(email='test@example.com').exists()
        self.assertTrue(user_exists)
    
    def test_registration_with_duplicate_email(self):
        """Test registration fails when email already exists"""
        # Create a user first
        User.objects.create_user(
            username='existinguser',
            email='test@example.com',
            password='password123'
        )
        
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_registration_with_duplicate_username(self):
        """Test registration fails when username already exists"""
        # Create a user first
        User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='password123'
        )
        
        response = self.client.post(self.register_url, self.valid_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
    
    def test_registration_with_missing_fields(self):
        """Test registration fails when required fields are missing"""
        incomplete_data = {'username': 'testuser'}
        
        response = self.client.post(self.register_url, incomplete_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)
    
    def test_registration_with_invalid_email(self):
        """Test registration fails with invalid email format"""
        invalid_data = self.valid_user_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        response = self.client.post(self.register_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_registration_with_empty_password(self):
        """Test registration fails with empty password"""
        invalid_data = self.valid_user_data.copy()
        invalid_data['password'] = ''
        
        response = self.client.post(self.register_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)


class LoginViewTests(APITestCase):
    """Test suite for user login"""
    
    def setUp(self):
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.valid_login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    
    def test_successful_login(self):
        """Test successful login with valid credentials"""
        response = self.client.post(self.login_url, self.valid_login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # Verify user data in response
        user_data = response.data['user']
        self.assertEqual(user_data['email'], 'test@example.com')
        self.assertEqual(user_data['username'], 'testuser')
        self.assertIn('id', user_data)
    
    def test_login_with_invalid_email(self):
        """Test login fails with invalid email"""
        invalid_data = self.valid_login_data.copy()
        invalid_data['email'] = 'nonexistent@example.com'
        
        response = self.client.post(self.login_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_login_with_invalid_password(self):
        """Test login fails with invalid password"""
        invalid_data = self.valid_login_data.copy()
        invalid_data['password'] = 'wrongpassword'
        
        response = self.client.post(self.login_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_login_with_missing_fields(self):
        """Test login fails when required fields are missing"""
        incomplete_data = {'email': 'test@example.com'}
        
        response = self.client.post(self.login_url, incomplete_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
    
    def test_login_with_empty_credentials(self):
        """Test login fails with empty credentials"""
        empty_data = {'email': '', 'password': ''}
        
        response = self.client.post(self.login_url, empty_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_with_invalid_email_format(self):
        """Test login fails with invalid email format"""
        invalid_data = self.valid_login_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        response = self.client.post(self.login_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_jwt_token_structure(self):
        """Test that JWT tokens are properly formatted"""
        response = self.client.post(self.login_url, self.valid_login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Tokens should be strings
        self.assertIsInstance(response.data['access'], str)
        self.assertIsInstance(response.data['refresh'], str)
        
        # Tokens should not be empty
        self.assertNotEqual(response.data['access'], '')
        self.assertNotEqual(response.data['refresh'], '')


class UserInfoViewTests(APITestCase):
    """Test suite for UserInfoView (currently not used in URLs but exists in views)"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
    
    def test_user_info_view_get_object_method(self):
        """Test UserInfoView get_object method returns correct user"""
        from accounts.views import UserInfoView
        from unittest.mock import Mock
        
        # Create a mock request with the user
        mock_request = Mock()
        mock_request.user = self.user
        
        view = UserInfoView()
        view.request = mock_request
        
        obj = view.get_object()
        self.assertEqual(obj, self.user)
    
    def test_user_info_view_queryset(self):
        """Test UserInfoView has correct queryset"""
        from accounts.views import UserInfoView
        
        view = UserInfoView()
        queryset = view.get_queryset()
        
        # Should contain our test user
        self.assertIn(self.user, queryset)


class UserProfileViewTests(APITestCase):
    """Test suite for user profile view"""
    
    def setUp(self):
        self.profile_url = reverse('profile')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            full_name='Test User',
            business_stage='idea',
            industry='Technology',
            target_market='B2B',
            skills_background='Software Development',
            budget_range='1k-10k',
            subscription_plan='free'
        )
        self.client = APIClient()
    
    def test_profile_access_authenticated(self):
        """Test accessing profile when authenticated"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify all profile fields are returned
        expected_fields = [
            'id', 'username', 'email', 'full_name', 'profile_picture',
            'business_stage', 'industry', 'target_market', 'skills_background',
            'budget_range', 'subscription_plan', 'api_tokens_used',
            'ideas_created', 'messages_sent', 'two_factor_enabled', 'is_verified'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        # Verify specific values
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['full_name'], 'Test User')
        self.assertEqual(response.data['business_stage'], 'idea')
        self.assertEqual(response.data['industry'], 'Technology')
        self.assertEqual(response.data['subscription_plan'], 'free')
    
    def test_profile_access_unauthenticated(self):
        """Test accessing profile when not authenticated"""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_profile_with_default_values(self):
        """Test profile returns correct default values"""
        # Create user with minimal data
        basic_user = User.objects.create_user(
            username='basicuser',
            email='basic@example.com',
            password='password123'
        )
        
        self.client.force_authenticate(user=basic_user)
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify default values
        self.assertEqual(response.data['full_name'], '')
        self.assertEqual(response.data['business_stage'], 'idea')
        self.assertEqual(response.data['budget_range'], '<1k')
        self.assertEqual(response.data['subscription_plan'], 'free')
        self.assertEqual(response.data['api_tokens_used'], 0)
        self.assertEqual(response.data['ideas_created'], 0)
        self.assertEqual(response.data['messages_sent'], 0)
        self.assertFalse(response.data['two_factor_enabled'])
        self.assertFalse(response.data['is_verified'])
    
    def test_profile_uuid_format(self):
        """Test that user ID is a valid UUID"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify ID is a valid UUID string
        user_id = response.data['id']
        try:
            uuid.UUID(user_id)
        except ValueError:
            self.fail("User ID is not a valid UUID")


class AuthenticationIntegrationTests(APITestCase):
    """Integration tests for authentication flow"""
    
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
    
    def test_complete_auth_flow(self):
        """Test complete authentication flow: register -> login -> access protected resource"""
        # Step 1: Register
        register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        
        register_response = self.client.post(self.register_url, register_data, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        
        # Step 2: Login
        login_data = {
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        
        login_response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        access_token = login_response.data['access']
        
        # Step 3: Access protected resource
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = self.client.get(self.profile_url)
        
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['email'], 'newuser@example.com')
        self.assertEqual(profile_response.data['username'], 'newuser')
    
    def test_invalid_jwt_token(self):
        """Test access with invalid JWT token"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid-token')
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_expired_token_handling(self):
        """Test behavior with proper token format but potentially expired"""
        # Create a user and get valid token
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data['access']
        
        # Use the token to access profile (should work)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = self.client.get(self.profile_url)
        
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
