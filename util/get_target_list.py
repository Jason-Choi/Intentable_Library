from pandas import DataFrame
from typing import Dict, List, Union
from dataclasses import dataclass
from util.dto import Target as Element


def get_element_list(table: DataFrame) -> List[Element]:
    element_list : List[Element] = []
    for i in range(len(table.columns)):
        for j in range(len(table.index)):
            element_list.append(Element(
                feature='none',
                row=str(table.index[j]),
                column=str(table.columns[i]),
                value=table.iloc[j, i]
            ))
    return element_list

def get_featured_element_list(table: DataFrame, value_type: str) -> List[Element]:
    features: List[Element] = []

    name_max = table.idxmax(axis=0).tolist()
    name_min = table.idxmin(axis=0).tolist()
    entity_max = table.max(axis=0).tolist()
    entity_min = table.min(axis=0).tolist()

    if value_type == "DATE":
        name_past = table.index.tolist()[0]
        entity_past = table.iloc[0].tolist()
        name_recent = table.index.tolist()[-1]
        entity_recent = table.iloc[-1].tolist()

        for i in range(len(table.columns)):
            features.append(Element(
                feature='past',
                row=str(name_past),
                column=str(table.columns[i]),
                value=entity_past[i]
            ))
            features.append(Element(
                feature='recent',
                row=str(name_recent),
                column=str(table.columns[i]),
                value=entity_recent[i]
            ))

    for i in range(len(table.columns)):
        features.append(Element(
            feature='max' if name_max[i] != 'total' else 'total',
            row=str(name_max[i]),
            column=str(table.columns[i]),
            value=entity_max[i]
        ))
        features.append(Element(
            feature='min',
            row=str(name_min[i]),
            column=str(table.columns[i]),
            value=entity_min[i]
        ))


    
            
    return features