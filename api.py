from operator import index
import pandas as pd
from simplet5 import SimpleT5
from fastapi import FastAPI
import json
import random
import io
from pydantic import BaseModel
from typing import List, Dict
from specification import Specification as DemoSpecification
from fastapi.middleware.cors import CORSMiddleware
origins = ["*"]
model = SimpleT5()


modelname = "trained_model"
model.load_model("t5", f"{modelname}", use_gpu=True)


class Input(BaseModel):
    chart_type: str
    title: str
    value_info: str = ""
    is_overall: bool = True
    selected_elements: List[str] = []
    table : str 


class InputSpecification:
    def __init__(self, input: Input) -> None:
        self.title = input.title
        self.chart_type = input.chart_type
        self.value_info = input.value_info
        self.table: pd.DataFrame = pd.read_csv(io.StringIO(input.table), header=0, index_col=0)
        self.is_overall = input.is_overall
        self.selected_elements = input.selected_elements

    def get_seq(self) -> str:
        seq = f"<is_overall>{self.is_overall}</is_overall>"
        seq += f"<chart_type>{self.chart_type}</chart_type>"
        seq += f"<title>{self.title}</title>"
        seq += f"<value_info>{self.value_info}</value_info>"
        selection = " ".join(self.selected_elements)
        seq += f"<selection>{selection}</selection>"
        return seq

    def predict(self) -> str:
        return model.predict(
            source_text=self.get_seq(),
            num_beams=4,
        )[0]


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

test_set = pd.read_csv("./data/statista_test.csv", header=0, index_col=0)
train_set = pd.read_csv("./data/statista_train_valid.csv", header=0, index_col=0)



@app.get("/get_from_test_set")
async def demo():
    sample = test_set.sample(1)
    sample_table = sample['table'].iloc[0]
    sample_table = pd.read_csv(io.StringIO(sample_table), header=0, index_col=0)
    
    table = []
    for index, row in sample_table.iterrows():
        row = row.to_dict()
        if len(row.keys()) == 1:
            row = {"value": row.popitem()[1]}
        if row.get(" ") is not None:
            row["value"] = row.pop(" ")
        row["characteristic"] = index
        table.append(row)
    print(table)
    return {
        "title": sample['title'].iloc[0],
        "value_info": sample['value_info'].iloc[0],
        "chart_type": sample['chart_type'].iloc[0],
        "table": table,
    }


@app.get("/get_from_train_set")
async def demo():
    sample = train_set.sample(1)
    sample_table = sample['table'].iloc[0]
    sample_table = pd.read_csv(io.StringIO(table), header=0, index_col=0)

    table = []
    for index, row in sample_table.iterrows():
        row = row.to_dict()
        if len(row.keys()) == 1:
            row = {"value": row.popitem()[1]}
        if row.get(" ") is not None:
            row["value"] = row.pop(" ")
        row["characteristic"] = index
        table.append(row)
    print(table)
    return {
        "title": sample['title'].iloc[0],
        "value_info": sample['value_info'].iloc[0],
        "chart_type": sample['chart_type'].iloc[0],
        "table": table,
    }


@app.get("/predict/")
async def predict(caption : str):
    print(caption)
    print(model.predict(source_text=caption.lower(), num_beams=4)[0])
    return {'predict' : model.predict(source_text=caption, num_beams=4)[0]}