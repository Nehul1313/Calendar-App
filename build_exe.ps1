Write-Host "Installing PyInstaller..."
.\venv\Scripts\pip install pyinstaller

Write-Host "Building Executable..."
.\venv\Scripts\pyinstaller --name "CalendarApp" `
    --onefile `
    --add-data "cal/templates;cal/templates" `
    --add-data "config;config" `
    --hidden-import "daphne" `
    --hidden-import "channels" `
    --hidden-import "cal" `
    --noconfirm `
    run_server.py

Write-Host "Build complete! Check the dist folder."
