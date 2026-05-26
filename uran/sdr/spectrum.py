import numpy as np


def estimate_psd(iq_samples: np.ndarray, sample_rate: float = 1e6):
    n = len(iq_samples)
    window = np.hanning(n)
    x = iq_samples * window
    spectrum = np.fft.fftshift(np.fft.fft(x))
    psd = 20 * np.log10(np.abs(spectrum) + 1e-12)
    freqs = np.fft.fftshift(np.fft.fftfreq(n, d=1.0 / sample_rate))
    return freqs, psd