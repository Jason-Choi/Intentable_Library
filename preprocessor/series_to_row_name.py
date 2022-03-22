from typing import Dict, List
from Specification.label_cleaner import label_cleaner

def series_to_row_name(series: List[Dict]) -> List[str]:
    index = []
    for row in series:
        index.append(
            label_cleaner(str(row['name']))
        )
    return index
