from spacy import displacy

def visualize_ner(string : str) -> None:
    displacy.render(string, style="ent", manual=True)
