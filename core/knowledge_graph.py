"""core/knowledge_graph.py — Lightweight knowledge graph for NINA vNext.

Provides entity-relationship storage and GraphRAG-style retrieval:
  - Entity nodes with typed attributes stored in NetworkX DiGraph
  - Relation edges with confidence scores and provenance
  - ChromaDB-backed semantic search over entity descriptions
  - Multi-hop neighbour traversal and shortest-path queries
  - GraphRAG context builder: given a query, returns ranked
    entity+relation context passages for LLM grounding

Design rules:
  - All mutations are idempotent (upsert semantics).
  - Graph is persisted to disk as GEXF + ChromaDB collection.
  - Operations fail open: errors are logged, not raised.
  - Thread-safe via asyncio.Lock on write paths.

Dependencies (add to requirements.txt):
    networkx>=3.3
    chromadb  (already present)

Usage:
    from core.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    await kg.add_entity("NINA", entity_type="system",
                        description="Personal AI operating system")
    await kg.add_relation("NINA", "uses", "ChromaDB",
                          confidence=0.95, source="codebase")
    context = await kg.graphrag_context("What does NINA use for memory?")
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger("nina.kg")

KG_DIR       = Path(os.getenv("NINA_KG_DIR", "./data/knowledge_graph"))
GEXF_PATH    = KG_DIR / "graph.gexf"
MAX_HOPS     = int(os.getenv("NINA_KG_MAX_HOPS", "3"))
TOP_K        = int(os.getenv("NINA_KG_TOP_K", "10"))
COLLECTION   = "nina_kg_entities"


@dataclass
class Entity:
    name:        str
    entity_type: str  = "concept"
    description: str  = ""
    attributes:  dict = field(default_factory=dict)
    created_at:  str  = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at:  str  = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __getitem__(self, key: str) -> Any:
        if key == "type":
            return self.entity_type
        if hasattr(self, key):
            return getattr(self, key)
        if key in self.attributes:
            return self.attributes[key]
        raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key: str) -> Any:
        if key == "type":
            return self.entity_type
        if hasattr(self, key):
            return getattr(self, key)
        if key in self.attributes:
            return self.attributes[key]
        raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default


@dataclass
class Relation:
    source:     str
    relation:   str
    target:     str
    confidence: float = 1.0
    source_ref: str   = ""
    created_at: str   = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_text(self) -> str:
        return f"{self.source} --[{self.relation}]--> {self.target}"


@dataclass
class GraphRAGContext:
    query:     str
    entities:  list[Entity]
    relations: list[Relation]
    passages:  list[str]

    def to_prompt_block(self) -> str:
        if not self.passages:
            return ""
        lines = ["[Knowledge Graph Context]"] + self.passages[:8]
        return "\n".join(lines)


class KnowledgeGraph:
    """Entity-relationship graph with semantic retrieval."""

    def __init__(self, chroma_client: Any = None, file_path: str | Path | None = None):
        self._lock   = asyncio.Lock()
        self._chroma = chroma_client
        self._coll   = None
        self._graph  = None
        self._ready  = False
        self.file_path = file_path

    async def init(self) -> None:
        """Initialise graph and ChromaDB collection. Call once at startup."""
        import networkx as nx
        KG_DIR.mkdir(parents=True, exist_ok=True)
        if GEXF_PATH.exists():
            try:
                self._graph = nx.read_gexf(str(GEXF_PATH))
                log.info("kg: loaded graph — %d nodes %d edges",
                         self._graph.number_of_nodes(),
                         self._graph.number_of_edges())
            except Exception as exc:
                log.warning("kg: could not load graph, starting fresh: %s", exc)
                self._graph = nx.DiGraph()
        else:
            self._graph = nx.DiGraph()

        if self._chroma is not None:
            try:
                self._coll = self._chroma.get_or_create_collection(
                    COLLECTION,
                    metadata={"hnsw:space": "cosine"},
                )
                log.info("kg: chroma collection ready (%d entities)",
                         self._coll.count())
            except Exception as exc:
                log.warning("kg: chroma init failed: %s", exc)
        self._ready = True

    # ── write operations ──────────────────────────────────────────────

    async def add_entity(
        self,
        name: str,
        entity_type: str = "concept",
        description: str = "",
        attributes: dict | None = None,
    ) -> Entity:
        """Upsert an entity node."""
        async with self._lock:
            if isinstance(description, dict):
                attributes = (attributes or {}) | description
                description = ""
            entity = Entity(
                name=name,
                entity_type=entity_type,
                description=description,
                attributes=attributes or {},
            )
            self._ensure_graph()
            if self._graph.has_node(name):
                # Update existing
                node_attrs = self._graph.nodes[name]
                node_attrs.update({
                    "entity_type": entity_type,
                    "description": description,
                    "updated_at":  entity.updated_at,
                })
                existing_attribs = node_attrs.get("attributes", {})
                node_attrs["attributes"] = existing_attribs | (attributes or {})
            else:
                self._graph.add_node(
                    name,
                    entity_type=entity_type,
                    description=description,
                    created_at=entity.created_at,
                    updated_at=entity.updated_at,
                    attributes=attributes or {},
                )
            await self._upsert_chroma(entity)
            self._persist()
            return entity

    async def add_relation(
        self,
        source: str,
        relation: str,
        target: str,
        confidence: float = 1.0,
        source_ref: str = "",
    ) -> Relation:
        """Upsert a directed relation edge."""
        async with self._lock:
            rel = Relation(
                source=source, relation=relation, target=target,
                confidence=confidence, source_ref=source_ref,
            )
            self._ensure_graph()
            # Auto-create missing nodes
            for node in (source, target):
                if not self._graph.has_node(node):
                    self._graph.add_node(
                        node,
                        entity_type="concept",
                        description="",
                        created_at=rel.created_at,
                        updated_at=rel.created_at,
                    )
            self._graph.add_edge(
                source, target,
                relation=relation,
                confidence=confidence,
                source_ref=source_ref,
                created_at=rel.created_at,
            )
            self._persist()
            return rel

    async def remove_entity(self, name: str) -> bool:
        """Remove an entity and all its edges."""
        async with self._lock:
            self._ensure_graph()
            if not self._graph.has_node(name):
                return False
            self._graph.remove_node(name)
            if self._coll:
                try:
                    self._coll.delete(ids=[name])
                except Exception:
                    pass
            self._persist()
            return True

    # ── read operations ───────────────────────────────────────────────

    async def get_entity(self, name: str) -> Entity | None:
        """Retrieve a single entity by name."""
        self._ensure_graph()
        if not self._graph.has_node(name):
            return None
        attrs = self._graph.nodes[name]
        return Entity(
            name=name,
            entity_type=attrs.get("entity_type", "concept"),
            description=attrs.get("description", ""),
            attributes=attrs.get("attributes", {}),
            created_at=attrs.get("created_at", ""),
            updated_at=attrs.get("updated_at", ""),
        )

    async def get_neighbours(
        self,
        name: str,
        hops: int = 1,
        relation_filter: str | None = None,
    ) -> list[Relation]:
        """Return all relations within N hops of an entity."""
        self._ensure_graph()
        if not self._graph.has_node(name):
            return []
        import networkx as nx
        visited: set[str] = {name}
        frontier: set[str] = {name}
        relations: list[Relation] = []
        for _ in range(min(hops, MAX_HOPS)):
            next_frontier: set[str] = set()
            for node in frontier:
                for nbr in self._graph.successors(node):
                    edge = self._graph.edges[node, nbr]
                    rel_type = edge.get("relation", "related")
                    if relation_filter and rel_type != relation_filter:
                        continue
                    relations.append(Relation(
                        source=node,
                        relation=rel_type,
                        target=nbr,
                        confidence=edge.get("confidence", 1.0),
                        source_ref=edge.get("source_ref", ""),
                        created_at=edge.get("created_at", ""),
                    ))
                    if nbr not in visited:
                        next_frontier.add(nbr)
                        visited.add(nbr)
            frontier = next_frontier
        return relations

    async def shortest_path(
        self, source: str, target: str
    ) -> list[str] | None:
        """Return the shortest directed path between two entities."""
        self._ensure_graph()
        import networkx as nx
        try:
            return nx.shortest_path(self._graph, source=source, target=target)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    async def search_entities(
        self, query: str, top_k: int = TOP_K
    ) -> list[Entity]:
        """Semantic search over entity descriptions via ChromaDB."""
        if not self._coll:
            return self._keyword_search(query, top_k)
        try:
            results = self._coll.query(
                query_texts=[query],
                n_results=min(top_k, max(1, self._coll.count())),
                include=["metadatas", "ids"],
            )
            ids   = (results.get("ids")       or [[]])[0]
            metas = (results.get("metadatas") or [[]])[0]
            entities = []
            for eid, meta in zip(ids, metas):
                entities.append(Entity(
                    name=eid,
                    entity_type=meta.get("entity_type", "concept"),
                    description=meta.get("description", ""),
                ))
            return entities
        except Exception as exc:
            log.debug("kg: chroma search failed: %s", exc)
            return self._keyword_search(query, top_k)

    async def graphrag_context(
        self,
        query: str,
        top_k: int = TOP_K,
        hops: int = 2,
    ) -> GraphRAGContext:
        """Build a GraphRAG context block for LLM grounding.

        1. Semantic search finds seed entities matching the query.
        2. Graph traversal expands to related entities within N hops.
        3. Returns ranked passages: entity descriptions + relations.
        """
        seed_entities = await self.search_entities(query, top_k=top_k // 2 or 5)
        all_relations: list[Relation] = []
        all_entities  = list(seed_entities)
        seen_names    = {e.name for e in seed_entities}

        for entity in seed_entities:
            rels = await self.get_neighbours(entity.name, hops=hops)
            for rel in rels:
                all_relations.append(rel)
                for node_name in (rel.source, rel.target):
                    if node_name not in seen_names:
                        e = await self.get_entity(node_name)
                        if e:
                            all_entities.append(e)
                            seen_names.add(node_name)

        # Build text passages
        passages: list[str] = []
        for entity in all_entities[:top_k]:
            if entity.description:
                passages.append(
                    f"Entity [{entity.entity_type}] {entity.name}: {entity.description}"
                )
        for rel in all_relations[:top_k]:
            passages.append(f"Relation: {rel.to_text()}"
                            + (f" (conf={rel.confidence:.2f})" if rel.confidence < 1 else ""))

        # Deduplicate
        seen: set[str] = set()
        deduped = []
        for p in passages:
            if p not in seen:
                deduped.append(p)
                seen.add(p)

        return GraphRAGContext(
            query=query,
            entities=all_entities,
            relations=all_relations,
            passages=deduped,
        )

    def stats(self) -> dict:
        """Return graph statistics."""
        self._ensure_graph()
        return {
            "nodes":    self._graph.number_of_nodes(),
            "edges":    self._graph.number_of_edges(),
            "chroma":   self._coll.count() if self._coll else 0,
        }

    # ── internals ──────────────────────────────────────────────────────

    def _ensure_graph(self) -> None:
        if self._graph is None:
            import networkx as nx
            self._graph = nx.DiGraph()
            if self.file_path:
                path = Path(self.file_path)
                if path.exists():
                    try:
                        if path.suffix == ".json":
                            data = json.loads(path.read_text())
                            for node_id, attrs in data.get("nodes", {}).items():
                                self._graph.add_node(node_id, **attrs)
                            for edge in data.get("edges", []):
                                self._graph.add_edge(edge["source"], edge["target"], **edge.get("attrs", {}))
                        else:
                            self._graph = nx.read_gexf(str(path))
                    except Exception as exc:
                        log.warning("kg: could not load from file_path %s: %s", self.file_path, exc)

    def _persist(self) -> None:
        try:
            import networkx as nx
            if self.file_path:
                path = Path(self.file_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                if path.suffix == ".json":
                    nodes = {node: attrs for node, attrs in self._graph.nodes(data=True)}
                    edges = []
                    for u, v, attrs in self._graph.edges(data=True):
                        edges.append({"source": u, "target": v, "attrs": attrs})
                    data = {"nodes": nodes, "edges": edges}
                    path.write_text(json.dumps(data, indent=2))
                else:
                    nx.write_gexf(self._graph, str(path))
            else:
                nx.write_gexf(self._graph, str(GEXF_PATH))
        except Exception as exc:
            log.debug("kg: persist failed: %s", exc)

    def save(self) -> None:
        self._persist()

    def get_all_entities_by_type(self, type_name: str) -> dict:
        self._ensure_graph()
        return {
            node: attrs for node, attrs in self._graph.nodes(data=True)
            if attrs.get("entity_type") == type_name
        }

    def query_neighbors(self, node_id: str) -> list:
        self._ensure_graph()
        if node_id in self._graph:
            return list(self._graph.neighbors(node_id))
        return []

    async def _upsert_chroma(
        self, entity: Entity
    ) -> None:
        if not self._coll:
            return
        try:
            text = entity.description or entity.name
            self._coll.upsert(
                ids=[entity.name],
                documents=[text],
                metadatas=[{
                    "entity_type": entity.entity_type,
                    "description": entity.description,
                    "updated_at":  entity.updated_at,
                }],
            )
        except Exception as exc:
            log.debug("kg: chroma upsert failed: %s", exc)

    def _keyword_search(
        self, query: str, top_k: int
    ) -> list[Entity]:
        """Fallback keyword search when ChromaDB is unavailable."""
        self._ensure_graph()
        q = query.lower()
        results = []
        for node, attrs in self._graph.nodes(data=True):
            text = (node + " " + attrs.get("description", "")).lower()
            if q in text:
                results.append(Entity(
                    name=node,
                    entity_type=attrs.get("entity_type", "concept"),
                    description=attrs.get("description", ""),
                ))
            if len(results) >= top_k:
                break
        return results

knowledge_graph = KnowledgeGraph()
