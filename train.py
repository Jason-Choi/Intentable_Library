import pandas as pd
from simplet5 import SimpleT5
from sklearn.model_selection import train_test_split
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--data_folder", type=str, default="data")
parser.add_argument("--batch_size", type=int, default=16)
parser.add_argument("--use_wandb", type=int, default=True)
parser.add_argument("--model_name", type=str, default=None)
parser.add_argument("--from_checkpoint", type=bool, default=False)
parser.add_argument("--gpu_num", type=int, default=0)
parser.add_argument("--e2e", type=bool, default=False)


args = parser.parse_args()

data_folder = args.data_folder
batch_size = args.batch_size
use_wandb = args.use_wandb
model_size = None
model_name = args.model_name
if "small" in model_name:
    model_size = "small"
elif "large" in model_name:
    model_size = "large"
elif "base" in model_name:
    model_size = "base"

from_checkpoint = args.from_checkpoint
gpu_num = args.gpu_num
model_type = "t5" if "t5" in model_name else "bart"
output_folder = f"/root/exthdd/outputs/{data_folder}/{model_type}-{model_size}"
e2e = "" if args.e2e is False else "_e2e"



df = pd.read_csv(f"./{data_folder}/statista_train{e2e}.csv")
train_df = pd.DataFrame({
    "source_text": df["recipe"],
    "target_text": df["caption"]
})

df = pd.read_csv(f"./{data_folder}/statista_valid{e2e}.csv")
valid_df = pd.DataFrame({
    "source_text": df["recipe"],
    "target_text": df["caption"]
})


model = SimpleT5(use_wandb=use_wandb)

if from_checkpoint:
    model.load_model(model_type=model_type, outputdir=output_folder, model_name=model_name, use_gpu=True)

else:
    model.from_pretrained(model_type=model_type, model_name=model_name, outputdir=output_folder, use_gpu=True)
    



model.train(train_df=train_df,
            eval_df=valid_df,
            source_max_token_len=512,
            target_max_token_len=128,
            batch_size=batch_size,
            max_epochs=100,
            use_gpu=True,
            dataloader_num_workers=8,
            gpu_num=[gpu_num],
            outputdir=output_folder
            )
