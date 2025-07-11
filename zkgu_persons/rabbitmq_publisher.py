import pika
import json
import logging
from django.conf import settings
from django.utils import timezone
from typing import Union, Dict, Any

logger = logging.getLogger(__name__)

class RabbitMQPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None
        
    def connect(self):
        try:
            credentials = pika.PlainCredentials(
                getattr(settings, 'RABBITMQ_USER', 'guest'),
                getattr(settings, 'RABBITMQ_PASSWORD', 'guest')
            )
            parameters = pika.ConnectionParameters(
                host=getattr(settings, 'RABBITMQ_HOST', 'localhost'),
                port=getattr(settings, 'RABBITMQ_PORT', 5672),
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            self.channel.exchange_declare(
                exchange='zkgu_events',
                exchange_type='topic',
                durable=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    def publish(self, routing_key: str, message: Dict[Any, Any]):
        if not self.connection or self.connection.is_closed:
            if not self.connect():
                return False
                
        try:
            self.channel.basic_publish(
                exchange='zkgu_events',
                routing_key=routing_key,
                body=json.dumps(message, ensure_ascii=False, default=str),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            return True
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return False
    
    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

publisher = RabbitMQPublisher()

def publish_person_event(action: str, person_data: Union[object, dict]):
    try:
        from django.conf import settings
        
        if not getattr(settings, 'RABBITMQ_ENABLED', True):
            logger.info(f"RabbitMQ disabled, skipping event: {action}")
            return
            
        if hasattr(person_data, '__dict__'):
            from .serializers import ZkguPersonSerializer
            data = ZkguPersonSerializer(person_data).data
        else:
            data = person_data
            
        message = {
            'action': action,
            'data': data,
            'timestamp': str(timezone.now())
        }
        
        routing_key = f'person.{action}'
        result = publisher.publish(routing_key, message)
        logger.info(f"Published event {action}: {result}")
        
    except Exception as e:
        logger.error(f"Failed to publish person event: {e}")