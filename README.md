# Meeting Room Booking System

A backend application for a small office to manage meeting room bookings, built with **FastAPI** and **fastapi-users** for robust authentication, and packaged for easy deployment with **Docker**.

## Features

### User Authentication
- **Login & Registration:** Secure authentication using fastapi-users.
- **Role-based Access:** Supports regular users and admins.

### Room Booking
- **View Rooms & Schedules:** See all available rooms and their booking schedules.
- **Book a Room:** Reserve rooms for a specific date and time (maximum 4 hours per booking).
- **Conflict Prevention:** No double-bookings allowed.
- **Manage Bookings:** Users can view and cancel their own bookings.

### Admin Controls
- **Room Management:** Admins can add or edit rooms.
- **User Management:** Admin can view,update and delete users
- **Booking Oversight:** Admins can view all bookings and cancel any booking.

## Tech Stack

- **Backend:** FastAPI (Python), fastapi-users (for authentication)
- **Containerization:** Docker (for deployment)
- **Testing:** Integration tests for API endpoints
- **Environment:** [uv](https://github.com/astral-sh/uv) for fast Python package management and execution

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) installed on your machine
- [Git](https://git-scm.com/)
- [uv](https://github.com/astral-sh/uv) installed for running and installing Python packages

### Clone the Repository

```bash
git clone https://github.com/arjun-mighty/MeetingRoom_BookingSystem.git
cd MeetingRoom_BookingSystem
```
### Running with uv
```bash
uv sync
uv run fastapi run
```
**OR**

### Running with Docker

Build and start the application using Docker:

```bash
docker build -t fastapi-backend:v1 .
docker run -p 8080:80 -v ./meeting.db:/room-booking/meeting.db fastapi-backend:v1
```

The FastAPI app will be available at [http://localhost:8080](http://localhost:8080).

### API Documentation

FastAPI provides interactive docs at:

- [Swagger UI](http://localhost:8080/docs)

### Running Tests

Integration tests for API endpoints are included. To run tests:

Make sure Pytest is installed

Then, run tests with pytest:
```bash
pytest -v tests/integration.py
```

## User Management

### Upgrading a User to Super User

To promote a user to super user (admin), run the following command:

```bash
python3 -m app.scripts.upgrade_user
```

Follow the prompts to specify the user to upgrade.

This command-line script is available in the `app/scripts` directory and is intended for administrators.

## Usage

- **Regular Users:** Register, log in, view rooms, book a meeting slot, and manage your own bookings.
- **Admins:** Log in with admin credentials to add/edit rooms and oversee all bookings.
