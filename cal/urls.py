from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('create_calendar/', views.create_calendar, name='create_calendar'),
    path('import_ics/', views.import_ics, name='import_ics'),
    path('export_ics/', views.export_ics, name='export_ics'),
    path('calendar/<uuid:calendar_uuid>/rename/', views.rename_calendar, name='rename_calendar'),
    path('calendar/<uuid:calendar_uuid>/delete/', views.delete_calendar, name='delete_calendar'),
    path('calendars/browse/', views.browse_calendars, name='browse_calendars'),
    path('calendar/<uuid:calendar_uuid>/preview/', views.preview_calendar, name='preview_calendar'),
    path('calendar/<uuid:calendar_uuid>/subscribe/', views.subscribe_calendar, name='subscribe_calendar'),
    path('calendar/<uuid:calendar_uuid>/unsubscribe/', views.unsubscribe_calendar, name='unsubscribe_calendar'),
    path('settings/', views.calendar_settings, name='calendar_settings'),
    path('calendar/<uuid:calendar_uuid>/visibility/', views.update_visibility, name='update_visibility'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('password_change/', PasswordChangeView.as_view(template_name='registration/password_change.html'), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
]
