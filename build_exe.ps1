Write-Host "Installing PyInstaller..."
Write-Host "Loading pip from .venv..."
.\venv\Scripts\pip install pyinstaller

Write-Host "Building Executable..."
Write-Host "Loading pyinstaller from .venv..."
.\venv\Scripts\pyinstaller --name "CalendarApp" `
    --onefile `
    --add-data "cal/templates;cal/templates" `
    --add-data "cal/static;cal/static" `
    --add-data "config;config" `
    --hidden-import "daphne" `
    --hidden-import "channels" `
    --hidden-import "cal" `
    --noconfirm `
    run_server.py

Write-Host "Build complete! Check the dist folder."
