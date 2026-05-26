from uran.modules.base import CommunicationModule


class PowerControlModule(CommunicationModule):
    def __init__(self, control_type: str):
        super().__init__(
            module_id=f"pc_{control_type}",
            name=f"Power Control {control_type.replace('_', ' ').title()}",
            module_type="power_control",
        )
        self.control_type = control_type

    def process(self, context):
        context["power_control"] = self.control_type
        return context