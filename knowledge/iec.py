"""Unidade epistemológica básica do KALATRACE."""

from utils.embeddings import get_embedding


class IEC:
    """
    IEC = Informational Epistemic Cell.

    É a unidade básica de conhecimento do KALATRACE. O contrato mantém os
    campos epistemológicos e de ciclo de vida existentes e acrescenta os
    atributos necessários às camadas cognitivas legadas: classificação,
    representação semântica e contexto.
    """

    def __init__(
        self,
        id,
        content,
        domain=None,
        node_type="Conhecimento",
        embedding=None,
        metadata=None,
    ):
        self.id = id
        self.content = content
        self.domain = domain
        self.node_type = node_type

        # Representação semântica. Permite injeção explícita para reconstrução
        # persistente/testes e gera embedding quando nenhum foi fornecido.
        self.embedding = (
            list(embedding)
            if embedding is not None
            else get_embedding(content)
        )

        # Contexto adicional do conhecimento.
        self.metadata = dict(metadata) if metadata is not None else {}

        # -----------------------
        # CAMADA EPISTEMOLÓGICA
        # -----------------------
        self.sources = []
        self.confidence = 0.5

        # -----------------------
        # CICLO DE VIDA
        # -----------------------
        self.created_at = None
        self.updated_at = None

    def add_source(self, source):
        """Adiciona uma fonte de evidência ao IEC."""
        self.sources.append(source)

    def update_confidence(self, value):
        """Atualiza a confiança do conhecimento no intervalo [0, 1]."""
        self.confidence = max(0.0, min(1.0, float(value)))

    def reinforce(self, delta=0.1):
        """Aumenta a confiança do IEC."""
        self.update_confidence(self.confidence + delta)

    def weaken(self, delta=0.1):
        """Reduz a confiança do IEC."""
        self.update_confidence(self.confidence - delta)

    def __repr__(self):
        return (
            f"IEC(id={self.id}, confidence={self.confidence:.2f}, "
            f"domain={self.domain}, node_type={self.node_type})"
        )
