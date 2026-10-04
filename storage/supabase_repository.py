"""Persistence boundary between the KALATRACE kernel and Supabase.

The repository maps the existing epistemic model to the existing Supabase
schema. It deliberately does not change the database schema.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from supabase import create_client


class SupabasePersistenceError(RuntimeError):
    pass


class SupabaseRepository:
    def __init__(self, url=None, key=None):
        url = url or os.getenv("KALATRACE_SUPABASE_URL")
        key = key or os.getenv("KALATRACE_SUPABASE_KEY")
        if not url or not key:
            raise SupabasePersistenceError(
                "Configure KALATRACE_SUPABASE_URL and KALATRACE_SUPABASE_KEY."
            )
        self.client = create_client(url, key)

    @staticmethod
    def stable_uuid(kind, external_id):
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"kalatrace:{kind}:{external_id}"))

    @staticmethod
    def iso(value):
        value = value or datetime.now(timezone.utc)
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()

    def persist_graph(self, graph, evidence_store, owner_id):
        counts = {"iecs": 0, "nodes": 0, "edges": 0, "evidence": 0}

        for iec in graph.nodes.values():
            iec_id = self.stable_uuid("iec", str(iec.id))
            node_id = self.stable_uuid("node", str(iec.id))

            self.client.table("iecs").upsert({
                "id": iec_id,
                "owner_id": owner_id,
                "name": str(iec.id),
                "statement": iec.content,
                "methodology": {
                    "domain": iec.domain,
                    "external_id": str(iec.id),
                    "sources": list(iec.sources),
                },
                "result": {"confidence": float(iec.confidence)},
                "updated_at": self.iso(iec.updated_at),
            }).execute()

            self.client.table("knowledge_nodes").upsert({
                "id": node_id,
                "owner_id": owner_id,
                "node_type": "iec",
                "label": str(iec.id),
                "description": iec.content,
                "properties": {
                    "external_id": str(iec.id),
                    "domain": iec.domain,
                    "confidence": float(iec.confidence),
                },
                "updated_at": self.iso(iec.updated_at),
            }).execute()

            self.client.table("iec_nodes").upsert({
                "iec_id": iec_id,
                "node_id": node_id,
                "relation_type": "derived_from",
            }).execute()
            counts["iecs"] += 1
            counts["nodes"] += 1

        for edge in graph.edges:
            external_id = (
                f"{edge['source']}::{edge['target']}::{edge.get('type', 'related')}"
            )
            self.client.table("knowledge_edges").upsert({
                "id": self.stable_uuid("edge", external_id),
                "owner_id": owner_id,
                "source_node_id": self.stable_uuid("node", str(edge["source"])),
                "target_node_id": self.stable_uuid("node", str(edge["target"])),
                "edge_type": edge.get("type", "related"),
                "properties": {
                    "external_id": external_id,
                    "weight": float(edge.get("weight", 1.0)),
                    "confidence": float(edge.get("confidence", 0.5)),
                    "evidence": edge.get("evidence", []),
                },
            }).execute()
            counts["edges"] += 1

        for evidence in evidence_store.evidences.values():
            self.client.table("evidence").upsert({
                "id": self.stable_uuid("evidence", str(evidence["id"])),
                "owner_id": owner_id,
                "evidence_type": evidence.get("source_type", "unknown"),
                "content": evidence["content"],
                "reliability": float(evidence.get("reliability", 0.5)),
                "metadata": {
                    "external_id": str(evidence["id"]),
                    "iec_external_ids": sorted(
                        evidence.get("linked_iec", set())
                    ),
                },
            }).execute()
            counts["evidence"] += 1

        return counts

    def recover_graph(self, owner_id):
        return {
            "iecs": self.client.table("iecs")
                .select("*").eq("owner_id", owner_id).execute().data,
            "knowledge_nodes": self.client.table("knowledge_nodes")
                .select("*").eq("owner_id", owner_id).execute().data,
            "knowledge_edges": self.client.table("knowledge_edges")
                .select("*").eq("owner_id", owner_id).execute().data,
            "evidence": self.client.table("evidence")
                .select("*").eq("owner_id", owner_id).execute().data,
        }
