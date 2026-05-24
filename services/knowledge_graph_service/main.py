"""
NeuroForge — Knowledge Graph Service
Provides access to concepts, skills, content modules, and their relationships via Neo4j.
"""

from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from neo4j import AsyncGraphDatabase

# ── Config ───────────────────────────────────────────────────
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neuroforge_secret")

app = FastAPI(title="NeuroForge Knowledge Graph Service", version="0.1.0")
driver = None


# ── Lifecycle ────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    global driver
    driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


@app.on_event("shutdown")
async def shutdown():
    if driver:
        await driver.close()


# ── Helpers ──────────────────────────────────────────────────
def _concept_from_record(record) -> dict:
    n = record["c"]
    return {
        "conceptId": n.get("conceptId"),
        "name": n.get("name"),
        "description": n.get("description"),
        "difficultyLevel": n.get("difficultyLevel"),
        "domain": n.get("domain"),
        "subDomain": n.get("subDomain"),
        "keywords": list(n.get("keywords", [])),
    }


def _skill_from_record(record) -> dict:
    n = record["s"]
    return {
        "skillId": n.get("skillId"),
        "name": n.get("name"),
        "description": n.get("description"),
        "proficiencyLevels": list(n.get("proficiencyLevels", [])),
        "domain": n.get("domain"),
        "keywords": list(n.get("keywords", [])),
    }


def _module_from_record(record) -> dict:
    n = record["m"]
    return {
        "moduleId": n.get("moduleId"),
        "title": n.get("title"),
        "type": n.get("type"),
        "format": n.get("format"),
        "url": n.get("url"),
        "estimatedDurationMinutes": n.get("estimatedDurationMinutes"),
        "difficultyLevel": n.get("difficultyLevel"),
        "description": n.get("description"),
        "publishedDate": n.get("publishedDate"),
    }


