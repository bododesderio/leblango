# core/tests/test_permissions.py

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, AnonymousUser
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView
from rest_framework.response import Response

from core.permissions import (
    IsAuthenticatedOrReadOnly,
    IsManagerOrAdmin,
    IsModeratorOrAdmin,
    IsStaffUser,
    IsStaffOrReadOnly,
    IsAdminOrReadOnly,
)

User = get_user_model()


# Test view for permission testing
class PermissionTestView(APIView):
    def get(self, request):
        return Response({'method': 'GET'})
    
    def post(self, request):
        return Response({'method': 'POST'})


@pytest.mark.django_db
class TestIsAuthenticatedOrReadOnly:
    """Test IsAuthenticatedOrReadOnly permission"""
    
    def setup_method(self):
        self.factory = APIRequestFactory()
        self.permission = IsAuthenticatedOrReadOnly()
        self.user = User.objects.create_user(username='testuser', password='pass123')
    
    def test_allows_read_for_anonymous(self):
        """Test GET requests allowed for anonymous users"""
        request = self.factory.get('/test/')
        request.user = AnonymousUser()
        
        assert self.permission.has_permission(request, PermissionTestView())
    
    def test_allows_read_for_authenticated(self):
        """Test GET requests allowed for authenticated users"""
        request = self.factory.get('/test/')
        force_authenticate(request, user=self.user)
        
        assert self.permission.has_permission(request, PermissionTestView())
    
    def test_denies_write_for_anonymous(self):
        """Test POST requests denied for anonymous users"""
        request = self.factory.post('/test/')
        request.user = AnonymousUser()
        
        assert not self.permission.has_permission(request, PermissionTestView())
    
    def test_allows_write_for_authenticated(self):
        """Test POST requests allowed for authenticated users"""
        request = self.factory.post('/test/')
        request.user = self.user
        force_authenticate(request, user=self.user)
        
        assert self.permission.has_permission(request, PermissionTestView())
    
    def test_allows_put_for_authenticated(self):
        """Test PUT requests allowed for authenticated users"""
        request = self.factory.put('/test/')
        request.user = self.user
        force_authenticate(request, user=self.user)
        
        assert self.permission.has_permission(request, PermissionTestView())
    
    def test_denies_delete_for_anonymous(self):
        """Test DELETE requests denied for anonymous users"""
        request = self.factory.delete('/test/')
        request.user = AnonymousUser()
        
        assert not self.permission.has_permission(request, PermissionTestView())


@pytest.mark.django_db
class TestIsManagerOrAdmin:
    """Test IsManagerOrAdmin permission"""
    
    def setup_method(self):
        self.factory = APIRequestFactory()
        self.permission = IsManagerOrAdmin()
        
        # Create different user types
        self.regular_user = User.objects.create_user(username='regular', password='pass123')
        
        self.staff_user = User.objects.create_user(username='staff', password='pass123')
        self.staff_user.is_staff = True
        self.staff_user.save()
        
        self.superuser = User.objects.create_user(username='super', password='pass123')
        self.superuser.is_superuser = True
        self.superuser.save()
        
        # Create manager group and user (use get_or_create to avoid duplicates)
        self.manager_group, _ = Group.objects.get_or_create(name='manager')
        self.manager_user = User.objects.create_user(username='manager', password='pass123')
        self.manager_user.groups.add(self.manager_group)
    
    def test_denies_anonymous(self):
        """Test permission denied for anonymous users"""
        request = self.factory.get('/test/')
        request.user = AnonymousUser()
        
        assert not self.permission.has_permission(request, PermissionTestView())
    
    def test_denies_regular_user(self):
        """Test permission denied for regular authenticated users"""
        request = self.factory.get('/test/')
        request.user = self.regular_user
        force_authenticate(request, user=self.regular_user)
        
        assert not self.permission.has_permission(request, PermissionTestView())
    
    def test_allows_staff_user(self):
        """Test permission allowed for staff users"""
        request = self.factory.get('/test/')
        request.user = self.staff_user
        force_authenticate(request, user=self.staff_user)
        
        assert self.permission.has_permission(request, PermissionTestView())
    
    def test_allows_superuser(self):
        """Test permission allowed for superusers"""
        request = self.factory.get('/test/')
        request.user = self.superuser
        force_authenticate(request, user=self.superuser)
        
        assert self.permission.has_permission(request, PermissionTestView())
    
    def test_allows_manager_group(self):
        """Test permission allowed for users in manager group"""
        request = self.factory.get('/test/')
        request.user = self.manager_user
        force_authenticate(request, user=self.manager_user)
        
        assert self.permission.has_permission(request, PermissionTestView())


