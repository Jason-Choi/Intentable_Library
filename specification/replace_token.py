from .util import *
from nltk.tokenize.treebank import TreebankWordDetokenizer, TreebankWordTokenizer
from typing import List
from util.entity_formatter import number_to_word


def replace_token(caption: str, target_value: str, token: str) -> str:
    if target_value.isnumeric() or target_value.replace(".", "").isnumeric():
        caption_tokens: List[str] = TreebankWordTokenizer().tokenize(caption)
        if number_to_word(target_value) in caption_tokens:
            caption_tokens[caption_tokens.index(number_to_word(target_value))] = token
        else:
            skip_token = False
            for i, caption_token in enumerate(caption_tokens):
                if skip_token == False and caption_token == "<":
                    skip_token = True
                elif skip_token == True and caption_token == ">":
                    skip_token = False
                elif skip_token:
                    continue
                elif caption_token == target_value:
                    caption_tokens[i] = token
                elif caption_token.rstrip(",.?!") == target_value:
                    caption_tokens[i] = token + "."

        caption: str = TreebankWordDetokenizer().detokenize(caption_tokens)
    else:
        caption = caption.replace(get_left_spaced_string(target_value), get_left_spaced_string(token))
        caption = caption.replace(get_braketed_string(target_value), get_braketed_string(token))

    return caption
