class LLMAdapter:
    def __init__(self, provider: str = "rule_based"):
        self.provider = provider

    def generate(self, prompt: str) -> str:
        raise NotImplementedError(
            "LLMAdapter is reserved for future LLM integration."
        )