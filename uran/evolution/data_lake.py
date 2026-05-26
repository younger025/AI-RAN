import json
import os
from uran.common.serialization import to_dict
from uran.evolution.experience import Experience


class DataLake:
    def __init__(self, path="outputs/evolution/experience_log.jsonl"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def append(self, exp: Experience):
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(to_dict(exp), ensure_ascii=False) + "\n")

    def load_all(self):
        if not os.path.exists(self.path):
            return []
        rows = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
        return rows

    def query_by_scenario(self, scenario_type: str):
        all_exp = self.load_all()
        return [e for e in all_exp if e.get("intent", {}).get("scenario_type") == scenario_type]