# backfill_status.py
import json
import os

CLEAN_FOLDER = "data/clean_text"
STATUS_FILE = "data/document_status.json"

categories = {
    "harassment_act": "women", "anti_rape_act": "women",
    "child_labor_act": "children", "child_marriage_act": "children",
    "employment_ordinance": "employees",
    "minorities_commission_act": "minorities",
    "ppc_1860": "defamation", "peca_2016": "defamation",
    "hec_harassment_policy": "students"
}

status = {}
for filename in os.listdir(CLEAN_FOLDER):
    file_id = filename.replace(".txt", "")
    status[file_id] = {"status": "active", "category": categories.get(file_id, "uncategorized")}

with open(STATUS_FILE, "w", encoding="utf-8") as f:
    json.dump(status, f, indent=2)

print("Backfilled status for existing documents.")