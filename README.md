# Local Services Platform

A robust, Flask-based platform designed to connect customers with local service providers (electricians, plumbers, etc.) in Embu County. The platform features real-time communication, proximity-based search, and a secure admin portal.

##  Features

-   **Provider Directory**: Browse and search for verified service providers.
-   **Proximity Sorting**: Automatically sorts providers based on their distance from the user (using Haversine formula).
-   **Service Requests**: Simple form for customers to request specific services.
-   **Real-time Chat**: Integrated SocketIO chat for instant communication between customers and admins regarding service requests.
-   **Admin Portal**: Secure dashboard to manage providers and track service request statuses (Pending, In Progress, Completed).
-   **Interactive Maps**: Mapbox integration for visualizing provider locations.
-   **Security**: Password hashing, secure session management, and rate limiting for security-sensitive routes.

## Tech Stack

-   **Backend**: Flask (Python)
-   **Database**: SQLAlchemy (SQLite for development, Postgres for production)
-   **Real-time**: Flask-SocketIO with Eventlet
-   **Frontend**: Vanilla HTML/CSS, JavaScript
-   **Maps**: Mapbox GL JS
