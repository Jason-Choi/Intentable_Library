from nltk.tokenize.treebank import TreebankWordDetokenizer, TreebankWordTokenizer
from typing import List
from util.entity_formatter import number_to_word


def is_token_includes(caption: str, token: str) -> bool:
    token_split: List[str] = TreebankWordTokenizer().tokenize(token)
    token_length = len(token_split)

    caption_tokens: List[str] = TreebankWordTokenizer().tokenize(caption)
    
    for i, caption_token in enumerate(caption_tokens):
        if caption_token == token_split[0]:
            if token_length == 1:
                return True
            else:
                for j in range(1, token_length):
                    if i + j >= len(caption_tokens):
                        return False
                    if caption_tokens[i + j] != token_split[j]:
                        return False
                return True