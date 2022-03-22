import json

from typing import Dict


def spec_to_dict(spec : str) -> Dict:
    cutstart = spec.find('"headerFormat"')-1
    cutend = spec.find('"plotOptions"')-2

    cut2start = spec.find('"<b><span')-10
    cut2end = spec.find('"line":{')-3

    fixedjson = spec[:cutstart] + spec[cutend:cut2start] + spec[cut2end:]
    try:
        return json.loads(fixedjson)
    except json.JSONDecodeError as e:
        errorindex = int(str(e).split(" ")[-1].rstrip(")"))