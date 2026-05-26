from uran.ai.agent_base import AgentBase
from uran.ai.intent_schema import IntentSpec
from uran.ai.plan_schema import PlanSpec


class CriticAgent(AgentBase):
    def __init__(self):
        super().__init__("CriticAgent")

    def run(self, intent: IntentSpec, plans: list) -> list:
        self.log("Reviewing candidate plans against intent constraints")

        for plan in plans:
            self._review_plan(intent, plan)

        return plans

    def _review_plan(self, intent: IntentSpec, plan: PlanSpec):
        notes = []

        if intent.priority == "reliability" and plan.modulation in ["16QAM", "64QAM"]:
            plan.risk_level = "high"
            notes.append("High-order modulation may violate reliability objective under low SNR.")

        if intent.priority == "throughput" and plan.modulation in ["BPSK"]:
            notes.append("BPSK modulation severely limits throughput, may not meet capacity requirements.")

        if intent.priority == "latency" and plan.harq_max_retx >= 4:
            plan.risk_level = "high"
            notes.append("Too many HARQ retransmissions may increase latency beyond target.")

        if intent.priority == "anti_jamming" and plan.pilot_density == "low":
            plan.risk_level = "high"
            notes.append("Low pilot density may degrade channel estimation under jamming.")

        if intent.priority == "energy" and plan.tx_power_dbm > 20:
            notes.append("TX power exceeds typical energy-saving range.")

        if plan.harq_max_retx == 0 and plan.modulation in ["16QAM", "64QAM"]:
            notes.append("No HARQ with high-order modulation may cause reliability issues in fading channels.")

        if plan.coding_rate > 0.7 and plan.pilot_density == "low":
            notes.append("High coding rate without sufficient pilot support may degrade reliability.")

        if notes:
            plan.metadata["critic_notes"] = notes
            self.log(f"Plan '{plan.name}': {len(notes)} concern(s) raised - risk={plan.risk_level}")
        else:
            plan.metadata["critic_notes"] = []
            self.log(f"Plan '{plan.name}': No critical concerns identified")