# ── Concept Endpoints ───────────────────────────────────────
@app.get("/concepts")
async def list_concepts(
    domain: Optional[str] = None,
    subDomain: Optional[str] = None,
    difficultyLevel: Optional[str] = None,
    keyword: Optional[str] = None,
    name: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    filters, params = [], {}
    if domain:
        filters.append("c.domain = $domain"); params["domain"] = domain
    if subDomain:
        filters.append("c.subDomain = $subDomain"); params["subDomain"] = subDomain
    if difficultyLevel:
        filters.append("c.difficultyLevel = $difficultyLevel"); params["difficultyLevel"] = difficultyLevel
    if keyword:
        filters.append("$keyword IN c.keywords"); params["keyword"] = keyword
    if name:
        filters.append("toLower(c.name) CONTAINS toLower($name)"); params["name"] = name

    where = "WHERE " + " AND ".join(filters) if filters else ""
    params["limit"] = limit
    params["offset"] = offset

    async with driver.session() as session:
        count_result = await session.run(f"MATCH (c:Concept) {where} RETURN count(c) as total", params)
        total = (await count_result.single())["total"]

        result = await session.run(
            f"MATCH (c:Concept) {where} RETURN c ORDER BY c.name SKIP $offset LIMIT $limit",
            params,
        )
        records = [_concept_from_record(r) async for r in result]

    return {"total": total, "limit": limit, "offset": offset, "data": records}


@app.get("/concepts/{concept_id}")
async def get_concept(concept_id: str):
    async with driver.session() as session:
        result = await session.run(
            "MATCH (c:Concept {conceptId: $cid}) RETURN c", {"cid": concept_id}
        )
        record = await result.single()
    if not record:
        raise HTTPException(404, f"Concept '{concept_id}' not found")
    return _concept_from_record(record)


@app.get("/concepts/{concept_id}/prerequisites")
async def get_prerequisites(concept_id: str):
    async with driver.session() as session:
        result = await session.run("""
            MATCH (pre:Concept)-[:PREREQUISITE_OF]->(c:Concept {conceptId: $cid})
            RETURN pre as c
        """, {"cid": concept_id})
        return [_concept_from_record(r) async for r in result]


@app.get("/concepts/{concept_id}/related")
async def get_related(concept_id: str):
    async with driver.session() as session:
        result = await session.run("""
            MATCH (c:Concept {conceptId: $cid})-[:RELATED_TO]-(rel:Concept)
            RETURN rel as c
        """, {"cid": concept_id})
        return [_concept_from_record(r) async for r in result]


@app.get("/concepts/{concept_id}/modules")
async def get_concept_modules(concept_id: str):
    async with driver.session() as session:
        result = await session.run("""
            MATCH (m:ContentModule)-[:TEACHES_CONCEPT]->(c:Concept {conceptId: $cid})
            RETURN m
        """, {"cid": concept_id})
        return [_module_from_record(r) async for r in result]


# ── Skill Endpoints ──────────────────────────────────────────
@app.get("/skills")
async def list_skills(
    domain: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    filters, params = [], {}
    if domain:
        filters.append("s.domain = $domain"); params["domain"] = domain
    if keyword:
        filters.append("$keyword IN s.keywords"); params["keyword"] = keyword
    where = "WHERE " + " AND ".join(filters) if filters else ""
    params["limit"] = limit
    params["offset"] = offset

    async with driver.session() as session:
        count_result = await session.run(f"MATCH (s:Skill) {where} RETURN count(s) as total", params)
        total = (await count_result.single())["total"]

        result = await session.run(
            f"MATCH (s:Skill) {where} RETURN s ORDER BY s.name SKIP $offset LIMIT $limit",
            params,
        )
        records = [_skill_from_record(r) async for r in result]

    return {"total": total, "limit": limit, "offset": offset, "data": records}


@app.get("/skills/{skill_id}")
async def get_skill(skill_id: str):
    async with driver.session() as session:
        result = await session.run(
            "MATCH (s:Skill {skillId: $sid}) RETURN s", {"sid": skill_id}
        )
        record = await result.single()
    if not record:
        raise HTTPException(404, f"Skill '{skill_id}' not found")
    return _skill_from_record(record)


@app.get("/skills/{skill_id}/modules")
async def get_skill_modules(skill_id: str):
    async with driver.session() as session:
        result = await session.run("""
            MATCH (m:ContentModule)-[:DEVELOPS_SKILL]->(s:Skill {skillId: $sid})
            RETURN m
        """, {"sid": skill_id})
        return [_module_from_record(r) async for r in result]


# ── Module Endpoints ─────────────────────────────────────────
@app.get("/modules")
async def list_modules(
    type: Optional[str] = None,
    difficultyLevel: Optional[str] = None,
    conceptId: Optional[str] = None,
    skillId: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    match_clauses = ["(m:ContentModule)"]
    filters, params = [], {}

    if type:
        filters.append("m.type = $type"); params["type"] = type
    if difficultyLevel:
        filters.append("m.difficultyLevel = $difficultyLevel"); params["difficultyLevel"] = difficultyLevel
    if conceptId:
        match_clauses.append("(m)-[:TEACHES_CONCEPT]->(:Concept {conceptId: $conceptId})")
        params["conceptId"] = conceptId
    if skillId:
        match_clauses.append("(m)-[:DEVELOPS_SKILL]->(:Skill {skillId: $skillId})")
        params["skillId"] = skillId

    match_str = "MATCH " + ", ".join(match_clauses)
    where = "WHERE " + " AND ".join(filters) if filters else ""
    params["limit"] = limit
    params["offset"] = offset

    async with driver.session() as session:
        count_result = await session.run(
            f"{match_str} {where} RETURN count(DISTINCT m) as total", params
        )
        total = (await count_result.single())["total"]

        result = await session.run(
            f"{match_str} {where} RETURN DISTINCT m ORDER BY m.title SKIP $offset LIMIT $limit",
            params,
        )
        records = [_module_from_record(r) async for r in result]

    return {"total": total, "limit": limit, "offset": offset, "data": records}


@app.get("/modules/{module_id}")
async def get_module(module_id: str):
    async with driver.session() as session:
        result = await session.run(
            "MATCH (m:ContentModule {moduleId: $mid}) RETURN m", {"mid": module_id}
        )
        record = await result.single()
    if not record:
        raise HTTPException(404, f"Module '{module_id}' not found")
    return _module_from_record(record)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "knowledge_graph_service"}
