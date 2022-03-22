from typing import Dict, List


def get_chart_type(spec : Dict) -> List[str]:
    type = spec['chart']['type'] if spec['chart']['type'] != 'column' else 'bar'
    stacked = True if spec['plotOptions']['series']['stacking'] == 'normal' else False
    transposed = True if spec['chart']['type'] == 'column' else False
    return {
        'type': type,
        'stacked': stacked,
        'transposed': transposed
    }