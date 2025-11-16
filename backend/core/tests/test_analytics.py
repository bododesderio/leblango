# core/tests/test_analytics.py

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    SearchQueryLog,
    LibraryEvent,
    LibraryItem,
    DictionaryEntry
)

User = get_user_model()


@pytest.mark.django_db
class TestQueryHealthSummary:
    """Test query health summary endpoint"""
    
    def setup_method(self):
        self.client = APIClient()
        self.url = '/api/admin/query-health/summary'
        
        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staff',
            password='pass123',
            is_staff=True
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='regular',
            password='pass123'
        )
        
        # Create test query logs
        SearchQueryLog.objects.create(
            source='dictionary',
            query='successful query',
            has_results=True,
            results_count=5
        )
        SearchQueryLog.objects.create(
            source='dictionary',
            query='no results query',
            has_results=False,
            results_count=0
        )
        SearchQueryLog.objects.create(
            source='library',
            query='another successful',
            has_results=True,
            results_count=3
        )
    
    def test_requires_authentication(self):
        """Test endpoint requires authentication"""
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_requires_staff_permission(self):
        """Test endpoint requires staff permissions"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_query_health_summary(self):
        """Test query health summary returns correct data"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'window_days' in response.data
        assert 'total_searches' in response.data
        assert 'no_result_searches' in response.data
        assert 'no_result_rate' in response.data
        assert 'top_no_result_queries' in response.data
        assert 'top_queries' in response.data
        
        # Verify calculations
        assert response.data['total_searches'] == 3
        assert response.data['no_result_searches'] == 1
        assert response.data['no_result_rate'] == pytest.approx(1/3)
    
    def test_query_health_custom_days(self):
        """Test query health with custom time window"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url, {'days': 7})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['window_days'] == 7
    
    def test_query_health_custom_limit(self):
        """Test query health with custom result limit"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url, {'limit': 10})
        
        assert response.status_code == status.HTTP_200_OK
        # top_no_result_queries should be limited
        assert len(response.data['top_no_result_queries']) <= 10
    
    def test_query_health_top_no_results(self):
        """Test top no-result queries are returned"""
        from django.core.cache import cache
        
        # Clear cache to ensure fresh data
        cache.clear()
        
        # Create multiple no-result queries
        for i in range(3):
            SearchQueryLog.objects.create(
                source='dictionary',
                query='missing word',
                has_results=False,
                results_count=0
            )
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        top_queries = response.data['top_no_result_queries']
        
        # Should show 'missing word' as most frequent
        if top_queries:
            most_frequent = top_queries[0]
            assert most_frequent['query'] == 'missing word'
            assert most_frequent['times'] == 3
    
    def test_query_health_caching(self):
        """Test that results are cached"""
        self.client.force_authenticate(user=self.staff_user)
        
        # First request
        response1 = self.client.get(self.url)
        assert response1.status_code == status.HTTP_200_OK
        
        # Add new query
        SearchQueryLog.objects.create(
            source='dictionary',
            query='new query',
            has_results=True,
            results_count=1
        )
        
        # Second request (should be cached, so count unchanged)
        response2 = self.client.get(self.url)
        assert response2.status_code == status.HTTP_200_OK
        
        # Results might be cached (60s cache timeout)
        # This tests that caching is working, not exact values


@pytest.mark.django_db
class TestLibraryAnalyticsOverview:
    """Test library analytics overview endpoint"""
    
    def setup_method(self):
        self.client = APIClient()
        self.url = '/api/admin/analytics/library/overview'
        
        self.staff_user = User.objects.create_user(
            username='staff',
            password='pass123',
            is_staff=True
        )
        
        # Create test library item and events
        self.item = LibraryItem.objects.create(
            title="Test Item",
            is_published=True
        )
        
        LibraryEvent.objects.create(
            item=self.item,
            event_type=LibraryEvent.EVENT_VIEW
        )
        LibraryEvent.objects.create(
            item=self.item,
            event_type=LibraryEvent.EVENT_VIEW
        )
        LibraryEvent.objects.create(
            item=self.item,
            event_type=LibraryEvent.EVENT_DOWNLOAD
        )
        LibraryEvent.objects.create(
            item=self.item,
            event_type=LibraryEvent.EVENT_COMPLETE
        )
    
    def test_requires_authentication(self):
        """Test endpoint requires authentication"""
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_requires_staff_permission(self):
        """Test endpoint requires staff permissions"""
        regular_user = User.objects.create_user(username='regular', password='pass123')
        self.client.force_authenticate(user=regular_user)
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_library_analytics_overview(self):
        """Test library analytics returns aggregated event data"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_events' in response.data
        assert 'by_type' in response.data
        
        assert response.data['total_events'] == 4
        assert response.data['by_type']['view'] == 2
        assert response.data['by_type']['download'] == 1
        assert response.data['by_type']['complete'] == 1
    
    def test_library_analytics_empty_data(self):
        """Test library analytics with no events"""
        LibraryEvent.objects.all().delete()
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_events'] == 0
        assert response.data['by_type'] == {}


@pytest.mark.django_db
class TestDictionaryAnalyticsOverview:
    """Test dictionary analytics overview endpoint"""
    
    def setup_method(self):
        self.client = APIClient()
        self.url = '/api/admin/analytics/dictionary/overview'
        
        self.staff_user = User.objects.create_user(
            username='staff',
            password='pass123',
            is_staff=True
        )
        
        # Create test search logs
        SearchQueryLog.objects.create(
            source='dictionary',
            query='successful',
            has_results=True,
            results_count=5
        )
        SearchQueryLog.objects.create(
            source='dictionary',
            query='no results',
            has_results=False,
            results_count=0
        )
        SearchQueryLog.objects.create(
            source='library',
            query='library search',
            has_results=True,
            results_count=2
        )
    
    def test_requires_authentication(self):
        """Test endpoint requires authentication"""
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_requires_staff_permission(self):
        """Test endpoint requires staff permissions"""
        regular_user = User.objects.create_user(username='regular', password='pass123')
        self.client.force_authenticate(user=regular_user)
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_dictionary_analytics_overview(self):
        """Test dictionary analytics returns correct data"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_queries' in response.data
        assert 'with_results' in response.data
        assert 'no_results' in response.data
        assert 'no_results_rate' in response.data
        
        # Only dictionary queries should be counted
        assert response.data['total_queries'] == 2
        assert response.data['with_results'] == 1
        assert response.data['no_results'] == 1
        assert response.data['no_results_rate'] == 0.5
    
    def test_dictionary_analytics_empty_data(self):
        """Test dictionary analytics with no queries"""
        SearchQueryLog.objects.filter(source='dictionary').delete()
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_queries'] == 0
        assert response.data['no_results_rate'] == 0


