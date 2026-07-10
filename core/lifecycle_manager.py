from datetime import datetime


class LifecycleManager:
    """
    Orquestrador central do ciclo de vida do conhecimento no KALATRACE.
    """

    def __init__(self, graph, evidence_store, validator, reasoner):
        self.graph = graph
        self.evidence_store = evidence_store
        self.validator = validator
        self.reasoner = reasoner

    # -----------------------------
    # 1. CRIAÇÃO DE CONHECIMENTO
    # -----------------------------
    def create_iec(self, iec):
        """
        Registra um novo IEC no sistema.
        """

        iec.created_at = datetime.now()
        self.graph.add_node(iec)

        return iec.id

    # -----------------------------
    # 2. REGISTRO DE EVIDÊNCIA
    # -----------------------------
    def attach_evidence(self, iec_id, evidence_id, content, reliability=0.5):
        """
        Cria e vincula evidência a um IEC.
        """

        self.evidence_store.add_evidence(
            evidence_id=evidence_id,
            content=content,
            reliability=reliability
        )

        self.evidence_store.link_to_iec(evidence_id, iec_id)

    # -----------------------------
    # 3. CONECTAR CONHECIMENTO
    # -----------------------------
    def connect(self, source_id, target_id, relation_type="related", weight=1.0):
        """
        Cria relação entre dois IECs.
        """

        self.graph.add_edge(
            source=source_id,
            target=target_id,
            relation_type=relation_type,
            weight=weight
        )

    # -----------------------------
    # 4. CICLO DE VALIDAÇÃO
    # -----------------------------
    def validate(self, iec_id=None):
        """
        Valida um IEC específico ou todo o sistema.
        """

        if iec_id:
            return self.validator.validate_iec(iec_id)

        return self.validator.validate_all()

    # -----------------------------
    # 5. RACIOCÍNIO (INFERÊNCIA)
    # -----------------------------
    def reason(self, iec_id):
        """
        Executa inferência sobre um IEC.
        """

        suggestions = self.reasoner.infer_connections(iec_id)

        return suggestions

    # -----------------------------
    # 6. ATUALIZAÇÃO DO CONHECIMENTO
    # -----------------------------
    def update_iec(self, iec_id):
        """
        Atualiza estado de um IEC com base em evidência e rede.
        """

        iec = self.graph.get_node(iec_id)
        if not iec:
            return None

        # 1. validar
        validation_result = self.validator.validate_iec(iec_id)

        # 2. propagar confiança no grafo
        self.reasoner.propagate_confidence(iec_id)

        # 3. atualizar timestamp
        iec.updated_at = datetime.now()

        return validation_result

    # -----------------------------
    # 7. REMOÇÃO CONTROLADA
    # -----------------------------
    def remove_iec(self, iec_id, threshold=0.2):
        """
        Remove conhecimento fraco ou inválido.
        """

        iec = self.graph.get_node(iec_id)
        if not iec:
            return False

        if iec.confidence > threshold:
            return False  # ainda é considerado válido

        self.graph.remove_node(iec_id)

        return True

    # -----------------------------
    # 8. CICLO COMPLETO AUTOMÁTICO
    # -----------------------------
    def run_cycle(self):
        """
        Executa ciclo completo de manutenção do sistema.
        """

        report = self.validator.report()
        weak = self.validator.weak_knowledge()

        removed = []

        # 1. validar sistema inteiro
        self.validator.validate_all()

        # 2. atualizar todos os nós
        for iec_id in self.graph.nodes:
            self.reasoner.propagate_confidence(iec_id)

        # 3. remover conhecimento muito fraco
        for iec in weak:
            if self.remove_iec(iec.id):
                removed.append(iec.id)

        return {
            "report": report,
            "removed_nodes": removed,
        }

    # -----------------------------
    # 9. ESTADO DO SISTEMA
    # -----------------------------
    def status(self):
        return {
            "graph": self.graph.stats(),
            "evidence": self.evidence_store.stats(),
            "system_quality": self.validator.system_quality_score(),
        }