from core.iec import IEC


class CoreEngine:
    """Fábrica de IECs. Ponto único de criação de conhecimento no sistema."""

    def create_iec(self, id, content, node_type="Conhecimento", metadata=None):
        return IEC(id=id, content=content, node_type=node_type, metadata=metadata)
