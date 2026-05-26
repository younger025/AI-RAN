from uran.modules.base import CommunicationModule


class CodingModule(CommunicationModule):
    def __init__(self, module_id: str, name: str, coding_rate: float, coding_gain_db: float):
        super().__init__(module_id, name, "coding")
        self.coding_rate = coding_rate
        self.coding_gain_db = coding_gain_db

    def process(self, context):
        context["coding_rate"] = self.coding_rate
        context["coding_gain_db"] = self.coding_gain_db
        return context