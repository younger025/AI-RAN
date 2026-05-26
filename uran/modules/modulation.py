from uran.modules.base import CommunicationModule


class ModulationModule(CommunicationModule):
    def __init__(self, modulation: str, bits_per_symbol: int, robustness: float):
        super().__init__(
            module_id=f"mod_{modulation.lower()}",
            name=f"{modulation} Modulation",
            module_type="modulation",
        )
        self.modulation = modulation
        self.bits_per_symbol = bits_per_symbol
        self.robustness = robustness

    def process(self, context):
        context["modulation"] = self.modulation
        context["bits_per_symbol"] = self.bits_per_symbol
        context["modulation_robustness"] = self.robustness
        return context