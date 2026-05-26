from uran.ai.agent_base import AgentBase
from uran.ai.intent_schema import IntentSpec, EnvironmentSpec


class ModuleSelectionAgent(AgentBase):
    def __init__(self):
        super().__init__("ModuleSelectionAgent")

    def run(self, intent: IntentSpec, environment: EnvironmentSpec) -> dict:
        self.log(f"Selecting modules for scenario '{intent.scenario_type}' with priority '{intent.priority}'")

        selection = self._select_by_scenario(intent, environment)

        self.log(f"Selected modulation: {selection['modulation']}")
        self.log(f"Selected coding: {selection['coding_scheme']}")
        self.log(f"Selected HARQ: enabled={selection['harq_enabled']}, max_retx={selection['harq_max_retx']}")
        self.log(f"Selected pilot: {selection['pilot_density']}")
        self.log(f"Selected scheduler: {selection['scheduler']}")
        self.log(f"Selected power control: {selection['power_control']}")

        return selection

    def _select_by_scenario(self, intent: IntentSpec, environment: EnvironmentSpec) -> dict:
        snr = environment.avg_snr_db
        priority = intent.priority

        if priority == "reliability" or intent.scenario_type == "emergency":
            return self._reliable_selection(intent)
        elif priority == "throughput":
            return self._throughput_selection(intent)
        elif priority == "anti_jamming":
            return self._anti_jamming_selection(intent)
        elif priority == "latency":
            return self._low_latency_selection(intent)
        elif priority == "energy":
            return self._energy_selection(intent)
        else:
            return self._balanced_selection(intent)

    def _reliable_selection(self, intent: IntentSpec) -> dict:
        return {
            "modulation": "BPSK",
            "coding_scheme": "repetition_3",
            "harq_enabled": True,
            "harq_max_retx": 4,
            "pilot_density": "high",
            "scheduler": "reliability_first",
            "power_control": "snr_based",
        }

    def _throughput_selection(self, intent: IntentSpec) -> dict:
        return {
            "modulation": "16QAM",
            "coding_scheme": "ldpc_mock_3_4",
            "harq_enabled": True,
            "harq_max_retx": 1,
            "pilot_density": "low",
            "scheduler": "throughput_first",
            "power_control": "fixed",
        }

    def _anti_jamming_selection(self, intent: IntentSpec) -> dict:
        return {
            "modulation": "QPSK",
            "coding_scheme": "repetition_3",
            "harq_enabled": True,
            "harq_max_retx": 4,
            "pilot_density": "high",
            "scheduler": "reliability_first",
            "power_control": "snr_based",
        }

    def _low_latency_selection(self, intent: IntentSpec) -> dict:
        return {
            "modulation": "QPSK",
            "coding_scheme": "convolutional_1_2",
            "harq_enabled": True,
            "harq_max_retx": 1,
            "pilot_density": "medium",
            "scheduler": "latency_first",
            "power_control": "fixed",
        }

    def _energy_selection(self, intent: IntentSpec) -> dict:
        return {
            "modulation": "BPSK",
            "coding_scheme": "repetition_3",
            "harq_enabled": True,
            "harq_max_retx": 2,
            "pilot_density": "low",
            "scheduler": "balanced",
            "power_control": "energy_saving",
        }

    def _balanced_selection(self, intent: IntentSpec) -> dict:
        return {
            "modulation": "QPSK",
            "coding_scheme": "convolutional_1_2",
            "harq_enabled": True,
            "harq_max_retx": 2,
            "pilot_density": "medium",
            "scheduler": "balanced",
            "power_control": "snr_based",
        }