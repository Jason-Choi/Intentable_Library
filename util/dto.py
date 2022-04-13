from dataclasses import dataclass
import json
from typing import List, Dict, Union
from spec import Specification

summary_type = ("describe", "question")
identify_type = ("one", "two")
compare_type = ("greater", "less")
trend_type = ("greater", "less", "fluctuate")
period_type = ("since", "for", "before")


@dataclass
class Target:
    feature: str
    row: str
    column: str
    value: Union[float, int]

    def get(self) -> Dict[str, str]:
        return {
            "feature": self.feature,
            "row": self.row,
            "column": self.column,
            "value": str(self.value)
        }


class Intent:
    def __init__(self, sentence) -> None:
        self.action: str = None  # summary, identify, compare, trends
        self.type: str = None
        # Summary: describe, question
        # Identify: one, two
        # Comapre, Trends: bigger, smaller
        self.period: str = None
        self.targets: List[Target] = []
        self.sentence: str = sentence

    def __str__(self) -> str:
        return f"Intent({self.action} {self.type} {self.period} {self.targets})"

    def complete(self):
        if self.action == "summary" and self.type in summary_type:
            return True
        elif self.action == "identify" and self.type in identify_type and len(self.targets) > 0:
            return True
        elif self.action == "compare" and self.type in compare_type and len(self.targets) > 1:
            return True
        elif self.action == "discover" and \
                self.type in trend_type and \
                self.period in period_type:
            return True
        else:
            return False

    def get(self) -> Dict[str, str]:
        obj = {
            "action": self.action,
            "type": self.type,
        }
        if self.period:
            obj["period"] = self.period
        if self.targets:
            obj["targets"] = [target.get() for target in self.targets]

        return obj


class Recipe:
    def __init__(self, chart_type, title, unit, intents, is_full=False):
        self.chart_type: str = chart_type
        self.title: str = title
        self.unit: str = unit
        self.intents: List[Intent] = intents
        self.is_full: bool = is_full
        self.caption = " ".join([intent.sentence for intent in self.intents])

    def get(self) -> str:
        return json.dumps({
            "chart_type": self.chart_type,
            "title": self.title,
            "unit": self.unit,
            "intents": [intent.get() for intent in self.intents]
        }) if len(self.intents) > 0 else None

    def print_recipe(self):
        print(self.get())
