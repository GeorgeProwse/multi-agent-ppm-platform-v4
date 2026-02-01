from __future__ import annotations

import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parents[3]
SRC_DIR = TESTS_DIR.parent / "src"

sys.path.extend([str(REPO_ROOT), str(SRC_DIR)])

from knowledge_management_agent import KnowledgeManagementAgent


def build_agent(tmp_path: Path) -> KnowledgeManagementAgent:
    return KnowledgeManagementAgent(
        config={
            "document_store_path": str(tmp_path / "documents.json"),
            "knowledge_db_path": str(tmp_path / "knowledge.db"),
            "document_schema_path": "data/schemas/document.schema.json",
            "similarity_threshold": 0.0,
        }
    )


@pytest.mark.anyio
async def test_ingestion_from_github_repo(tmp_path: Path) -> None:
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    doc_path = repo_path / "readme.md"
    doc_path.write_text("Author: Jane Doe\nDate: 2024-01-01\nTags: risk, policy\nRisk plan")

    agent = build_agent(tmp_path)
    await agent.initialize()

    result = await agent._ingest_sources(
        tenant_id="tenant-a",
        sources=[{"type": "github", "repo_path": str(repo_path), "tags": ["repo-doc"]}],
    )

    assert result["total_documents"] == 1
    assert result["sources"][0]["source_type"] == "github"


@pytest.mark.anyio
async def test_semantic_search_returns_ranked_results(tmp_path: Path) -> None:
    agent = build_agent(tmp_path)
    await agent.initialize()
    upload = await agent._upload_document(
        "tenant-a",
        {
            "title": "Security Policy",
            "content": "Access control policy for cybersecurity operations.",
            "permissions": {"public": True},
        },
    )

    result = await agent._search_documents(
        query="access control policy",
        filters={},
        access_context={"user_id": "analyst", "roles": []},
        tenant_id="tenant-a",
    )

    assert result["total_results"] >= 1
    assert result["results"][0]["document_id"] == upload["document_id"]


@pytest.mark.anyio
async def test_knowledge_graph_builds_relationships(tmp_path: Path) -> None:
    agent = build_agent(tmp_path)
    await agent.initialize()
    upload = await agent._upload_document(
        "tenant-a",
        {
            "title": "Project Atlas Update",
            "content": "Decision: proceed with rollout.\nRisk: schedule delay.",
            "permissions": {"public": True},
        },
    )

    await agent._extract_entities(upload["document_id"], "tenant-a")
    graph = await agent._build_knowledge_graph(upload["document_id"], "tenant-a")

    assert graph["relationships"] >= 0
    assert agent.graph_edges


@pytest.mark.anyio
async def test_document_curation_workflow(tmp_path: Path) -> None:
    agent = build_agent(tmp_path)
    await agent.initialize()
    upload = await agent._upload_document(
        "tenant-a",
        {
            "title": "Lessons Learned",
            "content": "Retrospective summary.",
            "permissions": {"public": True},
        },
    )

    annotation = await agent._annotate_document(
        upload["document_id"],
        {"text": "Add timeline detail"},
        {"user_id": "reviewer"},
        "tenant-a",
    )
    review = await agent._review_document(
        upload["document_id"],
        {"status": "in_review", "comments": ["Looks good"]},
        {"user_id": "reviewer"},
        "tenant-a",
    )
    approval = await agent._approve_document(
        upload["document_id"],
        {"status": "approved", "notes": "Approved"},
        {"user_id": "approver"},
        "tenant-a",
    )

    assert annotation["annotation"]["text"] == "Add timeline detail"
    assert review["review"]["status"] == "in_review"
    assert approval["approval"]["status"] == "approved"
