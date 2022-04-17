import string
from pandas import DataFrame
from typing import Dict, List, Union
from dataclasses import dataclass
from util.dto import Target


@dataclass
class Feature:
    max: Union[float, int]
    min: Union[float, int]
    recent: int
    past: int = 0


def get_feature(features: Feature, row_number: int, value: Union[float, int], value_type: string) -> List[str]:
    feature_list: List[str] = []
    if value_type == "DATE":
        if row_number == features.recent:
            feature_list.append('recent')
        if row_number == features.past:
            feature_list.append('past')
    if value == features.max:
        feature_list.append('max')
    if value == features.min:
        feature_list.append('min')
    return feature_list


def get_target_list(table: DataFrame, value_type: str) -> List[Target]:
    target_list: List[Target] = []
    columnwise_max = table.max(axis=0).tolist()
    columnwise_min = table.min(axis=0).tolist()
    column_name = table.columns.tolist()
    column_target_lists = []

    for i in range(len(table.columns)):
        features = Feature(columnwise_max[i], columnwise_min[i], len(table.index)-1)
        column_target_list: List[Target] = []
        for j in range(len(table.index)):
            column_target_list.append(
                Target(
                    value=table.iloc[j, i],
                    key=str(table.index[j]),
                    series=str(table.columns[i]),
                    feature=get_feature(features, j, table.iloc[j, i], value_type)
                )
            )
        column_target_lists.append(column_target_list)
    
    return dict(zip(column_name, column_target_lists))
