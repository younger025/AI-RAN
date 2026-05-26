SUPPORTED_MODULATIONS = ["BPSK", "QPSK", "16QAM", "64QAM"]

SUPPORTED_CODING_SCHEMES = [
    "repetition_2",
    "repetition_3",
    "convolutional_1_2",
    "convolutional_2_3",
    "ldpc_mock_2_3",
    "ldpc_mock_3_4",
    "ldpc_mock",
]

SUPPORTED_PILOT_DENSITIES = ["low", "medium", "high"]

SUPPORTED_SCHEDULERS = [
    "reliability_first",
    "throughput_first",
    "latency_first",
    "balanced",
    "fairness",
]

SUPPORTED_POWER_CONTROL = [
    "fixed",
    "snr_based",
    "conservative",
    "aggressive",
    "energy_saving",
]

SUPPORTED_PRIORITIES = [
    "reliability",
    "throughput",
    "latency",
    "energy",
    "balanced",
    "anti_jamming",
]

SUPPORTED_SCENARIO_TYPES = [
    "emergency",
    "high_throughput",
    "anti_jamming",
    "low_latency",
    "satellite_iot",
    "balanced",
]

MODULATION_BITS_PER_SYMBOL = {
    "BPSK": 1,
    "QPSK": 2,
    "16QAM": 4,
    "64QAM": 6,
}

MODULATION_ROBUSTNESS = {
    "BPSK": 1.0,
    "QPSK": 0.8,
    "16QAM": 0.5,
    "64QAM": 0.3,
}

CODING_GAIN_DB = {
    "repetition_2": 3,
    "repetition_3": 5,
    "convolutional_1_2": 3,
    "convolutional_2_3": 2,
    "ldpc_mock_2_3": 4,
    "ldpc_mock_3_4": 3,
    "ldpc_mock": 4,
}

CODING_RATE = {
    "repetition_2": 0.5,
    "repetition_3": 1 / 3,
    "convolutional_1_2": 0.5,
    "convolutional_2_3": 2 / 3,
    "ldpc_mock_2_3": 2 / 3,
    "ldpc_mock_3_4": 0.75,
    "ldpc_mock": 0.75,
}

CODING_DELAY_MS = {
    "repetition_2": 12,
    "repetition_3": 15,
    "convolutional_1_2": 8,
    "convolutional_2_3": 6,
    "ldpc_mock_2_3": 5,
    "ldpc_mock_3_4": 4,
    "ldpc_mock": 5,
}

PILOT_GAIN_DB = {
    "high": 2,
    "medium": 1,
    "low": 0,
}

PILOT_EFFICIENCY = {
    "high": 0.75,
    "medium": 0.88,
    "low": 0.95,
}

SCHEDULER_DELAY_MS = {
    "reliability_first": 10,
    "throughput_first": 5,
    "latency_first": 0,
    "balanced": 4,
    "fairness": 6,
}

MODULATION_THRESHOLD_DB = {
    "BPSK": -2,
    "QPSK": 2,
    "16QAM": 8,
    "64QAM": 14,
}

MODULATION_PENALTY_DB = {
    "BPSK": 0,
    "QPSK": 2,
    "16QAM": 6,
    "64QAM": 10,
}

INTERFERENCE_PENALTY_DB = {
    "none": 0,
    "low": -1,
    "medium": -3,
    "high": -6,
}