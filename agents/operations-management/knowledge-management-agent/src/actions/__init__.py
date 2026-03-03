"""Action handlers for the Knowledge Management Agent."""

from actions.classification_actions import (
    auto_classify_document,
    capture_lesson_learned,
    categorize_lesson,
    classify_document,
    extract_metadata,
    find_similar_lessons,
    generate_tags,
    manage_taxonomy,
    summarize_document,
)
from actions.collaboration_actions import (
    annotate_document,
    approve_document,
    link_documents,
    review_document,
)
from actions.document_actions import (
    delete_document,
    get_document,
    get_document_version_history,
    track_document_access,
    update_document,
    upload_document,
)
from actions.ingestion_actions import (
    ingest_agent_output,
    ingest_sources,
)
from actions.knowledge_graph_actions import (
    build_knowledge_graph,
    extract_entities,
    query_knowledge_graph,
)
from actions.search_actions import (
    recommend_documents,
    search_documents,
)

__all__ = [
    # document
    "upload_document",
    "get_document",
    "update_document",
    "delete_document",
    "get_document_version_history",
    "track_document_access",
    # search
    "search_documents",
    "recommend_documents",
    # knowledge graph
    "extract_entities",
    "build_knowledge_graph",
    "query_knowledge_graph",
    # ingestion
    "ingest_sources",
    "ingest_agent_output",
    # classification / NLP
    "classify_document",
    "summarize_document",
    "capture_lesson_learned",
    "manage_taxonomy",
    "auto_classify_document",
    "extract_metadata",
    "generate_tags",
    "categorize_lesson",
    "find_similar_lessons",
    # collaboration
    "annotate_document",
    "review_document",
    "approve_document",
    "link_documents",
]
