# Collaborative Calendar App

A real-time, collaborative calendar application built with Django and Django Channels.

## Features

- **Multiple Calendars:** Create and manage multiple calendars for different purposes.
- **Public & Private Visibility:** Set your calendars to public to share them with others, or keep them private.
- **Browse & Subscribe:** Discover other users' public calendars, preview their events seamlessly, and subscribe to add them to your "Other Calendars" list.
- **Secure URLs:** Calendar URLs use cryptographically secure UUIDs (e.g., `/calendar/550e8400-e29b-41d4-a716-446655440000/`) preventing unguessable access.
- **Real-time Updates:** Seamless collaboration with real-time event updates across clients using WebSockets (Django Channels).
- **Event Management:** Add, edit, and organize events with properties like title, description, location, start/end times, and color-coding.
- **Import/Export:** Easily import and export calendar data using the standard `.ics` (iCalendar) format.
- **User Authentication:** Secure individual user accounts and data privacy.

## Tech Stack

- **Backend:** Python, Django
- **Real-time Communication:** Django Channels (WebSockets), Redis (typically used as the channel layer)
- **Database:** SQLite (default)
- **Frontend:** HTML, CSS, JavaScript (using libraries like FullCalendar for rendering)

## Setup and Installation

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Local Development Setup

1. **Clone the repository (if applicable)**
   ```bash
   git clone <repository-url>
   cd Calendar
   ```

2. **Set up a Virtual Environment**
   It's highly recommended to use a virtual environment to manage dependencies.
   
   If you encounter an execution policy error on Windows PowerShell when activating the virtual environment, you can set the execution policy for your current user:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
   
   Create and activate the virtual environment:
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure you have `django`, `channels`, `icalendar`, `python-dateutil`, `pytz` installed)*

4. **Apply Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

6. **Access the Application**
   Open your browser and navigate to `http://127.0.0.1:8000/`.

## Application Structure

- `cal/`: Main application directory handling models, views, and WebSocket consumers.
  - `models.py`: Defines the `Calendar` and `Event` data structures.
  - `views.py`: Handles HTTP requests for rendering the calendar, creating calendars, and ICS import/export.
  - `consumers.py`: Manages WebSocket connections for real-time event creation and updates.
- `config/`: Django project configuration directory containing settings, URLs, and ASGI/WSGI entry points.
