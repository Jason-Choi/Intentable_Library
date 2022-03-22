from flair.data import Sentence
from typing import Dict, List, Union
from typing import Dict
from flair.models import SequenceTagger
# tagger = SequenceTagger.load('ner-ontonotes-large')

def ner_tagger(string: str) -> Dict[str, Union[str, List]]:
    sentence: Sentence = Sentence(string)
    tagger.predict(sentence)

    dict_flair: Dict[str, Union[str, List]] = sentence.to_dict(tag_type='ner')
    for i in dict_flair['entities']:
        i['end'] = i.pop('end_pos')
        i['start'] = i.pop('start_pos')
        label = i.pop('labels')[0]
        i['label'] = str(label).split(" ")[0]

    dict_flair['ents'] = dict_flair.pop('entities')

    return dict_flair