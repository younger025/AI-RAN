import math
import numpy as np


class ChannelTimeline:
    def __init__(
        self,
        mode: str = "linear_fading",
        initial_snr_db: float = 18.0,
        final_snr_db: float = 3.0,
        total_steps: int = 100,
        seed: int = 42,
        noise_std_db: float = 0.8,
    ):
        self.mode = mode
        self.initial_snr_db = initial_snr_db
        self.final_snr_db = final_snr_db
        self.total_steps = max(total_steps, 1)
        self.noise_std_db = noise_std_db
        self.rng = np.random.default_rng(seed)
        self._random_walk_cache: dict[int, float] = {}

    def snr_at(self, step: int, link_offset_db: float = 0.0) -> float:
        step = max(0, min(step, self.total_steps))

        if self.mode == "constant":
            snr = self.initial_snr_db

        elif self.mode == "linear_fading":
            ratio = step / self.total_steps
            snr = self.initial_snr_db + ratio * (
                self.final_snr_db - self.initial_snr_db
            )

        elif self.mode == "sinusoidal":
            base = (self.initial_snr_db + self.final_snr_db) / 2.0
            amp = abs(self.initial_snr_db - self.final_snr_db) / 2.0
            snr = base + amp * math.sin(2.0 * math.pi * step / self.total_steps)

        elif self.mode == "random_walk":
            snr = self._random_walk_snr(step)

        elif self.mode == "blockage":
            if step < self.total_steps * 0.45:
                snr = self.initial_snr_db
            elif step < self.total_steps * 0.7:
                snr = self.final_snr_db
            else:
                snr = (self.initial_snr_db + self.final_snr_db) / 2.0

        elif self.mode == "jamming_spike":
            if self.total_steps * 0.4 <= step <= self.total_steps * 0.65:
                snr = self.final_snr_db
            else:
                snr = self.initial_snr_db

        elif self.mode == "handover_like":
            if step < self.total_steps * 0.3:
                snr = self.initial_snr_db
            elif step < self.total_steps * 0.55:
                ratio = (step - self.total_steps * 0.3) / (self.total_steps * 0.25)
                snr = self.initial_snr_db + ratio * (
                    self.final_snr_db - self.initial_snr_db
                )
            elif step < self.total_steps * 0.75:
                snr = self.final_snr_db
            else:
                ratio = (step - self.total_steps * 0.75) / (self.total_steps * 0.25)
                snr = self.final_snr_db + ratio * (
                    self.initial_snr_db - self.final_snr_db
                )

        else:
            snr = self.initial_snr_db

        return float(snr + link_offset_db)

    def sinr_at(
        self,
        step: int,
        link_offset_db: float = 0.0,
        interference_penalty_db: float = 1.0,
    ) -> float:
        return self.snr_at(step, link_offset_db) - interference_penalty_db

    def _random_walk_snr(self, step: int) -> float:
        if step in self._random_walk_cache:
            return self._random_walk_cache[step]

        value = self.initial_snr_db
        self._random_walk_cache[0] = value

        for s in range(1, step + 1):
            if s in self._random_walk_cache:
                value = self._random_walk_cache[s]
                continue
            drift = (self.final_snr_db - self.initial_snr_db) / self.total_steps
            noise_val = self.rng.normal(0.0, self.noise_std_db)
            value = value + drift + noise_val
            value = max(-5.0, min(30.0, value))
            self._random_walk_cache[s] = value

        return self._random_walk_cache[step]