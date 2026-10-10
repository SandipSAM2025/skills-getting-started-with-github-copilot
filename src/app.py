"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },

    # Sports-related activities
    "Soccer Team": {
        "description": "Competitive soccer team practicing and playing matches",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Pickup games, skills training, and interschool tournaments",
        "schedule": "Tuesdays and Thursdays, 5:00 PM - 6:30 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "isabella@mergington.edu"]
    },

    # Artistic activities
    "Art Club": {
        "description": "Explore painting, drawing, and mixed media projects",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["mia@mergington.edu"]
    },
    "Drama Club": {
        "description": "Acting workshops and school theater productions",
        "schedule": "Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 25,
        "participants": ["lucas@mergington.edu"]
    },

    # Intellectual activities
    "Debate Club": {
        "description": "Public speaking, argumentation, and competitive debate",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["oliver@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Hands-on STEM challenges and competition preparation",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["charlotte@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Normalize email
    email_clean = email.strip().lower()

    # Validate student is not already signed up
    if any(p.strip().lower() == email_clean for p in activity.get("participants", [])):
        raise HTTPException(status_code=409, detail="Student already registered for activity")

    # Validate capacity
    if len(activity.get("participants", [])) >= activity.get("max_participants", 0):
        raise HTTPException(status_code=400, detail="Activity is full")

    # Add student
    activity.setdefault("participants", []).append(email_clean)
    return {"message": f"Signed up {email_clean} for {activity_name}"}


@app.delete("/activities/{activity_name}/participants")
def remove_participant(activity_name: str, email: str):
    """Unregister a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    email_clean = email.strip().lower()
    participants = activity.get("participants", [])

    for participant in participants:
        if participant.strip().lower() == email_clean:
            participants.remove(participant)
            return {"message": f"Unregistered {email_clean} from {activity_name}"}

    raise HTTPException(status_code=404, detail="Participant not found")