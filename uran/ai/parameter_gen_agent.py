from uran.ai.agent_base import AgentBase
from uran.ai.intent_schema import IntentSpec
from uran.ai.plan_schema import PlanSpec
from uran.common.ids import new_id

PLAN_TEMPLATES = {
    "emergency": {
        "Conservative": {
            "modulation": "BPSK", "coding_scheme": "repetition_3", "coding_rate": 1/3, "mcs": 1,
            "harq_enabled": True, "harq_max_retx": 4, "pilot_density": "high", "tx_power_dbm": 23,
            "scheduler": "reliability_first", "power_control": "snr_based", "risk_level": "low",
            "description": "保守高可靠方案：BPSK + 重复码 + 4次HARQ + 高导频密度",
        },
        "Balanced": {
            "modulation": "QPSK", "coding_scheme": "convolutional_1_2", "coding_rate": 0.5, "mcs": 4,
            "harq_enabled": True, "harq_max_retx": 3, "pilot_density": "medium", "tx_power_dbm": 20,
            "scheduler": "balanced", "power_control": "snr_based", "risk_level": "medium",
            "description": "均衡方案：QPSK + 卷积码 + 3次HARQ + 中导频密度",
        },
        "Aggressive": {
            "modulation": "16QAM", "coding_scheme": "ldpc_mock_2_3", "coding_rate": 2/3, "mcs": 10,
            "harq_enabled": True, "harq_max_retx": 1, "pilot_density": "low", "tx_power_dbm": 18,
            "scheduler": "throughput_first", "power_control": "fixed", "risk_level": "high",
            "description": "激进高吞吐方案：16QAM + LDPC + 1次HARQ + 低导频密度",
        },
    },
    "high_throughput": {
        "Conservative": {
            "modulation": "QPSK", "coding_scheme": "convolutional_2_3", "coding_rate": 2/3, "mcs": 7,
            "harq_enabled": True, "harq_max_retx": 2, "pilot_density": "medium", "tx_power_dbm": 18,
            "scheduler": "throughput_first", "power_control": "fixed", "risk_level": "low",
            "description": "保守高吞吐方案：QPSK + 卷积码 + 中导频密度",
        },
        "Balanced": {
            "modulation": "16QAM", "coding_scheme": "ldpc_mock_3_4", "coding_rate": 0.75, "mcs": 15,
            "harq_enabled": True, "harq_max_retx": 1, "pilot_density": "medium", "tx_power_dbm": 20,
            "scheduler": "throughput_first", "power_control": "fixed", "risk_level": "medium",
            "description": "均衡高吞吐方案：16QAM + LDPC 3/4 + 中导频密度",
        },
        "Aggressive": {
            "modulation": "64QAM", "coding_scheme": "ldpc_mock_3_4", "coding_rate": 0.75, "mcs": 22,
            "harq_enabled": True, "harq_max_retx": 1, "pilot_density": "low", "tx_power_dbm": 22,
            "scheduler": "throughput_first", "power_control": "fixed", "risk_level": "high",
            "description": "激进超高吞吐方案：64QAM + LDPC 3/4 + 低导频密度",
        },
    },
    "anti_jamming": {
        "Conservative": {
            "modulation": "BPSK", "coding_scheme": "repetition_3", "coding_rate": 1/3, "mcs": 1,
            "harq_enabled": True, "harq_max_retx": 4, "pilot_density": "high", "tx_power_dbm": 23,
            "scheduler": "reliability_first", "power_control": "snr_based", "risk_level": "low",
            "description": "保守抗干扰方案：BPSK + 重复码 + 4次HARQ + 高导频",
        },
        "Balanced": {
            "modulation": "QPSK", "coding_scheme": "convolutional_1_2", "coding_rate": 0.5, "mcs": 4,
            "harq_enabled": True, "harq_max_retx": 3, "pilot_density": "high", "tx_power_dbm": 22,
            "scheduler": "balanced", "power_control": "snr_based", "risk_level": "medium",
            "description": "均衡抗干扰方案：QPSK + 卷积码 + 3次HARQ + 高导频",
        },
        "Aggressive": {
            "modulation": "16QAM", "coding_scheme": "ldpc_mock_2_3", "coding_rate": 2/3, "mcs": 10,
            "harq_enabled": True, "harq_max_retx": 2, "pilot_density": "medium", "tx_power_dbm": 21,
            "scheduler": "throughput_first", "power_control": "snr_based", "risk_level": "high",
            "description": "激进抗干扰方案：16QAM + LDPC + 中导频 + 高功率",
        },
    },
    "low_latency": {
        "Conservative": {
            "modulation": "QPSK", "coding_scheme": "convolutional_1_2", "coding_rate": 0.5, "mcs": 4,
            "harq_enabled": True, "harq_max_retx": 1, "pilot_density": "medium", "tx_power_dbm": 18,
            "scheduler": "latency_first", "power_control": "fixed", "risk_level": "low",
            "description": "保守低时延方案：QPSK + 卷积码 + 1次HARQ + 低时延调度",
        },
        "Balanced": {
            "modulation": "16QAM", "coding_scheme": "ldpc_mock_2_3", "coding_rate": 2/3, "mcs": 12,
            "harq_enabled": True, "harq_max_retx": 1, "pilot_density": "medium", "tx_power_dbm": 20,
            "scheduler": "latency_first", "power_control": "fixed", "risk_level": "medium",
            "description": "均衡低时延方案：16QAM + LDPC + 低时延调度",
        },
        "Aggressive": {
            "modulation": "16QAM", "coding_scheme": "ldpc_mock_3_4", "coding_rate": 0.75, "mcs": 16,
            "harq_enabled": False, "harq_max_retx": 0, "pilot_density": "low", "tx_power_dbm": 21,
            "scheduler": "latency_first", "power_control": "fixed", "risk_level": "high",
            "description": "激进低时延方案：16QAM + LDPC + 无HARQ + 低时延调度",
        },
    },
    "satellite_iot": {
        "Conservative": {
            "modulation": "BPSK", "coding_scheme": "repetition_3", "coding_rate": 1/3, "mcs": 1,
            "harq_enabled": True, "harq_max_retx": 3, "pilot_density": "high", "tx_power_dbm": 17,
            "scheduler": "balanced", "power_control": "energy_saving", "risk_level": "low",
            "description": "保守低功耗方案：BPSK + 重复码 + 节能功控",
        },
        "Balanced": {
            "modulation": "QPSK", "coding_scheme": "convolutional_1_2", "coding_rate": 0.5, "mcs": 3,
            "harq_enabled": True, "harq_max_retx": 2, "pilot_density": "medium", "tx_power_dbm": 15,
            "scheduler": "balanced", "power_control": "energy_saving", "risk_level": "medium",
            "description": "均衡低功耗方案：QPSK + 卷积码 + 节能功控",
        },
        "Aggressive": {
            "modulation": "QPSK", "coding_scheme": "ldpc_mock_2_3", "coding_rate": 2/3, "mcs": 7,
            "harq_enabled": True, "harq_max_retx": 1, "pilot_density": "low", "tx_power_dbm": 13,
            "scheduler": "balanced", "power_control": "energy_saving", "risk_level": "high",
            "description": "激进低功耗方案：QPSK + LDPC + 最低功率",
        },
    },
    "balanced": {
        "Conservative": {
            "modulation": "QPSK", "coding_scheme": "convolutional_1_2", "coding_rate": 0.5, "mcs": 4,
            "harq_enabled": True, "harq_max_retx": 3, "pilot_density": "high", "tx_power_dbm": 20,
            "scheduler": "balanced", "power_control": "snr_based", "risk_level": "low",
            "description": "保守均衡方案：QPSK + 卷积码 + 高导频",
        },
        "Balanced": {
            "modulation": "QPSK", "coding_scheme": "ldpc_mock_2_3", "coding_rate": 2/3, "mcs": 8,
            "harq_enabled": True, "harq_max_retx": 2, "pilot_density": "medium", "tx_power_dbm": 18,
            "scheduler": "balanced", "power_control": "snr_based", "risk_level": "medium",
            "description": "均衡方案：QPSK + LDPC + 中导频 + 中HARQ",
        },
        "Aggressive": {
            "modulation": "16QAM", "coding_scheme": "ldpc_mock_3_4", "coding_rate": 0.75, "mcs": 16,
            "harq_enabled": True, "harq_max_retx": 1, "pilot_density": "low", "tx_power_dbm": 20,
            "scheduler": "throughput_first", "power_control": "fixed", "risk_level": "high",
            "description": "激进均衡方案：16QAM + LDPC 3/4 + 低导频",
        },
    },
}


