"""
NeuroForge — Cognitive Profiling Service (PoC Mock)
Accepts interaction events and provides mock cognitive profile summaries.
In production this would run PyTorch models for behavioral heatmapping
and predictive learning trajectories.
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="NeuroForge Cognitive Profiling Service", version="0.1.0")

# In-memory interaction store (PoC)
interactions: dict[str, list[dict]] = defaultdict(list)


# ── Models ───────────────────────────────────────────────────
class InteractionEvent(BaseModel):
    eventId: Optional[str] = None
    userId: str
    targetId: Optional[str] = None
    targetType: Optional[str] = None
    eventType: str
    timestamp: Optional[str] = None
    durationSeconds: Optional[int] = None
    details: Optional[dict] = None


# ── Endpoints ────────────────────────────────────────────────
@app.post("/profiling/interactions", status_code=202)
async def submit_interaction(event: InteractionEvent):
    """Accept and log an interaction event for future profiling."""
    eid = event.eventId or f"event_{uuid.uuid4().hex[:12]}"
    ts = event.timestamp or datetime.now(timezone.utc).isoformat()

    record = {
        "eventId": eid,
        "userId": event.userId,
        "targetId": event.targetId,
        "targetType": event.targetType,
        "eventType": event.eventType,
        "timestamp": ts,
        "durationSeconds": event.durationSeconds,
        "details": event.details or {},
    }
    interactions[event.userId].append(record)

    return {"message": "Interaction event accepted for processing.", "eventId": eid}


@app.get("/profiling/users/{user_id}/summary")
async def get_profile_summary(user_id: str):
    """Return a mock cognitive profile summary based on logged interactions."""
    user_events = interactions.get(user_id, [])
    event_count = len(user_events)

    # Mock profile — in production this would come from PyTorch models
    event_types = defaultdict(int)
    for e in user_events:
        event_types[e["eventType"]] += 1

    return {
        "userId": user_id,
        "summary": {
            "dominantLearningStyles": ["Visual", "Reading/Writing"],
            "strengths": ["Pattern Recognition", "Conceptual Understanding"],
            "areasForDevelopment": ["Hands-on Practice", "Timed Assessments"],
            "engagementMetrics": {
                "totalInteractions": event_count,
                "eventBreakdown": dict(event_types),
                "preferredContentTypes": ["VIDEO", "ARTICLE"],
                "averageSessionDurationMinutes": 35,
            },
            "lastUpdated": datetime.now(timezone.utc).isoformat(),
        },
    }


@app.get("/profiling/users/{user_id}/heatmap")
async def get_heatmap(
    user_id: str,
    topic: Optional[str] = None,
    dataType: Optional[str] = None,
):
    """Return mock behavioral heatmap data."""
    user_events = interactions.get(user_id, [])

    # Aggregate concept interactions for mock heatmap
    concept_scores = defaultdict(lambda: {"engagement": 0.0, "count": 0})
    for e in user_events:
        tid = e.get("targetId", "unknown")
        concept_scores[tid]["count"] += 1
        concept_scores[tid]["engagement"] = min(
            1.0, concept_scores[tid]["count"] * 0.15
        )

    heatmap_data = [
        {"topicId": tid, "engagementScore": round(info["engagement"], 2)}
        for tid, info in concept_scores.items()
        if tid != "unknown"
    ]

    # Add some defaults if no data yet
    if not heatmap_data:
        heatmap_data = [
            {"topicId": "concept_machine_learning", "engagementScore": 0.0},
            {"topicId": "concept_neural_networks", "engagementScore": 0.0},
            {"topicId": "concept_python_basics", "engagementScore": 0.0},
        ]

    return {
        "userId": user_id,
        "heatmapType": dataType or "engagement_by_topic",
        "data": heatmap_data,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/profiling/users/{user_id}/interactions")
async def get_interactions(user_id: str, limit: int = 50):
    """Return raw interaction log for a user."""
    user_events = interactions.get(user_id, [])
    return {
        "userId": user_id,
        "total": len(user_events),
        "events": user_events[-limit:],
    }


@app.get("/health")
async def health():
    total_events = sum(len(v) for v in interactions.values())
    return {
        "status": "healthy",
        "service": "cognitive_profiling_service",
        "note": "PoC mock — no PyTorch models running",
        "totalEventsLogged": total_events,
    }
