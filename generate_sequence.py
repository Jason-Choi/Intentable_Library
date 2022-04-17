from cgi import test
from concurrent.futures import process
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from spec import Specification
from typing import List, Dict, Tuple
import json
from multiprocessing import Pool, cpu_count
from pandas import DataFrame
from dataclasses import dataclass
import os

output_folder = "data6"
test_set_ratio = 0.1
valid_set_ratio = test_set_ratio / (1-test_set_ratio)
try:
    os.mkdir(f"./{output_folder}")
except:
    pass


def specify_worker(datas: List[Dict[str, str]]) -> List[Specification]:
    intent_counter = {
        "all_sentence": 0,
        "overview": 0,
        "describe": 0,
        "compare": 0,
        "trend": 0
    }
    results: List[Specification] = []
    err_id: List[int] = []
    setences_num = 0
    processed_nums = 0
    for data in datas:
        try:
            spec: Specification = Specification(data)
            intent_counter['all_sentence'] += len(spec.sentences)
            processed_nums += 1
            if len(spec.recipes) == 0:
                continue
            for intent in spec.intent_objects:
                intent_counter[intent.action] += 1
            results.append(spec)
        except:
            err_id.append(data['id'])
    return results, processed_nums, intent_counter


if __name__ == "__main__":
    print(f"Convering Raw Datasets to Specifications...")
    corenum = cpu_count()
    data_length = 0

    data_schemas: List[Dict[str, str]] = []
    with open(f"./data/statista.json", "r") as f:
        data_schemas = json.load(f)

    limit = len(data_schemas) // (corenum - 1)
    splited_data = [data_schemas[i*limit: (i+1)*limit] for i in range(corenum)]
    print("=" * 50)
    print(f"Dataset Size : {len(data_schemas)}\nNumber of processes: {corenum}\nNumber of data per thread: {limit}")
    print("=" * 50)
    print("Processing...")
    chart_type_counter = {
        "all_datas": 0,
        "bar": 0,
        "grouped_bar": 0,
        "stacked_bar": 0,
        "line": 0,
        "multi_line": 0,
        "pie": 0
    }
    intent_counter = {
        "all_sentence": 0,
        "overview": 0,
        "describe": 0,
        "compare": 0,
        "trend": 0
    }
    pool = Pool(processes=corenum)
    result_pool: Tuple[List[Specification], int, Dict[str, int]] = pool.map(specify_worker, splited_data)
    pool.close()
    pool.join()

    results: List[Specification] = []
    for p in result_pool:
        results.extend(p[0])
        chart_type_counter["all_datas"] += p[1]
        counter: Dict[str, int] = p[2]
        for k, v in p[2].items():
            intent_counter[k] += v

    train_set: List[Specification]
    test_set: List[Specification]
    train_set, test_set = train_test_split(results, test_size=test_set_ratio)

    train_dicts: List[Dict] = []
    test_dicts: List[Dict] = []

    print("=" * 50)
    print(f"Number of data processed: ", chart_type_counter["all_datas"])
    print("=" * 50)
    print("Converting Specifications to Train/Test Datasets...")

    for spec in train_set:
        chart_type_counter[spec.chart_type] += 1
        if len(spec.recipes) == 0:
            continue
        for recipe in spec.recipes:
            result = {
                'recipe': recipe.get(),
                'table': spec.table.to_csv(index=True),
                'row_type': spec.row_type,
                'caption': recipe.caption,
            }

            train_dicts.append(result)

    for spec in test_set:
        chart_type_counter[spec.chart_type] += 1
        if len(spec.recipes) == 0:
            continue
        for recipe in spec.recipes:
            result = {
                'recipe': recipe.get(),
                'table': spec.table.to_csv(index=True),
                'row_type': spec.row_type,
                'caption': recipe.caption,
            }

            test_dicts.append(result)

    print("=" * 50)
    print(f"Number of Recipe processed: {len(train_dicts)}, {len(test_dicts)}")
    print(chart_type_counter)
    print(intent_counter)
    print("=" * 50)
    print("Convert To DataFrame...")

    train_df: DataFrame = DataFrame({
        "recipe": [data["recipe"] for data in train_dicts],
        "table": [data["table"] for data in train_dicts],
        "row_type": [data["row_type"] for data in train_dicts],
        "caption": [data["caption"] for data in train_dicts],
    })

    test_df: DataFrame = DataFrame({
        "recipe": [data["recipe"] for data in test_dicts],
        "table": [data["table"] for data in test_dicts],
        "row_type": [data["row_type"] for data in test_dicts],
        "caption": [data["caption"] for data in test_dicts],
    })

    valid_df: DataFrame

    train_df, valid_df = train_test_split(train_df, test_size=valid_set_ratio)

    print("Writing File... ")
    try:
        train_df.to_csv(f"./{output_folder}/statista_train.csv", index=False)
        valid_df.to_csv(f"./{output_folder}/statista_valid.csv", index=False)
        test_df.to_csv(f"./{output_folder}/statista_test.csv", index=False)
        print("Done!")
    except:
        print("Writing file error")
