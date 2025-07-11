import json
import asyncio
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def send_person_update(action, person_data):
    """
    Отправить обновление персоны через WebSocket всем подключенным клиентам
    
    Args:
        action (str): 'created', 'updated', 'deleted'
        person_data (dict): Данные персоны
    """
    try:
        channel_layer = get_channel_layer()
        
        if not channel_layer:
            logger.warning("Channel layer not configured")
            return
        
        message = {
            'type': f'person_{action}',
            'action': action,
            'data': person_data,
            'timestamp': timezone.now().isoformat()
        }
        
        async_to_sync(channel_layer.group_send)(
            'person_updates',
            message
        )
        
        logger.info(f"WebSocket notification sent: {action} for person {person_data.get('ID_REC', 'unknown')}")
        
    except Exception as e:
        logger.error(f"Failed to send WebSocket notification: {e}")

def send_person_created(person_data):
    send_person_update('created', person_data)

def send_person_updated(person_data):
    send_person_update('updated', person_data)

def send_person_deleted(person_data):
    send_person_update('deleted', person_data)