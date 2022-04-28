from sklearn.model_selection import train_test_split
from spec import Specification
from typing import List, Dict, Tuple
import json
from multiprocessing import Pool, cpu_count
from pandas import DataFrame
import os
import argparse
parser = argparse.ArgumentParser()

parser.add_argument("--data_folder", type=str, default="data_e2e2")

args = parser.parse_args()

output_folder = args.data_folder

try:
    os.mkdir(f"./{output_folder}")
except:
    pass


def specify_worker(datas: List[Dict[str, str]]) -> List[Specification]:
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
    results: List[Specification] = []
    err_id: List[int] = []
    for data in datas:
        try:
            spec: Specification = Specification(data)
            intent_counter['all_sentence'] += len(spec.sentences)
            chart_type_counter['all_datas'] += 1
            if len(spec.recipes) == 0:
                continue
            for intent in spec.intent_objects:
                intent_counter[intent.action] += 1

            chart_type_counter[spec.chart_type] += 1

            table = spec.table.to_csv(index=True)

            spec.e2es = {
                'recipe': spec.e2erecipe.get(),
                'table': table,
                'row_type': spec.row_type,
                'caption': spec.e2ecaption,
            }

            for recipe in spec.recipes:
                spec.objs.append({
                    'recipe': recipe.get(),
                    'table': table,
                    'row_type': spec.row_type,
                    'caption': recipe.caption,
                })

            results.append(spec)
        except:
            err_id.append(data['id'])
    return results, chart_type_counter, intent_counter


if __name__ == "__main__":
    print(f"Convering Raw Datasets to Specifications...")
    corenum = cpu_count()
    data_length = 0

    data_schemas: List[Dict[str, str]] = []
    with open(f"./data/statista.json", "r") as f:
        data_schemas = json.load(f)[0:100]

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
        for k, v in p[1].items():
            chart_type_counter[k] += v

        for k, v in p[2].items():
            intent_counter[k] += v

    train_set: List[Specification]
    valid_and_test_set: List[Specification]
    valid_set: List[Specification]
    test_set: List[Specification]

    print(len(results))

    train_set, valid_and_test_set = train_test_split(results, test_size=0.2)
    valid_set, test_set = train_test_split(valid_and_test_set, test_size=0.5)

    train_dicts = []
    valid_dicts = []
    test_dicts = []

    train_e2e_dicts = []
    valid_e2e_dicts = []
    test_e2e_dicts = []

    print("=" * 50)
    print(f"Number of data processed: ", chart_type_counter["all_datas"])
    print("=" * 50)
    print("Converting Specifications to Train/Test Datasets...")

    for spec in train_set:
        train_dicts.extend(spec.objs)
        train_e2e_dicts.append(spec.e2es)

    for spec in valid_set:
        valid_dicts.extend(spec.objs)
        valid_e2e_dicts.append(spec.e2es)

    for spec in test_set:
        test_dicts.append(spec.objs[-1])
        test_e2e_dicts.append(spec.e2es)


    print("=" * 50)
    print(f"Number of Recipe processed: {len(train_dicts)},{len(valid_dicts)}, {len(test_dicts)}")
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

    valid_df: DataFrame = DataFrame({
        "recipe": [data["recipe"] for data in valid_dicts],
        "table": [data["table"] for data in valid_dicts],
        "row_type": [data["row_type"] for data in valid_dicts],
        "caption": [data["caption"] for data in valid_dicts],
    })

    test_df: DataFrame = DataFrame({
        "recipe": [data["recipe"] for data in test_dicts],
        "table": [data["table"] for data in test_dicts],
        "row_type": [data["row_type"] for data in test_dicts],
        "caption": [data["caption"] for data in test_dicts],
    })

    train_e2e_df : DataFrame = DataFrame({
        "recipe": [data["recipe"] for data in train_e2e_dicts],
        "table": [data["table"] for data in train_e2e_dicts],
        "row_type": [data["row_type"] for data in train_e2e_dicts],
        "caption": [data["caption"] for data in train_e2e_dicts],
    })

    valid_e2e_df : DataFrame = DataFrame({
        "recipe": [data["recipe"] for data in valid_e2e_dicts],
        "table": [data["table"] for data in valid_e2e_dicts],
        "row_type": [data["row_type"] for data in valid_e2e_dicts],
        "caption": [data["caption"] for data in valid_e2e_dicts],
    })

    test_e2e_df : DataFrame = DataFrame({
        "recipe": [data["recipe"] for data in test_e2e_dicts],
        "table": [data["table"] for data in test_e2e_dicts],
        "row_type": [data["row_type"] for data in test_e2e_dicts],
        "caption": [data["caption"] for data in test_e2e_dicts],
    })




    print("Writing File... ")
    try:
        train_df.to_csv(f"./{output_folder}/statista_train.csv", index=False)
        valid_df.to_csv(f"./{output_folder}/statista_valid.csv", index=False)
        test_df.to_csv(f"./{output_folder}/statista_test.csv", index=False)
        train_e2e_df.to_csv(f"./{output_folder}/statista_train_e2e.csv", index=False)
        valid_e2e_df.to_csv(f"./{output_folder}/statista_valid_e2e.csv", index=False)
        test_e2e_df.to_csv(f"./{output_folder}/statista_test_e2e.csv", index=False)
        print("Done!")
    except:
        print("Writing file error")
