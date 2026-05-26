from pathlib import Path
from typing import Optional
from uran.sim.scenario_loader import load_scenario_config, build_runner_from_config
from uran.common.band_config import BandConfig, BAND_PRESETS


class ResearchDemoController:
    def __init__(self, band_config: Optional[BandConfig] = None):
        self.band_config = band_config or BAND_PRESETS["sim_default"]
        self.scenario_file: str | None = None
        self.config: dict | None = None
        self.runner = None
        self.latest_records = []

    def set_band_config(self, band_config: BandConfig):
        self.band_config = band_config
        if self.scenario_file and self.config:
            scenario_path = Path("configs/research_scenarios") / self.scenario_file
            self.runner = build_runner_from_config(self.config, band_config=band_config)

    def load_scenario(self, scenario_file: str):
        scenario_path = Path("configs/research_scenarios") / scenario_file
        self.config = load_scenario_config(scenario_path)
        self.scenario_file = scenario_file
        self.runner = build_runner_from_config(self.config, band_config=self.band_config)
        self.latest_records = []
        return self.runner.topology

    def is_loaded(self) -> bool:
        return self.runner is not None

    def step(self):
        if self.runner is None:
            return []
        self.latest_records = self.runner.step()
        return self.latest_records

    def run_all(self):
        if self.runner is None:
            return []
        records = self.runner.run_all()
        if self.runner.topology.links:
            n = len(self.runner.topology.get_active_links())
            self.latest_records = records[-n:] if records else []
        return records

    def reset(self):
        if self.runner:
            self.runner.reset()
        self.latest_records = []

    def dataframe(self):
        if self.runner is None:
            return None
        return self.runner.recorder.to_dataframe()

    def latest_records_by_link(self):
        if self.runner is None:
            return {}
        return self.runner.recorder.latest_records_by_link()

    def topology(self):
        if self.runner is None:
            return None
        return self.runner.topology

    def current_step(self) -> int:
        if self.runner is None:
            return 0
        return self.runner.current_step

    def total_steps(self) -> int:
        if self.runner is None:
            return 0
        return self.runner.total_steps

    def is_finished(self) -> bool:
        if self.runner is None:
            return False
        return self.runner.is_finished()