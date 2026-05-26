from uran.sdr.adapter_base import SDRAdapterBase


class GNURadioAdapter(SDRAdapterBase):
    def configure(self, config):
        raise NotImplementedError("GNU Radio adapter is reserved for future hardware integration.")

    def transmit(self, iq_samples):
        raise NotImplementedError("GNU Radio adapter is reserved for future hardware integration.")

    def receive(self, duration_ms=10):
        raise NotImplementedError("GNU Radio adapter is reserved for future hardware integration.")

    def measure_spectrum(self):
        raise NotImplementedError("GNU Radio adapter is reserved for future hardware integration.")

    def measure_metrics(self):
        raise NotImplementedError("GNU Radio adapter is reserved for future hardware integration.")

    def close(self) -> None:
        raise NotImplementedError("GNU Radio adapter is reserved for future hardware integration.")