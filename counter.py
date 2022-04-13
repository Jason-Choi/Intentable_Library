from dataclasses import dataclass
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from spec import Specification
from typing import List, Dict
import json
from multiprocessing import Pool, cpu_count
from pandas import DataFrame

@dataclass
class Counter:
    id1 : int = 0
    id2 : int = 0
    cmp : int = 0
    dis : int = 0
    smr : int = 0

def worker(datas : List[Dict[str, str]]) -> None:
    counter = Counter()
    for data in datas:
        try:
            spec : Specification = Specification(data)
            for intent in spec.intent_objects:
                if intent.action == "identify" and intent.type == "one":
                    counter.id1 += 1
                elif intent.action == "identify" and intent.type == "two":
                    counter.id2 += 1
                elif intent.action == "compare":
                    counter.cmp += 1
                elif intent.action == "discover":
                    counter.dis += 1
                elif intent.action == "summary":
                    counter.smr += 1
        except:
            pass
    return counter


if __name__ == "__main__":
    print(f"Generating datasets...")
    corenum = cpu_count()
    data_length = 0

    data_schemas: List[Dict[str, str]] = []
    with open("./data/statista.json", "r") as f:
        data_schemas = json.load(f)
    limit = len(data_schemas) // (corenum - 1)
    splited_data = [data_schemas[i*limit: (i+1)*limit] for i in range(corenum)]
    print("=" * 50)
    print(f"Dataset Size : {len(data_schemas)}\nNumber of processes: {corenum}\nNumber of data per thread: {limit}")
    print("=" * 50)
    print("Processing...")

    pool = Pool(processes=corenum)
    result_pool : List[Counter] = pool.map(worker, splited_data)
    pool.close()
    pool.join()

    counter = Counter()

    for c in result_pool:
        counter.id1 += c.id1
        counter.id2 += c.id2
        counter.cmp += c.cmp
        counter.dis += c.dis
        counter.smr += c.smr

    print(counter)