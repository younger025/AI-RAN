from uran.sim.topology import NetworkTopology
from uran.sim.channel_timeline import ChannelTimeline
from uran.sim.adaptation import LinkAdaptationController
from uran.sim.kpi_model import KPIModel
from uran.sim.kpi_recorder import KPIRecorder, LinkKPIRecord
from uran.common.band_config import BandConfig
from typing import Optional


class ResearchExperimentRunner:
    def __init__(
        self,
        topology: NetworkTopology,
        channel_timeline: ChannelTimeline,
        total_steps: int = 100,
        step_interval_s: float = 0.1,
        link_offsets_db: dict[str, float] | None = None,
        band_config: Optional[BandConfig] = None,
    ):
        self.topology = topology
        self.channel_timeline = channel_timeline
        self.total_steps = total_steps
        self.step_interval_s = step_interval_s

        self.current_step = 0
        self.adapter = LinkAdaptationController()
        self.kpi_model = KPIModel(band_config=band_config)
        self.recorder = KPIRecorder()

        self.link_offsets_db = link_offsets_db or {}

    def reset(self) -> None:
        self.current_step = 0
        self.recorder.clear()
        for link in self.topology.links:
            link.established = False

    def is_finished(self) -> bool:
        return self.current_step >= self.total_steps

    def step(self) -> list[LinkKPIRecord]:
        if self.is_finished():
            return []

        time_s = self.current_step * self.step_interval_s

        self.topology.update_node_positions(self.step_interval_s)
        self.topology.update_link_distances()

        step_records = []

        for link in self.topology.get_active_links():
            if not link.established:
                link.mark_established()

            link_offset = self.link_offsets_db.get(link.link_id, 0.0)

            snr_db = self.channel_timeline.snr_at(
                self.current_step,
                link_offset_db=link_offset,
            )

            sinr_db = self.channel_timeline.sinr_at(
                self.current_step,
                link_offset_db=link_offset,
                interference_penalty_db=self._estimate_interference_penalty(link.link_id),
            )

            previous_bler = self.recorder.get_previous_bler(link.link_id)

            decision = self.adapter.decide(
                snr_db=snr_db,
                sinr_db=sinr_db,
                previous_bler=previous_bler,
            )

            link.snr_db = snr_db
            link.sinr_db = sinr_db

            link.update_adaptation_state(
                mcs=decision.mcs,
                modulation=decision.modulation,
                coding=decision.coding,
                coding_rate=decision.coding_rate,
                pilot_density=decision.pilot_density,
                harq_retx=decision.harq_retx,
                tx_power_dbm=decision.tx_power_dbm,
            )

            kpi = self.kpi_model.estimate(
                snr_db=snr_db,
                sinr_db=sinr_db,
                modulation=decision.modulation,
                coding_rate=decision.coding_rate,
                pilot_density=decision.pilot_density,
                harq_retx=decision.harq_retx,
            )

            record = LinkKPIRecord(
                step=self.current_step,
                time_s=time_s,
                link_id=link.link_id,
                source_node_id=link.source_node_id,
                target_node_id=link.target_node_id,
                snr_db=snr_db,
                sinr_db=sinr_db,
                bler=kpi["bler"],
                throughput_kbps=kpi["throughput_kbps"],
                latency_ms=kpi["latency_ms"],
                mcs=decision.mcs,
                modulation=decision.modulation,
                coding=decision.coding,
                coding_rate=decision.coding_rate,
                spectral_efficiency=kpi["spectral_efficiency"],
                pilot_density=decision.pilot_density,
                tx_power_dbm=decision.tx_power_dbm,
                harq_retx=decision.harq_retx,
                packet_success_rate=kpi["packet_success_rate"],
                reliability=kpi["reliability"],
                event=decision.reason,
                event_level=decision.event_level,
            )

            self.recorder.append(record)
            step_records.append(record)

        self.current_step += 1

        return step_records

    def run_all(self) -> list[LinkKPIRecord]:
        records = []
        while not self.is_finished():
            records.extend(self.step())
        return records

    def _estimate_interference_penalty(self, link_id: str) -> float:
        has_jammer = any(node.node_type == "jammer" for node in self.topology.nodes)
        if has_jammer:
            return 3.0
        return 1.0