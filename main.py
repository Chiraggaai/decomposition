# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.plans import router as plans_router
from routes.plan_review import router as plan_review_router
from routes.tasks import router as task_router
from routes.checklist import router as checklist_router
from routes.summary import router as summary_router
from routes.task_details import router as task_detail_router
from routes.revision import router as revision_router
from routes.confirm import router as confirm_router
from routes.revised import router as revised_router
from routes.revision_details import router as revision_detail_router
from routes.lock import router as lock_router
from routes.action import router as actions_router





app = FastAPI(
    title="Glimmora — Enterprise Plan Review API",
    description=(
        "Plan status lifecycle:\n\n"
        "`PLAN_REVIEW_REQUIRED` → `REVISION_IN_PROGRESS` / `PLAN_CONFIRMED` → `PLAN_LOCKED`"
    ),
    version="1.0.0",
)

# ─────────────────────────────────────────────────────────────
# CORS
# Replace "*" with your frontend URL in production:
#   allow_origins=["https://your-frontend.com"]
# ─────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plans_router,)
app.include_router(plan_review_router) 
app.include_router(task_router, prefix="/plans", tags=["Tasks"])
app.include_router(checklist_router, prefix="/plans", tags=["Checklist"])
app.include_router(summary_router, prefix="/plans", tags=["Summary"])
app.include_router(task_detail_router, prefix="/plans", tags=["Task Detail"])
app.include_router(revision_router, prefix="/plans", tags=["Revision"])
app.include_router(confirm_router, prefix="/plans", tags=["Confirm"])
app.include_router(revised_router, prefix="/plans", tags=["Revised Plan"])
app.include_router(revision_detail_router, prefix="/plans", tags=["Revision Detail"])
app.include_router(lock_router, prefix="/plans", tags=["Plan Lock"])
app.include_router(actions_router)

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "api":    "Glimmora Enterprise Plan Review API",
        "docs":   "/docs",
        "endpoints": {
            "list_plans":       "GET  /plans",
            "get_plan":         "GET  /plans/{plan_id}",
            "get_plan_status":  "GET  /plans/{plan_id}/status",
            "confirm_plan":     "POST /plans/{plan_id}/confirm",
            "request_revision": "POST /plans/{plan_id}/request-revision",
            "lock_plan":        "POST /plans/{plan_id}/lock",
        },
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
