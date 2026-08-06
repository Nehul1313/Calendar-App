import os
import sys
import webbrowser
from threading import Timer

def open_browser():
    # Wait a moment for the server to start before opening browser
    try:
        webbrowser.open_new("http://127.0.0.1:8000")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
        import django
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    django.setup()
    
    print("Running database migrations...")
    # Run migrations silently
    execute_from_command_line([sys.argv[0], 'migrate'])

    # Auto-create superuser if it doesn't exist
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not User.objects.filter(username='admin').exists():
        print("Creating default superuser: admin / admin")
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    
    # Launch browser after a short delay
    Timer(1.5, open_browser).start()
    
    # Run the Daphne ASGI server via Django runserver with --noreload
    # (noreload is required for PyInstaller frozen executables)
    print("Starting Django server at http://127.0.0.1:8000...")
    execute_from_command_line([sys.argv[0], 'runserver', '127.0.0.1:8000', '--noreload'])

if __name__ == '__main__':
    main()
