from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from unittest.mock import patch
from zkgu_persons.models import ZkguPerson, APIToken
from zkgu_persons.authentication import generate_api_token

class IntegrationTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='integration_user',
            password='integration_pass'
        )
        self.token = generate_api_token(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    @patch('zkgu_persons.rabbitmq_publisher.publish_person_event')
    def test_complete_person_lifecycle(self, mock_publish):
        person_data = {
            'ID_REC': 'LIFECYCLE001',
            'LASTNAME': 'Жизненциклов',
            'FIRSTNAME': 'Полный',
            'MIDNAME': 'Интеграционович'
        }
        
        response = self.client.post('/api/v1/persons/', person_data)
        self.assertEqual(response.status_code, 201)
        
        person = ZkguPerson.objects.get(ID_REC='LIFECYCLE001')
        self.assertEqual(person.LASTNAME, 'Жизненциклов')
        
        update_data = {'LASTNAME': 'Обновленциклов'}
        response = self.client.patch(f'/api/v1/persons/{person.ID_REC}/', update_data)
        self.assertEqual(response.status_code, 200)
        
        person.refresh_from_db()
        self.assertEqual(person.LASTNAME, 'Обновленциклов')
        
        response = self.client.delete(f'/api/v1/persons/{person.ID_REC}/')
        self.assertEqual(response.status_code, 204)
        
        self.assertFalse(ZkguPerson.objects.filter(ID_REC='LIFECYCLE001').exists())

    def test_authentication_workflow(self):
        api_token = APIToken.objects.get(user=self.user)
        
        response = self.client.get('/api/v1/persons/')
        self.assertEqual(response.status_code, 200)
        
        api_token.is_active = False
        api_token.save()
        
        response = self.client.get('/api/v1/persons/')
        self.assertEqual(response.status_code, 401)
        
        api_token.is_active = True
        api_token.save()
        
        response = self.client.get('/api/v1/persons/')
        self.assertEqual(response.status_code, 200)

class DatabaseIntegrityTest(TestCase):
    def test_unique_constraints(self):
        ZkguPerson.objects.create(ID_REC='UNIQUE001', LASTNAME='Уникальный')
        
        with self.assertRaises(Exception):
            ZkguPerson.objects.create(ID_REC='UNIQUE001', LASTNAME='Дублирующий')

    def test_index_performance(self):
        for i in range(50):
            ZkguPerson.objects.create(
                ID_REC=f'PERF{i:03d}',
                LASTNAME=f'Производительный{i}'
            )
        
        import time
        start_time = time.time()
        
        person = ZkguPerson.objects.get(ID_REC='PERF025')
        
        end_time = time.time()
        query_time = end_time - start_time
        
        self.assertLess(query_time, 0.1)
        self.assertEqual(person.LASTNAME, 'Производительный25')