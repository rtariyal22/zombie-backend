#  ZSSN - Zombie Survival Social Network (Backend API)

This is the backend implementation of the **Zombie Survival Social Network (ZSSN)** — a Django REST API that helps survivors of the zombie apocalypse register, share resources, and report infections in a secure, race-free system.

---

## Tech Stack

- Python
- Django
- PostgreSQL (optional)
- Poetry (dependency management)
- Docker

---

## Setup Instructions

### Clone and Install

```bash
git clone  https://github.com/rtariyal22/zombie-backend.git
cd zssn-backend

# Install dependencies
poetry install

# Activate virtualenv
poetry shell

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

## Build and run Docker container
```
docker build -t zssn-backend .
docker run -p 8000:8000 zssn-backend

# Or with Docker Compose:
docker-compose up --build
```

⸻

API Endpoints

The server runs locally at: http://localhost:8000/

All request bodies should be sent as JSON and include the Content-Type: application/json header. CSRF is currently disabled for ease of testing.

⸻

Register a New Survivor

POST /survivors/register/

Registers a new survivor along with their initial inventory.

Request Body

{
  "name": "Alice",
  "age": 30,
  "gender": "F",
  "latitude": 52.5200,
  "longitude": 13.4050,
  "inventory": [
    { "item": "Water", "quantity": 2 },
    { "item": "Food", "quantity": 5 }
  ]
}

Response

{
  "message": "Survivor registered",
  "id": 1
}

Errors
	•	400: Missing required field or invalid item in inventory.
	•	500: Unexpected server error.

⸻

Update Survivor Location

PATCH /survivors/<survivor_id>/location/

Updates the latitude and longitude of a survivor.

Request Body

{
  "latitude": 40.7128,
  "longitude": -74.0060
}

Response

{
  "message": "Location updated"
}

Errors
	•	404: Survivor not found.
	•	400: Missing latitude or longitude.
	•	500: Unexpected server error.

⸻

Report an Infected Survivor

POST /survivors/report/

Reports a survivor as infected. If a survivor receives 3 unique reports, they are marked as infected.

Request Body

{
  "reporter_id": 2,
  "infected_id": 1,
}

Response

{
  "message": "Report submitted"
}

Additional Behavior
	•	If the survivor is already reported by the same reporter:

{ "message": "You have already reported this survivor" }


	•	If a survivor reports themselves:

{ "error": "You cannot report yourself" }


	•	If the reporter is infected:

{ "error": "Infected survivors cannot report others" }



Errors
	•	404: Reporter or reported survivor not found.
	•	400: Missing or invalid reporter ID.
	•	403: Infected reporter attempted to report someone.
	•	500: Unexpected server error.

Trade Items Between Survivors

PATCH /resources/trade/

Allows two non-infected survivors to trade items. The trade must be fair in terms of item points and both survivors must have the items and quantities they are offering.

Request Body

{
  "survivor_a": 1,
  "survivor_b": 2,
  "items_a": [
    { "item": "Water", "quantity": 1 },
    { "item": "Food", "quantity": 2 }
  ],
  "items_b": [
    { "item": "Medication", "quantity": 1 }
  ]
}

Response

{
  "message": "Trade completed"
}

Rules & Behavior
	•	The trade must involve equal point value for both parties.
	•	Neither survivor can be infected.
	•	Each survivor must own the items and sufficient quantity they are offering.

Errors
	•	400: Invalid input or business rule violation. Example:

{ "errors": { "items_a": ["This field is required."] } }

or

{ "error": "Trade is unfair: point mismatch" }


	•	500: Unexpected server error.

⸻

# Running Tests
 - docker container exec -it zzsn_web pytest
