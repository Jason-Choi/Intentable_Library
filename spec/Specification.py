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
        self.id = data["id"]
        self.title = data["title"]
        self.market = data["market"]
        self.topic = data["topic"]
        self.table: DataFrame = pd.read_csv(io.StringIO(data["data"]), header=0, index_col=0)
        self.column_number = len(self.table.columns)
        self.row_number = len(self.table.index)
        self.column_type = data["column_type"]
        self.row_type = data["row_type"]
        self.unit = data["axis_title"]
        self.mark = data["chart_type"]
        self.bar_stacked = data["chart_stacked"]
        self.chart_type = self.get_chart_type()
        self.paragraph: str = get_raw_caption(data["raw_caption"], self.chart_type)
        self.column_names = self.table.columns.tolist()
        if self.column_names[0] == " ":
            self.column_names[0] = "value"
            self.table.columns = self.column_names
        self.row_names = self.table.index.tolist()



        self.target_list : Dict[str, List[Target]] = get_target_list(self.table, self.row_type)

        sentences: List[str] = sent_tokenize(self.paragraph)
        i = 0
        while i < len(sentences):
            if is_append(sentence=sentences[i]):
                sentences[i-1] += (" " + sentences.pop(i))
                i -= 1
            i += 1
        self.sentences = sentences
        self.intent_objects: List[Intent] = [self.get_intent_from_sentence(sentence) for sentence in sentences]
        self.intent_objects = [intent for intent in self.intent_objects if intent != None and intent.is_complete()]
        self.recipes: List[Recipe] = []
        for i in range(1, len(self.intent_objects) + 1):
            for combi in combinations(self.intent_objects, i):
                recipe = Recipe(
                    chart_type=self.chart_type,
                    title=self.title,
                    unit=self.unit,
                    intents=list(combi),
                )

                if recipe.is_complte():
                    self.recipes.append(recipe)

    def get_intent_from_sentence(self, sentence: str) -> Intent:
        intent = Intent(caption=sentence)
        overviewType = is_overview(sentence)
        if overviewType:
            intent.action = "overview"
            return intent

        targets = self.get_targets(sentence)
        diff_keyword = is_diff(sentence)
        has_trend_keyword = has_keyword(trendDict, sentence)
        has_compare_keyword = has_keyword(compareDict, sentence)
        period_keyword = has_period(sentence)
        # print(sentence)
        # print(f"diff: {diff_keyword} trend: {has_trend_keyword} compare: {has_compare_keyword} period: {period_keyword}")
        # print()
        # print(f"targets: {targets} ")

        
        # Classify Comapre, Discover
        if diff_keyword:
            if self.row_type != "DATE" or has_compare_keyword:
                intent.action = "compare"
                intent.relation = diff_keyword
            elif has_trend_keyword or period_keyword:
                intent.action = "trend"
            elif len(targets) > 0:
                intent.action = "compare"
                intent.relation = diff_keyword
            else:
                intent.action = "trend"

            # If Compare, One Target, DATE in X-AXIS, Find Previous, Following Year
            if intent.action == 'compare' and len(targets) == 1 and self.row_type == "DATE":
                if has_next_year(sentence):
                    key = targets[0].key
                    series = targets[0].series
                    column : List[Target]= self.target_list[series]
                    for i in range(column):
                        if column[i].key == key:
                            targets.append(
                                column[i+1]
                            )
                            break
                else:
                    key = targets[0].key
                    series = targets[0].series
                    column: List[Target] = self.target_list[series]
                    for i in range(len(column)):
                        if i>1 and column[i].key == key:
                            targets.append(
                                column[i-1]
                            )
                            break


            # Compare target value and change to describe if target value is same
            if intent.action == 'compare' and len(targets) == 2:
                if intent.relation == "greater" and (targets[0].value > targets[1].value):
                    targets[0], targets[1] = targets[1], targets[0]
                elif intent.relation == "less" and (targets[0].value < targets[1].value):
                    targets[0], targets[1] = targets[1], targets[0]
                elif targets[0].value == targets[1].value:
                    intent.action = "describe"
                    intent.relation = None
                    

            # Extract year keys and series from trend
            # find max year and min year
            # add all targets and relations between extracted year keys
            if intent.action == 'trend':
                years = self.row_names
                targets: List[Target] = []
                relations: List[str]  = []


                
                targets_series: str = 'value'
                for s in self.column_names:
                    targets_series = s if is_token_includes(sentence.lower(), str(s).lower()) else 'value'
                all_target_list = self.target_list[targets_series]

                extracted_date = []
                target_dates = []

                for year in years:
                    date_strings = date_formatter(year)
                    for date_string in date_strings:
                        if is_token_includes(sentence.lower(), str(date_string)):
                            extracted_date.append(year)
                
                extracted_date = sorted(target_dates, key=lambda x: years.index(year))

                if len(extracted_date) == 0:
                    targets = all_target_list
                elif len(extracted_date) == 1:
                    if period_keyword == 'since':
                        targets = [all_target_list[years.index(extracted_date[0]):]]
                    elif period_keyword == 'until':
                        targets = [all_target_list[:years.index(extracted_date[0])+1]]
                    elif period_keyword == 'during':
                        index = years.index(extracted_date[0])
                        if index > len(all_target_list)//2:
                            targets = [all_target_list[index:]]
                        else:
                            targets = [all_target_list[:index+1]]
                else:
                    targets = [all_target_list[years.index(extracted_date[0]):years.index(extracted_date[1])+1]]
                

                for i in range(len(targets)-1):
                    if targets[i].value == targets[i+1].value:
                        relations.append("equal")
                    elif targets[i].value > targets[i+1].value:
                        relations.append("less")
                    else:
                        relations.append("greater")

                intent.relations = relations
            
            intent.targets = targets

        else:
            intent.action = "describe"
            intent.targets = targets

        return intent

    def get_targets(self, caption: str) -> List[Target]:
        masked_caption = caption
        source_elements: Dict[str, Target] = {}

        for series, target_list in self.target_list.items():
            for target in target_list:
                value_strings = entity_formatter(str(target.value), self.unit)
                for value_string in value_strings:
                    if is_token_includes(masked_caption, value_string):
                        org = masked_caption
                        masked_caption = masked_caption.replace(value_string, "[MASK]")
                        if org != masked_caption:
                            source_elements[target.key+series+str(target.value)] = target

        return list(source_elements.values())

    def get_chart_type(self) -> str:
        if self.mark == 'bar' and self.column_number == 1:
            return "bar"
        elif self.mark == 'bar' and self.column_number > 1 and self.bar_stacked == True:
            return "stacked_bar"
        elif self.mark == 'bar' and self.column_number > 1 and self.bar_stacked == False:
            return "grouped_bar"
        elif self.mark == 'line' and self.column_number == 1:
            return "line"
        elif self.mark == 'line' and self.column_number > 1:
            return "multi_line"
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
        # print(self.featured_element_list)
        # print(self.element_list)
        print(self.paragraph)
        for recipe in self.recipes:
            recipe.print_recipe()
        print(self.table)
