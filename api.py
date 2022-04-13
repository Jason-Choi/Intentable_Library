import pandas as pd
from simplet5 import SimpleT5
from fastapi import FastAPI
import io
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from itertools import permutations, combinations

origins = ["*"]
model = SimpleT5()


modelname = "simplet5-epoch-16-train-loss-0.6413-val-loss-0.6287"
model.load_model("t5", f"outputs/{modelname}", use_gpu=False)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Elements(BaseModel):
    caption: str
    elements: List[str]

    def get_captions(self):
        captions: List[str] = []
        for i in range(1, 4):
            for caption_list in permutations(self.elements, i):
                caption = self.caption
                caption_overall = self.caption + "<selection_item>overall</selection_item>"
                caption += "".join(caption_list)
                caption_overall += "".join(caption_list)
                caption_overall += "</selection>"
                caption += "</selection>"
                captions += [caption, caption_overall]
        return captions


test_set = pd.read_csv("./data/statista_test.csv", header=0, index_col=0)
train_set = pd.read_csv("./data/statista_train.csv", header=0, index_col=0)


def get_response_from_sample(sample):
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
    row_type = "DATE" if sample['row_type'].iloc[0] == "DATE" else "NOMINAL"
    return {
        "title": sample['title'].iloc[0],
        "value_info": sample['value_info'].iloc[0],
        "chart_type": sample['chart_type'].iloc[0],
        "row_type": row_type,
        "table": table,
    }


@app.get("/get_from_test_set")
async def demo():
    sample = test_set.sample(1)
    res = get_response_from_sample(sample)
    print(res)
    return res


@app.get("/get_from_train_set")
async def demo():
    sample = test_set.sample(1)
    res = get_response_from_sample(sample)
    print(res)
    return res


@app.get("/predict/")
async def predict(caption: str):
    print(caption)
    return {'predict': model.predict(source_text=caption, max_length=256, num_beams=10)[0]}


@app.post("/automatic/")
async def automatic(elements: Elements):
    captions = elements.get_captions()
    ranked_caption = [(model.score(caption)[0][0], caption) for caption in captions]
    sorted_caption = sorted(ranked_caption, reverse=True, key=lambda x: x[0])
    print(sorted_caption)
    return {'predict': model.predict(
        source_text=sorted_caption[0][1].replace("Score:", "Generate:"),
        max_length=256,
        num_beams=10
    )[0]}
