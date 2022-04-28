from typing import Tuple
from dataclasses import dataclass
import json
from typing import List, Dict, Union
from spec import Specification
import numpy as np

from util.dictionary import is_overview

chart_type = ("bar", "grouped_bar", "stacked_bar", "line", "multi_line", "pie")
period_type = ("since", "during", "until")


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


@dataclass
class Target:
    value: Union[float, int]
    key: str
    series: str
    feature: List[str]

    def get(self) -> Dict[str, str]:
        obj = {
            "value": self.value,
            "key": self.key,
        }
        if self.series != "value":
            obj["series"] = self.series
        if len(self.feature) > 0:
            obj["feature"] = self.feature
        return obj


class Intent:
    def __init__(self, caption) -> None:
        self.action: str = None  # overview, describe, compare, trends, other
        self.diff: List[str] = []
        self.targets: List[Target] = []
        self.caption: str = caption

    def __str__(self) -> str:
        return f"Intent({self.action} {self.diff} {self.targets})"

    def __repr__(self) -> str:
        return self.__str__()

    def is_overview(self) -> bool:
        return self.action == "overview" and len(self.targets) == 0

    def is_describe(self) -> bool:
        return self.action == "describe" and len(self.targets) > 0

    def is_compare(self) -> bool:
        return self.action == "compare" and len(self.targets) == 2

    def is_trend(self) -> bool:
        return self.action == "trend" and len(self.targets) == 2

    def is_complete(self) -> bool:
        if self.is_overview() or self.is_describe() or self.is_compare() or self.is_trend():
            return True
        else:
            return False

    def get(self) -> Dict[str, str]:
        obj = {
            "action": self.action,
        }
        if self.is_overview():
            pass
        elif self.is_describe():
            obj["targets"] = [t.get() for t in self.targets]
        elif self.is_compare():
            obj["targets"] = [t.get() for t in self.targets]
            # obj["diff"] = self.diff
        elif self.is_trend():
            obj["targets"] = [t.get() for t in self.targets]
            # obj["diff"] = self.diff
        else:
            return None
        return obj


class Recipe:
    def __init__(self, chart_type, title, unit, intents):
        self.chart_type: str = chart_type
        self.title: str = title
        self.unit: str = unit
        self.intents: List[Intent] = [intent for intent in intents if intent is not None]
        self.caption = " ".join([intent.caption for intent in self.intents])

    def is_complte(self) -> bool:
        intents = [intent.get() for intent in self.intents]
        intents = [intent for intent in intents if intent is not None]
        return len(intents) > 0 and self.chart_type in chart_type

    def get(self) -> str:
        return json.dumps({
            "chart_type": self.chart_type,
            "title": self.title,
            "unit": self.unit,
            "intents": [i for i in [intent.get() for intent in self.intents] if i is not None]
        }, cls=NpEncoder) if len(self.intents) > 0 else None

    def print_recipe(self):
        print(
            json.dumps({
                "caption": self.caption,
                "chart_type": self.chart_type,
                "title": self.title,
                "unit": self.unit,
                "intents": [intent.get() for intent in self.intents]
            }, cls=NpEncoder, indent=4) if len(self.intents) > 0 else None
        )


class E2ERecipe:
    def __init__(self, chart_type, title, unit, datas, caption):
        self.chart_type: str = chart_type
        self.title: str = title
        self.unit: str = unit
        self.datas: List[Tuple(str, str, int)] = datas
        self.caption = caption

    def get(self) -> str:
        return json.dumps({
            "chart_type": self.chart_type,
            "title": self.title,
            "unit": self.unit,
            "datas" : self.datas,
        }, cls=NpEncoder)
