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
        self.objs = []
        self.e2es = None



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

        # Linearize Data
        linearized_table = []

        for series_index in range(len(self.table.columns)):
            for key_index in range(len(self.table.index)):
                if self.column_number != 1:
                    linearized_table.append(
                        (
                            self.column_names[series_index],
                            self.row_names[key_index],
                            self.table.iloc[key_index, series_index]
                        )
                    )
                else:
                    linearized_table.append(
                        (
                            self.row_names[key_index],
                            self.table.iloc[key_index, series_index]
                        )
                    )
                    
        self.linearized_table = str(linearized_table)
        self.e2ecaption = " ".join([intent.caption for intent in self.intent_objects])

        self.e2erecipe = E2ERecipe(
            chart_type=self.chart_type,
            title=self.title,
            unit=self.unit,
            datas=linearized_table,
            caption=self.e2ecaption
        )



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
            elif has_trend_keyword or period_keyword:
                intent.action = "trend"
            elif len(targets) > 0:
                intent.action = "compare"
            else:
                intent.action = "trend"

            # Compare target value and change to describe if target value is same
            if intent.action == 'compare' and len(targets) == 2:
                if diff_keyword == "greater" and (targets[0].value > targets[1].value):
                    targets[0], targets[1] = targets[1], targets[0]
                elif diff_keyword == "less" and (targets[0].value < targets[1].value):
                    targets[0], targets[1] = targets[1], targets[0]
                elif targets[0].value == targets[1].value:
                    intent.action = "describe"


            if intent.action == 'compare' and len(targets) == 2:
                intent.diff = self.get_diffrence_of_target_values(targets)

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
                
                extracted_date = sorted(target_dates, key=lambda x: years.index(x))

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
                
                intent.diff = self.get_diffrence_of_target_values(targets)
                targets = [targets[0], targets[-1]]
            
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

    def get_diffrence_of_target_values(self, targets: List[Target]) -> List[str]:
        diff_list : List[str] = []
        for i in range(len(targets)-1):
            sub = targets[i+1].value - targets[i].value
            # if sub is integer
            if sub == 0:
                diff_list.append("0")
            elif sub == int(sub):
                diff_list.append("%+d" % sub)
            else:
                diff_list.append("%+.2f" % sub)
        return diff_list

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
        # for recipe in self.recipes:
        #     recipe.print_recipe()

        print(self.e2erecipe.get())
        print(self.table)
