# core/tests/test_auth.py

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestSignUp:
    """Test user registration endpoint"""
    
    def setup_method(self):
        self.client = APIClient()
        self.signup_url = '/api/auth/sign-up'
    
    def test_signup_success(self):
        """Test successful user registration"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.signup_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'token' in response.data
        assert 'user' in response.data
        assert response.data['user']['username'] == 'testuser'
        
        # Verify user was created in database
        assert User.objects.filter(username='testuser').exists()
    
    def test_signup_duplicate_username(self):
        """Test signup with existing username"""
        User.objects.create_user(username='existing', password='pass123')
        
        data = {
            'username': 'existing',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.signup_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data
    
    def test_signup_weak_password(self):
        """Test signup with weak password"""
        data = {
            'username': 'newuser',
            'password': '123'
        }
        response = self.client.post(self.signup_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
    
    def test_signup_missing_fields(self):
        """Test signup with missing required fields"""
        data = {'username': 'incomplete'}
        response = self.client.post(self.signup_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestSignIn:
    """Test user login endpoint"""
    
    def setup_method(self):
        self.client = APIClient()
        self.signin_url = '/api/auth/sign-in'
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            email='test@example.com'
        )
    
    def teardown_method(self):
        """Clear throttle cache between tests"""
        from django.core.cache import cache
        cache.clear()
    
    def test_signin_success(self):
        """Test successful login"""
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.signin_url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'token' in response.data
        assert 'user' in response.data
        assert response.data['user']['username'] == 'testuser'
    
    def test_signin_wrong_password(self):
        """Test login with incorrect password"""
        data = {
            'username': 'testuser',
            'password': 'WrongPassword'
        }
        response = self.client.post(self.signin_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Invalid credentials' in str(response.data)
    
    def test_signin_nonexistent_user(self):
        """Test login with non-existent user"""
        data = {
            'username': 'nonexistent',
            'password': 'SomePass123'
        }
        response = self.client.post(self.signin_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_signin_inactive_user(self):
        """Test login with inactive user"""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.signin_url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'disabled' in str(response.data).lower()
    
    def test_signin_missing_fields(self):
        """Test login with missing fields"""
        data = {'username': 'testuser'}
        response = self.client.post(self.signin_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST