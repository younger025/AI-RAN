import numpy as np


def generate_iq_symbols(modulation: str, n_symbols: int = 1024, seed: int = 42):
    rng = np.random.default_rng(seed)

    if modulation == "BPSK":
        bits = rng.integers(0, 2, n_symbols)
        return (2 * bits - 1 + 0j).astype(np.complex128)

    if modulation == "QPSK":
        bits_i = rng.integers(0, 2, n_symbols)
        bits_q = rng.integers(0, 2, n_symbols)
        return ((2 * bits_i - 1) + 1j * (2 * bits_q - 1)) / np.sqrt(2)

    if modulation == "16QAM":
        vals = np.array([-3, -1, 1, 3])
        i = rng.choice(vals, n_symbols)
        q = rng.choice(vals, n_symbols)
        return (i + 1j * q) / np.sqrt(10)

    if modulation == "64QAM":
        vals = np.array([-7, -5, -3, -1, 1, 3, 5, 7])
        i = rng.choice(vals, n_symbols)
        q = rng.choice(vals, n_symbols)
        return (i + 1j * q) / np.sqrt(42)

    raise ValueError(f"Unsupported modulation: {modulation}")


def add_awgn(samples: np.ndarray, snr_db: float, seed: int = 42):
    rng = np.random.default_rng(seed)
    signal_power = np.mean(np.abs(samples) ** 2)
    if signal_power < 1e-12:
        return samples
    noise_power = signal_power / (10 ** (snr_db / 10))
    noise = np.sqrt(noise_power / 2) * (
        rng.normal(size=samples.shape) + 1j * rng.normal(size=samples.shape)
    )
    return samples + noise