from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Event, Calendar
import json
import icalendar
from datetime import datetime, date
import pytz

@login_required
def calendar_view(request):
    # Ensure user has at least one calendar
    if not request.user.calendars.exists():
        Calendar.objects.create(name="My Calendar", user=request.user)
    
    calendars = request.user.calendars.all()
    selected_calendar_id = request.GET.get('calendar_id')
    
    if selected_calendar_id:
        selected_calendar = get_object_or_404(Calendar, id=selected_calendar_id, user=request.user)
    else:
        selected_calendar = calendars.first()

    events = Event.objects.filter(calendar=selected_calendar)
    events_list = [event.to_dict() for event in events]
    
    context = {
        'initial_events_json': json.dumps(events_list),
        'calendars': calendars,
        'selected_calendar': selected_calendar,
    }
    return render(request, 'cal/calendar.html', context)

@login_required
def create_calendar(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Calendar.objects.create(name=name, user=request.user)
            messages.success(request, f"Calendar '{name}' created successfully!")
    return redirect('calendar')

@login_required
def import_ics(request):
    if request.method == 'POST' and request.FILES.get('ics_file'):
        calendar_id = request.POST.get('calendar_id')
        cal_obj = get_object_or_404(Calendar, id=calendar_id, user=request.user)
        
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
        url = f"/?calendar_id={calendar_id}" if calendar_id else "/"
        return redirect(url)
    return redirect('calendar')

from django.http import HttpResponse

@login_required
def export_ics(request):
    calendar_id = request.GET.get('calendar_id')
    if calendar_id:
        selected_calendar = get_object_or_404(Calendar, id=calendar_id, user=request.user)
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
