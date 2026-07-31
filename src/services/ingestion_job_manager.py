"""
IntelAI Asynchronous Ingestion Job Manager.

Tracks non-blocking background ingestion jobs, progress percentages, processed files,
and errors for real-time frontend status polling.
"""

from __future__ import annotations

import uuid
import time
import threading
from typing import Dict, Any, Optional, List


class IngestionJobManager:
    _instance: Optional[IngestionJobManager] = None
    _lock = threading.Lock()

    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_instance(cls) -> IngestionJobManager:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def create_job(self, filename: str, category: str, file_type: str = "document") -> str:
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        now = time.time()
        with cls._lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "filename": filename,
                "category": category,
                "file_type": file_type,
                "status": "queued",  # queued | processing | completed | failed
                "progress_pct": 0,
                "current_step": "Queued in background worker pool",
                "processed_items": 0,
                "total_items": 1,
                "details": {},
                "error": None,
                "created_at": now,
                "updated_at": now,
                "completed_at": None,
            }
        return job_id

    def update_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        progress_pct: Optional[int] = None,
        current_step: Optional[str] = None,
        processed_items: Optional[int] = None,
        total_items: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        with cls._lock:
            if job_id not in self._jobs:
                return
            job = self._jobs[job_id]
            now = time.time()
            if status is not None:
                job["status"] = status
                if status in ("completed", "failed"):
                    job["completed_at"] = now
            if progress_pct is not None:
                job["progress_pct"] = max(0, min(100, progress_pct))
            if current_step is not None:
                job["current_step"] = current_step
            if processed_items is not None:
                job["processed_items"] = processed_items
            if total_items is not None:
                job["total_items"] = total_items
            if details is not None:
                job["details"].update(details)
            if error is not None:
                job["error"] = error
            job["updated_at"] = now

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        with cls._lock:
            job = self._jobs.get(job_id)
            return dict(job) if job else None

    def list_active_jobs(self) -> List[Dict[str, Any]]:
        with cls._lock:
            return [dict(j) for j in self._jobs.values() if j["status"] in ("queued", "processing")]


def get_job_manager() -> IngestionJobManager:
    return IngestionJobManager.get_instance()
