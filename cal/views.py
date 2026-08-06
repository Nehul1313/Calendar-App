from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Event, Calendar
import json
import icalendar
from datetime import datetime, date
import pytz

@login_required
def calendar_view(request):
    # Ensure user has at least one calendar
    if not request.user.calendars.exists():
        Calendar.objects.create(name=request.user.username, user=request.user, is_public=True)
    
    calendars = request.user.calendars.all()
    subscribed_calendars = request.user.subscribed_calendars.all()
    selected_calendar_uuid = request.GET.get('calendar_uuid')
    
    if selected_calendar_uuid:
        try:
            selected_calendar = Calendar.objects.get(uuid=selected_calendar_uuid, user=request.user)
        except Calendar.DoesNotExist:
            selected_calendar = get_object_or_404(Calendar, uuid=selected_calendar_uuid, subscribers=request.user)
    else:
        selected_calendar = calendars.first()

    events = Event.objects.filter(calendar=selected_calendar)
    events_list = [event.to_dict() for event in events]
    
    context = {
        'initial_events_json': json.dumps(events_list),
        'calendars': calendars,
        'subscribed_calendars': subscribed_calendars,
        'selected_calendar': selected_calendar,
    }
    return render(request, 'cal/calendar.html', context)

@login_required
def create_calendar(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Calendar.objects.create(name=name, user=request.user, is_public=True)
            messages.success(request, f"Calendar '{name}' created successfully!")
    return redirect('calendar')

@login_required
def import_ics(request):
    if request.method == 'POST' and request.FILES.get('ics_file'):
        calendar_uuid = request.POST.get('calendar_uuid')
        cal_obj = get_object_or_404(Calendar, uuid=calendar_uuid, user=request.user)
        
        ics_file = request.FILES['ics_file']
        cal = icalendar.Calendar.from_ical(ics_file.read())
        
        for component in cal.walk():
            if component.name == "VEVENT":
                title = component.get('summary')
                description = component.get('description')
                location = component.get('location')
                
                dtstart = component.get('dtstart')
                dtend = component.get('dtend')
                
                if not dtstart:
                    continue
                    
                start = dtstart.dt
                end = dtend.dt if dtend else start
                
                # Convert date to datetime if necessary
                if isinstance(start, date) and not isinstance(start, datetime):
                    start = datetime.combine(start, datetime.min.time())
                    start = pytz.utc.localize(start)
                if isinstance(end, date) and not isinstance(end, datetime):
                    end = datetime.combine(end, datetime.min.time())
                    end = pytz.utc.localize(end)
                    
                Event.objects.create(
                    calendar=cal_obj,
                    title=str(title) if title else "Untitled Event",
                    description=str(description) if description else "",
                    location=str(location) if location else "",
                    start_date=start,
                    end_date=end,
                    user=request.user
                )
    
        messages.success(request, "Calendar imported successfully!")
        url = f"/?calendar_uuid={calendar_uuid}" if calendar_uuid else "/"
        return redirect(url)
    return redirect('calendar')

from django.http import HttpResponse

@login_required
def export_ics(request):
    calendar_uuid = request.GET.get('calendar_uuid')
    if calendar_uuid:
        selected_calendar = get_object_or_404(Calendar, uuid=calendar_uuid, user=request.user)
    else:
        selected_calendar = request.user.calendars.first()
        
    if not selected_calendar:
        return redirect('calendar')
        
    events = Event.objects.filter(calendar=selected_calendar)
    
    cal = icalendar.Calendar()
    cal.add('prodid', '-//Calendar//')
    cal.add('version', '2.0')
    
    for event in events:
        ievent = icalendar.Event()
        ievent.add('summary', event.title)
        ievent.add('description', event.description)
        ievent.add('location', event.location)
        ievent.add('dtstart', event.start_date)
        ievent.add('dtend', event.end_date)
        cal.add_component(ievent)
        
    response = HttpResponse(cal.to_ical(), content_type="text/calendar")
    response['Content-Disposition'] = f'attachment; filename="{selected_calendar.name}.ics"'
    return response

@login_required
def rename_calendar(request, calendar_uuid):
    if request.method == 'POST':
        calendar = get_object_or_404(Calendar, uuid=calendar_uuid, user=request.user)
        new_name = request.POST.get('name')
        if new_name:
            calendar.name = new_name
            calendar.save()
            messages.success(request, f"Calendar renamed to '{new_name}'.")
    return redirect('calendar')

@login_required
def delete_calendar(request, calendar_uuid):
    if request.method == 'POST':
        calendar = get_object_or_404(Calendar, uuid=calendar_uuid, user=request.user)
        default_calendar = request.user.calendars.order_by('id').first()
        if calendar.uuid == default_calendar.uuid:
            messages.error(request, "The default calendar cannot be deleted.")
        else:
            calendar.delete()
            messages.success(request, "Calendar deleted successfully.")
    return redirect('calendar')

@login_required
def browse_calendars(request):
    query = request.GET.get('q', '')
    public_calendars = Calendar.objects.filter(is_public=True).exclude(user=request.user)
    if query:
        public_calendars = public_calendars.filter(
            Q(name__icontains=query) | Q(user__username__icontains=query)
        )
    else:
        public_calendars = public_calendars.order_by('id')[:5]
    context = {
        'calendars': public_calendars,
        'query': query,
        'subscribed_uuids': request.user.subscribed_calendars.values_list('uuid', flat=True)
    }
    return render(request, 'cal/browse_calendars.html', context)

@login_required
def subscribe_calendar(request, calendar_uuid):
    if request.method == 'POST':
        calendar = get_object_or_404(Calendar, uuid=calendar_uuid, is_public=True)
        calendar.subscribers.add(request.user)
        messages.success(request, f"Subscribed to {calendar.name}.")
        return redirect(request.META.get('HTTP_REFERER', 'browse_calendars'))
    return redirect('browse_calendars')

@login_required
def unsubscribe_calendar(request, calendar_uuid):
    if request.method == 'POST':
        calendar = get_object_or_404(Calendar, uuid=calendar_uuid, subscribers=request.user)
        calendar.subscribers.remove(request.user)
        messages.success(request, f"Unsubscribed from {calendar.name}.")
        
        # If user was viewing this calendar, redirect to their default
        return redirect('calendar')
    return redirect('calendar')

@login_required
def preview_calendar(request, calendar_uuid):
    calendar = get_object_or_404(Calendar, uuid=calendar_uuid, is_public=True)
    events = Event.objects.filter(calendar=calendar)
    events_list = [event.to_dict() for event in events]
    
    context = {
        'initial_events_json': json.dumps(events_list),
        'selected_calendar': calendar,
        'is_preview_mode': True,
        'subscribed_calendars': request.user.subscribed_calendars.all()
    }
    return render(request, 'cal/calendar.html', context)

@login_required
def calendar_settings(request):
    calendars = request.user.calendars.all()
    context = {
        'calendars': calendars
    }
    return render(request, 'cal/settings.html', context)

@login_required
def update_visibility(request, calendar_uuid):
    if request.method == 'POST':
        calendar = get_object_or_404(Calendar, uuid=calendar_uuid, user=request.user)
        is_public = request.POST.get('is_public') == 'true'
        calendar.is_public = is_public
        calendar.save()
        messages.success(request, f"'{calendar.name}' visibility updated.")
    return redirect('calendar_settings')
