from .get_chart_type import *
from .get_column_type import *
from .get_entity_scale import *
from .label_cleaner import *
from .series_to_list import *
from .series_to_row_name import *
from .spec_to_dict import *
from ctypes import Union
from typing import Dict, List, Union
from pandas import DataFrame
from util import ner_tagger


class Preprocessor:
    def __init__(self, spec: str, raw_caption: str) -> None:
        # Private variables
        self.__hicharts: Dict = spec_to_dict(spec)
        self.__data: List[List] = series_to_list(self.__hicharts['series'])

        #Chart Metadata
        self.chart_type: Dict[str, Union[bool, str]] = get_chart_type(self.__hicharts)
        self.axis_title: str = None
        try:
            self.axis_title = self.__hicharts['yAxis'][0]["title"]["text"]
        except:
            self.axis_title = self.__hicharts['yAxis']["title"]["text"]

        #Table Metadata
        self.entity_scale: int = get_entity_scale(self.axis_title)
        self.column_names: List[str] = [label_cleaner(column_name) for column_name in self.__hicharts['xAxis']['categories']]
        self.row_names:  List[str] = series_to_row_name(self.__hicharts['series'])

        self.column_number: int = len(self.column_names)
        self.row_number: int = len(self.row_names)

        self.column_type: str = get_column_type(self.column_names)
        self.row_type: str = get_column_type(self.row_names)

        #Table Data
        self.table: DataFrame = DataFrame(self.__data, columns=self.column_names, index=self.row_names)

        # Natural Language Summary Data
        paragraphs: List[str] = raw_caption.split("\n")
        selected_paragraph: str = None

        if len(paragraphs) == 1:
            selected_paragraph = paragraphs[0]
        else:
            selected_paragraph = paragraphs[0] if len(paragraphs[0]) > len(paragraphs[1]) else paragraphs[1]

        self.caption: str = selected_paragraph
        self.ner_tagged: Dict[str, Union[str, List]] = ner_tagger(self.caption)
        self.data_tagged: str = None