@pytest.mark.django_db
class TestIsModeratorOrAdmin:
    """Test IsModeratorOrAdmin permission"""
    
    def setup_method(self):
        self.factory = APIRequestFactory()
        self.permission = IsModeratorOrAdmin()
        
        # Create user types
        self.regular_user = User.objects.create_user(username='regular', password='pass123')
        
        self.staff_user = User.objects.create_user(username='staff', password='pass123')
        self.staff_user.is_staff = True
        self.staff_user.save()
        
        # Create manager and editor groups (use get_or_create to avoid duplicates)
        self.manager_group, _ = Group.objects.get_or_create(name='manager')
        self.editor_group, _ = Group.objects.get_or_create(name='editor')
        
        self.manager_user = User.objects.create_user(username='manager', password='pass123')
        self.manager_user.groups.add(self.manager_group)
        
        self.editor_user = User.objects.create_user(username='editor', password='pass123')
        self.editor_user.groups.add(self.editor_group)
    
    def test_denies_anonymous(self):
        """Test permission denied for anonymous users"""
        request = self.factory.get('/test/')
        request.user = AnonymousUser()
        
        assert not self.permission.has_permission(request, PermissionTestView())
    
    def test_denies_regular_user(self):
        """Test permission denied for regular users"""
        request = self.factory.get('/test/')
        request.user = self.regular_user
        force_authenticate(request, user=self.regular_user)
        
        assert not self.permission.has_permission(request, PermissionTestView())
    
    def test_allows_staff_user(self):
        """Test permission allowed for staff users"""
        request = self.factory.get('/test/')
        request.user = self.staff_user
        force_authenticate(request, user=self.staff_user)
        
        assert self.permission.has_permission(request, PermissionTestView())
    
    def test_allows_manager_group(self):
        """Test permission allowed for manager group"""
        request = self.factory.get('/test/')
        request.user = self.manager_user
        force_authenticate(request, user=self.manager_user)
        
        assert self.permission.has_permission(request, PermissionTestView())
    
    def test_allows_editor_group(self):
        """Test permission allowed for editor group"""
        request = self.factory.get('/test/')
        request.user = self.editor_user
        force_authenticate(request, user=self.editor_user)
        
        assert self.permission.has_permission(request, PermissionTestView())


@pytest.mark.django_db
class TestIsStaffUser:
    """Test IsStaffUser permission"""
    
    def setup_method(self):
        self.factory = APIRequestFactory()
        self.permission = IsStaffUser()
        
        self.regular_user = User.objects.create_user(username='regular', password='pass123')
        
        self.staff_user = User.objects.create_user(username='staff', password='pass123')
        self.staff_user.is_staff = True
        self.staff_user.save()
    
    def test_denies_anonymous(self):
        """Test permission denied for anonymous users"""
        request = self.factory.get('/test/')
        request.user = AnonymousUser()
        
        assert not self.permission.has_permission(request, PermissionTestView())
    
    def test_denies_regular_user(self):
        """Test permission denied for regular users"""
        request = self.factory.get('/test/')
        request.user = self.regular_user
        force_authenticate(request, user=self.regular_user)
        
        assert not self.permission.has_permission(request, PermissionTestView())
    
    def test_allows_staff_user(self):
        """Test permission allowed for staff users"""
        request = self.factory.get('/test/')
        request.user = self.staff_user
        force_authenticate(request, user=self.staff_user)
        
        assert self.permission.has_permission(request, PermissionTestView())
    
    def test_allows_all_methods_for_staff(self):
        """Test staff users can use all HTTP methods"""
        for method in ['get', 'post', 'put', 'patch', 'delete']:
            request = getattr(self.factory, method)('/test/')
            request.user = self.staff_user
            force_authenticate(request, user=self.staff_user)
            
            assert self.permission.has_permission(request, PermissionTestView())


