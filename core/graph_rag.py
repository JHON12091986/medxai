"""
NINA GraphRAG Integration (LT-3)
Combines vector/keyword similarity lookups with multi-hop knowledge graph traversals.
"""
from __future__ import annotations
import logging
from typing import Any, Dict, Set
from .knowledge_graph import knowledge_graph
from .knowledge import recall

logger = logging.getLogger("nina.core.graph_rag")

class GraphRAG:
    def __init__(self, kg: Any = None) -> None:
        self.kg = kg or knowledge_graph

    async def hybrid_query(self, query: str, max_depth: int = 2) -> Dict[str, Any]:
        """
        Performs vector-substitute keyword/similarity query, 
        identifies matched entity nodes in the NetworkX graph,
        performs multi-hop traversals to collect neighboring context,
        and returns the unified context result.
        """
        logger.info(f"GraphRAG performing hybrid query: '{query}'")
        
        # 1. Retrieve raw database records
        db_results = recall(query)
        
        # 2. Extract entities associated with the query from knowledge base
        matched_entities: Set[str] = set()
        for term in query.lower().split():
            if len(term) < 4:
                continue
            # Simple substring node-matching heuristics
            for entity_id in self.kg.get_all_entities_by_type("concept").keys():
                if term in entity_id.lower():
                    matched_entities.add(entity_id)
            for entity_id in self.kg.get_all_entities_by_type("file").keys():
                if term in entity_id.lower():
                    matched_entities.add(entity_id)

        # 3. Perform multi-hop graph traversal starting from matched entities
        traversed_entities: Dict[str, Any] = {}
        for start_entity in matched_entities:
            await self._traverse_graph_recursive(start_entity, traversed_entities, depth=0, max_depth=max_depth)

        # 4. Format into beautifully detailed output
        graph_text = []
        if traversed_entities:
            graph_text.append("[KNOWLEDGE GRAPH MULTI-HOP CONTEXT]")
            for entity_id, properties in traversed_entities.items():
                ent_type = properties.get("type", "unknown")
                props_str = ", ".join([f"{k}={v}" for k, v in properties.items() if k != "type"])
                graph_text.append(f"• Entity: {entity_id} ({ent_type}) -> {props_str}")
        else:
            graph_text.append("• No multi-hop graph relations matched the query terms.")

        unified_context = (
            f"[VECTOR DATABASE RESULTS]\n{db_results}\n\n" +
            "\n".join(graph_text)
        )
        
        return {
            "query": query,
            "db_results": db_results,
            "entities_found": list(matched_entities),
            "traversed_entities": traversed_entities,
            "context": unified_context
        }

    async def _traverse_graph_recursive(self, node_id: str, visited: Dict[str, Any], depth: int, max_depth: int) -> None:
        if depth > max_depth or node_id in visited:
            return
        
        props = self.kg.get_entity(node_id)
        if props:
            visited[node_id] = props
            
        neighbors = self.kg.query_neighbors(node_id)
        for neighbor in neighbors:
            await self._traverse_graph_recursive(neighbor, visited, depth + 1, max_depth)


# Global GraphRAG singleton
graph_rag = GraphRAG()
