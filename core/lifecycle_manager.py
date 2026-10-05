from datetime import datetime


class LifecycleManager:
    """Orquestrador central do ciclo de vida do conhecimento."""

    def __init__(self, graph, evidence_store, validator, reasoner):
        self.graph = graph
        self.evidence_store = evidence_store
        self.validator = validator
        self.reasoner = reasoner

    def create_iec(self, iec):
        iec.created_at = datetime.now()
        self.graph.add_node(iec)
        return iec.id

    def attach_evidence(self, iec_id, evidence_id, content, reliability=0.5,
                        source_type="unknown", provenance=None):
        self.evidence_store.add_evidence(
            evidence_id=evidence_id, content=content, reliability=reliability,
            source_type=source_type, provenance=provenance,
        )
        self.evidence_store.link_to_iec(evidence_id, iec_id)

    def connect(self, source_id, target_id, relation_type="related", weight=1.0):
        self.graph.add_edge(source=source_id, target=target_id, relation_type=relation_type, weight=weight)

    def validate(self, iec_id=None):
        return self.validator.validate_iec(iec_id) if iec_id else self.validator.validate_all()

    def reason(self, iec_id):
        return self.reasoner.infer_connections(iec_id)

    def promote_relation(self, source_id, target_id, evidence_ids,
                         relation_type="supports", weight=1.0, threshold=0.75):
        decision = self.validator.evaluate_edge_candidate(
            source_id, target_id, evidence_ids, weight=weight, threshold=threshold
        )
        if not decision["eligible"]:
            return {"promoted": False, "decision": decision}

        conflict = self.validator.evaluate_relation_conflict(source_id, target_id, candidate_relation_type=relation_type)
        if conflict["conflict"]:
            decision["status"] = "conflicted"
            decision["conflict"] = dict(conflict)
            decision["conflict"]["candidate_evidence"] = list(evidence_ids)
            decision["conflict"]["candidate_relation_type"] = relation_type

        self.graph.add_edge(
            source=source_id, target=target_id, relation_type=relation_type,
            weight=weight, confidence=decision["score"], evidence=list(evidence_ids),
        )
        return {"promoted": True, "decision": decision}

    def update_iec(self, iec_id):
        iec = self.graph.get_node(iec_id)
        if not iec:
            return None
        validation_result = self.validator.validate_iec(iec_id)
        self.reasoner.propagate_confidence(iec_id)
        iec.updated_at = datetime.now()
        return validation_result

    def remove_iec(self, iec_id, threshold=0.2):
        iec = self.graph.get_node(iec_id)
        if not iec or iec.confidence > threshold:
            return False
        self.graph.remove_node(iec_id)
        return True

    def run_cycle(self):
        report = self.validator.report()
        weak = self.validator.weak_knowledge()
        removed = []
        self.validator.validate_all()
        for iec_id in self.graph.nodes:
            self.reasoner.propagate_confidence(iec_id)
        for iec in weak:
            if self.remove_iec(iec.id):
                removed.append(iec.id)
        return {"report": report, "removed_nodes": removed}

    def status(self):
        return {
            "graph": self.graph.stats(),
            "evidence": self.evidence_store.stats(),
            "system_quality": self.validator.system_quality_score(),
        }
