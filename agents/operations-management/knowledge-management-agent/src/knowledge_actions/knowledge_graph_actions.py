"""Knowledge graph and entity extraction action handlers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from knowledge_utils import graph_document_id, graph_entity_id, graph_risk_id

if TYPE_CHECKING:
    from knowledge_management_agent import KnowledgeManagementAgent


async def extract_entities(
    agent: KnowledgeManagementAgent, document_id: str, tenant_id: str
) -> dict[str, Any]:
    """
    Extract entities from document using NLP.

    Returns extracted entities.
    """
    agent.logger.info("Extracting entities from document: %s", document_id)

    document = agent._load_document(tenant_id, document_id)
    if not document:
        raise ValueError(f"Document not found: {document_id}")

    # Extract entities using NLP
    entities = agent.entity_extractor.extract(document.get("content", ""), limit=20)

    # Store in knowledge graph
    if document_id not in agent.knowledge_graph:
        agent.knowledge_graph[document_id] = {"entities": [], "relationships": []}

    agent.knowledge_graph[document_id]["entities"] = entities
    document_node = graph_document_id(document_id)
    agent._register_graph_node(
        document_node,
        "document",
        {"title": document.get("title"), "doc_type": document.get("type")},
    )
    for entity in entities:
        entity_node = graph_entity_id(entity.get("text"))
        agent._register_graph_node(entity_node, "entity", entity)
        agent._register_graph_edge(document_node, entity_node, "mentions")
    agent.knowledge_db.upsert_graph(agent.graph_nodes, agent.graph_edges)

    return {"document_id": document_id, "entities": entities, "entity_count": len(entities)}


async def build_knowledge_graph(
    agent: KnowledgeManagementAgent, document_id: str, tenant_id: str
) -> dict[str, Any]:
    """
    Build knowledge graph relationships.

    Returns graph structure.
    """
    agent.logger.info("Building knowledge graph for document: %s", document_id)

    document = agent._load_document(tenant_id, document_id)
    if not document:
        raise ValueError(f"Document not found: {document_id}")

    # Get entities
    entities = agent.knowledge_graph.get(document_id, {}).get("entities", [])

    # Build relationships
    relationships = await _build_entity_relationships(document_id, entities)

    # Update knowledge graph
    if document_id not in agent.knowledge_graph:
        agent.knowledge_graph[document_id] = {"entities": [], "relationships": []}

    agent.knowledge_graph[document_id]["relationships"] = relationships
    agent.knowledge_db.upsert_graph(agent.graph_nodes, agent.graph_edges)

    return {
        "document_id": document_id,
        "entities": len(entities),
        "relationships": len(relationships),
        "graph": agent.knowledge_graph[document_id],
    }


async def query_knowledge_graph(
    agent: KnowledgeManagementAgent, query: dict[str, Any]
) -> dict[str, Any]:
    """Query graph relationships for insights."""
    query_type = query.get("type", "traverse")
    if query_type == "impact_analysis":
        risk = query.get("risk")
        if not risk:
            raise ValueError("Missing risk for impact analysis")
        risk_node = graph_risk_id(risk)
        impacted = agent._traverse_graph(risk_node, target_type="project")
        return {"risk": risk, "impacted_projects": impacted}

    start_node = query.get("start_node")
    relation = query.get("relation")
    target_type = query.get("target_type")
    if not start_node:
        raise ValueError("Missing start_node for graph query")
    results = agent._traverse_graph(start_node, relation, target_type)
    return {
        "start_node": start_node,
        "relation": relation,
        "target_type": target_type,
        "results": results,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _build_entity_relationships(
    document_id: str, entities: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Build relationships between entities."""
    relationships = []

    for i, entity1 in enumerate(entities):
        for entity2 in entities[i + 1 :]:
            relationships.append(
                {
                    "from": entity1.get("text"),
                    "to": entity2.get("text"),
                    "type": "related",
                    "confidence": 0.6,
                }
            )

    return relationships