class ParameterGenAgent(AgentBase):
    def __init__(self):
        super().__init__("ParameterGenAgent")

    def run(self, intent: IntentSpec, module_selection: dict) -> list:
        self.log(f"Generating candidate plans for scenario '{intent.scenario_type}'")
        self.log(f"Base module selection: {module_selection}")

        scenario = intent.scenario_type
        templates = PLAN_TEMPLATES.get(scenario, PLAN_TEMPLATES["balanced"])

        plans = []
        for profile_name in ["Conservative", "Balanced", "Aggressive"]:
            t = templates[profile_name]
            tx_power = min(t["tx_power_dbm"], intent.max_tx_power_dbm)

            plan = PlanSpec(
                plan_id=new_id("plan"),
                intent_id=intent.intent_id,
                name=f"{profile_name} - {t.get('description', '')}",
                description=t.get("description", ""),
                modulation=t["modulation"],
                coding_scheme=t["coding_scheme"],
                coding_rate=t["coding_rate"],
                mcs=t["mcs"],
                harq_enabled=t["harq_enabled"],
                harq_max_retx=t["harq_max_retx"],
                pilot_density=t["pilot_density"],
                tx_power_dbm=tx_power,
                scheduler=t["scheduler"],
                power_control=t["power_control"],
                risk_level=t["risk_level"],
                metadata={"profile": profile_name},
            )
            plans.append(plan)
            self.log(f"Generated {profile_name} plan: mod={plan.modulation}, mcs={plan.mcs}, "
                     f"harq={plan.harq_max_retx}, pilot={plan.pilot_density}, tx={plan.tx_power_dbm}dBm")

        return plans