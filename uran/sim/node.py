from typing import Literal
from pydantic import BaseModel, Field


class Position2D(BaseModel):
    x: float = Field(..., description="X position in meters")
    y: float = Field(..., description="Y position in meters")


class CommNode(BaseModel):
    node_id: str
    node_type: Literal["gNB", "UE", "relay", "jammer", "satellite", "edge_server"]
    name: str
    position: Position2D

    tx_power_dbm: float = 20.0
    antenna_gain_db: float = 0.0
    noise_figure_db: float = 5.0

    mobility_enabled: bool = False
    velocity_x: float = 0.0
    velocity_y: float = 0.0

    def update_position(self, delta_t_s: float) -> None:
        if not self.mobility_enabled:
            return
        self.position.x += self.velocity_x * delta_t_s
        self.position.y += self.velocity_y * delta_t_s