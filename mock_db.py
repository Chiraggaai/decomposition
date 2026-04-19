# mock_db.py
"""
Loads test data from db/mock_db.json at startup and exposes pre-seeded
stores for every route (action_store, edit_store, wizard_store).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

_path = Path(__file__).parent / "db" / "mock_db.json"
with _path.open(encoding="utf-8") as _f:
    _DB: dict = json.load(_f)

action_store: dict[str, dict] = copy.deepcopy(_DB["_test_plans_actions"])
edit_store:   dict[str, dict] = copy.deepcopy(_DB["_test_plan_edits"])
wizard_store: dict[str, dict] = copy.deepcopy(_DB["_test_wizards"])
