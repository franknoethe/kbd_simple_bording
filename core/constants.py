MANAGEMENT_PATHS = {
    "/employees",
    "/templates",
    "/template-tasks",
    "/tasks",
    "/api/employees",
    "/api/employee-options",
    "/api/templates",
    "/api/template-tasks",
    "/api/template-tasks/options",
    "/api/task-options",
}
MASTER_DATA_PATHS = {
    "/locations",
    "/functions",
    "/jobs",
    "/roles",
    "/email-templates",
    "/process-types",
    "/api/locations",
    "/api/functions",
    "/api/jobs",
    "/api/roles",
    "/api/email-templates",
    "/api/process-types",
    "/api/job-options",
    "/api/templates/options",
}

TASK_STATUSES = {
    "open": "Offen",
    "in_progress": "In Bearbeitung",
    "completed": "Erledigt",
}

STATUS_LABELS = {
    "approved": "Genehmigt",
    "in_progress": "In Bearbeitung",
    "pending": "Ausstehend",
    "review": "In Prüfung",
}

# Legacy mock data, unused by any active route. Retained as-is for parity with the
# pre-refactor app.py (was never removed there either).
EMPLOYEES = [
    {
        "id": 1,
        "name": "Maya Schneider",
        "department": "IT",
        "role": "Junior Developer",
        "status": "in_progress",
        "progress": 72,
        "start_date": "2026-08-20",
        "location": "Berlin",
    },
    {
        "id": 2,
        "name": "Luca Meyer",
        "department": "HR",
        "role": "HR Specialist",
        "status": "approved",
        "progress": 100,
        "start_date": "2026-08-15",
        "location": "Hamburg",
    },
    {
        "id": 3,
        "name": "Nora Patel",
        "department": "Finance",
        "role": "Finance Analyst",
        "status": "pending",
        "progress": 36,
        "start_date": "2026-08-27",
        "location": "Munich",
    },
    {
        "id": 4,
        "name": "Felix Mueller",
        "department": "Operations",
        "role": "Operations Lead",
        "status": "review",
        "progress": 81,
        "start_date": "2026-09-02",
        "location": "Cologne",
    },
]


def compute_stats():
    total = len(EMPLOYEES)
    approved = sum(1 for item in EMPLOYEES if item["status"] == "approved")
    in_progress = sum(1 for item in EMPLOYEES if item["status"] == "in_progress")
    pending = sum(1 for item in EMPLOYEES if item["status"] == "pending")
    avg_progress = round(sum(item["progress"] for item in EMPLOYEES) / total, 1)
    return {
        "total": total,
        "approved": approved,
        "in_progress": in_progress,
        "pending": pending,
        "avg_progress": avg_progress,
    }
