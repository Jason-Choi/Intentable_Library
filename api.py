import pandas as pd
from simplet5 import SimpleT5
from fastapi import FastAPI
import io
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from itertools import permutations, combinations
import json

origins = ["*"]
model = SimpleT5()
data_folder = "data6"
model_folder = "outputs"

modelname = "simplet5-epoch-2-train-loss-0.6924-val-loss-0.5216"
model.load_model("t5", f"{model_folder}/{modelname}", use_gpu=False)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



test_set = pd.read_csv(f"./{data_folder}/statista_test.csv", header=0)


def get_response_from_sample(sample):
    sample_table = sample['table'].iloc[0]
    sample_recipe = json.loads(sample['recipe'].iloc[0])
    sample_table = pd.read_csv(io.StringIO(sample_table), header=0, index_col=0)
    sample_caption = sample['caption'].iloc[0]
    table = []
    for index, row in sample_table.iterrows():
        row = row.to_dict()
        if len(row.keys()) == 1:
            row = {"value": row.popitem()[1]}
        if row.get(" ") is not None:
            row["value"] = row.pop(" ")
        row["characteristic"] = str(index)
        table.append(row)
    print(table)
    row_type = "DATE" if sample['row_type'].iloc[0] == "DATE" else "NOMINAL"
    return {
        "recipe": sample_recipe,
        "row_type": row_type,
        "table": table,
        "caption" : sample_caption
    }


@app.get("/get_from_test_set")
async def demo():
    sample = test_set.sample(1)
    res = get_response_from_sample(sample)
    print(res)
    return res


@app.get("/predict/")
async def predict(caption: str):
    print(caption)
    return {'predict': model.predict(source_text=caption, num_beams=4)[0]}