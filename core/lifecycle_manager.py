from datetime import datetime, timezone


class LifecycleManager:
    """
    Orquestrador central do ciclo de vida do conhecimento no KALATRACE.

    A persistência é opcional: o Kernel continua funcionando em memória,
    mas pode agora salvar e reconstruir seu estado epistemológico.
    """

    def __init__(
        self,
        graph,
        evidence_store,
        validator,
        reasoner,
        persistence=None,
    ):
        self.graph = graph
        self.evidence_store = evidence_store
        self.validator = validator
        self.reasoner = reasoner
        self.persistence = persistence

    def create_iec(self, iec):
        iec.created_at = datetime.now(timezone.utc)
        self.graph.add_node(iec)
        return iec.id

    def attach_evidence(self, iec_id, evidence_id, content, reliability=0.5):
        self.evidence_store.add_evidence(
            evidence_id=evidence_id,
            content=content,
            reliability=reliability,
        )
        self.evidence_store.link_to_iec(evidence_id, iec_id)

    def connect(self, source_id, target_id, relation_type="related", weight=1.0):
        self.graph.add_edge(
            source=source_id,
            target=target_id,
            relation_type=relation_type,
            weight=weight,
        )

    def validate(self, iec_id=None):
        if iec_id:
            return self.validator.validate_iec(iec_id)
        if hasattr(self.validator, "validate_all"):
            return self.validator.validate_all()
        return self.validator.validate_graph()

    def reason(self, iec_id):
        return self.reasoner.infer_connections(iec_id)

    def update_iec(self, iec_id):
        iec = self.graph.get_node(iec_id)
        if not iec:
            return None

        validation_result = self.validator.validate_iec(iec_id)
        self.reasoner.propagate_confidence(iec_id)
        iec.updated_at = datetime.now(timezone.utc)
        return validation_result

    def persist(self, owner_id):
        """Persiste o estado epistemológico atual no backend configurado."""
        if self.persistence is None:
            raise RuntimeError("Nenhuma camada de persistência foi configurada.")
        return self.persistence.persist_graph(
            self.graph,
            self.evidence_store,
            owner_id,
        )

    def restore(self, owner_id):
        """
        Reconstrói o estado em memória a partir do Supabase.

        Retorna contagens e mantém os mesmos IDs externos usados pelo Kernel.
        """
        if self.persistence is None:
            raise RuntimeError("Nenhuma camada de persistência foi configurada.")

        from knowledge.iec import IEC

        state = self.persistence.recover_graph(owner_id)

        self.graph.nodes.clear()
        self.graph.edges.clear()
        self.evidence_store.evidences.clear()
        self.evidence_store.iec_index.clear()

        node_by_db_id = {}

        for row in state["iecs"]:
            methodology = row.get("methodology") or {}
            result = row.get("result") or {}
            external_id = methodology.get("external_id") or row["name"]

            iec = IEC(
                id=external_id,
                content=row["statement"],
                domain=methodology.get("domain"),
            )
            iec.sources = list(methodology.get("sources") or [])
            iec.confidence = float(result.get("confidence", 0.5))
            iec.created_at = row.get("created_at")
            iec.updated_at = row.get("updated_at")

            self.graph.add_node(iec)
            node_by_db_id[
                self.persistence.stable_uuid("node", str(external_id))
            ] = external_id

        for row in state["knowledge_edges"]:
            props = row.get("properties") or {}
            source = node_by_db_id.get(row["source_node_id"])
            target = node_by_db_id.get(row["target_node_id"])
            if source is None or target is None:
                continue

            self.graph.add_edge(
                source=source,
                target=target,
                relation_type=row.get("edge_type", "related"),
                weight=float(props.get("weight", 1.0)),
                confidence=float(props.get("confidence", 0.5)),
                evidence=props.get("evidence", []),
            )

        for row in state["evidence"]:
            metadata = row.get("metadata") or {}
            external_id = metadata.get("external_id") or row["id"]
            self.evidence_store.add_evidence(
                evidence_id=external_id,
                content=row.get("content") or "",
                source_type=row.get("evidence_type", "unknown"),
                reliability=float(row.get("reliability") or 0.5),
            )
            for iec_id in metadata.get("iec_external_ids", []):
                self.evidence_store.link_to_iec(external_id, iec_id)

        return {
            "iecs": len(self.graph.nodes),
            "edges": len(self.graph.edges),
            "evidence": len(self.evidence_store.evidences),
        }

    def remove_iec(self, iec_id, threshold=0.2):
        iec = self.graph.get_node(iec_id)
        if not iec or iec.confidence > threshold:
            return False
        self.graph.remove_node(iec_id)
        return True

    def run_cycle(self):
        if hasattr(self.validator, "report"):
            report = self.validator.report()
        else:
            report = self.validator.validate_graph()

        if hasattr(self.validator, "weak_knowledge"):
            weak = self.validator.weak_knowledge()
        else:
            weak = self.validator.weak_nodes()

        removed = []

        if hasattr(self.validator, "validate_all"):
            self.validator.validate_all()
        else:
            self.validator.validate_graph()

        for iec_id in list(self.graph.nodes):
            self.reasoner.propagate_confidence(iec_id)

        for item in weak:
            iec_id = item.id if hasattr(item, "id") else item.get("iec")
            if iec_id and self.remove_iec(iec_id):
                removed.append(iec_id)

        return {
            "report": report,
            "removed_nodes": removed,
        }

    def status(self):
        quality = (
            self.validator.system_quality_score()
            if hasattr(self.validator, "system_quality_score")
            else self.validator.validate_graph()
        )
        return {
            "graph": self.graph.stats(),
            "evidence": self.evidence_store.stats(),
            "system_quality": quality,
            "persistence": self.persistence is not None,
        }
