from typing import Dict, List, Union
from util import ner_tagger


def get_column_type(column : List[str]) -> str:
    if len(column) == 0:
        return None
        
    dict_flair: Dict[str, Union[str, List]] = ner_tagger(column[0])
    if len(dict_flair['ents']) != 1:
        return None
    else:
        label = dict_flair['ents'][0]['labels'][0]
        return str(label).split(" ")[0]

