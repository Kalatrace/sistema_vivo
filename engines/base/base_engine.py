from knowledge.iec import IEC


class CoreEngine:
    """Fábrica compatível de IECs para a camada de engenharia."""

    def create_iec(self, id, content, node_type="Conhecimento", metadata=None, domain=None):
        return IEC(
            id=id,
            content=content,
            domain=domain,
            node_type=node_type,
            metadata=metadata,
        )
