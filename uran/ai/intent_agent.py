from uran.ai.agent_base import AgentBase
from uran.ai.intent_schema import IntentSpec
from uran.common.ids import new_id

EMERGENCY_KEYWORDS = ["应急", "灾害", "救援", "低snr", "低 snr", "弱覆盖", "高可靠", "恶劣"]
THROUGHPUT_KEYWORDS = ["高吞吐", "大吞吐", "高清视频", "热点", "容量", "高速下载", "视频上传"]
JAMMING_KEYWORDS = ["干扰", "抗干扰", "压制", "电子对抗", "阻塞", "对抗"]
LATENCY_KEYWORDS = ["低时延", "低延时", "无人机", "控制", "实时", "机器人", "自动驾驶"]
SATELLITE_KEYWORDS = ["卫星", "物联网", "低功耗", "广域", "遥测", "iot"]


class IntentAgent(AgentBase):
    def __init__(self):
        super().__init__("IntentAgent")

    def run(self, raw_text: str) -> IntentSpec:
        text = raw_text.lower()
        self.log(f"Received raw intent text: {raw_text}")

        intent_id = new_id("intent")

        if any(kw in text for kw in EMERGENCY_KEYWORDS):
            scenario = "emergency"
            priority = "reliability"
            self.log("Recognized scenario: emergency (disaster / low SNR)")
            self.log("Priority: reliability")
            spec = IntentSpec(
                intent_id=intent_id,
                raw_text=raw_text,
                scenario_type="emergency",
                priority="reliability",
                min_throughput_kbps=64,
                max_latency_ms=150,
                target_bler=0.05,
                max_tx_power_dbm=23,
                mobility_level="low",
                interference_level="medium",
                snr_hint_db=-3,
                notes={"keywords": [k for k in EMERGENCY_KEYWORDS if k in text]},
            )
        elif any(kw in text for kw in THROUGHPUT_KEYWORDS):
            scenario = "high_throughput"
            priority = "throughput"
            self.log("Recognized scenario: high_throughput (capacity / video)")
            self.log("Priority: throughput")
            spec = IntentSpec(
                intent_id=intent_id,
                raw_text=raw_text,
                scenario_type="high_throughput",
                priority="throughput",
                min_throughput_kbps=500,
                max_latency_ms=100,
                target_bler=0.10,
                max_tx_power_dbm=23,
                mobility_level="low",
                interference_level="low",
                snr_hint_db=18,
                notes={"keywords": [k for k in THROUGHPUT_KEYWORDS if k in text]},
            )
        elif any(kw in text for kw in JAMMING_KEYWORDS):
            scenario = "anti_jamming"
            priority = "anti_jamming"
            self.log("Recognized scenario: anti_jamming (electronic warfare)")
            self.log("Priority: anti_jamming")
            spec = IntentSpec(
                intent_id=intent_id,
                raw_text=raw_text,
                scenario_type="anti_jamming",
                priority="anti_jamming",
                min_throughput_kbps=100,
                max_latency_ms=120,
                target_bler=0.07,
                max_tx_power_dbm=23,
                mobility_level="low",
                interference_level="high",
                snr_hint_db=0,
                notes={"keywords": [k for k in JAMMING_KEYWORDS if k in text]},
            )
        elif any(kw in text for kw in LATENCY_KEYWORDS):
            scenario = "low_latency"
            priority = "latency"
            self.log("Recognized scenario: low_latency (UAV / real-time control)")
            self.log("Priority: latency")
            spec = IntentSpec(
                intent_id=intent_id,
                raw_text=raw_text,
                scenario_type="low_latency",
                priority="latency",
                min_throughput_kbps=200,
                max_latency_ms=30,
                target_bler=0.08,
                max_tx_power_dbm=21,
                mobility_level="high",
                interference_level="medium",
                snr_hint_db=10,
                notes={"keywords": [k for k in LATENCY_KEYWORDS if k in text]},
            )
        elif any(kw in text for kw in SATELLITE_KEYWORDS):
            scenario = "satellite_iot"
            priority = "energy"
            self.log("Recognized scenario: satellite_iot (low power, wide area)")
            self.log("Priority: energy")
            spec = IntentSpec(
                intent_id=intent_id,
                raw_text=raw_text,
                scenario_type="satellite_iot",
                priority="energy",
                min_throughput_kbps=10,
                max_latency_ms=500,
                target_bler=0.10,
                max_tx_power_dbm=17,
                mobility_level="high",
                interference_level="low",
                snr_hint_db=0,
                notes={"keywords": [k for k in SATELLITE_KEYWORDS if k in text]},
            )
        else:
            scenario = "balanced"
            priority = "balanced"
            self.log("Recognized scenario: balanced (general communication)")
            self.log("Priority: balanced")
            spec = IntentSpec(
                intent_id=intent_id,
                raw_text=raw_text,
                scenario_type="balanced",
                priority="balanced",
                min_throughput_kbps=200,
                max_latency_ms=80,
                target_bler=0.08,
                max_tx_power_dbm=20,
                mobility_level="medium",
                interference_level="low",
                snr_hint_db=8,
                notes={"keywords": []},
            )

        self.log(f"IntentSpec created: scenario={scenario}, priority={priority}")
        return spec