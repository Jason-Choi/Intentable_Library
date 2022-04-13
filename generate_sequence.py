from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from spec import Specification
from typing import List, Dict
import json
from multiprocessing import Pool, cpu_count
from pandas import DataFrame


def worker(datas: List[Dict[str, str]]) -> None:
    err_id: List[int] = []
    results: List[Dict[str, str]] = []

    for data in datas:
        try:
            spec: Specification = Specification(data)
            for recipe in spec.recipes:
                result = {
                    'recipe': recipe.get(),
                    'table': spec.table.to_csv(index=True),
                    'row_type': spec.row_type,
                    'caption' : recipe.caption,
                    'automatic': str(recipe.is_full).lower()
                }
                results.append(result)
        except:
            err_id.append(data["id"])
    return err_id, results


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
    result_pool = pool.map(worker, splited_data)
    pool.close()
    pool.join()

    res = []
    err = []
    for err_id, results in result_pool:
        res += results
        err += err_id

    print("=" * 50)
    print(f"Number of data processed: {len(res)}")
    print(f"Number of data error: {len(err)}")
    print("=" * 50)
    print("Convert To DataFrame...")
    res_df: DataFrame = DataFrame({
        "recipe": [data["recipe"] for data in res],
        "table": [data["table"] for data in res],
        "row_type": [data["row_type"] for data in res],
        "caption": [data["caption"] for data in res],
        "automatic": [data["automatic"] for data in res]
    })
    err_df: DataFrame = DataFrame({
        "id": err,
    })
    train_df, test_df = train_test_split(res_df, test_size=0.2)
    train_df: DataFrame = train_df
    test_df: DataFrame = test_df

    gen_df = train_df[['recipe', 'caption']].copy()
    gen_df['recipe'] = "Generate: " + gen_df['recipe'].astype(str)
    score_df = train_df[['recipe', 'automatic']].copy()
    score_df.rename(columns={'automatic': 'caption'}, inplace=True)
    score_df['recipe'] = "Score: " + score_df['recipe'].astype(str)
    train_df = score_df.append(gen_df)
    shuffle(train_df)
    train_df, valid_df = train_test_split(train_df, test_size=0.25)
    valid_df: DataFrame = valid_df

    print("Writing File... ")
    try:
        res_df.to_csv("./data/statista_all.csv", index=False)
        train_df.to_csv("./data/statista_train.csv", index=False)
        valid_df.to_csv("./data/statista_valid.csv", index=False)
        test_df.to_csv("./data/statista_test.csv", index=False)
        err_df.to_csv("./data/statista_err.csv", index=False)
        print("Done!")
        print(len(train_df), len(valid_df), len(test_df))
    except:
        print("Writing file error")
