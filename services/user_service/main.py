"""
NeuroForge — User Service
Handles user registration, authentication (JWT), and profile management.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import asyncpg
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

# ── Config ───────────────────────────────────────────────────
PG = dict(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    user=os.getenv("POSTGRES_USER", "neuroforge"),
    password=os.getenv("POSTGRES_PASSWORD", "neuroforge_secret"),
    database=os.getenv("POSTGRES_DB", "neuroforge"),
)
JWT_SECRET = os.getenv("JWT_SECRET", "neuroforge-dev-secret-change-in-prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

app = FastAPI(title="NeuroForge User Service", version="0.1.0")
pool = None
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


# ── Models ───────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: str
    password: str
    displayName: str
    role: Optional[str] = "learner"


class LoginRequest(BaseModel):
    email: str
    password: str


class UpdateProfileRequest(BaseModel):
    displayName: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[dict] = None


# ── Lifecycle ────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(**PG, min_size=2, max_size=10)
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id       TEXT PRIMARY KEY,
                email         TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                display_name  TEXT NOT NULL,
                role          TEXT NOT NULL DEFAULT 'learner',
                bio           TEXT DEFAULT '',
                preferences   JSONB DEFAULT '{}',
                created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
                last_login    TIMESTAMPTZ
            );
        """)
        # Seed demo user
        exists = await conn.fetchval(
            "SELECT 1 FROM users WHERE user_id = 'poc_user_01'"
        )
        if not exists:
            await conn.execute("""
                INSERT INTO users (user_id, email, password_hash, display_name, role, bio)
                VALUES ($1, $2, $3, $4, $5, $6)
            """,
                "poc_user_01",
                "learner@neuroforge.dev",
                pwd_ctx.hash("demo1234"),
                "Demo Learner",
                "learner",
                "PoC demo user for NeuroForge platform.",
            )


@app.on_event("shutdown")
async def shutdown():
    if pool:
        await pool.close()


# ── Auth helpers ─────────────────────────────────────────────
def _create_token(user_id: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode({"sub": user_id, "email": email, "exp": expire}, JWT_SECRET, JWT_ALGORITHM)


async def _get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)):
    if not creds:
        raise HTTPException(401, "Missing auth token")
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload["sub"]
    except JWTError:
        raise HTTPException(401, "Invalid token")


def _user_row_to_dict(row) -> dict:
    return {
        "userId": row["user_id"],
        "email": row["email"],
        "displayName": row["display_name"],
        "role": row["role"],
        "bio": row["bio"],
        "preferences": row["preferences"],
        "createdAt": row["created_at"].isoformat() if row["created_at"] else None,
        "lastLogin": row["last_login"].isoformat() if row["last_login"] else None,
    }


# ── Endpoints ────────────────────────────────────────────────
@app.post("/users/register", status_code=201)
async def register(req: RegisterRequest):
    uid = f"user_{uuid.uuid4().hex[:12]}"
    pw_hash = pwd_ctx.hash(req.password)
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (user_id, email, password_hash, display_name, role)
                VALUES ($1, $2, $3, $4, $5)
            """, uid, req.email, pw_hash, req.displayName, req.role or "learner")
    except asyncpg.UniqueViolationError:
        raise HTTPException(409, "Email already registered")
    return {"userId": uid, "email": req.email, "displayName": req.displayName, "role": req.role}


@app.post("/users/login")
async def login(req: LoginRequest):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE email = $1", req.email)
    if not row or not pwd_ctx.verify(req.password, row["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    # Update last login
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET last_login = now() WHERE user_id = $1", row["user_id"]
        )
    token = _create_token(row["user_id"], row["email"])
    return {"token": token, "userId": row["user_id"], "displayName": row["display_name"]}


@app.get("/users/{user_id}")
async def get_user(user_id: str):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
    if not row:
        raise HTTPException(404, "User not found")
    return _user_row_to_dict(row)


@app.put("/users/{user_id}")
async def update_user(user_id: str, req: UpdateProfileRequest):
    sets, vals, idx = [], [], 1
    if req.displayName is not None:
        sets.append(f"display_name = ${idx}"); vals.append(req.displayName); idx += 1
    if req.bio is not None:
        sets.append(f"bio = ${idx}"); vals.append(req.bio); idx += 1
    if req.preferences is not None:
        import json
        sets.append(f"preferences = ${idx}::jsonb"); vals.append(json.dumps(req.preferences)); idx += 1
    if not sets:
        raise HTTPException(400, "No fields to update")
    vals.append(user_id)

    async with pool.acquire() as conn:
        result = await conn.execute(
            f"UPDATE users SET {', '.join(sets)} WHERE user_id = ${idx}", *vals
        )
    if result == "UPDATE 0":
        raise HTTPException(404, "User not found")
    return {"message": "Profile updated", "userId": user_id}


@app.get("/users")
async def list_users(limit: int = 20, offset: int = 0):
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT count(*) FROM users")
        rows = await conn.fetch(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2",
            limit, offset,
        )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": [_user_row_to_dict(r) for r in rows],
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "user_service"}
