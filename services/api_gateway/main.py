"""
NeuroForge — API Gateway
Single entry point for all client requests. Routes to internal microservices,
handles CORS, and provides a unified API surface.
"""

from __future__ import annotations

import os

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

# ── Service URLs ─────────────────────────────────────────────
SERVICES = {
    "users": os.getenv("USER_SERVICE_URL", "http://localhost:8001"),
    "concepts": os.getenv("KNOWLEDGE_GRAPH_SERVICE_URL", "http://localhost:8002"),
    "skills": os.getenv("KNOWLEDGE_GRAPH_SERVICE_URL", "http://localhost:8002"),
    "modules": os.getenv("KNOWLEDGE_GRAPH_SERVICE_URL", "http://localhost:8002"),
    "mentor": os.getenv("AI_MENTOR_SERVICE_URL", "http://localhost:8003"),
    "profiling": os.getenv("COGNITIVE_PROFILING_SERVICE_URL", "http://localhost:8004"),
    "content": os.getenv("CONTENT_DELIVERY_SERVICE_URL", "http://localhost:8005"),
    "paths": os.getenv("LEARNING_PATHWAY_SERVICE_URL", "http://localhost:8006"),
}

app = FastAPI(
    title="NeuroForge API Gateway",
    version="0.1.0",
    description="Unified API entry point for all NeuroForge services",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

http: httpx.AsyncClient | None = None


@app.on_event("startup")
async def startup():
    global http
    http = httpx.AsyncClient(timeout=60.0)


@app.on_event("shutdown")
async def shutdown():
    if http:
        await http.aclose()


# ── Health & Discovery ───────────────────────────────────────
@app.get("/health")
async def health():
    """Check gateway and downstream service health."""
    statuses = {}
    for name, url in SERVICES.items():
        if name in statuses:
            continue
        try:
            resp = await http.get(f"{url}/health", timeout=5.0)
            statuses[name] = resp.json() if resp.status_code == 200 else {"status": "error"}
        except Exception as e:
            statuses[name] = {"status": "unreachable", "error": str(e)}
    return {"gateway": "healthy", "services": statuses}


@app.get("/")
async def root():
    return {
        "service": "NeuroForge API Gateway",
        "version": "0.1.0",
        "endpoints": {
            "users": "/api/v1/users/...",
            "concepts": "/api/v1/concepts/...",
            "skills": "/api/v1/skills/...",
            "modules": "/api/v1/modules/...",
            "mentor": "/api/v1/mentor/...",
            "profiling": "/api/v1/profiling/...",
            "content": "/api/v1/content/...",
            "paths": "/api/v1/paths/...",
            "health": "/health",
        },
    }


# ── Generic proxy ────────────────────────────────────────────
async def _proxy(service_key: str, path: str, request: Request) -> Response:
    """Forward request to the appropriate microservice."""
    base_url = SERVICES.get(service_key)
    if not base_url:
        return Response(content='{"error":"Unknown service"}', status_code=404,
                        media_type="application/json")

    url = f"{base_url}/{path}"
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length", "transfer-encoding")
    }

    body = await request.body()

    try:
        resp = await http.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
            params=dict(request.query_params),
        )
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            media_type=resp.headers.get("content-type", "application/json"),
        )
    except httpx.ConnectError:
        return Response(
            content=f'{{"error":"Service {service_key} is unreachable"}}',
            status_code=503,
            media_type="application/json",
        )
    except Exception as e:
        return Response(
            content=f'{{"error":"{str(e)}"}}',
            status_code=502,
            media_type="application/json",
        )


# ── Route definitions ────────────────────────────────────────
# User Service
@app.api_route("/api/v1/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_users(path: str, request: Request):
    return await _proxy("users", f"users/{path}", request)


# Knowledge Graph — Concepts
@app.api_route("/api/v1/concepts/{path:path}", methods=["GET"])
async def proxy_concepts_path(path: str, request: Request):
    return await _proxy("concepts", f"concepts/{path}", request)


@app.api_route("/api/v1/concepts", methods=["GET"])
async def proxy_concepts(request: Request):
    return await _proxy("concepts", "concepts", request)


# Knowledge Graph — Skills
@app.api_route("/api/v1/skills/{path:path}", methods=["GET"])
async def proxy_skills_path(path: str, request: Request):
    return await _proxy("skills", f"skills/{path}", request)


@app.api_route("/api/v1/skills", methods=["GET"])
async def proxy_skills(request: Request):
    return await _proxy("skills", "skills", request)


# Knowledge Graph — Modules
@app.api_route("/api/v1/modules/{path:path}", methods=["GET"])
async def proxy_modules_path(path: str, request: Request):
    return await _proxy("modules", f"modules/{path}", request)


@app.api_route("/api/v1/modules", methods=["GET"])
async def proxy_modules(request: Request):
    return await _proxy("modules", "modules", request)


# AI Mentor
@app.api_route("/api/v1/mentor/{path:path}", methods=["GET", "POST"])
async def proxy_mentor(path: str, request: Request):
    return await _proxy("mentor", f"mentor/{path}", request)


# Cognitive Profiling
@app.api_route("/api/v1/profiling/{path:path}", methods=["GET", "POST"])
async def proxy_profiling(path: str, request: Request):
    return await _proxy("profiling", f"profiling/{path}", request)


# Content Delivery
@app.api_route("/api/v1/content/{path:path}", methods=["GET"])
async def proxy_content_path(path: str, request: Request):
    return await _proxy("content", f"content/{path}", request)


@app.api_route("/api/v1/content", methods=["GET"])
async def proxy_content(request: Request):
    return await _proxy("content", "content", request)


# Learning Pathways
@app.api_route("/api/v1/paths/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_paths_sub(path: str, request: Request):
    return await _proxy("paths", f"paths/{path}", request)


@app.api_route("/api/v1/paths", methods=["GET", "POST"])
async def proxy_paths(request: Request):
    return await _proxy("paths", "paths", request)


# User enrollment routes (proxied to learning pathway service)
@app.api_route("/api/v1/users/{user_id}/paths/{path:path}", methods=["GET", "POST", "PUT"])
async def proxy_user_paths(user_id: str, path: str, request: Request):
    return await _proxy("paths", f"users/{user_id}/paths/{path}", request)


@app.api_route("/api/v1/users/{user_id}/paths", methods=["GET"])
async def proxy_user_paths_list(user_id: str, request: Request):
    return await _proxy("paths", f"users/{user_id}/paths", request)
