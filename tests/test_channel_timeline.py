from uran.sim.channel_timeline import ChannelTimeline


def test_linear_fading_decreases():
    timeline = ChannelTimeline(
        mode="linear_fading",
        initial_snr_db=20,
        final_snr_db=0,
        total_steps=100,
    )
    assert timeline.snr_at(0) > timeline.snr_at(100)


def test_constant_channel():
    timeline = ChannelTimeline(
        mode="constant",
        initial_snr_db=10,
        final_snr_db=0,
        total_steps=100,
    )
    assert timeline.snr_at(0) == timeline.snr_at(50)
    assert timeline.snr_at(50) == timeline.snr_at(100)


def test_jamming_spike():
    timeline = ChannelTimeline(
        mode="jamming_spike",
        initial_snr_db=15,
        final_snr_db=2,
        total_steps=100,
    )
    assert timeline.snr_at(10) == 15.0
    assert timeline.snr_at(50) == 2.0


def test_sinusoidal_oscillates():
    timeline = ChannelTimeline(
        mode="sinusoidal",
        initial_snr_db=20,
        final_snr_db=0,
        total_steps=100,
    )
    mid = timeline.snr_at(25)
    end = timeline.snr_at(75)
    assert mid != end


def test_sinr_with_interference():
    timeline = ChannelTimeline(
        mode="constant",
        initial_snr_db=12,
        final_snr_db=12,
        total_steps=100,
    )
    assert timeline.sinr_at(0, interference_penalty_db=3.0) == 9.0