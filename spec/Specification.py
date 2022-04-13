from pandas import DataFrame
import pandas as pd
from typing import List, Union, Dict
from db.schema import Dataset
import io
from IPython.core.display import display, HTML
from nltk.tokenize import sent_tokenize
from itertools import combinations
from util import *


class Specification():
    def __init__(self, data: Union[Dataset, Dict]):
        # Metadata
        self.id = data["id"]
        self.title = data["title"]
        self.market = data["market"]
        self.topic = data["topic"]

        # Table Specification
        self.table: DataFrame = pd.read_csv(io.StringIO(data["data"]), header=0, index_col=0)
        self.column_number = len(self.table.columns)
        self.row_number = len(self.table.index)
        self.column_type = data["column_type"]
        self.row_type = data["row_type"]

        # Chart Specification
        self.unit = data["axis_title"]
        self.mark = data["chart_type"]
        self.chart_stacked = data["chart_stacked"]
        self.chart_type = self.get_chart_type()
        # Natural Language Summary
        self.raw_caption: str = get_raw_caption(data["raw_caption"], self.chart_type)

        self.column_names = self.table.columns.tolist()
        if self.column_names[0] == " ":
            self.column_names[0] = "value"
            self.table.columns = self.column_names
        self.row_names = self.table.index.tolist()
        self.feature = get_featured_element_list(self.table, self.row_type)
        self.element_list = get_element_list(self.table)

        sentences: List[str] = sent_tokenize(self.raw_caption)
        i = 0
        while i < len(sentences):
            if is_append(sentence=sentences[i]):
                sentences[i-1] += (" " + sentences.pop(i))
                i -= 1
            i += 1
        self.intent_objects: List[Intent] = [self.get_intent_from_sentence(sentence) for sentence in sentences]
        self.intent_objects = [intent for intent in self.intent_objects if intent != None]
        self.recipes: List[Recipe] = []
        for i in range(1, len(self.intent_objects) + 1):
            for combi in combinations(self.intent_objects, i):
                self.recipes.append(
                    Recipe(
                        chart_type=self.chart_type,
                        title=self.title,
                        unit=self.unit,
                        intents=list(combi),
                        is_full=True if i == len(self.intent_objects) else False
                    )
                )

    def get_intent_from_sentence(self, sentence: str) -> Intent:
        intent = Intent(sentence=sentence)
        summaryType = is_summary(sentence)
        if summaryType:
            intent.action = "summary"
            intent.type = summaryType
            return intent

        targets = self.get_targets(sentence)

        diff_keyword = is_diff(sentence)
        has_trend_keyword = has_keyword(trendDict, sentence)
        has_compare_keyword = has_keyword(compareDict, sentence)
        period_keyword = has_period(sentence)

        # Comapre, Discover
        if diff_keyword or has_compare_keyword:
            intent.type = diff_keyword
            if self.row_type != "DATE":
                intent.action = "compare"
            elif has_compare_keyword:
                intent.action = "compare"
            elif has_trend_keyword:
                intent.action = "discover"
                intent.period = period_keyword

            elif period_keyword:
                intent.action = "discover"
                intent.period = period_keyword
            elif len(targets) > 0:
                intent.action = "compare"
            else:
                intent.action = "discover"
                intent.period = period_keyword
            if intent.action == 'compare' and len(targets) == 1 and self.row_type == "DATE":
                if has_next_year(sentence):
                    for i in range(len(self.element_list)):
                        if (self.element_list[i].row == targets[0].row) and \
                                (self.element_list[i].column == targets[0].column):
                            targets.append(
                                self.element_list[i+1]
                            )
                            break
                else:
                    for i in range(len(self.element_list)):
                        if i > 1 and ((self.element_list[i].row == targets[0].row) and
                                      (self.element_list[i].column == targets[0].column)):
                            targets.append(
                                self.element_list[i-1]
                            )
                            break
            if intent.action == 'discover' and has_trend_keyword == False:
                intent.period = "for"

            if intent.action == 'comapare' or intent.action == "discover" and len(targets) == 2:
                if intent.type == "greater" and (targets[0].value > targets[1].value):
                    targets[0], targets[1] = targets[1], targets[0]
                elif intent.type == "less" and (targets[0].value < targets[1].value):
                    targets[0], targets[1] = targets[1], targets[0]
            intent.targets = targets

        # Identify
        else:
            intent.action = "identify"
            intent.targets = targets
            if len(intent.targets) == 1:
                intent.type = "one"
            elif len(intent.targets) == 2:
                intent.type = "two"

        if intent.complete():
            return intent
        else:
            return None

    def get_targets(self, caption: str) -> List[Target]:
        masked_caption = caption
        source_elements: Dict[str, Target] = {}
        for element in self.feature:
            value_strings = entity_formatter(str(element.value), self.unit)
            for value_string in value_strings:
                if is_token_includes(masked_caption, value_string):
                    org = masked_caption
                    masked_caption = masked_caption.replace(value_string, "[MASK]")
                    if org != masked_caption:
                        source_elements[element.column + element.row] = element
            if self.column_number == 1 and self.row_type == "DATE":
                try:
                    date_strings = date_formatter(str(element.row))
                    for date_string in date_strings:
                        if is_token_includes(masked_caption, date_string):
                            org = masked_caption
                            masked_caption = masked_caption.replace(date_string, "[MASK]")
                            if org != masked_caption:
                                source_elements[element.column + element.row] = element
                except:
                    pass

        for element in self.element_list:
            value_strings = entity_formatter(str(element.value), self.unit)
            for value_string in value_strings:
                if is_token_includes(masked_caption, value_string):
                    org = masked_caption
                    masked_caption = masked_caption.replace(value_string, "[MASK]")
                    if org != masked_caption:
                        source_elements[element.column + element.row] = element
            if self.column_number == 1 and self.row_type == "DATE":
                try:
                    date_strings = date_formatter(str(element.row))
                    for date_string in date_strings:
                        if is_token_includes(masked_caption, date_string):
                            org = masked_caption
                            masked_caption = masked_caption.replace(date_string, "[MASK]")
                            if org != masked_caption:
                                source_elements[element.column + element.row] = element
                except:
                    pass

        return list(source_elements.values())

    def get_chart_type(self) -> str:
        if self.mark == 'bar' and self.column_number == 1:
            return "bar"
        elif self.mark == 'bar' and self.column_number > 1 and self.chart_stacked == True:
            return "stacked_bar"
        elif self.mark == 'bar' and self.column_number > 1 and self.chart_stacked == False:
            return "grouped_bar"
        elif self.mark == 'line':
            return "line"
        elif self.mark == 'pie':
            return "pie"

    def print_information(self):
        print()
        display(HTML(f"""<a href="https://www.statista.com/statistics/{self.id}">Statista Link</a>"""))
        # print("id: ", self.id)
        print("title: ", self.title)
        # print("market: ", self.market)
        # print("topic: ", self.topic)
        print("unit: ", self.unit)
        print("chart_type: ", self.chart_type)
        # print()
        # print(self.feature)
        # print(self.element_list)
        print(self.raw_caption)
        for recipe in self.recipes:
            recipe.print_recipe()
        print(self.table)