@pytest.mark.django_db
class TestIsStaffOrReadOnly:
    """Test IsStaffOrReadOnly permission"""
    
    def setup_method(self):
        self.factory = APIRequestFactory()
        self.permission = IsStaffOrReadOnly()
        
        self.regular_user = User.objects.create_user(username='regular', password='pass123')
        
        self.staff_user = User.objects.create_user(username='staff', password='pass123')
        self.staff_user.is_staff = True
        self.staff_user.save()
    
    def test_allows_read_for_anonymous(self):
        """Test GET requests allowed for anonymous users"""
        request = self.factory.get('/test/')
        request.user = AnonymousUser()
        
        assert self.permission.has_permission(request, PermissionTestView())
    
    def test_allows_read_for_regular_user(self):
        """Test GET requests allowed for regular users"""
        request = self.factory.get('/test/')
        force_authenticate(request, user=self.regular_user)
        
        assert self.permission.has_permission(request, PermissionTestView())
    
    def test_denies_write_for_regular_user(self):
        """Test POST requests denied for regular users"""
        request = self.factory.post('/test/')
        request.user = self.regular_user
        force_authenticate(request, user=self.regular_user)
        
        assert not self.permission.has_permission(request, PermissionTestView())
    
    def test_allows_write_for_staff(self):
        """Test POST requests allowed for staff users"""
        request = self.factory.post('/test/')
        request.user = self.staff_user
        force_authenticate(request, user=self.staff_user)
        
        assert self.permission.has_permission(request, PermissionTestView())


@pytest.mark.django_db
class TestIsAdminOrReadOnly:
    """Test IsAdminOrReadOnly permission"""
    
    def setup_method(self):
        self.factory = APIRequestFactory()
        self.permission = IsAdminOrReadOnly()
        
        self.regular_user = User.objects.create_user(username='regular', password='pass123')
        
        self.staff_user = User.objects.create_user(username='staff', password='pass123')
        self.staff_user.is_staff = True
        self.staff_user.save()
        
        self.superuser = User.objects.create_user(username='super', password='pass123')
        self.superuser.is_superuser = True
        self.superuser.save()
    
    def test_allows_read_for_everyone(self):
        """Test GET requests allowed for everyone"""
        request = self.factory.get('/test/')
        request.user = AnonymousUser()
        
        assert self.permission.has_permission(request, PermissionTestView())
    
    def test_denies_write_for_regular_user(self):
        """Test POST requests denied for regular users"""
        request = self.factory.post('/test/')
        request.user = self.regular_user
        force_authenticate(request, user=self.regular_user)
        
        assert not self.permission.has_permission(request, PermissionTestView())
    
    def test_denies_write_for_staff(self):
        """Test POST requests denied for staff users (not superuser)"""
        request = self.factory.post('/test/')
        request.user = self.staff_user
        force_authenticate(request, user=self.staff_user)
        
        assert not self.permission.has_permission(request, PermissionTestView())
    
    def test_allows_write_for_superuser(self):
        """Test POST requests allowed for superusers"""
        request = self.factory.post('/test/')
        request.user = self.superuser
        force_authenticate(request, user=self.superuser)
        
        assert self.permission.has_permission(request, PermissionTestView())


@pytest.mark.django_db
class TestPermissionHelpers:
    """Test permission helper functions"""
    
    def test_user_in_multiple_groups(self):
        """Test user can be in multiple groups"""
        user = User.objects.create_user(username='multi', password='pass123')
        manager_group, _ = Group.objects.get_or_create(name='manager')
        editor_group, _ = Group.objects.get_or_create(name='editor')
        
        user.groups.add(manager_group, editor_group)
        
        assert user.groups.filter(name='manager').exists()
        assert user.groups.filter(name='editor').exists()
    
    def test_staff_and_group_combination(self):
        """Test user can be staff and in groups"""
        user = User.objects.create_user(username='combo', password='pass123')
        user.is_staff = True
        user.save()
        
        manager_group, _ = Group.objects.get_or_create(name='manager')
        user.groups.add(manager_group)
        
        # Should pass both IsManagerOrAdmin and IsStaffUser
        factory = APIRequestFactory()
        request = factory.get('/test/')
        request.user = user
        force_authenticate(request, user=user)
        
        assert IsManagerOrAdmin().has_permission(request, PermissionTestView())
        assert IsStaffUser().has_permission(request, PermissionTestView())
