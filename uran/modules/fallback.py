from uran.modules.base import CommunicationModule


class FallbackSafeBPSKModule(CommunicationModule):
    def __init__(self):
        super().__init__("fallback_safe_bpsk", "Safe BPSK Fallback", "fallback")

    def process(self, context):
        context["modulation"] = "BPSK"
        context["bits_per_symbol"] = 1
        context["coding_rate"] = 1 / 3
        context["coding_gain_db"] = 5
        context["harq_max_retx"] = 4
        context["pilot_density"] = "high"
        context["scheduler"] = "reliability_first"
        context["power_control"] = "conservative"
        context["fallback_active"] = True
        return context