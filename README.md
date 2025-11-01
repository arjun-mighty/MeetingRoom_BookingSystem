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
- **Booking Oversight:** Admins can view all bookings and cancel any booking.

## Tech Stack

- **Backend:** FastAPI (Python), fastapi-users (for authentication)
- **Containerization:** Docker (for deployment)
- **Testing:** Integration tests for API endpoints

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) installed on your machine
- [Git](https://git-scm.com/)

### Clone the Repository

```bash
git clone https://github.com/arjun-mighty/MeetingRoom_BookingSystem.git
cd MeetingRoom_BookingSystem
```

### Running with Docker

Build and start the application using Docker Compose:

```bash
docker-compose up --build
```

The FastAPI app will be available at [http://localhost:8000](http://localhost:8000).

### API Documentation

FastAPI provides interactive docs at:

- [Swagger UI](http://localhost:8000/docs)
- [ReDoc](http://localhost:8000/redoc)

### Running Tests

Integration tests for API endpoints are included. To run tests:

```bash
docker-compose run backend pytest
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
- **Admins:** Log in with admin credentials to add
