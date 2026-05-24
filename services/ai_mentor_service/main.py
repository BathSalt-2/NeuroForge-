"""
NeuroForge — AI Mentor Service
Powers the AI learning assistant with LLM integration, Knowledge Graph context,
and conversation management.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel

# ── Config ───────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
KG_URL = os.getenv("KNOWLEDGE_GRAPH_SERVICE_URL", "http://localhost:8002")
PROFILING_URL = os.getenv("COGNITIVE_PROFILING_SERVICE_URL", "http://localhost:8004")

app = FastAPI(title="NeuroForge AI Mentor Service", version="0.1.0")
llm_client: Optional[AsyncOpenAI] = None
http: Optional[httpx.AsyncClient] = None

# In-memory conversation store (PoC — replace with DB in production)
conversations: dict[str, list[dict]] = {}

# ── Persona definitions ──────────────────────────────────────
PERSONAS = {
    "socratic": (
        "You are the NeuroForge AI Mentor adopting the persona of a Socratic Questioner. "
        "Guide the learner by asking probing questions that lead them to discover answers "
        "on their own. Be patient and encouraging while challenging their thinking."
    ),
    "coach": (
        "You are the NeuroForge AI Mentor adopting the persona of an Encouraging Coach. "
        "Provide positive reinforcement, celebrate progress, and motivate the learner. "
        "Break complex topics into manageable steps and offer plenty of encouragement."
    ),
    "expert": (
        "You are the NeuroForge AI Mentor adopting the persona of a Direct Expert. "
        "Provide clear, concise, and accurate information. Use precise technical language "
        "when appropriate and give straight-to-the-point answers with examples."
    ),
    "default": (
        "You are the NeuroForge AI Mentor — a knowledgeable, friendly, and adaptive "
        "learning companion. Explain concepts clearly, use examples and analogies, "
        "and tailor your language to the learner's level. When referencing NeuroForge "
        "Knowledge Graph data, cite it naturally."
    ),
}


# ── Models ───────────────────────────────────────────────────
class QueryRequest(BaseModel):
    userId: str
    text: str
    context: Optional[dict] = None
    conversationId: Optional[str] = None
    persona: Optional[str] = None  # socratic | coach | expert


class MentorResponse(BaseModel):
    responseId: str
    conversationId: str
    userId: str
    responseText: str
    suggestedActions: list[dict]
    timestamp: str


# ── Lifecycle ────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    global llm_client, http
    llm_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    http = httpx.AsyncClient(timeout=30.0)


@app.on_event("shutdown")
async def shutdown():
    if http:
        await http.aclose()


# ── Helpers ──────────────────────────────────────────────────
async def _fetch_concept_by_name(name: str) -> Optional[dict]:
    """Search KG for a concept by name."""
    try:
        resp = await http.get(f"{KG_URL}/concepts", params={"name": name, "limit": 1})
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            return data[0] if data else None
    except Exception:
        return None


async def _fetch_concept_by_id(concept_id: str) -> Optional[dict]:
    """Fetch concept by ID from KG."""
    try:
        resp = await http.get(f"{KG_URL}/concepts/{concept_id}")
        return resp.json() if resp.status_code == 200 else None
    except Exception:
        return None


async def _fetch_modules_for_concept(concept_id: str) -> list[dict]:
    """Fetch content modules related to a concept."""
    try:
        resp = await http.get(f"{KG_URL}/concepts/{concept_id}/modules")
        return resp.json() if resp.status_code == 200 else []
    except Exception:
        return []


async def _fetch_related_concepts(concept_id: str) -> list[dict]:
    """Fetch related concepts from KG."""
    try:
        resp = await http.get(f"{KG_URL}/concepts/{concept_id}/related")
        return resp.json() if resp.status_code == 200 else []
    except Exception:
        return []


async def _fetch_prerequisites(concept_id: str) -> list[dict]:
    """Fetch prerequisite concepts."""
    try:
        resp = await http.get(f"{KG_URL}/concepts/{concept_id}/prerequisites")
        return resp.json() if resp.status_code == 200 else []
    except Exception:
        return []


async def _log_interaction(user_id: str, event_type: str, details: dict):
    """Send interaction event to Cognitive Profiling Service."""
    try:
        await http.post(f"{PROFILING_URL}/profiling/interactions", json={
            "eventId": f"event_{uuid.uuid4().hex[:12]}",
            "userId": user_id,
            "targetId": details.get("conceptId", "ai_mentor"),
            "targetType": "AIMentor",
            "eventType": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details,
        })
    except Exception:
        pass  # Non-critical for PoC


def _build_kg_context(concept: dict, modules: list, related: list, prerequisites: list) -> str:
    """Build a knowledge graph context string for the LLM prompt."""
    parts = []
    parts.append(f"=== Knowledge Graph Context ===")
    parts.append(f"Concept: {concept['name']}")
    parts.append(f"Description: {concept.get('description', 'N/A')}")
    parts.append(f"Difficulty: {concept.get('difficultyLevel', 'N/A')}")
    parts.append(f"Domain: {concept.get('domain', 'N/A')} > {concept.get('subDomain', 'N/A')}")

    if prerequisites:
        names = ", ".join(p["name"] for p in prerequisites)
        parts.append(f"Prerequisites: {names}")

    if related:
        names = ", ".join(r["name"] for r in related)
        parts.append(f"Related Concepts: {names}")

    if modules:
        parts.append("Available Learning Modules:")
        for m in modules:
            parts.append(f"  - [{m['type']}] {m['title']} ({m.get('estimatedDurationMinutes', '?')} min, {m.get('difficultyLevel', '?')})")

    return "\n".join(parts)


# ── Endpoints ────────────────────────────────────────────────
@app.post("/mentor/query", response_model=MentorResponse)
async def submit_query(req: QueryRequest):
    if not llm_client:
        raise HTTPException(503, "LLM not configured — set OPENAI_API_KEY")

    conv_id = req.conversationId or f"conv_{uuid.uuid4().hex[:12]}"
    if conv_id not in conversations:
        conversations[conv_id] = []

    # Log the interaction
    await _log_interaction(req.userId, "ASK_CONCEPT", {
        "query": req.text,
        "conversationId": conv_id,
    })

    # ── Try to find a relevant concept from the query ──
    kg_context = ""
    concept = None
    modules = []

    # Check if context provides a conceptId
    if req.context and req.context.get("currentConceptId"):
        concept = await _fetch_concept_by_id(req.context["currentConceptId"])

    # Try to find concept from query text via search
    if not concept:
        # Extract potential concept names — simple heuristic for PoC
        query_lower = req.text.lower()
        # Search KG for any matching concept
        try:
            resp = await http.get(f"{KG_URL}/concepts", params={"limit": 50})
            if resp.status_code == 200:
                all_concepts = resp.json().get("data", [])
                for c in all_concepts:
                    if c["name"].lower() in query_lower or any(
                        kw.lower() in query_lower for kw in c.get("keywords", [])
                    ):
                        concept = c
                        break
        except Exception:
            pass

    # Build KG context if concept found
    suggested_actions = []
    if concept:
        cid = concept["conceptId"]
        modules = await _fetch_modules_for_concept(cid)
        related = await _fetch_related_concepts(cid)
        prerequisites = await _fetch_prerequisites(cid)
        kg_context = _build_kg_context(concept, modules, related, prerequisites)

        # Build suggested actions
        for m in modules[:3]:
            suggested_actions.append({
                "type": "VIEW_MODULE",
                "label": f"View: {m['title']}",
                "moduleId": m["moduleId"],
            })
        for r in related[:2]:
            suggested_actions.append({
                "type": "VIEW_CONCEPT",
                "label": f"Explore: {r['name']}",
                "conceptId": r["conceptId"],
            })

    # ── Build LLM prompt ──
    persona_key = (req.persona or "default").lower()
    system_prompt = PERSONAS.get(persona_key, PERSONAS["default"])

    if kg_context:
        system_prompt += f"\n\nUse the following Knowledge Graph data to inform your response:\n{kg_context}"

    # Include conversation history (last 10 messages)
    history = conversations[conv_id][-10:]
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": req.text})

    # ── Call LLM ──
    try:
        completion = await llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        response_text = completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(502, f"LLM call failed: {str(e)}")

    # Store in conversation history
    conversations[conv_id].append({"role": "user", "content": req.text})
    conversations[conv_id].append({"role": "assistant", "content": response_text})

    # Log the response
    await _log_interaction(req.userId, "MENTOR_RESPONSE", {
        "conversationId": conv_id,
        "conceptId": concept["conceptId"] if concept else None,
        "modulesReturned": len(modules),
    })

    now = datetime.now(timezone.utc).isoformat()
    return MentorResponse(
        responseId=f"resp_{uuid.uuid4().hex[:12]}",
        conversationId=conv_id,
        userId=req.userId,
        responseText=response_text,
        suggestedActions=suggested_actions,
        timestamp=now,
    )


@app.get("/mentor/history/{user_id}")
async def get_history(user_id: str, conversationId: Optional[str] = None, limit: int = 20):
    """Retrieve conversation history (PoC: all conversations are accessible)."""
    if conversationId:
        history = conversations.get(conversationId, [])
        return {
            "userId": user_id,
            "conversations": [{
                "conversationId": conversationId,
                "messages": history[-limit:],
            }],
        }
    # Return all conversations (PoC simplification)
    all_convos = []
    for cid, messages in conversations.items():
        all_convos.append({
            "conversationId": cid,
            "messages": messages[-limit:],
        })
    return {"userId": user_id, "conversations": all_convos}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ai_mentor_service",
        "llm_configured": bool(OPENAI_API_KEY),
    }
