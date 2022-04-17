import pandas as pd
from simplet5 import SimpleT5
from sklearn.model_selection import train_test_split

data_folder = "data6"

df = pd.read_csv(f"./{data_folder}/statista_train.csv")
train_df = pd.DataFrame({
    "source_text": df["recipe"],
    "target_text": df["caption"]
})

df = pd.read_csv(f"./{data_folder}/statista_valid.csv")
valid_df = pd.DataFrame({
    "source_text": df["recipe"],
    "target_text": df["caption"]
})

model = SimpleT5()

model.from_pretrained(model_type="t5", model_name="google/t5-v1_1-base")
model.train(train_df=train_df,
    eval_df=valid_df,
    source_max_token_len=512,
    target_max_token_len=512,
    batch_size=16,
    max_epochs=100,
    use_gpu=True
)
