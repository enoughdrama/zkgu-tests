import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import logging

logger = logging.getLogger(__name__)

class PersonUpdatesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'person_updates'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connected: {self.channel_name}")
        
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to person updates'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected: {self.channel_name}, code: {close_code}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            logger.info(f"WebSocket received: {data}")
            
            if data.get('type') == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")

    async def person_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'person_update',
            'action': event['action'],
            'data': event['data'],
            'timestamp': event['timestamp']
        }))

    async def person_created(self, event):
        await self.send(text_data=json.dumps({
            'type': 'person_created',
            'data': event['data'],
            'timestamp': event['timestamp']
        }))

    async def person_updated(self, event):
        await self.send(text_data=json.dumps({
            'type': 'person_updated',
            'data': event['data'],
            'timestamp': event['timestamp']
        }))

    async def person_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'person_deleted',
            'data': event['data'],
            'timestamp': event['timestamp']
        }))