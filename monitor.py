import json
import os
from datetime import datetime, timezone

LOG_FILE = "data/query_log.json"

def log_query(query, retrieval_time, generation_time, top_scores, file_id_sources, time_to_first_token=None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "retrieval_time_sec": round(retrieval_time, 3),
        "time_to_first_token_sec": round(time_to_first_token, 3) if time_to_first_token is not None else None,
        "generation_time_sec": round(generation_time, 3),
        "total_time_sec": round(retrieval_time + generation_time, 3),
        "top_scores": top_scores,
        "sources": file_id_sources
    }

    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)

    logs.append(entry)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)

    return entry