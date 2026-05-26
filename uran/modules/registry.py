from uran.modules.base import CommunicationModule
from uran.modules.modulation import ModulationModule
from uran.modules.coding import CodingModule
from uran.modules.harq import HARQModule
from uran.modules.pilot import PilotModule
from uran.modules.scheduler import SchedulerModule
from uran.modules.power_control import PowerControlModule
from uran.modules.fallback import FallbackSafeBPSKModule


class ModuleRegistry:
    def __init__(self):
        self._modules = {}

    def register(self, module: CommunicationModule):
        self._modules[module.module_id] = module

    def get(self, module_id: str) -> CommunicationModule:
        if module_id not in self._modules:
            raise KeyError(f"Module not found: {module_id}")
        return self._modules[module_id]

    def list_modules(self):
        return list(self._modules.values())

    def describe_all(self):
        return [m.describe() for m in self._modules.values()]


def build_default_registry() -> ModuleRegistry:
    registry = ModuleRegistry()

    registry.register(ModulationModule("BPSK", 1, 1.0))
    registry.register(ModulationModule("QPSK", 2, 0.8))
    registry.register(ModulationModule("16QAM", 4, 0.5))
    registry.register(ModulationModule("64QAM", 6, 0.3))

    registry.register(CodingModule("code_repetition_2", "Repetition Code Rate 1/2", 0.5, 3))
    registry.register(CodingModule("code_repetition_3", "Repetition Code Rate 1/3", 1 / 3, 5))
    registry.register(CodingModule("code_conv_1_2", "Convolutional Code Rate 1/2", 0.5, 3))
    registry.register(CodingModule("code_conv_2_3", "Convolutional Code Rate 2/3", 2 / 3, 2))
    registry.register(CodingModule("code_ldpc_mock_2_3", "LDPC Mock Code Rate 2/3", 2 / 3, 4))
    registry.register(CodingModule("code_ldpc_mock_3_4", "LDPC Mock Code Rate 3/4", 0.75, 3))

    registry.register(HARQModule("harq_none", "No HARQ", 0))
    registry.register(HARQModule("harq_stop_and_wait", "HARQ Stop-and-Wait", 2))
    registry.register(HARQModule("harq_incremental_redundancy_mock", "HARQ Incremental Redundancy Mock", 4))

    registry.register(PilotModule("low"))
    registry.register(PilotModule("medium"))
    registry.register(PilotModule("high"))

    registry.register(SchedulerModule("throughput_first"))
    registry.register(SchedulerModule("reliability_first"))
    registry.register(SchedulerModule("latency_first"))
    registry.register(SchedulerModule("balanced"))

    registry.register(PowerControlModule("fixed"))
    registry.register(PowerControlModule("snr_based"))
    registry.register(PowerControlModule("conservative"))
    registry.register(PowerControlModule("energy_saving"))

    registry.register(FallbackSafeBPSKModule())

    return registry