"""
Graph Retrieval Service for GraphRAG-lite

Implements graph-based traversal for multi-hop entity queries.
Uses entity relationships to find connected KPI records.
"""

import os
from typing import Dict, List, Optional, Any, Set, Tuple
import logging
from dataclasses import dataclass
from collections import defaultdict

from src.services.entity_extractor import get_entity_extractor

logger = logging.getLogger(__name__)


@dataclass
class EntityNode:
    """Represents an entity node in the graph."""
    entity_type: str
    entity_value: str
    record_ids: Set[int]  # KPI record IDs that have this entity


class GraphRetriever:
    """
    Graph-based retrieval for multi-hop entity queries.
    
    Enables finding KPI records connected through entity relationships,
    e.g., "Show me all metrics related to the Finance department"
    would find all records with department=Finance or metrics that reference Finance.
    """
    
    def __init__(self):
        self.entity_extractor = get_entity_extractor()
        self.graph: Dict[str, EntityNode] = defaultdict(list)  # Key: entity_type:entity_value
        self.record_entities: Dict[int, List[Dict[str, str]]] = {}  # record_id -> list of entities
        self._graph_built = False
    
    def build_graph(self, kpi_records: List[Dict[str, Any]]) -> None:
        """
        Build entity graph from KPI records.
        
        Args:
            kpi_records: List of KPI record dictionaries
        """
        self.record_entities = {}
        
        for i, record in enumerate(kpi_records):
            entities = self.entity_extractor.extract_entities(record)
            self.record_entities[i] = entities
            
            # Add to graph
            for entity in entities:
                key = f"{entity['entity_type']}:{entity['entity_value']}"
                if key not in self.graph:
                    self.graph[key] = EntityNode(
                        entity_type=entity['entity_type'],
                        entity_value=entity['entity_value'],
                        record_ids=set()
                    )
                self.graph[key].record_ids.add(i)
        
        self._graph_built = True
        logger.info(f"Built graph with {len(self.graph)} entity nodes from {len(kpi_records)} records")
    
    def traverse(self, query_entities: List[str], max_hops: int = 2) -> Set[int]:
        """
        Traverse graph to find records connected to query entities.
        
        Args:
            query_entities: List of entities from query
            max_hops: Maximum number of hops to traverse
            
        Returns:
            Set of KPI record IDs matching the graph traversal
        """
        if not self._graph_built:
            logger.warning("Graph not built, returning empty set")
            return set()
        
        matched_records = set()
        visited_entities = set()
        
        # Start with direct matches
        for q_ent in query_entities:
            # Find all graph nodes containing this entity
            for key, node in self.graph.items():
                if node.entity_value.lower() == q_ent.lower():
                    matched_records.update(node.record_ids)
                    visited_entities.add(key)
        
        # Multi-hop traversal
        if max_hops > 1:
            for hop in range(1, max_hops):
                new_matches = set()
                
                # Find entities co-occurring with already matched records
                for record_id in matched_records:
                    if record_id in self.record_entities:
                        for entity in self.record_entities[record_id]:
                            key = f"{entity['entity_type']}:{entity['entity_value']}"
                            if key in self.graph and key not in visited_entities:
                                new_matches.update(self.graph[key].record_ids)
                                visited_entities.add(key)
                
                if new_matches:
                    matched_records.update(new_matches)
                else:
                    break
        
        logger.info(f"Graph traversal found {len(matched_records)} records from {len(query_entities)} query entities")
        return matched_records
    
    def get_related_entities(self, record_id: int, max_hops: int = 1) -> List[Dict[str, str]]:
        """
        Get entities related to a specific KPI record through graph traversal.
        
        Args:
            record_id: KPI record ID
            max_hops: Maximum number of hops
            
        Returns:
            List of related entities
        """
        if not self._graph_built or record_id not in self.record_entities:
            return []
        
        related_entities = []
        visited = set()
        
        for entity in self.record_entities[record_id]:
            key = f"{entity['entity_type']}:{entity['entity_value']}"
            if key in self.graph:
                # Find other records that share this entity
                for other_record_id in self.graph[key].record_ids:
                    if other_record_id != record_id and other_record_id in self.record_entities:
                        for other_entity in self.record_entities[other_record_id]:
                            other_key = f"{other_entity['entity_type']}:{other_entity['entity_value']}"
                            if other_key not in visited:
                                related_entities.append(other_entity)
                                visited.add(other_key)
        
        return related_entities
    
    def rank_by_entity_overlap(self, query: str, kpi_records: List[Dict[str, Any]], top_k: int = 10) -> List[int]:
        """
        Rank KPI records by entity overlap with query.
        
        Args:
            query: User query string
            kpi_records: List of KPI records
            top_k: Number of top records to return
            
        Returns:
            List of record IDs ranked by overlap score
        """
        # Extract query entities
        query_entities = self.entity_extractor.extract_query_entities(query)
        
        if not query_entities:
            # No entities found, return empty
            return []
        
        # Extract all KPI entities
        all_kpi_entities = []
        for record in kpi_records:
            entities = self.entity_extractor.extract_entities(record)
            all_kpi_entities.append(entities)
        
        # Calculate overlap scores
        overlap_scores = self.entity_extractor.find_entity_overlap(
            query_entities, all_kpi_entities
        )
        
        # Sort by score and return top K record IDs
        sorted_records = sorted(
            overlap_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        return [record_id for record_id, _ in sorted_records]


# Singleton instance
_graph_retriever = None

def get_graph_retriever() -> GraphRetriever:
    """Get the singleton graph retriever instance."""
    global _graph_retriever
    if _graph_retriever is None:
        _graph_retriever = GraphRetriever()
    return _graph_retriever


def graph_rag_enabled() -> bool:
    """GraphRAG-lite is opt-in via the USE_GRAPH_RAG env flag (default off)."""
    return os.getenv("USE_GRAPH_RAG", "false").strip().lower() in ("1", "true", "yes", "on")


def _rank_from_persisted_entities(query_entities, top_k: int = 6) -> List[Tuple[str, str, float]]:
    """Rank KPI records via the persisted ``kpi_entities`` table (ingest-time extraction).

    Returns ``[(title, content, score)]`` or ``[]`` if the table is empty / no overlap.
    """
    try:
        from src.services.pg_store import get_kpi_entities, get_kpi_metrics
        edf = get_kpi_entities()
        if edf is None or edf.empty:
            return []
        q = {e.lower() for e in query_entities}
        by_ref: Dict[str, set] = {}
        for ref, val in zip(edf["record_ref"], edf["entity_value"]):
            by_ref.setdefault(str(ref), set()).add(str(val).lower())
        scored = sorted(
            ((ref, len(q & vals)) for ref, vals in by_ref.items()),
            key=lambda x: -x[1],
        )
        scored = [s for s in scored if s[1] > 0][:top_k]
        if not scored:
            return []
        vmap: Dict[str, Tuple[Any, str]] = {}
        mdf = get_kpi_metrics()
        if mdf is not None and not mdf.empty:
            for _, r in mdf.iterrows():
                key = f"{r.get('category','')}|{r.get('metric','')}|{r.get('period','')}"
                vmap[key] = (r.get("value"), r.get("unit", "") or "")
        out: List[Tuple[str, str, float]] = []
        for ref, _score in scored:
            cat, metric, period = (ref.split("|") + ["", "", ""])[:3]
            value, unit = vmap.get(ref, (None, ""))
            unit = f" {unit}" if unit else ""
            val = f": {value}{unit}" if value is not None else ""
            out.append((
                f"KPI: {metric} ({cat}, {period})",
                f"{metric} for {cat} in {period}{val}.",
                1.0,
            ))
        return out
    except Exception as e:
        logger.warning("GraphRAG-lite persisted ranking failed: %s", e)
        return []


def graph_kpi_context(query: str, top_k: int = 6, min_entities: int = 2) -> List[Tuple[str, str, float]]:
    """GraphRAG-lite retrieval for the RAG context.

    When ``USE_GRAPH_RAG`` is on AND the query mentions at least ``min_entities``
    distinct entities (multi-hop intent, e.g. "headcount in Engineering vs Finance
    margin"), rank the KPI records by entity overlap (graph) and return the top ones
    as ``(title, content, score)`` tuples — the same shape the chatbot's vector
    retrieval returns, so they slot straight into the RAG prompt + sources.

    Returns ``[]`` (fall back to pure vector retrieval) when the flag is off, the
    query has too few entities, there is no KPI data, or anything fails. Safe to
    call unconditionally.
    """
    if not graph_rag_enabled():
        return []
    try:
        retriever = get_graph_retriever()
        query_entities = retriever.entity_extractor.extract_query_entities(query)
        if len(set(e.lower() for e in query_entities)) < min_entities:
            return []  # not multi-hop enough → let vector search handle it

        # Preferred path: rank using the persisted kpi_entities sidecar table
        # (populated at ingest). Falls back to the in-memory graph build below.
        persisted = _rank_from_persisted_entities(query_entities, top_k)
        if persisted:
            logger.info("GraphRAG-lite (persisted) selected %d records for %s",
                        len(persisted), query_entities)
            return persisted

        from src.services.pg_store import get_kpi_metrics
        df = get_kpi_metrics()
        if df is None or df.empty:
            return []

        records: List[Dict[str, Any]] = []
        for _, r in df.iterrows():
            records.append({
                "category": r.get("category", "") or "",
                "metric_name": r.get("metric", "") or "",   # pg column is `metric`
                "period": r.get("period", "") or "",
                "value": r.get("value"),
                "segment": r.get("segment", "") or "",
                "unit": r.get("unit", "") or "",
            })

        ranked_ids = retriever.rank_by_entity_overlap(query, records, top_k=top_k)
        results: List[Tuple[str, str, float]] = []
        for rid in ranked_ids:
            rec = records[rid]
            unit = f" {rec['unit']}" if rec["unit"] else ""
            seg = f" — segment {rec['segment']}" if rec["segment"] else ""
            title = f"KPI: {rec['metric_name']} ({rec['category']}, {rec['period']})"
            content = (
                f"{rec['metric_name']} for {rec['category']} in {rec['period']}: "
                f"{rec['value']}{unit}{seg}."
            )
            results.append((title, content, 1.0))

        if results:
            logger.info("GraphRAG-lite selected %d KPI records for entities %s",
                        len(results), query_entities)
        return results
    except Exception as e:  # never break the chat path
        logger.warning("GraphRAG-lite context failed (falling back to vector): %s", e)
        return []