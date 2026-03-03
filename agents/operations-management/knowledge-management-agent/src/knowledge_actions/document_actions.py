"""Document CRUD action handlers for the Knowledge Management Agent."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from knowledge_utils import generate_document_id

if TYPE_CHECKING:
    from knowledge_management_agent import KnowledgeManagementAgent


async def upload_document(
    agent: KnowledgeManagementAgent, tenant_id: str, document_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Upload and classify document.

    Returns document ID and metadata.
    """
    agent.logger.info("Uploading document: %s", document_data.get("title"))

    # Generate document ID
    document_id = await generate_document_id()

    # Extract metadata
    from knowledge_actions.classification_actions import auto_classify_document, extract_metadata, generate_tags

    metadata = await extract_metadata(agent, document_data)

    # Auto-classify document
    classification = await auto_classify_document(agent, document_data)

    # Generate initial tags
    tags = await generate_tags(agent, document_data, classification)

    classification_label = document_data.get("classification", "internal")
    doc_type = await agent._map_doc_type_for_schema(classification.get("type"))
    owner = document_data.get("owner") or document_data.get("author") or "unknown"
    status = document_data.get("status", "draft")

    # Create document record
    document = {
        "document_id": document_id,
        "tenant_id": tenant_id,
        "title": document_data.get("title"),
        "content": document_data.get("content"),
        "type": classification.get("type"),
        "doc_type": doc_type,
        "tags": tags,
        "author": document_data.get("author"),
        "project_id": document_data.get("project_id"),
        "program_id": document_data.get("program_id"),
        "portfolio_id": document_data.get("portfolio_id"),
        "metadata": metadata,
        "source": document_data.get("source"),
        "version": 1,
        "permissions": document_data.get("permissions", {"public": False}),
        "classification": classification_label,
        "status": status,
        "owner": owner,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "modified_at": datetime.now(timezone.utc).isoformat(),
        "accessed_count": 0,
        "topic": classification.get("topic"),
        "phase": classification.get("phase"),
        "domain": classification.get("domain"),
    }

    await agent._validate_document_schema(
        {
            "id": document_id,
            "tenant_id": tenant_id,
            "title": document.get("title"),
            "doc_type": doc_type,
            "status": status,
            "classification": classification_label,
            "owner": owner,
            "created_at": document.get("created_at"),
            "updated_at": document.get("modified_at"),
            "metadata": metadata,
        }
    )

    # Store document
    agent.documents[document_id] = document
    agent.document_store.upsert(tenant_id, document_id, document.copy())
    agent.knowledge_db.upsert_document(document)
    agent.knowledge_db.record_version(document)
    agent._index_document(document)
    await agent._update_graph_for_document(document)
    agent._update_classifier_with_document(document)

    # Store version
    agent.document_versions[document_id] = [document.copy()]

    # Generate summary asynchronously
    from knowledge_actions.classification_actions import summarize_document
    from knowledge_actions.knowledge_graph_actions import extract_entities

    if agent.async_processing_enabled:
        asyncio.create_task(summarize_document(agent, document_id, tenant_id))
        asyncio.create_task(extract_entities(agent, document_id, tenant_id))
    else:
        await summarize_document(agent, document_id, tenant_id)
        await extract_entities(agent, document_id, tenant_id)

    await agent._publish_event(
        "knowledge.document.ingested",
        {
            "document_id": document_id,
            "tenant_id": tenant_id,
            "title": document.get("title"),
            "type": document.get("type"),
            "source": document.get("source"),
        },
    )

    await agent._publish_document_external(document)
    await agent._publish_event(
        "document.uploaded",
        {
            "document_id": document_id,
            "tenant_id": tenant_id,
            "title": document.get("title"),
            "type": document.get("type"),
            "uploaded_at": document.get("created_at"),
        },
    )

    return {
        "document_id": document_id,
        "title": document["title"],
        "version": document["version"],
        "type": document["type"],
        "tags": tags,
        "classification": classification,
        "topic": classification.get("topic"),
        "phase": classification.get("phase"),
        "domain": classification.get("domain"),
        "next_steps": "Document indexed and ready for search",
    }


async def get_document(
    agent: KnowledgeManagementAgent,
    document_id: str,
    access_context: dict[str, Any],
    tenant_id: str,
) -> dict[str, Any]:
    """
    Retrieve document with metadata.

    Returns full document.
    """
    agent.logger.info("Retrieving document: %s", document_id)

    document = agent._load_document(tenant_id, document_id)
    if not document:
        raise ValueError(f"Document not found: {document_id}")

    if not await agent._is_access_allowed(document, access_context):
        raise PermissionError("Access denied for requested document")

    # Update access count
    document["accessed_count"] = document.get("accessed_count", 0) + 1
    document["last_accessed_at"] = datetime.now(timezone.utc).isoformat()
    agent.document_store.upsert(tenant_id, document_id, document.copy())

    # Get summary if available
    summary = agent.summaries.get(document_id, {}).get("content")

    # Get related documents
    from knowledge_actions.search_actions import find_related_documents

    related_documents = await find_related_documents(agent, document_id)

    access_payload = {
        "document_id": document_id,
        "tenant_id": tenant_id,
        "accessed_at": document["last_accessed_at"],
        "actor": access_context.get("user_id"),
    }
    agent.knowledge_db.record_interaction(document_id, "access", access_payload)

    return {
        "document_id": document_id,
        "title": document.get("title"),
        "content": document.get("content"),
        "type": document.get("type"),
        "tags": document.get("tags"),
        "metadata": document.get("metadata"),
        "summary": summary,
        "version": document.get("version"),
        "author": document.get("author"),
        "created_at": document.get("created_at"),
        "modified_at": document.get("modified_at"),
        "accessed_count": document.get("accessed_count"),
        "related_documents": related_documents,
        "annotations": agent.document_annotations.get(document_id, []),
        "reviews": agent.document_reviews.get(document_id, []),
        "approvals": agent.document_approvals.get(document_id, []),
    }


