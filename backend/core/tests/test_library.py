# core/tests/test_library.py

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    LibraryItem,
    LibrarySubmission,
    LibraryEvent,
    LibraryCategory
)

User = get_user_model()


@pytest.mark.django_db
class TestLibrarySearch:
    """Test library search endpoint (authenticated)"""
    
    def setup_method(self):
        self.client = APIClient()
        self.search_url = '/api/library/search'
        self.user = User.objects.create_user(username='testuser', password='pass123')
        
        # Create test category
        self.category = LibraryCategory.objects.create(
            name="Books",
            slug="books"
        )
        
        # Create test data
        self.item1 = LibraryItem.objects.create(
            title="Lango Stories",
            description="Collection of traditional stories",
            url="http://example.com/stories",
            item_type="book",
            category=self.category,
            is_published=True
        )
        self.item2 = LibraryItem.objects.create(
            title="Learning Lango",
            description="Language learning guide",
            url="http://example.com/learning",
            item_type="document",
            category=self.category,
            is_published=True
        )
        # Unpublished item (should not appear in results)
        self.item3 = LibraryItem.objects.create(
            title="Unpublished",
            description="Not visible",
            is_published=False
        )
    
    def test_search_requires_authentication(self):
        """Test that library search requires authentication"""
        response = self.client.get(self.search_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_search_authenticated_success(self):
        """Test authenticated user can search library"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.search_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'results' in response.data
        assert response.data['count'] == 2  # Only published items
    
    def test_search_only_returns_published(self):
        """Test that search only returns published items"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.search_url)
        
        assert response.status_code == status.HTTP_200_OK
        titles = [item['title'] for item in response.data['results']]
        assert 'Unpublished' not in titles
    
    def test_search_by_title(self):
        """Test search filters by title"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.search_url, {'q': 'Stories'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'Lango Stories'
    
    def test_search_by_description(self):
        """Test search filters by description"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.search_url, {'q': 'learning guide'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
    
    def test_search_by_category(self):
        """Test search filters by category slug"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.search_url, {'category': 'books'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
    
    def test_search_pagination(self):
        """Test search respects pagination parameters"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.search_url, {'limit': 1})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
    
    def test_search_case_insensitive(self):
        """Test search is case insensitive"""
        self.client.force_authenticate(user=self.user)
        response1 = self.client.get(self.search_url, {'q': 'LANGO'})
        response2 = self.client.get(self.search_url, {'q': 'lango'})
        
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response1.data['count'] == response2.data['count']


@pytest.mark.django_db
class TestLibrarySubmit:
    """Test library submission endpoint"""
    
    def setup_method(self):
        self.client = APIClient()
        self.submit_url = '/api/library/submit'
        self.user = User.objects.create_user(username='testuser', password='pass123')
    
    def test_submit_requires_authentication(self):
        """Test submission requires authentication"""
        response = self.client.post(self.submit_url, {})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_submit_success(self):
        """Test successful submission"""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Resource',
            'description': 'A great resource',
            'url': 'http://example.com/resource'
        }
        response = self.client.post(self.submit_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data
        assert 'status' in response.data
        assert response.data['status'] == 'pending'
        
        # Verify submission was created
        submission = LibrarySubmission.objects.get(id=response.data['id'])
        assert submission.title == 'New Resource'
        assert submission.submitted_by == self.user
    
    def test_submit_missing_title(self):
        """Test submission fails without title"""
        self.client.force_authenticate(user=self.user)
        data = {'description': 'No title'}
        response = self.client.post(self.submit_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_submit_empty_title(self):
        """Test submission fails with empty title"""
        self.client.force_authenticate(user=self.user)
        data = {'title': '   ', 'description': 'Empty title'}
        response = self.client.post(self.submit_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_submit_optional_fields(self):
        """Test submission works with only required fields"""
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Minimal Submission'}
        response = self.client.post(self.submit_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestLibraryTrack:
    """Test library event tracking endpoint"""
    
    def setup_method(self):
        self.client = APIClient()
        self.track_url = '/api/library/track'
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.item = LibraryItem.objects.create(
            title="Test Item",
            is_published=True
        )
    
    def test_track_requires_authentication(self):
        """Test tracking requires authentication"""
        response = self.client.post(self.track_url, {})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_track_view_event(self):
        """Test tracking a view event"""
        self.client.force_authenticate(user=self.user)
        data = {
            'item_id': self.item.id,
            'event_type': 'view'
        }
        response = self.client.post(self.track_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify event was created
        event = LibraryEvent.objects.latest('created_at')
        assert event.item == self.item
        assert event.event_type == 'view'
        assert event.user == self.user
    
    def test_track_download_event(self):
        """Test tracking a download event"""
        self.client.force_authenticate(user=self.user)
        data = {
            'item_id': self.item.id,
            'event_type': 'download'
        }
        response = self.client.post(self.track_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        event = LibraryEvent.objects.latest('created_at')
        assert event.event_type == 'download'
    
    def test_track_complete_event(self):
        """Test tracking a complete event"""
        self.client.force_authenticate(user=self.user)
        data = {
            'item_id': self.item.id,
            'event_type': 'complete'
        }
        response = self.client.post(self.track_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        event = LibraryEvent.objects.latest('created_at')
        assert event.event_type == 'complete'
    
    def test_track_invalid_event_type(self):
        """Test tracking with invalid event type fails"""
        self.client.force_authenticate(user=self.user)
        data = {
            'item_id': self.item.id,
            'event_type': 'invalid'
        }
        response = self.client.post(self.track_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_track_nonexistent_item(self):
        """Test tracking non-existent item fails"""
        self.client.force_authenticate(user=self.user)
        data = {
            'item_id': 99999,
            'event_type': 'view'
        }
        response = self.client.post(self.track_url, data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_track_unpublished_item(self):
        """Test tracking unpublished item fails"""
        unpublished = LibraryItem.objects.create(
            title="Unpublished",
            is_published=False
        )
        self.client.force_authenticate(user=self.user)
        data = {
            'item_id': unpublished.id,
            'event_type': 'view'
        }
        response = self.client.post(self.track_url, data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_track_invalid_item_id(self):
        """Test tracking with invalid item_id format"""
        self.client.force_authenticate(user=self.user)
        data = {
            'item_id': 'invalid',
            'event_type': 'view'
        }
        response = self.client.post(self.track_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLibrarySubmissionApprove:
    """Test library submission approval endpoint"""
    
    def setup_method(self):
        self.client = APIClient()
        
        # Create manager user with permissions
        self.manager = User.objects.create_user(username='manager', password='pass123')
        self.manager.is_staff = True
        self.manager.save()
        
        # Create regular user
        self.user = User.objects.create_user(username='regular', password='pass123')
        
        # Create test submission
        self.submission = LibrarySubmission.objects.create(
            title="Test Submission",
            description="Test description",
            url="http://example.com/test",
            submitted_by=self.user,
            status=LibrarySubmission.STATUS_PENDING
        )
        
        self.approve_url = f'/api/admin/library/submissions/{self.submission.id}/approve'
    
    def test_approve_requires_authentication(self):
        """Test approval requires authentication"""
        response = self.client.post(self.approve_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_approve_requires_manager_permission(self):
        """Test approval requires manager permissions"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.approve_url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_approve_success(self):
        """Test successful submission approval"""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(self.approve_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'item_id' in response.data
        
        # Verify submission was approved
        self.submission.refresh_from_db()
        assert self.submission.status == LibrarySubmission.STATUS_APPROVED
        assert self.submission.reviewed_by == self.manager
        assert self.submission.reviewed_at is not None
        
        # Verify library item was created
        item = LibraryItem.objects.get(id=response.data['item_id'])
        assert item.title == self.submission.title
        assert item.is_published is True
    
    def test_approve_nonexistent_submission(self):
        """Test approving non-existent submission"""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post('/api/admin/library/submissions/99999/approve')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_approve_already_approved(self):
        """Test approving already approved submission fails"""
        self.submission.status = LibrarySubmission.STATUS_APPROVED
        self.submission.save()
        
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(self.approve_url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_approve_already_rejected(self):
        """Test approving already rejected submission fails"""
        self.submission.status = LibrarySubmission.STATUS_REJECTED
        self.submission.save()
        
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(self.approve_url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLibrarySubmissionReject:
    """Test library submission rejection endpoint"""
    
    def setup_method(self):
        self.client = APIClient()
        
        # Create manager user
        self.manager = User.objects.create_user(username='manager', password='pass123')
        self.manager.is_staff = True
        self.manager.save()
        
        # Create test submission
        self.submission = LibrarySubmission.objects.create(
            title="Test Submission",
            status=LibrarySubmission.STATUS_PENDING
        )
        
        self.reject_url = f'/api/admin/library/submissions/{self.submission.id}/reject'
    
    def test_reject_requires_authentication(self):
        """Test rejection requires authentication"""
        response = self.client.post(self.reject_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_reject_success(self):
        """Test successful submission rejection"""
        self.client.force_authenticate(user=self.manager)
        data = {'reason': 'Does not meet quality standards'}
        response = self.client.post(self.reject_url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify submission was rejected
        self.submission.refresh_from_db()
        assert self.submission.status == LibrarySubmission.STATUS_REJECTED
        assert self.submission.reviewed_by == self.manager
        assert self.submission.reviewed_at is not None
        assert self.submission.rejection_reason == 'Does not meet quality standards'
    
    def test_reject_without_reason(self):
        """Test rejection without reason still works"""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(self.reject_url)
        
        assert response.status_code == status.HTTP_200_OK
        self.submission.refresh_from_db()
        assert self.submission.status == LibrarySubmission.STATUS_REJECTED
    
    def test_reject_nonexistent_submission(self):
        """Test rejecting non-existent submission"""
        self.client.force_authenticate(user=self.manager)
        response = self.client.post('/api/admin/library/submissions/99999/reject')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestLibraryModels:
    """Test library model behavior"""
    
    def test_library_category_creation(self):
        """Test creating a library category"""
        category = LibraryCategory.objects.create(
            name="Videos",
            slug="videos"
        )
        
        assert category.id is not None
        assert str(category) == "Videos"
    
    def test_library_item_creation(self):
        """Test creating a library item"""
        item = LibraryItem.objects.create(
            title="Test Resource",
            description="Test description",
            item_type="book",
            is_published=True
        )
        
        assert item.id is not None
        assert str(item) == "Test Resource"
        assert item.is_published is True
    
    def test_library_submission_defaults(self):
        """Test library submission default values"""
        submission = LibrarySubmission.objects.create(
            title="Test Submission"
        )
        
        assert submission.status == LibrarySubmission.STATUS_PENDING
        assert submission.reviewed_by is None
        assert submission.reviewed_at is None
    
    def test_library_event_creation(self):
        """Test creating a library event"""
        user = User.objects.create_user(username='testuser', password='pass123')
        item = LibraryItem.objects.create(
            title="Test Item",
            is_published=True
        )
        
        event = LibraryEvent.objects.create(
            user=user,
            item=item,
            event_type=LibraryEvent.EVENT_VIEW
        )
        
        assert event.id is not None
        assert event.user == user
        assert event.item == item
    
    def test_library_event_cascade_delete(self):
        """Test events are deleted when item is deleted"""
        item = LibraryItem.objects.create(title="Test", is_published=True)
        event = LibraryEvent.objects.create(
            item=item,
            event_type=LibraryEvent.EVENT_VIEW
        )
        
        item.delete()
        
        assert not LibraryEvent.objects.filter(id=event.id).exists()
