import math
from pydantic import BaseModel
from uran.sim.node import CommNode
from uran.sim.link import CommLink


class NetworkTopology(BaseModel):
    topology_id: str
    name: str
    description: str = ""

    nodes: list[CommNode]
    links: list[CommLink]

    def get_node(self, node_id: str) -> CommNode | None:
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None

    def get_link(self, link_id: str) -> CommLink | None:
        for link in self.links:
            if link.link_id == link_id:
                return link
        return None

    def get_active_links(self) -> list[CommLink]:
        return [link for link in self.links if link.active]

    def update_node_positions(self, delta_t_s: float) -> None:
        for node in self.nodes:
            node.update_position(delta_t_s)

    def update_link_distances(self) -> None:
        for link in self.links:
            src = self.get_node(link.source_node_id)
            dst = self.get_node(link.target_node_id)
            if src is None or dst is None:
                continue
            dx = src.position.x - dst.position.x
            dy = src.position.y - dst.position.y
            link.distance_m = math.sqrt(dx * dx + dy * dy)

    def validate_topology(self) -> list[str]:
        errors = []
        node_ids = {node.node_id for node in self.nodes}
        for link in self.links:
            if link.source_node_id not in node_ids:
                errors.append(
                    f"Link {link.link_id} source node {link.source_node_id} does not exist"
                )
            if link.target_node_id not in node_ids:
                errors.append(
                    f"Link {link.link_id} target node {link.target_node_id} does not exist"
                )
        return errors