async def update_document(
    agent: KnowledgeManagementAgent,
    document_id: str,
    updates: dict[str, Any],
    tenant_id: str,
) -> dict[str, Any]:
    """
    Update document and create new version.

    Returns updated document version.
    """
    agent.logger.info("Updating document: %s", document_id)

    document = agent._load_document(tenant_id, document_id)
    if not document:
        raise ValueError(f"Document not found: {document_id}")

    # Save current version
    if document_id not in agent.document_versions:
        agent.document_versions[document_id] = []
    agent.document_versions[document_id].append(document.copy())

    # Apply updates
    for key, value in updates.items():
        if key not in ["document_id", "created_at", "version"]:
            document[key] = value

    # Increment version
    document["version"] = document.get("version", 1) + 1
    document["modified_at"] = datetime.now(timezone.utc).isoformat()

    # Re-classify if content changed
    if "content" in updates:
        from knowledge_actions.classification_actions import auto_classify_document, summarize_document

        classification = await auto_classify_document(agent, document)
        document["type"] = classification.get("type")

        # Regenerate summary
        await summarize_document(agent, document_id, tenant_id)

    await agent._validate_document_schema(
        {
            "id": document_id,
            "tenant_id": tenant_id,
            "title": document.get("title"),
            "doc_type": await agent._map_doc_type_for_schema(document.get("type")),
            "status": document.get("status", "draft"),
            "classification": document.get("classification", "internal"),
            "owner": document.get("owner") or document.get("author") or "unknown",
            "created_at": document.get("created_at"),
            "updated_at": document.get("modified_at"),
            "metadata": document.get("metadata", {}),
        }
    )

    agent.document_store.upsert(tenant_id, document_id, document.copy())
    agent.knowledge_db.upsert_document(document)
    agent.knowledge_db.record_version(document)
    agent._index_document(document)
    await agent._update_graph_for_document(document)
    agent._update_classifier_with_document(document)

    await agent._publish_event(
        "knowledge.document.updated",
        {
            "document_id": document_id,
            "tenant_id": tenant_id,
            "version": document.get("version"),
            "changes": list(updates.keys()),
        },
    )
    await agent._publish_event(
        "document.updated",
        {
            "document_id": document_id,
            "tenant_id": tenant_id,
            "version": document.get("version"),
            "updated_at": document.get("modified_at"),
        },
    )

    return {
        "document_id": document_id,
        "version": document["version"],
        "modified_at": document["modified_at"],
        "changes": list(updates.keys()),
    }


async def delete_document(
    agent: KnowledgeManagementAgent, document_id: str, tenant_id: str
) -> dict[str, Any]:
    """
    Delete document (soft delete).

    Returns deletion confirmation.
    """
    agent.logger.info("Deleting document: %s", document_id)

    document = agent._load_document(tenant_id, document_id)
    if not document:
        raise ValueError(f"Document not found: {document_id}")

    # Soft delete
    document["deleted"] = True
    document["deleted_at"] = datetime.now(timezone.utc).isoformat()
    agent.document_store.upsert(tenant_id, document_id, document.copy())
    agent.knowledge_db.upsert_document(document)

    await agent._publish_event(
        "knowledge.document.deleted",
        {"document_id": document_id, "tenant_id": tenant_id},
    )
    await agent._publish_event(
        "document.deleted",
        {
            "document_id": document_id,
            "tenant_id": tenant_id,
            "deleted_at": document.get("deleted_at"),
        },
    )

    return {"document_id": document_id, "deleted": True, "deleted_at": document["deleted_at"]}


async def track_document_access(
    agent: KnowledgeManagementAgent, document_id: str, tenant_id: str
) -> dict[str, Any]:
    """
    Track document access patterns.

    Returns access statistics.
    """
    agent.logger.info("Tracking access for document: %s", document_id)

    document = agent._load_document(tenant_id, document_id)
    if not document:
        raise ValueError(f"Document not found: {document_id}")

    # Get access statistics
    interactions = agent.knowledge_db.list_interactions(document_id)
    unique_users = {
        interaction.get("payload", {}).get("actor")
        for interaction in interactions
        if interaction.get("interaction_type") == "access"
    }
    access_trend = "stable"
    if len(interactions) >= 2:
        access_trend = (
            "increasing"
            if interactions[-1]["created_at"] > interactions[0]["created_at"]
            else "stable"
        )
    access_stats = {
        "total_accesses": document.get("accessed_count", 0),
        "last_accessed": document.get("last_accessed_at"),
        "unique_users": len([user for user in unique_users if user]),
        "access_trend": access_trend,
    }

    return {"document_id": document_id, "access_stats": access_stats}


async def get_document_version_history(
    agent: KnowledgeManagementAgent, document_id: str, tenant_id: str
) -> dict[str, Any]:
    """
    Get document version history.

    Returns version list.
    """
    agent.logger.info("Retrieving version history for document: %s", document_id)

    if document_id not in agent.document_versions:
        raise ValueError(f"Document not found: {document_id}")

    versions = agent.document_versions.get(document_id, [])

    version_list = [
        {
            "version": v.get("version"),
            "modified_at": v.get("modified_at"),
            "author": v.get("author"),
        }
        for v in versions
    ]

    return {
        "document_id": document_id,
        "current_version": len(versions),
        "version_history": version_list,
    }
