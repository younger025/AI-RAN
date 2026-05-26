import yaml
from pathlib import Path
from typing import Optional

from uran.sim.node import CommNode
from uran.sim.link import CommLink
from uran.sim.topology import NetworkTopology
from uran.sim.channel_timeline import ChannelTimeline
from uran.sim.experiment import ResearchExperimentRunner
from uran.common.band_config import BandConfig


def load_scenario_config(path: str | Path) -> dict:
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_topology_from_config(cfg: dict) -> NetworkTopology:
    nodes = [CommNode(**node_cfg) for node_cfg in cfg["nodes"]]
    links = [CommLink(**link_cfg) for link_cfg in cfg["links"]]

    topology = NetworkTopology(
        topology_id=cfg["scenario_id"],
        name=cfg["name"],
        description=cfg.get("description", ""),
        nodes=nodes,
        links=links,
    )

    errors = topology.validate_topology()
    if errors:
        raise ValueError("Invalid topology: " + "; ".join(errors))

    topology.update_link_distances()

    return topology


def build_runner_from_config(cfg: dict, band_config: Optional[BandConfig] = None) -> ResearchExperimentRunner:
    topology = build_topology_from_config(cfg)

    channel_cfg = cfg.get("channel", {})

    total_steps = cfg.get("total_steps", 100)
    step_interval_s = cfg.get("step_interval_s", 0.1)

    timeline = ChannelTimeline(
        mode=channel_cfg.get("mode", "linear_fading"),
        initial_snr_db=channel_cfg.get("initial_snr_db", 18.0),
        final_snr_db=channel_cfg.get("final_snr_db", 3.0),
        total_steps=total_steps,
        seed=channel_cfg.get("seed", 42),
        noise_std_db=channel_cfg.get("noise_std_db", 0.8),
    )

    link_offsets_db = cfg.get("link_offsets_db", {})

    return ResearchExperimentRunner(
        topology=topology,
        channel_timeline=timeline,
        total_steps=total_steps,
        step_interval_s=step_interval_s,
        link_offsets_db=link_offsets_db,
        band_config=band_config,
    )