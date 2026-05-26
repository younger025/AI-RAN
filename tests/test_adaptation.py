from uran.sim.adaptation import LinkAdaptationController


def test_high_snr_selects_high_mcs():
    adapter = LinkAdaptationController()
    decision = adapter.decide(snr_db=20, sinr_db=18)
    assert decision.mcs >= 6
    assert decision.modulation in ["16QAM", "64QAM"]
    assert decision.coding_rate >= 0.66


def test_low_snr_selects_robust_mode():
    adapter = LinkAdaptationController()
    decision = adapter.decide(snr_db=2, sinr_db=1)
    assert decision.mcs <= 1
    assert decision.modulation == "BPSK"
    assert decision.coding_rate <= 0.33
    assert decision.harq_retx >= 3


def test_previous_high_bler_penalizes_decision():
    adapter = LinkAdaptationController()
    d1 = adapter.decide(snr_db=11, sinr_db=11, previous_bler=None)
    d2 = adapter.decide(snr_db=11, sinr_db=11, previous_bler=0.5)
    assert d2.mcs <= d1.mcs


def test_medium_snr_selects_qpsk():
    adapter = LinkAdaptationController()
    decision = adapter.decide(snr_db=7, sinr_db=6)
    assert decision.modulation == "QPSK"
    assert decision.harq_retx == 2