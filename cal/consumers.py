import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Event, Calendar
from dateutil import parser
from datetime import datetime
import pytz

class CalendarConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'calendar_updates'
        
        # Check authentication
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'create':
            event = await self.create_event(data)
            if event:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'calendar_update',
                        'action': 'create',
                        'event': event
                    }
                )
        elif action == 'update':
            event = await self.update_event(data)
            if event:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'calendar_update',
                        'action': 'update',
                        'event': event
                    }
                )
        elif action == 'delete':
            result = await self.delete_event(data)
            if result:
                if result['action'] == 'delete':
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'calendar_update',
                            'action': 'delete',
                            'event': {'id': result['event_id'], 'calendar_id': data.get('calendar_id')}
                        }
                    )
                else:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'calendar_update',
                            'action': 'update',
                            'event': result['event_dict']
                        }
                    )

    # Receive message from room group
    async def calendar_update(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'action': event['action'],
            'event': event['event']
        }))

    @database_sync_to_async
    def create_event(self, data):
        start = parser.isoparse(data['start'])
        end = parser.isoparse(data['end']) if data.get('end') else start
        
        calendar_id = data.get('calendar_id')
        try:
            calendar = Calendar.objects.get(uuid=calendar_id, user=self.scope["user"]) if calendar_id else None
        except Calendar.DoesNotExist:
            calendar = None

        event = Event.objects.create(
            calendar=calendar,
            title=data.get('title', 'Untitled'),
            description=data.get('description', ''),
            location=data.get('location', ''),
            start_date=start,
            end_date=end,
            color=data.get('color', '#039be5'),
            all_day=data.get('all_day', False),
            recurring_rule=data.get('recurring_rule', ''),
            user=self.scope["user"]
        )
        return event.to_dict()

    @database_sync_to_async
    def update_event(self, data):
        try:
            event = Event.objects.get(id=data['id'])
            # Ensure the user owns this event's calendar or created the event
            if event.user != self.scope["user"]:
                return None
            
            event.title = data.get('title', event.title)
            event.description = data.get('description', event.description)
            event.location = data.get('location', event.location)
            event.start_date = parser.isoparse(data['start'])
            event.end_date = parser.isoparse(data['end']) if data.get('end') else event.start_date
            
            if 'color' in data:
                event.color = data['color']
            if 'all_day' in data:
                event.all_day = data['all_day']
            if 'recurring_rule' in data:
                event.recurring_rule = data['recurring_rule']
            
            calendar_id = data.get('calendar_id')
            if calendar_id:
                try:
                    calendar = Calendar.objects.get(uuid=calendar_id, user=self.scope["user"])
                    event.calendar = calendar
                except Calendar.DoesNotExist:
                    pass

            event.save()
            return event.to_dict()
        except Event.DoesNotExist:
            return None

    @database_sync_to_async
    def delete_event(self, data):
        try:
            event = Event.objects.get(id=data['id'])
            if event.user != self.scope["user"]:
                return None
            
            delete_mode = data.get('delete_mode', 'all')
            if delete_mode == 'all' or not event.recurring_rule:
                event_id = event.id
                event.delete()
                return {'action': 'delete', 'event_id': event_id}
            
            occ_date_str = data.get('occurrence_date')
            if occ_date_str:
                occ_date = parser.isoparse(occ_date_str)
                if delete_mode == 'this':
                    exdates = []
                    if event.exception_dates:
                        exdates = event.exception_dates.split(',')
                    # Store as ISO string
                    date_iso = occ_date.isoformat()
                    if date_iso not in exdates:
                        exdates.append(date_iso)
                    event.exception_dates = ','.join(exdates)
                    event.save()
                    return {'action': 'update', 'event_dict': event.to_dict()}
                elif delete_mode == 'following':
                    event.recurrence_until = occ_date
                    event.save()
                    return {'action': 'update', 'event_dict': event.to_dict()}
                    
            return None
        except Event.DoesNotExist:
            return None
