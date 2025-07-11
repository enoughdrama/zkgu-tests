from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from .models import ZkguPerson, ZkguPersonSync, APIToken
from .authentication import TokenAuthentication, generate_api_token
from .serializers import ZkguPersonSerializer

class ZkguPersonModelTest(TestCase):
    def setUp(self):
        self.person_data = {
            'ID_REC': 'TEST001',
            'LASTNAME': 'Иванов',
            'FIRSTNAME': 'Иван',
            'MIDNAME': 'Иванович'
        }

    def test_create_person(self):
        person = ZkguPerson.objects.create(**self.person_data)
        self.assertEqual(person.ID_REC, 'TEST001')
        self.assertEqual(person.LASTNAME, 'Иванов')
        self.assertEqual(person.DELETION_MARK, 0)
        self.assertIsNotNone(person.created_at)
        self.assertIsNotNone(person.last_update)

    def test_person_str_representation(self):
        person = ZkguPerson.objects.create(**self.person_data)
        self.assertIn('TEST001', str(person))

    def test_deletion_mark_default(self):
        person = ZkguPerson.objects.create(ID_REC='TEST002')
        self.assertEqual(person.DELETION_MARK, 0)

    def test_auto_update_timestamp(self):
        person = ZkguPerson.objects.create(**self.person_data)
        original_update = person.last_update
        person.LASTNAME = 'Петров'
        person.save()
        self.assertGreater(person.last_update, original_update)

class APITokenModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_generate_api_token(self):
        token = generate_api_token(self.user)
        self.assertEqual(len(token), 64)
        api_token = APIToken.objects.get(user=self.user)
        self.assertEqual(api_token.token, token)
        self.assertTrue(api_token.is_active)

    def test_regenerate_token(self):
        token1 = generate_api_token(self.user)
        token2 = generate_api_token(self.user)
        self.assertNotEqual(token1, token2)
        self.assertEqual(APIToken.objects.filter(user=self.user).count(), 1)

class TokenAuthenticationTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = generate_api_token(self.user)
        self.auth = TokenAuthentication()

    def test_valid_token_authentication(self):
        request = self.factory.get('/api/v1/persons/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {self.token}'
        
        user, token_obj = self.auth.authenticate(request)
        self.assertEqual(user, self.user)
        self.assertIsInstance(token_obj, APIToken)

    def test_invalid_token_authentication(self):
        request = self.factory.get('/api/v1/persons/')
        request.META['HTTP_AUTHORIZATION'] = 'Bearer invalid_token_12345'
        
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_missing_authorization_header(self):
        request = self.factory.get('/api/v1/persons/')
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

class PersonAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.token = generate_api_token(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.person_data = {
            'ID_REC': 'API001',
            'LASTNAME': 'Тестов',
            'FIRSTNAME': 'Тест',
            'MIDNAME': 'Тестович'
        }

    def test_create_person_success(self):
        response = self.client.post('/api/v1/persons/', self.person_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ZkguPerson.objects.filter(ID_REC='API001').exists())

    def test_get_person_list(self):
        ZkguPerson.objects.create(**self.person_data)
        response = self.client.get('/api/v1/persons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_unauthorized_access(self):
        client = APIClient()
        response = client.get('/api/v1/persons/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_person_detail(self):
        person = ZkguPerson.objects.create(**self.person_data)
        response = self.client.get(f'/api/v1/persons/{person.ID_REC}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ID_REC'], 'API001')

    def test_update_person(self):
        person = ZkguPerson.objects.create(**self.person_data)
        update_data = {'LASTNAME': 'Обновленов'}
        
        response = self.client.patch(f'/api/v1/persons/{person.ID_REC}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        person.refresh_from_db()
        self.assertEqual(person.LASTNAME, 'Обновленов')

    def test_delete_person(self):
        person = ZkguPerson.objects.create(**self.person_data)
        response = self.client.delete(f'/api/v1/persons/{person.ID_REC}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ZkguPerson.objects.filter(ID_REC='API001').exists())

class ZkguPersonSerializerTest(TestCase):
    def setUp(self):
        self.person_data = {
            'ID_REC': 'SER001',
            'LASTNAME': 'Сериализованов',
            'FIRSTNAME': 'Сериал',
            'MIDNAME': 'Сериалович'
        }

    def test_valid_serialization(self):
        person = ZkguPerson.objects.create(**self.person_data)
        serializer = ZkguPersonSerializer(person)
        
        data = serializer.data
        self.assertEqual(data['ID_REC'], 'SER001')
        self.assertEqual(data['LASTNAME'], 'Сериализованов')
        self.assertIn('created_at', data)
        self.assertIn('last_update', data)

    def test_valid_deserialization(self):
        serializer = ZkguPersonSerializer(data=self.person_data)
        self.assertTrue(serializer.is_valid())
        
        person = serializer.save()
        self.assertEqual(person.ID_REC, 'SER001')
        self.assertEqual(person.LASTNAME, 'Сериализованов')

    def test_partial_update(self):
        person = ZkguPerson.objects.create(**self.person_data)
        partial_data = {'FIRSTNAME': 'Частичный'}
        
        serializer = ZkguPersonSerializer(person, data=partial_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_person = serializer.save()
        self.assertEqual(updated_person.FIRSTNAME, 'Частичный')
        self.assertEqual(updated_person.LASTNAME, 'Сериализованов')

class ZkguPersonSyncModelTest(TestCase):
    def setUp(self):
        self.person = ZkguPerson.objects.create(
            ID_REC='SYNC001',
            LASTNAME='Тестов'
        )

    def test_create_sync_record(self):
        sync = ZkguPersonSync.objects.create(
            person=self.person,
            sync_status='pending'
        )
        self.assertEqual(sync.person, self.person)
        self.assertEqual(sync.sync_status, 'pending')
        self.assertEqual(sync.retry_count, 0)

    def test_sync_status_choices(self):
        valid_statuses = ['pending', 'synced', 'failed']
        for status in valid_statuses:
            sync = ZkguPersonSync.objects.create(
                person=self.person,
                sync_status=status
            )
            self.assertEqual(sync.sync_status, status)
            sync.delete()

    def test_cascade_delete(self):
        sync = ZkguPersonSync.objects.create(person=self.person)
        person_id = self.person.id
        self.person.delete()
        self.assertFalse(ZkguPersonSync.objects.filter(person_id=person_id).exists())