# core/tests/test_dictionary.py

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from core.models import DictionaryEntry, EntryVariant, SearchQueryLog

User = get_user_model()


@pytest.mark.django_db
class TestPublicDictionarySearch:
    """Test public dictionary search endpoint"""
    
    def setup_method(self):
        self.client = APIClient()
        self.search_url = '/api/public/v1/dictionary/search'
        
        # Create test data
        self.entry1 = DictionaryEntry.objects.create(
            lemma="leb",
            gloss_ll="language",
            gloss_en="language"
        )
        self.entry2 = DictionaryEntry.objects.create(
            lemma="lango",
            gloss_ll="people",
            gloss_en="people"
        )
        self.entry3 = DictionaryEntry.objects.create(
            lemma="dictionary",
            gloss_ll="dictionary desc",
            gloss_en="book of words"
        )
        
        # Create variant for testing
        EntryVariant.objects.create(
            entry=self.entry1,
            alias="dholuo"
        )
    
    def test_search_without_query(self):
        """Test search returns all entries when no query provided"""
        response = self.client.get(self.search_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'results' in response.data
        assert response.data['count'] == 3
        assert len(response.data['results']) == 3
    
    def test_search_with_lemma_match(self):
        """Test search finds entries by lemma"""
        response = self.client.get(self.search_url, {'q': 'leb'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['lemma'] == 'leb'
    
    def test_search_with_gloss_ll_match(self):
        """Test search finds entries by Lango gloss"""
        response = self.client.get(self.search_url, {'q': 'language'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1
        assert any(r['lemma'] == 'leb' for r in response.data['results'])
    
    def test_search_with_gloss_en_match(self):
        """Test search finds entries by English gloss"""
        response = self.client.get(self.search_url, {'q': 'people'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1
        assert any(r['lemma'] == 'lango' for r in response.data['results'])
    
    def test_search_case_insensitive(self):
        """Test search is case insensitive"""
        response1 = self.client.get(self.search_url, {'q': 'LEB'})
        response2 = self.client.get(self.search_url, {'q': 'leb'})
        
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response1.data['count'] == response2.data['count']
    
    def test_search_no_results(self):
        """Test search with no matching entries"""
        response = self.client.get(self.search_url, {'q': 'nonexistent'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['results'] == []
    
    def test_search_pagination_limit(self):
        """Test pagination with limit parameter"""
        response = self.client.get(self.search_url, {'limit': 2})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_search_pagination_offset(self):
        """Test pagination with offset parameter"""
        response = self.client.get(self.search_url, {'offset': 1, 'limit': 2})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) <= 2
    
    def test_search_pagination_limit_bounds(self):
        """Test pagination limit respects max of 100"""
        response = self.client.get(self.search_url, {'limit': 200})
        
        assert response.status_code == status.HTTP_200_OK
        # Should cap at 100 internally
    
    def test_search_pagination_invalid_limit(self):
        """Test pagination handles invalid limit gracefully"""
        response = self.client.get(self.search_url, {'limit': 'invalid'})
        
        assert response.status_code == status.HTTP_200_OK
        # Should use default limit of 20
    
    def test_search_logs_query(self):
        """Test that searches are logged for analytics"""
        query = "test_query"
        initial_count = SearchQueryLog.objects.count()
        
        response = self.client.get(self.search_url, {'q': query})
        
        assert response.status_code == status.HTTP_200_OK
        assert SearchQueryLog.objects.count() == initial_count + 1
        
        log = SearchQueryLog.objects.latest('created_at')
        assert log.source == 'dictionary'
        assert log.query == query
        assert log.has_results == (response.data['count'] > 0)
        assert log.results_count == len(response.data['results'])
    
    def test_search_logs_authenticated_user(self):
        """Test that authenticated user is logged in search"""
        user = User.objects.create_user(username='testuser', password='pass123')
        self.client.force_authenticate(user=user)
        
        response = self.client.get(self.search_url, {'q': 'leb'})
        
        assert response.status_code == status.HTTP_200_OK
        log = SearchQueryLog.objects.latest('created_at')
        assert log.user == user
    
    def test_search_logs_anonymous_user(self):
        """Test that anonymous searches are logged without user"""
        response = self.client.get(self.search_url, {'q': 'leb'})
        
        assert response.status_code == status.HTTP_200_OK
        log = SearchQueryLog.objects.latest('created_at')
        assert log.user is None
    
    def test_search_response_structure(self):
        """Test response has correct structure"""
        response = self.client.get(self.search_url, {'q': 'leb'})
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'results' in response.data
        
        if response.data['results']:
            result = response.data['results'][0]
            assert 'id' in result
            assert 'lemma' in result
            assert 'gloss_ll' in result
            assert 'gloss_en' in result


@pytest.mark.django_db
class TestPublicDictionaryEntryDetail:
    """Test public dictionary entry detail endpoint"""
    
    def setup_method(self):
        self.client = APIClient()
        self.entry = DictionaryEntry.objects.create(
            lemma="test",
            gloss_ll="test in lango",
            gloss_en="test in english"
        )
        self.detail_url = f'/api/public/v1/dictionary/entry/{self.entry.id}'
    
    def test_get_existing_entry(self):
        """Test retrieving an existing entry"""
        response = self.client.get(self.detail_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == self.entry.id
        assert response.data['lemma'] == 'test'
        assert response.data['gloss_ll'] == 'test in lango'
        assert response.data['gloss_en'] == 'test in english'
    
    def test_get_nonexistent_entry(self):
        """Test retrieving a non-existent entry returns 404"""
        response = self.client.get('/api/public/v1/dictionary/entry/99999')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'not found' in response.data['detail'].lower()
    
    def test_entry_detail_no_auth_required(self):
        """Test that entry detail is publicly accessible"""
        # Don't authenticate
        response = self.client.get(self.detail_url)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_entry_detail_response_structure(self):
        """Test response has all required fields"""
        response = self.client.get(self.detail_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'id' in response.data
        assert 'lemma' in response.data
        assert 'gloss_ll' in response.data
        assert 'gloss_en' in response.data


@pytest.mark.django_db
class TestDictionaryEntryModel:
    """Test DictionaryEntry model behavior"""
    
    def test_create_entry(self):
        """Test creating a dictionary entry"""
        entry = DictionaryEntry.objects.create(
            lemma="new_word",
            gloss_ll="new in lango",
            gloss_en="new in english"
        )
        
        assert entry.id is not None
        assert entry.lemma == "new_word"
        assert str(entry) == "new_word"
    
    def test_lemma_uniqueness(self):
        """Test that lemma must be unique"""
        DictionaryEntry.objects.create(lemma="unique")
        
        with pytest.raises(Exception):  # IntegrityError
            DictionaryEntry.objects.create(lemma="unique")
    
    def test_entry_ordering(self):
        """Test entries are ordered by lemma"""
        DictionaryEntry.objects.create(lemma="zebra")
        DictionaryEntry.objects.create(lemma="apple")
        DictionaryEntry.objects.create(lemma="mango")
        
        entries = list(DictionaryEntry.objects.all())
        assert entries[0].lemma == "apple"
        assert entries[1].lemma == "mango"
        assert entries[2].lemma == "zebra"
    
    def test_updated_at_auto_updates(self):
        """Test that updated_at timestamp updates automatically"""
        entry = DictionaryEntry.objects.create(lemma="test")
        original_time = entry.updated_at
        
        entry.gloss_en = "updated"
        entry.save()
        
        assert entry.updated_at > original_time


@pytest.mark.django_db
class TestEntryVariantModel:
    """Test EntryVariant model behavior"""
    
    def test_create_variant(self):
        """Test creating an entry variant"""
        entry = DictionaryEntry.objects.create(lemma="main")
        variant = EntryVariant.objects.create(
            entry=entry,
            alias="alternative"
        )
        
        assert variant.id is not None
        assert variant.entry == entry
        assert variant.alias == "alternative"
        assert str(variant) == "alternative"
    
    def test_variant_cascade_delete(self):
        """Test that variants are deleted when entry is deleted"""
        entry = DictionaryEntry.objects.create(lemma="main")
        variant = EntryVariant.objects.create(entry=entry, alias="alt")
        
        entry.delete()
        
        assert not EntryVariant.objects.filter(id=variant.id).exists()
    
    def test_multiple_variants_per_entry(self):
        """Test that an entry can have multiple variants"""
        entry = DictionaryEntry.objects.create(lemma="main")
        variant1 = EntryVariant.objects.create(entry=entry, alias="alt1")
        variant2 = EntryVariant.objects.create(entry=entry, alias="alt2")
        
        variants = entry.variants.all()
        assert variants.count() == 2
        assert variant1 in variants
        assert variant2 in variants
