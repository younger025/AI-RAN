from uran.modules.base import CommunicationModule


class PilotModule(CommunicationModule):
    def __init__(self, density: str):
        super().__init__(
            module_id=f"pilot_{density}",
            name=f"Pilot {density.capitalize()} Density",
            module_type="pilot",
        )
        self.density = density

    def process(self, context):
        context["pilot_density"] = self.density
        return context