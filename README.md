# Intentable Dataset Library

## Scrape

Setup databases with config.py, scraper/scrapy.cfg and follow insturction to scrape
```shell
cd scraper/statistaScrpae
scrapy crawl statistaSpider -s JOBDIR=log/statistalog
```
## Data Cleansing
```
See DatabaseInteraction.ipynb or JSONInteraction.ipynb
```
Using preprocessor module to cleansing / tagging / preprocess data. 

## Generate Train/Valid/Test Set

Copy [preprocessed JSON dataset](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/6fb36e64-e1de-4073-86cb-a9c996a7c12e/statista.json?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220322%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220322T073325Z&X-Amz-Expires=86400&X-Amz-Signature=e38b2d6a662dd07fdaf38d009483a0a1277297114360b1a66555a14816324e79&X-Amz-SignedHeaders=host&response-content-disposition=filename%20%3D%22statista.json%22&x-id=GetObject) to data/statista.json and 
```shell
# User Selection 
python generate_sequence_selection.py

# End to End
python generate_sequence_endto-end.py
```

## Train 
See train.py

## Predict
See predict.ipynb

## API Serve
See api.py
