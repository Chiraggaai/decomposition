# Glimmora — Enterprise Plan Review API

## Run

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

Docs: http://127.0.0.1:8000/docs

---

## Endpoints

| Method | Endpoint                          | Description                                      |
|--------|-----------------------------------|--------------------------------------------------|
| GET    | /plans                            | List all plans (dashboard sidebar)               |
| GET    | /plans/{plan_id}                  | Fetch full plan for dashboard card               |
| GET    | /plans/{plan_id}/status           | Lightweight status poll (use during revision)    |
| POST   | /plans/{plan_id}/confirm          | Enterprise confirms the plan                     |
| POST   | /plans/{plan_id}/request-revision | Enterprise requests a revision                   |
| POST   | /plans/{plan_id}/lock             | Lock plan when first contributor accepts         |

---

## Status Flow

```
[Kick-off]
    │
    ▼
PLAN_REVIEW_REQUIRED ──► REVISION_IN_PROGRESS
    │                           │
    │          AGI re-generates (15–60 min)
    │◄──────────────────────────┘
    │
    │ enterprise confirms
    ▼
PLAN_CONFIRMED
    │
    │ first contributor accepts offer
    ▼
PLAN_LOCKED — Delivery Started
```

---

## Project Structure

```
glimmora_plan_api/
├── main.py              ← App entry point
├── models.py            ← Pydantic request / response models
├── database.py          ← DB connection (plug your DB here)
├── routes/
│   └── plans.py         ← All /plans endpoints
├── requirements.txt
├── .env.example
└── README.md
```
