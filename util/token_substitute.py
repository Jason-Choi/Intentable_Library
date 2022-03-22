from typing import List
from pandas import DataFrame
import re

regname = re.compile("(?<=\<name>)(.*?)(?=<\/name>)")
regentity = re.compile("(?<=\<entity>)(.*?)(?=<\/entity>)")


def name_retokenzie(token: str) -> str:
    return f"<name> {token} </name>"

def entity_retokenzie(token: str) -> str:
    return f"<entity> {token} </entity>"

def excute_special_token(token : str, table : DataFrame) -> str:
    if token

def token_substitute(caption: str, talbe: DataFrame) -> str:
    """
    Substitute tokens in a caption with the corresponding token in the table.
    """

    name_token_list: List[str] = [t.strip().split(", ") for t in regname.findall(caption)]
    entity_token_list: List[str] = [t.strip().split(", ") for t in regentity.findall(caption)]
    token_list : List[str] = name_token_list + entity_token_list


    for token in token_list:
        if len(token) == 1:
            if token[0] == "namemostpast":
                caption.replace(name_retokenzie(token[0]), talbe.index.tolist()[0])
            elif token[0] == "namemostrecent":
                caption.replace(name_retokenzie(token[0]), talbe.index.tolist()[-1])
        elif len(token) == 2:
            atoms = token.split(" : ")
            if atoms[0] == 'col':
                if atoms[1].isnumeric():
                    caption.replace(entity_retokenzie(token), talbe.columns[int(atoms[1])])
                else:

            elif atoms[0] == 'row':
                caption.replace(entity_retokenzie(token), talbe.index[int(atoms[1])])
            
            elif atoms[1].isnumeric():




predicted_caption = """
this bar chart shows the annual turnover of the mining and quarrying industry in finland from <name> row : namemostpast </name> to <name> row : namemostrecent </name>. in <name> row : 7 </name>, the mining and quarrying industry produced a turnover of approximately <name> row : entitymostrecent, column : 0 </name> euros.
"""
