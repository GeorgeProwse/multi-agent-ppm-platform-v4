"""Collaborative editing action handlers: annotations, reviews, approvals, linking."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from knowledge_utils import graph_document_id

if TYPE_CHECKING:
    from knowledge_management_agent import KnowledgeManagementAgent


async def annotate_document(
    agent: KnowledgeManagementAgent,
    document_id: str,
    annotation: dict[str, Any],
    access_context: dict[str, Any],
    tenant_id: str,
) -> dict[str, Any]:
    """Add annotation to a document."""
    document = agent._load_document(tenant_id, document_id)
    if not document:
        raise ValueError(f"Document not found: {document_id}")
    if not await agent._is_access_allowed(document, access_context):
        raise PermissionError("Access denied for requested document")

    record = {
        "annotation_id": f"ANN-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "document_id": document_id,
        "text": annotation.get("text"),
        "selection": annotation.get("selection"),
        "author": access_context.get("user_id") or annotation.get("author"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    agent.document_annotations.setdefault(document_id, []).append(record)
    agent.knowledge_db.record_interaction(document_id, "annotation", record)
    await agent._publish_event("knowledge.document.annotated", record)
    return {"document_id": document_id, "annotation": record}


async def review_document(
    agent: KnowledgeManagementAgent,
    document_id: str,
    review: dict[str, Any],
    access_context: dict[str, Any],
    tenant_id: str,
) -> dict[str, Any]:
    """Capture document review feedback."""
    document = agent._load_document(tenant_id, document_id)
    if not document:
        raise ValueError(f"Document not found: {document_id}")
    if not await agent._is_access_allowed(document, access_context):
        raise PermissionError("Access denied for requested document")

    record = {
        "review_id": f"REV-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "document_id": document_id,
        "status": review.get("status", "in_review"),
        "comments": review.get("comments", []),
        "reviewer": access_context.get("user_id") or review.get("reviewer"),
        "version": document.get("version"),
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
    }
    agent.document_reviews.setdefault(document_id, []).append(record)
    agent.knowledge_db.record_interaction(document_id, "review", record)
    await agent._publish_event("knowledge.document.reviewed", record)
    return {"document_id": document_id, "review": record}


async def approve_document(
    agent: KnowledgeManagementAgent,
    document_id: str,
    approval: dict[str, Any],
    access_context: dict[str, Any],
    tenant_id: str,
) -> dict[str, Any]:
    """Approve document changes."""
    document = agent._load_document(tenant_id, document_id)
    if not document:
        raise ValueError(f"Document not found: {document_id}")
    if not await agent._is_access_allowed(document, access_context):
        raise PermissionError("Access denied for requested document")

    record = {
        "approval_id": f"APR-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "document_id": document_id,
        "status": approval.get("status", "approved"),
        "approver": access_context.get("user_id") or approval.get("approver"),
        "version": document.get("version"),
        "notes": approval.get("notes"),
        "approved_at": datetime.now(timezone.utc).isoformat(),
    }
    agent.document_approvals.setdefault(document_id, []).append(record)
    document["status"] = (
        "approved" if record["status"] == "approved" else document.get("status", "draft")
    )
    agent.document_store.upsert(tenant_id, document_id, document.copy())
    agent.knowledge_db.upsert_document(document)
    agent.knowledge_db.record_interaction(document_id, "approval", record)
    await agent._publish_event("knowledge.document.approved", record)
    return {"document_id": document_id, "approval": record}


async def link_documents(
    agent: KnowledgeManagementAgent, links: list[dict[str, Any]], tenant_id: str
) -> dict[str, Any]:
    """Link related documents in the knowledge graph."""
    created_links: list[dict[str, Any]] = []
    for link in links:
        source_id = link.get("source_document_id")
        target_id = link.get("target_document_id")
        relation = link.get("relation", "related")
        if not source_id or not target_id:
            continue
        source = agent._load_document(tenant_id, source_id)
        target = agent._load_document(tenant_id, target_id)
        if not source or not target:
            continue
        source_node = graph_document_id(source_id)
        target_node = graph_document_id(target_id)
        agent._register_graph_node(
            source_node,
            "document",
            {"title": source.get("title"), "doc_type": source.get("type")},
        )
        agent._register_graph_node(
            target_node,
            "document",
            {"title": target.get("title"), "doc_type": target.get("type")},
        )
        agent._register_graph_edge(source_node, target_node, relation)
        created_links.append(
            {
                "source_document_id": source_id,
                "target_document_id": target_id,
                "relation": relation,
            }
        )

    if created_links:
        await agent._publish_event(
            "knowledge.document.linked", {"links": created_links, "tenant_id": tenant_id}
        )
        agent.knowledge_db.upsert_graph(agent.graph_nodes, agent.graph_edges)
    return {"links": created_links, "count": len(created_links)}
