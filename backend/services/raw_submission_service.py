from datetime import datetime, timezone
import uuid


def build_raw_submission(data: dict) -> dict:
    """
    Wraps raw farmer input for private storage.
    This document is stored in the private raw_submissions collection
    and is NEVER exposed via the public /cases endpoint.
    """
    return {
        "submission_id": f"RS-{uuid.uuid4().hex[:8]}",
        "input":          data,
        "submitted_at":   datetime.now(timezone.utc).isoformat(),
        "privacy_level":  "private"
    }
