from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('create_calendar/', views.create_calendar, name='create_calendar'),
    path('import_ics/', views.import_ics, name='import_ics'),
    path('export_ics/', views.export_ics, name='export_ics'),
    path('calendar/<int:calendar_id>/rename/', views.rename_calendar, name='rename_calendar'),
    path('calendar/<int:calendar_id>/delete/', views.delete_calendar, name='delete_calendar'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]
