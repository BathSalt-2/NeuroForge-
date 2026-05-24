"""
NeuroForge — Learning Pathway Service
Manages creation, retrieval, enrollment, and progress tracking for learning paths.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

import asyncpg
import httpx
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

# ── Config ───────────────────────────────────────────────────
PG = dict(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    user=os.getenv("POSTGRES_USER", "neuroforge"),
    password=os.getenv("POSTGRES_PASSWORD", "neuroforge_secret"),
    database=os.getenv("POSTGRES_DB", "neuroforge"),
)
KG_URL = os.getenv("KNOWLEDGE_GRAPH_SERVICE_URL", "http://localhost:8002")

app = FastAPI(title="NeuroForge Learning Pathway Service", version="0.1.0")
pool = None
http = None


# ── Models ───────────────────────────────────────────────────
class ModuleInPath(BaseModel):
    moduleId: str
    order: int
    isOptional: bool = False


class CreatePathRequest(BaseModel):
    name: str
    description: str
    targetAudience: Optional[str] = None
    moduleSequence: list[ModuleInPath]
    conceptsTargeted: Optional[list[str]] = None
    skillsDeveloped: Optional[list[str]] = None


class UpdateProgressRequest(BaseModel):
    completedModuleId: str
    nextModuleId: Optional[str] = None
    status: Optional[str] = "active"


# ── Lifecycle ────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    global pool, http
    pool = await asyncpg.create_pool(**PG, min_size=2, max_size=10)
    http = httpx.AsyncClient(timeout=15.0)

    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_paths (
                path_id           TEXT PRIMARY KEY,
                name              TEXT NOT NULL,
                description       TEXT,
                target_audience   TEXT,
                module_sequence   JSONB NOT NULL DEFAULT '[]',
                concepts_targeted TEXT[] DEFAULT '{}',
                skills_developed  TEXT[] DEFAULT '{}',
                created_by        TEXT DEFAULT 'system',
                created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                user_id           TEXT NOT NULL,
                path_id           TEXT NOT NULL,
                enrollment_date   TIMESTAMPTZ NOT NULL DEFAULT now(),
                status            TEXT NOT NULL DEFAULT 'active',
                current_module_id TEXT,
                completed_modules TEXT[] DEFAULT '{}',
                progress_pct      REAL DEFAULT 0.0,
                PRIMARY KEY (user_id, path_id)
            );
        """)

        # Seed a default learning path
        exists = await conn.fetchval(
            "SELECT 1 FROM learning_paths WHERE path_id = 'path_ai_foundations'"
        )
        if not exists:
            await conn.execute("""
                INSERT INTO learning_paths
                    (path_id, name, description, target_audience, module_sequence,
                     concepts_targeted, skills_developed, created_by)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                "path_ai_foundations",
                "Foundations of AI & Machine Learning",
                "A comprehensive learning path covering the fundamentals of AI, "
                "machine learning, neural networks, and Python programming for beginners.",
                "Beginners with basic computer skills",
                json.dumps([
                    {"moduleId": "module_python_basics_interactive", "order": 1, "isOptional": False},
                    {"moduleId": "module_python_data_structures", "order": 2, "isOptional": False},
                    {"moduleId": "module_intro_ml_video", "order": 3, "isOptional": False},
                    {"moduleId": "module_ml_supervised_quiz", "order": 4, "isOptional": False},
                    {"moduleId": "module_neural_networks_article", "order": 5, "isOptional": False},
                    {"moduleId": "module_deep_learning_video", "order": 6, "isOptional": True},
                ]),
                ["concept_python_basics", "concept_machine_learning", "concept_neural_networks"],
                ["skill_python_programming", "skill_ml_fundamentals"],
                "system",
            )


@app.on_event("shutdown")
async def shutdown():
    if pool:
        await pool.close()
    if http:
        await http.aclose()


# ── Helpers ──────────────────────────────────────────────────
def _path_row_to_dict(row) -> dict:
    seq = json.loads(row["module_sequence"]) if isinstance(row["module_sequence"], str) else row["module_sequence"]
    return {
        "pathId": row["path_id"],
        "name": row["name"],
        "description": row["description"],
        "targetAudience": row["target_audience"],
        "moduleSequence": seq,
        "conceptsTargeted": list(row["concepts_targeted"] or []),
        "skillsDeveloped": list(row["skills_developed"] or []),
        "createdBy": row["created_by"],
        "createdAt": row["created_at"].isoformat() if row["created_at"] else None,
    }


def _enrollment_to_dict(row) -> dict:
    return {
        "userId": row["user_id"],
        "pathId": row["path_id"],
        "enrollmentDate": row["enrollment_date"].isoformat() if row["enrollment_date"] else None,
        "status": row["status"],
        "currentModuleId": row["current_module_id"],
        "completedModules": list(row["completed_modules"] or []),
        "progressPercentage": round(row["progress_pct"], 1),
    }


# ── Path CRUD ────────────────────────────────────────────────
@app.post("/paths", status_code=201)
async def create_path(req: CreatePathRequest):
    pid = f"path_{uuid.uuid4().hex[:12]}"
    seq = [m.model_dump() for m in req.moduleSequence]
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO learning_paths
                (path_id, name, description, target_audience, module_sequence,
                 concepts_targeted, skills_developed)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, pid, req.name, req.description, req.targetAudience,
            json.dumps(seq), req.conceptsTargeted or [], req.skillsDeveloped or [])
    return {"pathId": pid, "name": req.name, "moduleSequence": seq}


@app.get("/paths")
async def list_paths(
    keyword: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    filters, vals, idx = [], [], 1
    if keyword:
        filters.append(f"(name ILIKE ${idx} OR description ILIKE ${idx})")
        vals.append(f"%{keyword}%"); idx += 1
    where = "WHERE " + " AND ".join(filters) if filters else ""
    vals.extend([limit, offset])

    async with pool.acquire() as conn:
        total = await conn.fetchval(
            f"SELECT count(*) FROM learning_paths {where}", *vals[:-2]
        )
        rows = await conn.fetch(
            f"SELECT * FROM learning_paths {where} ORDER BY created_at DESC LIMIT ${idx} OFFSET ${idx+1}",
            *vals,
        )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": [_path_row_to_dict(r) for r in rows],
    }


@app.get("/paths/{path_id}")
async def get_path(path_id: str):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM learning_paths WHERE path_id = $1", path_id
        )
    if not row:
        raise HTTPException(404, "Path not found")
    return _path_row_to_dict(row)


@app.delete("/paths/{path_id}", status_code=204)
async def delete_path(path_id: str):
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM learning_paths WHERE path_id = $1", path_id
        )
    if result == "DELETE 0":
        raise HTTPException(404, "Path not found")


# ── Enrollment & Progress ────────────────────────────────────
@app.post("/users/{user_id}/paths/{path_id}/enroll")
async def enroll(user_id: str, path_id: str):
    async with pool.acquire() as conn:
        path_row = await conn.fetchrow(
            "SELECT * FROM learning_paths WHERE path_id = $1", path_id
        )
        if not path_row:
            raise HTTPException(404, "Path not found")

        seq = json.loads(path_row["module_sequence"]) if isinstance(
            path_row["module_sequence"], str
        ) else path_row["module_sequence"]
        first_module = seq[0]["moduleId"] if seq else None

        try:
            await conn.execute("""
                INSERT INTO enrollments (user_id, path_id, current_module_id)
                VALUES ($1, $2, $3)
            """, user_id, path_id, first_module)
        except asyncpg.UniqueViolationError:
            raise HTTPException(409, "Already enrolled")

    return {
        "userId": user_id,
        "pathId": path_id,
        "enrollmentDate": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "currentModuleId": first_module,
    }


@app.get("/users/{user_id}/paths/{path_id}/enrollment")
async def get_enrollment(user_id: str, path_id: str):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM enrollments WHERE user_id = $1 AND path_id = $2",
            user_id, path_id,
        )
    if not row:
        raise HTTPException(404, "Enrollment not found")
    return _enrollment_to_dict(row)


@app.put("/users/{user_id}/paths/{path_id}/progress")
async def update_progress(user_id: str, path_id: str, req: UpdateProgressRequest):
    async with pool.acquire() as conn:
        # Get enrollment
        enroll_row = await conn.fetchrow(
            "SELECT * FROM enrollments WHERE user_id = $1 AND path_id = $2",
            user_id, path_id,
        )
        if not enroll_row:
            raise HTTPException(404, "Enrollment not found")

        # Get path to calculate progress
        path_row = await conn.fetchrow(
            "SELECT module_sequence FROM learning_paths WHERE path_id = $1", path_id
        )
        seq = json.loads(path_row["module_sequence"]) if isinstance(
            path_row["module_sequence"], str
        ) else path_row["module_sequence"]
        total_required = sum(1 for m in seq if not m.get("isOptional", False))

        completed = list(enroll_row["completed_modules"] or [])
        if req.completedModuleId not in completed:
            completed.append(req.completedModuleId)

        completed_required = sum(
            1 for m in seq
            if m["moduleId"] in completed and not m.get("isOptional", False)
        )
        progress = (completed_required / total_required * 100) if total_required > 0 else 100
        status = req.status or ("completed" if progress >= 100 else "active")

        # Determine next module
        next_mod = req.nextModuleId
        if not next_mod and status != "completed":
            for m in sorted(seq, key=lambda x: x["order"]):
                if m["moduleId"] not in completed:
                    next_mod = m["moduleId"]
                    break

        await conn.execute("""
            UPDATE enrollments SET
                completed_modules = $1,
                current_module_id = $2,
                progress_pct = $3,
                status = $4
            WHERE user_id = $5 AND path_id = $6
        """, completed, next_mod, progress, status, user_id, path_id)

    return {
        "userId": user_id,
        "pathId": path_id,
        "status": status,
        "currentModuleId": next_mod,
        "completedModules": completed,
        "progressPercentage": round(progress, 1),
    }


@app.get("/users/{user_id}/paths")
async def list_user_paths(
    user_id: str,
    status: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    filters = ["e.user_id = $1"]
    vals = [user_id]
    idx = 2
    if status:
        filters.append(f"e.status = ${idx}")
        vals.append(status); idx += 1

    where = "WHERE " + " AND ".join(filters)
    vals.extend([limit, offset])

    async with pool.acquire() as conn:
        rows = await conn.fetch(f"""
            SELECT e.*, p.name as path_name, p.description as path_description
            FROM enrollments e
            JOIN learning_paths p ON e.path_id = p.path_id
            {where}
            ORDER BY e.enrollment_date DESC
            LIMIT ${idx} OFFSET ${idx+1}
        """, *vals)

    return {
        "userId": user_id,
        "enrollments": [
            {
                **_enrollment_to_dict(r),
                "pathName": r["path_name"],
                "pathDescription": r["path_description"],
            }
            for r in rows
        ],
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "learning_pathway_service"}
