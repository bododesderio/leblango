# core/tests/test_importers.py

import pytest
import io
import json
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status

from core.models import DictionaryEntry, LibraryItem, ImportJob

User = get_user_model()


@pytest.mark.django_db
class TestDictionaryImportCSV:
    """Test dictionary CSV import endpoint"""
    
    def setup_method(self):
        self.client = APIClient()
        self.import_url = '/api/admin/import/dictionary/csv'
        
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
    
    def test_import_requires_authentication(self):
        """Test import requires authentication"""
        response = self.client.post(self.import_url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_import_requires_staff_permission(self):
        """Test import requires staff permissions"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(self.import_url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_import_success(self):
        """Test successful CSV import"""
        csv_content = "lemma,gloss_ll,gloss_en\ntest,test_ll,test_en\nword,word_ll,word_en"
        csv_file = SimpleUploadedFile(
            "dict.csv",
            csv_content.encode('utf-8'),
            content_type='text/csv'
        )
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(
            self.import_url,
            {'file': csv_file},
            format='multipart'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert 'job_id' in response.data
        assert response.data['total_rows'] == 2
        assert response.data['success_rows'] == 2
        assert response.data['failed_rows'] == 0
        
        # Verify entries were created
        assert DictionaryEntry.objects.filter(lemma='test').exists()
        assert DictionaryEntry.objects.filter(lemma='word').exists()
        
        # Verify import job was logged
        job = ImportJob.objects.get(id=response.data['job_id'])
        assert job.job_type == 'dictionary'
        assert job.created_by == self.staff_user
    
    def test_import_missing_file(self):
        """Test import without file fails"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.import_url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_import_with_bom(self):
        """Test import handles UTF-8 BOM correctly"""
        csv_content = "\ufefflemma,gloss_ll,gloss_en\ntest,test_ll,test_en"
        csv_file = SimpleUploadedFile(
            "dict.csv",
            csv_content.encode('utf-8-sig'),
            content_type='text/csv'
        )
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(
            self.import_url,
            {'file': csv_file},
            format='multipart'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success_rows'] == 1
    
    def test_import_updates_existing(self):
        """Test import updates existing entries"""
        # Create existing entry
        DictionaryEntry.objects.create(
            lemma='existing',
            gloss_ll='old_ll',
            gloss_en='old_en'
        )
        
        csv_content = "lemma,gloss_ll,gloss_en\nexisting,new_ll,new_en"
        csv_file = SimpleUploadedFile(
            "dict.csv",
            csv_content.encode('utf-8'),
            content_type='text/csv'
        )
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(
            self.import_url,
            {'file': csv_file},
            format='multipart'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify entry was updated
        entry = DictionaryEntry.objects.get(lemma='existing')
        assert entry.gloss_ll == 'new_ll'
        assert entry.gloss_en == 'new_en'
    
    def test_import_skips_empty_lemma(self):
        """Test import skips rows with empty lemma"""
        csv_content = "lemma,gloss_ll,gloss_en\n,empty_ll,empty_en\nvalid,valid_ll,valid_en"
        csv_file = SimpleUploadedFile(
            "dict.csv",
            csv_content.encode('utf-8'),
            content_type='text/csv'
        )
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(
            self.import_url,
            {'file': csv_file},
            format='multipart'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_rows'] == 2
        assert response.data['success_rows'] == 1
        assert response.data['failed_rows'] == 1
        
        # Verify only valid entry was created
        assert DictionaryEntry.objects.filter(lemma='valid').exists()
        assert not DictionaryEntry.objects.filter(lemma='').exists()
    
    def test_import_handles_missing_columns(self):
        """Test import handles missing optional columns"""
        csv_content = "lemma\ntest_word"
        csv_file = SimpleUploadedFile(
            "dict.csv",
            csv_content.encode('utf-8'),
            content_type='text/csv'
        )
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(
            self.import_url,
            {'file': csv_file},
            format='multipart'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success_rows'] == 1
        
        entry = DictionaryEntry.objects.get(lemma='test_word')
        assert entry.gloss_ll == ''
        assert entry.gloss_en == ''


@pytest.mark.django_db
class TestDictionaryImportJSON:
    """Test dictionary JSON import endpoint"""
    
    def setup_method(self):
        self.client = APIClient()
        self.import_url = '/api/admin/import/dictionary/json'
        
        self.staff_user = User.objects.create_user(
            username='staff',
            password='pass123',
            is_staff=True
        )
    
    def test_import_json_success(self):
        """Test successful JSON import"""
        data = {
            'entries': [
                {'lemma': 'test', 'gloss_ll': 'test_ll', 'gloss_en': 'test_en'},
                {'lemma': 'word', 'gloss_ll': 'word_ll', 'gloss_en': 'word_en'}
            ]
        }
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.import_url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_rows'] == 2
        assert response.data['success_rows'] == 2
        assert response.data['failed_rows'] == 0
        
        # Verify entries were created
        assert DictionaryEntry.objects.filter(lemma='test').exists()
        assert DictionaryEntry.objects.filter(lemma='word').exists()
    
    def test_import_json_invalid_format(self):
        """Test import with invalid JSON format"""
        data = {'wrong_key': []}
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.import_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_import_json_not_list(self):
        """Test import fails when entries is not a list"""
        data = {'entries': 'not a list'}
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.import_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_import_json_updates_existing(self):
        """Test JSON import updates existing entries"""
        DictionaryEntry.objects.create(
            lemma='existing',
            gloss_ll='old',
            gloss_en='old'
        )
        
        data = {
            'entries': [
                {'lemma': 'existing', 'gloss_ll': 'new', 'gloss_en': 'new'}
            ]
        }
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.import_url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        entry = DictionaryEntry.objects.get(lemma='existing')
        assert entry.gloss_ll == 'new'
        assert entry.gloss_en == 'new'
    
    def test_import_json_skips_empty_lemma(self):
        """Test JSON import skips entries with empty lemma"""
        data = {
            'entries': [
                {'lemma': '', 'gloss_ll': 'test', 'gloss_en': 'test'},
                {'lemma': 'valid', 'gloss_ll': 'test', 'gloss_en': 'test'}
            ]
        }
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.import_url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success_rows'] == 1
        assert response.data['failed_rows'] == 1


@pytest.mark.django_db
class TestLibraryImportJSON:
    """Test library JSON import endpoint"""
    
    def setup_method(self):
        self.client = APIClient()
        self.import_url = '/api/admin/import/library/json'
        
        self.staff_user = User.objects.create_user(
            username='staff',
            password='pass123',
            is_staff=True
        )
    
    def test_import_library_success(self):
        """Test successful library JSON import"""
        data = {
            'items': [
                {
                    'title': 'Resource 1',
                    'description': 'Description 1',
                    'url': 'http://example.com/1',
                    'item_type': 'book',
                    'is_published': True
                },
                {
                    'title': 'Resource 2',
                    'description': 'Description 2',
                    'url': 'http://example.com/2',
                    'item_type': 'video',
                    'is_published': False
                }
            ]
        }
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.import_url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_rows'] == 2
        assert response.data['success_rows'] == 2
        assert response.data['failed_rows'] == 0
        
        # Verify items were created
        item1 = LibraryItem.objects.get(title='Resource 1')
        assert item1.item_type == 'book'
        assert item1.is_published is True
        
        item2 = LibraryItem.objects.get(title='Resource 2')
        assert item2.is_published is False
    
    def test_import_library_invalid_format(self):
        """Test library import with invalid format"""
        data = {'wrong_key': []}
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.import_url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_import_library_missing_title(self):
        """Test library import skips items without title"""
        data = {
            'items': [
                {'description': 'No title'},
                {'title': 'Valid', 'description': 'Has title'}
            ]
        }
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.import_url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success_rows'] == 1
        assert response.data['failed_rows'] == 1
        
        assert LibraryItem.objects.filter(title='Valid').exists()
    
    def test_import_library_updates_existing(self):
        """Test library import updates existing items"""
        LibraryItem.objects.create(
            title='Existing',
            description='Old description',
            is_published=False
        )
        
        data = {
            'items': [
                {
                    'title': 'Existing',
                    'description': 'New description',
                    'is_published': True
                }
            ]
        }
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.import_url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        item = LibraryItem.objects.get(title='Existing')
        assert item.description == 'New description'
        assert item.is_published is True
    
    def test_import_library_minimal_fields(self):
        """Test library import with only required fields"""
        data = {
            'items': [
                {'title': 'Minimal Item'}
            ]
        }
        
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.import_url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success_rows'] == 1
        
        item = LibraryItem.objects.get(title='Minimal Item')
        assert item.description == ''
        assert item.url == ''


@pytest.mark.django_db
class TestImportJobTracking:
    """Test import job tracking and logging"""
    
    def setup_method(self):
        self.staff_user = User.objects.create_user(
            username='staff',
            password='pass123',
            is_staff=True
        )
    
    def test_import_job_created(self):
        """Test that import jobs are tracked"""
        initial_count = ImportJob.objects.count()
        
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        
        data = {'entries': [{'lemma': 'test', 'gloss_ll': '', 'gloss_en': ''}]}
        response = client.post('/api/admin/import/dictionary/json', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert ImportJob.objects.count() == initial_count + 1
    
    def test_import_job_records_stats(self):
        """Test import job records correct statistics"""
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        
        data = {
            'entries': [
                {'lemma': 'valid', 'gloss_ll': 'test', 'gloss_en': 'test'},
                {'lemma': '', 'gloss_ll': 'invalid', 'gloss_en': 'invalid'}
            ]
        }
        response = client.post('/api/admin/import/dictionary/json', data, format='json')
        
        job = ImportJob.objects.get(id=response.data['job_id'])
        assert job.total_rows == 2
        assert job.success_rows == 1
        assert job.failed_rows == 1
    
    def test_import_job_records_creator(self):
        """Test import job records the user who created it"""
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        
        data = {'entries': [{'lemma': 'test', 'gloss_ll': '', 'gloss_en': ''}]}
        response = client.post('/api/admin/import/dictionary/json', data, format='json')
        
        job = ImportJob.objects.get(id=response.data['job_id'])
        assert job.created_by == self.staff_user
    
    def test_import_job_has_log(self):
        """Test import job contains log information"""
        client = APIClient()
        client.force_authenticate(user=self.staff_user)
        
        data = {'entries': [{'lemma': 'test', 'gloss_ll': '', 'gloss_en': ''}]}
        response = client.post('/api/admin/import/dictionary/json', data, format='json')
        
        job = ImportJob.objects.get(id=response.data['job_id'])
        assert job.log != ''
        assert 'Starting' in job.log
