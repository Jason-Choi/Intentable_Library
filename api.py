from fastapi.staticfiles import StaticFiles
import random
import time
import pandas as pd
from simplet5 import SimpleT5
from fastapi import FastAPI
import io
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from itertools import permutations, combinations
from fastapi.responses import RedirectResponse
import json

origins = ["*"]
model = SimpleT5()
data_folder = "data"
model_folder = "/root/exthdd/outputs/data/t5-small/"

modelname = "t5-v1_1-small-e-7-tl-0.9286-vl-0.9893-e-3-tl-0.7646-vl-0.9725"
model.load_model("t5", outputdir=model_folder, model_name=modelname, use_gpu=False, gpu_id=1)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

class PredictData(BaseModel):
    recipe: str


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
        "caption": sample_caption
    }


@app.get("/get_from_test_set")
async def demo():
    sample = test_set.sample(1, random_state=random.randint(0, 100000))
    res = get_response_from_sample(sample)
    print(res)
    return res


@app.post("/predict_sentencewise/")
async def predict(data: PredictData):
    print(data.recipe)
    org_recipe = json.loads(data.recipe)
    intents = org_recipe['intents']
    org_recipe['intents'] = []
    new_recipes = []

    for intent in intents:
        new_recipe = org_recipe.copy()
        print(new_recipe)
        new_recipe['intents'] = [intent]
        new_recipes.append(new_recipe)

    predicted_sentences = [model.predict(source_text=json.dumps(s), num_beams=4)[0] for s in new_recipes]

    return {'predict': " ".join(predicted_sentences)}


@app.post("/predict_paragraph/")
async def predict(data: PredictData):
    print(data.recipe)
    return {'predict': model.predict(source_text=data.recipe, num_beams=4)[0]}


@app.get("/")
async def root():
    # redirect to /static
    return RedirectResponse("/static/index.html", status_code=302)