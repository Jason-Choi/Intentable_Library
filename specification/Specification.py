from dataclasses import replace
from pandas import DataFrame
import pandas as pd
from typing import List, Union, Dict
from db.schema import Dataset
import io

from .get_feature_table import *
from .replace_token import *
from util import entity_formatter, date_formatter
from IPython.core.display import display, HTML
from nltk.tokenize import sent_tokenize, word_tokenize


class Tokens():
    sep = "</s>"


MAX_ROW_LENGTH = 25

positive_trends = ['increased', 'increase', 'increasing', 'grew', 'growing', 'rose', 'rising', 'gained', 'gaining']
negative_trends = ['decreased', 'decrease', 'decreasing', 'shrank', 'shrinking', 'fell', 'falling', 'dropped', 'dropping']



class Specification():
    def __init__(self, dataset: Union[Dataset, Dict]):
        if type(dataset) == type(dict()):
            self.init_with_json(dataset)
        elif type(dataset) == type(Input()):
            self.init_with_api(dataset)
        else:
            self.init_with_schema(dataset)

        self.column_names = self.table.columns.tolist()
        if self.column_names[0] == " ":
            self.column_names[0] = "<empty>"
        self.row_names = self.table.index.tolist()
        # Feature Table
        self.feature = get_feature_table(self.table, 0, self.row_type)

        # Target Sequence
        self.target_sequence = self.get_tagged_sequence(self.caption)

        # Source_Sequence
        self.source_sequence = self.get_source_sequence(title_tagged=False)
        self.source_sequence_tagged_title = self.get_source_sequence(title_tagged=True)

        self.tagged_sentence_list = self.get_tagged_sequence_list()

    def init_with_schema(self, data: Dataset):
        # Metadata
        self.id = data.id
        self.title = data.title
        self.market = data.market
        self.topic = data.topic

        # Chart Specification
        self.axis_title = data.axis_title
        self.chart_type = data.chart_type.lower().replace("[", "<").replace("]", ">")

        # Table Specification
        self.table: DataFrame = pd.read_csv(io.StringIO(data.data), header=0, index_col=0)
        self.column_number = data.column_number
        self.row_number = data.row_number
        self.column_type = data.column_type
        self.row_type = data.row_type
        self.column_names = self.table.columns.tolist()
        self.row_names = self.table.index.tolist()

        # Natural Language Summary
        self.caption = data.raw_caption.replace("&amp;", "&").replace("percentage", "percent").replace("*", "")

        if 'bar' in self.chart_type.lower():
            self.caption = self.caption.replace("The statistic", "The bar chart")
            self.caption = self.caption.replace("This statistic", "This bar chart")
        elif 'line' in self.chart_type.lower():
            self.caption = self.caption.replace("The statistic", "The line chart")
            self.caption = self.caption.replace("This statistic", "This line chart")
        elif 'pie' in self.chart_type.lower():
            self.caption = self.caption.replace("The statistic", "The pie chart")
            self.caption = self.caption.replace("This statistic", "This pie chart")

    def init_with_api(self, input):
        self. id = 0
        self.title = input.title
        self.axis_title = input.value_info
        self.chart_type = input.chart_type
        self.table : DataFrame = pd.read_csv(io.StringIO(input.table), header=0, index_col=0)



    def init_with_json(self, data: Dict[str, str]):
        # Metadata
        self.id = data["id"]
        self.title = data["title"]
        self.market = data["market"]
        self.topic = data["topic"]

        # Chart Specification
        self.axis_title = data["axis_title"]
        self.chart_type = self.get_tokenized_chart_type(data["chart_type"], data["chart_stacked"], data["column_number"])

        # Table Specification
        self.table: DataFrame = pd.read_csv(io.StringIO(data["data"]), header=0, index_col=0)
        self.column_number = data["column_number"]
        self.row_number = data["row_number"]
        self.column_type = data["column_type"]
        self.row_type = data["row_type"]

        # Natural Language Summary
        self.caption = data["raw_caption"].replace("&amp;", "&").lower().replace("percentage", "percent").replace("*", "")
        if 'bar' in self.chart_type.lower():
            self.caption = self.caption.replace("The statistic", "The bar chart")
            self.caption = self.caption.replace("This statistic", "This bar chart")
        elif 'line' in self.chart_type.lower():
            self.caption = self.caption.replace("The statistic", "The line chart")
            self.caption = self.caption.replace("This statistic", "This line chart")
        elif 'pie' in self.chart_type.lower():
            self.caption = self.caption.replace("The statistic", "The pie chart")
            self.caption = self.caption.replace("This statistic", "This pie chart")

    def get_tokenized_chart_type(self, chart_type, chart_stacked, column_number) -> str:
        # <simplebar>
        if chart_type == 'bar' and column_number == 1:
            return "<simplebar>"
        # <stackedbar>
        elif chart_type == 'bar' and column_number > 1 and chart_stacked == True:
            return "<stackedbar>"
        # <groupedbar>
        elif chart_type == 'bar' and column_number > 1 and chart_stacked == False:
            return "<groupedbar>"
        # <simpleline>
        elif chart_type == 'line' and column_number == 1:
            return "<simpleline>"
        # <multiline>
        elif chart_type == 'line' and column_number > 1:
            return "<multiline>"
        # <pie>
        elif chart_type == 'pie':
            return "<pie>"

    def get_source_sequence(self, title_tagged: bool) -> str:
        if not title_tagged:
            token_list: List[str] = [self.chart_type, self.title, Tokens.sep] + self.column_names + [Tokens.sep] + self.row_names + [Tokens.sep]
        else:
            token_list: List[str] = [self.chart_type, self.get_tagged_sequence(self.title), Tokens.sep] + self.column_names + [Tokens.sep] + self.row_names + [Tokens.sep]
        source_sequence = " ".join([str(t) for t in token_list])

        return source_sequence

    def get_tagged_sequence(self, input_string) -> str:
        caption = input_string

        # Feature Table
        token_queue: List[List[str, str]] = [[token, value] for token, value in self.feature.items()]

        # Column Names
        column_tmp_queue = []
        for i, column_name in enumerate(self.column_names):
            if column_name == '<empty>':
                break
            column_tmp_queue.append([f"<col> <{i}>", str(column_name)])
        token_queue += sorted(column_tmp_queue, key=lambda x: len(x[1]))

        # Row Names
        row_tmp_queue = []
        for i, row_name in enumerate(self.row_names):
            if i > MAX_ROW_LENGTH:
                break
            row_tmp_queue.append([f"<row> <{i}>", str(row_name)])
        token_queue += sorted(row_tmp_queue, key=lambda x: len(x[1]))

        # Entities
        for i, row in enumerate(self.table.itertuples()):
            if i > MAX_ROW_LENGTH:
                break
            for j, column_name in enumerate(self.column_names):
                token_queue.append([f"<entity> <{i}> <{j}>", str(row[j+1])])
        # Processing
        # print(token_queue)
        for token, value in token_queue:
            value: str = str(value[0]) if type(value) == type(list()) else str(value)
            if '<col>' in token or '<row>' in token or "name" in token:
                if self.row_type == "DATE":
                    date_list = date_formatter(value)
                    for date_string in date_list:
                        if date_string in caption:
                            caption = replace_token(caption, date_string, token)
                            break
                else:
                    caption = replace_token(caption, value, token)

            else:
                entity_strings = entity_formatter(value, self.axis_title)
                for entity_string in entity_strings:
                    if entity_string in caption:
                        caption = replace_token(caption, entity_string, token)

        return caption

    def get_tagged_sequence_list(self) -> List[List[str]]:
        captions: List[str] = sent_tokenize(self.caption)
        captions = [caption.lower() for caption in captions]
        tagged_pair: List[List[str, str]] = []

        for caption_index, caption in enumerate(captions):
            before_caption = caption
            after_caption = self.get_tagged_sequence(caption)

            # for positive_keyword in positive_trends:
            #     if positive_keyword in after_caption:
            #         after_caption = after_caption.replace(positive_keyword, "<positivetrends>")

            # for negative_keyword in negative_trends:
            #     if negative_keyword in after_caption:
            #         after_caption = after_caption.replace(negative_keyword, "<negativetrends>")
            replaced_tokens: List[str] = []

            tmpstr: str = ""
            new_word_tokens: List[str] = []
            word_tokens = TreebankWordTokenizer().tokenize(after_caption)
            in_token = False
            in_index = False
            for i, token in enumerate(word_tokens):
                if tmpstr == "" and token != "<":
                    new_word_tokens.append(token)
                else:
                    if token == "<":
                        if in_index and not word_tokens[i+1].isnumeric():
                            new_word_tokens.append(tmpstr.replace("><", "> <"))
                            tmpstr = ""
                        in_token = True
                        tmpstr += token
                    elif token == ">":
                        in_token = False
                        tmpstr += token
                    else:
                        if in_token:
                            if token.isnumeric():
                                in_index = True
                            tmpstr += token
                        else:
                            new_word_tokens.append(tmpstr.replace("><", "> <"))
                            tmpstr = ""

            tmpstr: str = ""
            replaced_tokens = [token for token in new_word_tokens if "<" in token and ">" in token]
            column_indices: List[int] = []
            row_indices: List[int] = []

            for replaced_token in replaced_tokens:
                splited = replaced_token.replace("<", "").replace(">", "").split(" ")
                if len(splited) == 3:
                    row_indices.append(int(splited[1]))
                    column_indices.append(int(splited[2]))
                elif len(splited) == 2:
                    if splited[0] == "row":
                        row_indices.append(int(splited[1]))
                    else:
                        column_indices.append(int(splited[1]))
            # sorted_row_indices = sorted(row_indices)
            # sorted_column_indices = sorted(column_indices)
            final_tokens: List[str] = []

            for replaced_token in replaced_tokens:
                final_token: str = ""
                splited = replaced_token.replace("<", "").replace(">", "").split(" ")
                if len(splited) == 3:
                    # row_index = sorted_row_indices.index(int(splited[1]))
                    # column_index = sorted_column_indices.index(int(splited[2]))

                    row_index = splited[1]
                    column_index = splited[2]

                    final_token = f"<entity> row : {row_index}, column : {column_index} </entity>"

                    after_caption = after_caption.replace(replaced_token, final_token)

                elif len(splited) == 2:
                    if splited[0] == "row":
                        # row_index = sorted_row_indices.index(int(splited[1]))
                        row_index = splited[1]
                        final_token = f"<name> row : {row_index} </name>"
                        after_caption = after_caption.replace(replaced_token, final_token)
                    elif splited[0] == "col":
                        # column_index = sorted_column_indices.index(int(splited[1]))
                        column_index = splited[1]
                        final_token = f"<name> column : {column_index} </name>"
                        after_caption = after_caption.replace(replaced_token, final_token)
                    else:
                        row_special = splited[0]
                        # column_index = sorted_column_indices.index(int(splited[1]))
                        column_index = splited[1]
                        final_token = f"<name> row : {row_special}, column : {column_index} </name>"
                        after_caption = after_caption.replace(replaced_token, final_token)

                elif len(splited) == 1:
                    final_token = f"<name> row : {splited[0]} </name>"
                    after_caption = after_caption.replace(replaced_token, final_token)

                final_tokens.append(final_token)

            first_token = "overall" if caption_index == 0 else "non overall"

            chart_string = "bar" if "bar" in self.chart_type else "line"
            chart_string = "pie" if "pie" in self.chart_type else chart_string

            source_sequence = f"<is_overall>{first_token}</is_overall>"
            source_sequence += f"<chart_type>{chart_string}</chart_type>"
            source_sequence += f"<title>{self.title}</title>"
            source_sequence += f"<value_info>{self.axis_title}</value_info><selecttion>"

            for token in final_tokens:
                source_sequence += token
            source_sequence += "</selecttion>"

            source_sequence = source_sequence.lower()
            after_caption = after_caption.lower()

            if 'bar' in self.chart_type.lower():
                after_caption = after_caption.replace("the statistic", "the bar chart")
                after_caption = after_caption.replace("this statistic", "this bar chart")
            elif 'line' in self.chart_type.lower():
                after_caption = after_caption.replace("the statistic", "the line chart")
                after_caption = after_caption.replace("this statistic", "this line chart")
            elif 'pie' in self.chart_type.lower():
                after_caption = after_caption.replace("the statistic", "the pie chart")
                after_caption = after_caption.replace("this statistic", "this pie chart")
            else:
                raise Exception("Unknown chart type")
            tagged_pair.append([source_sequence, after_caption])
        return tagged_pair

    def print_information(self):
        print()
        display(HTML(f"""<a href="https://www.statista.com/statistics/{self.id}">Statista Link</a>"""))
        print("id: ", self.id)
        print("title: ", self.title)
        print("market: ", self.market)
        print("topic: ", self.topic)
        print()
        print("axis_title: ", self.axis_title)
        print("chart_type: ", self.chart_type)
        print()
        print(self.table)
        print(self.feature)
        print()
        print("RAW")
        print(self.caption)
        print()
        # print("E2E Source Sequence")
        # print(self.source_sequence)
        # print()
        # print("E2E Target Sequence")
        # print(self.target_sequence)
        print()
        for i, pair in enumerate(self.tagged_sentence_list):
            print(i)
            print()
            print("SOURCE")
            print(pair[0])
            print()
            print("TARGET")
            print(pair[1])
            print()
