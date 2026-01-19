# Local Services Platform

A robust, Flask-based platform designed to connect customers with local service providers (electricians, plumbers, etc.) in Embu County. The platform features real-time communication, proximity-based search, and a secure admin portal.

## 🚀 Features

-   **Provider Directory**: Browse and search for verified service providers.
-   **Proximity Sorting**: Automatically sorts providers based on their distance from the user (using Haversine formula).
-   **Service Requests**: Simple form for customers to request specific services.
-   **Real-time Chat**: Integrated SocketIO chat for instant communication between customers and admins regarding service requests.
-   **Admin Portal**: Secure dashboard to manage providers and track service request statuses (Pending, In Progress, Completed).
-   **Interactive Maps**: Mapbox integration for visualizing provider locations.
-   **Security**: Password hashing, secure session management, and rate limiting for security-sensitive routes.

## 🛠️ Tech Stack

-   **Backend**: Flask (Python)
-   **Database**: SQLAlchemy (SQLite for development, Postgres for production)
-   **Real-time**: Flask-SocketIO with Eventlet
-   **Frontend**: Vanilla HTML/CSS, JavaScript
-   **Maps**: Mapbox GL JS
-   **Deployment**: Gunicorn, Render Blueprint (`render.yaml`)

## 💻 Local Setup

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd local_services
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment**:
    Create a `.env` file in the root directory and add:
    ```env
    SECRET_KEY=your-secret-key
    DATABASE_URL=sqlite:///app.db
    MAPBOX_ACCESS_TOKEN=your-mapbox-token
    ```

5.  **Initialize Database**:
    ```bash
    flask db upgrade
    # or run the app once to let run.py create_all()
    ```

6.  **Run the application**:
    ```bash
    python run.py
    ```
    Access the app at `http://127.0.0.1:5000`.

## 🌐 Deployment

This project is optimized for deployment on **Render.com** using the included `render.yaml` blueprint. 

1.  Connect your GitHub repository to Render.
2.  Choose "Blueprint" and select the repository.
3.  Provide your production `MAPBOX_ACCESS_TOKEN`.
4.  Render will automatically provision a Postgres database and scale the web service.

## 🔒 Security Note

-   The `/portal-secure-access` route is rate-limited to prevent brute-force attacks.
-   Ensure `SECRET_KEY` is changed to a secure value in production.
-   `DATABASE_URL` should point to a secure Postgres instance for production persistence.
