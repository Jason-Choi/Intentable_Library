from typing import Dict, List


def series_to_list(series: List[Dict]) -> List[List]:
    allrows: List = []
    for row in series:
        rowlist = []
        for d in row['data']:
            if d is None:
                rowlist.append(0)
            else:
                rowlist.append(d["y"])
        allrows.append(rowlist)
    return allrows
