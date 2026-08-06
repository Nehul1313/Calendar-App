from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_superuser(sender, **kwargs):
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        print("Creating default superuser: admin/admin")
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')

class CalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cal'

    def ready(self):
        post_migrate.connect(create_superuser, sender=self)
