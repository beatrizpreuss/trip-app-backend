# ✈️ WanderWise — Travel Organizer App

WanderWise is a full-stack travel planner that lets users organize trips,
visualize locations on an interactive map, and receive AI-powered suggestions
for destinations and points of interest.

This repository contains the **backend** portion of the project.
🔗 **Frontend Repo:** [https://github.com/beatrizpreuss/trip-app-frontend]

---

## ⚙️ Backend Overview

The backend provides:
- REST API endpoints for trips, locations, and user data
- JWT-based authentication
- SQLite database powered by SQLAlchemy ORM
- AI-powered suggestions using OpenAI API
- Points of interest retrieval using Overpass API

---

## 🏗️ Tech Stack

- **Python**
- **Flask**
- **SQLite**
- **SQLAlchemy ORM**
- **OpenAI API** (AI suggestions)
- **Overpass API** (POI data)
- **JWT** (authentication)

---

## 📂 Backend Purpose

This repo includes:
- Database models and migrations
- Authentication and authorization logic
- API routes for all trip-related operations
- AI and POI integration services

---

## ⚙️ Installation & Local Setup

Follow these steps to run the backend locally.

1️⃣ Prerequisites

Make sure you have installed:

- Python 3.10+
- pip (Python package manager)
- (Optional) virtualenv or venv for isolated environments

2️⃣ Clone the Repository
```
git clone https://github.com/beatrizpreuss/trip-app-backend.git
cd trip-app-backend
```
3️⃣ Create and Activate a Virtual Environment (Recommended)
```
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\\Scripts\\activate     # Windows
```
4️⃣ Install Dependencies
```
pip install -r requirements.txt
```
5️⃣ Environment Variables

- Create a .env file in the root of the project and add the following:
```
OPENAI_API_KEY=your_openai_api_key
```
⚠️ Never commit your .env file to version control.

6️⃣ Initialize the Database (First Run Only)
- The database tables are created manually on the first run.
- In main.py, temporarily uncomment the following lines:
```
with app.app_context():
    db.create_all()
```
Then run:
```
flask run
```
Once the database has been created, comment these lines again to avoid recreating tables.

7️⃣ Run the Development Server
```
flask run
```
The API will be available at:
```
http://localhost:5000
```

---

## 🔐 Authentication Notes

- JWTs are generated and validated only on the backend
- Tokens are sent by the frontend via the Authorization: Bearer <token> header
- JWT secrets remain private and are never exposed to the frontend

---

## 📌 Notes

- This repository does not include frontend UI code
- The frontend must be running to fully use the application
- This backend is intended for local development and learning purposes

✨ Built as part of a full-stack project to practice API design, authentication, and AI integration.