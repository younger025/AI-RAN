from uran.modules.base import CommunicationModule


class HARQModule(CommunicationModule):
    def __init__(self, module_id: str, name: str, max_retx: int):
        super().__init__(module_id, name, "harq")
        self.max_retx = max_retx

    def process(self, context):
        context["harq_max_retx"] = self.max_retx
        context["harq_gain_db"] = self.max_retx * 1.2
        context["harq_latency_penalty_ms"] = self.max_retx * 8
        return context