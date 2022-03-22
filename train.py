import pandas as pd
from simplet5 import SimpleT5
from sklearn.model_selection import train_test_split

df = pd.read_csv("./data/statista_seq_selection_train.csv")
df_input = pd.DataFrame({
    "source_text": df["source_sequence"],
    "target_text": df["target_sequence"]
})

train_df, val_df = train_test_split(df_input, test_size=0.2, random_state=42)
model = SimpleT5()

model.from_pretrained(model_type="t5", model_name="google/t5-v1_1-small")
model.train(train_df=train_df,
    eval_df=val_df,
    source_max_token_len=128,
    target_max_token_len=128,
    batch_size=32,
    max_epochs=30,
    use_gpu=True
)