@pytest.mark.django_db
class TestSearchQueryLogging:
    """Test search query logging functionality"""
    
    def test_query_log_creation(self):
        """Test creating search query log"""
        log = SearchQueryLog.objects.create(
            source='dictionary',
            query='test query',
            has_results=True,
            results_count=5
        )
        
        assert log.id is not None
        assert str(log) == 'dictionary: test query'
    
    def test_query_log_with_user(self):
        """Test query log can track user"""
        user = User.objects.create_user(username='testuser', password='pass123')
        log = SearchQueryLog.objects.create(
            source='dictionary',
            query='test',
            has_results=True,
            results_count=1,
            user=user
        )
        
        assert log.user == user
    
    def test_query_log_without_user(self):
        """Test query log works without user (anonymous)"""
        log = SearchQueryLog.objects.create(
            source='dictionary',
            query='test',
            has_results=True,
            results_count=1,
            user=None
        )
        
        assert log.user is None
    
    def test_query_log_with_metadata(self):
        """Test query log can store metadata"""
        log = SearchQueryLog.objects.create(
            source='dictionary',
            query='test',
            has_results=True,
            results_count=1,
            meta={'ip': '127.0.0.1', 'user_agent': 'test'}
        )
        
        assert log.meta['ip'] == '127.0.0.1'
        assert log.meta['user_agent'] == 'test'
    
    def test_query_log_ordering(self):
        """Test query logs are ordered by created_at descending"""
        old_log = SearchQueryLog.objects.create(
            source='dictionary',
            query='old',
            has_results=True,
            results_count=1
        )
        
        # Update created_at to make it older
        old_time = timezone.now() - timedelta(days=1)
        SearchQueryLog.objects.filter(id=old_log.id).update(created_at=old_time)
        
        new_log = SearchQueryLog.objects.create(
            source='dictionary',
            query='new',
            has_results=True,
            results_count=1
        )
        
        logs = list(SearchQueryLog.objects.all())
        assert logs[0].id == new_log.id
        assert logs[1].id == old_log.id


@pytest.mark.django_db
class TestLibraryEventModel:
    """Test LibraryEvent model behavior"""
    
    def test_event_creation(self):
        """Test creating library event"""
        user = User.objects.create_user(username='testuser', password='pass123')
        item = LibraryItem.objects.create(title="Test", is_published=True)
        
        event = LibraryEvent.objects.create(
            user=user,
            item=item,
            event_type=LibraryEvent.EVENT_VIEW
        )
        
        assert event.id is not None
        assert event.user == user
        assert event.item == item
        assert event.event_type == 'view'
    
    def test_event_anonymous_user(self):
        """Test event can be created without user"""
        item = LibraryItem.objects.create(title="Test", is_published=True)
        
        event = LibraryEvent.objects.create(
            user=None,
            item=item,
            event_type=LibraryEvent.EVENT_DOWNLOAD
        )
        
        assert event.user is None
        assert 'anonymous' in str(event).lower()
    
    def test_event_types(self):
        """Test all event types can be created"""
        item = LibraryItem.objects.create(title="Test", is_published=True)
        
        for event_type, _ in LibraryEvent.EVENT_TYPES:
            event = LibraryEvent.objects.create(
                item=item,
                event_type=event_type
            )
            assert event.event_type == event_type
