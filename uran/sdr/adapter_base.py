from abc import ABC, abstractmethod
import numpy as np


class SDRAdapterBase(ABC):
    @abstractmethod
    def configure(self, config) -> None:
        pass

    @abstractmethod
    def transmit(self, iq_samples: np.ndarray):
        pass

    @abstractmethod
    def receive(self, duration_ms: int = 10) -> np.ndarray:
        pass

    @abstractmethod
    def measure_spectrum(self):
        pass

    @abstractmethod
    def measure_metrics(self):
        pass

    @abstractmethod
    def close(self) -> None:
        pass