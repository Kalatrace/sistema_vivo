class IEC:
    """
    IEC = Unidade básica de conhecimento do KALATRACE
    (Informational Epistemic Cell)
    """

    def __init__(self, id, content, domain=None):
        self.id = id
        self.content = content
        self.domain = domain

        # -----------------------
        # CAMADA EPISTEMOLÓGICA
        # -----------------------
        self.sources = []          # de onde veio a informação
        self.confidence = 0.5      # grau inicial de confiança (0 a 1)

        # -----------------------
        # CICLO DE VIDA
        # -----------------------
        self.created_at = None
        self.updated_at = None

    # -----------------------
    # ATUALIZAÇÃO DE CONHECIMENTO
    # -----------------------
    def add_source(self, source):
        """
        Adiciona uma fonte de evidência ao IEC
        """
        self.sources.append(source)

    def update_confidence(self, value):
        """
        Atualiza a confiança do conhecimento (0 a 1)
        """
        self.confidence = max(0.0, min(1.0, float(value)))

    def reinforce(self, delta=0.1):
        """
        Aumenta confiança (evidência positiva)
        """
        self.update_confidence(self.confidence + delta)

    def weaken(self, delta=0.1):
        """
        Reduz confiança (evidência negativa ou dúvida)
        """
        self.update_confidence(self.confidence - delta)

    # -----------------------
    # REPRESENTAÇÃO
    # -----------------------
    def __repr__(self):
        return (
            f"IEC("
            f"id={self.id}, "
            f"confidence={self.confidence:.2f}, "
            f"domain={self.domain})"
        )