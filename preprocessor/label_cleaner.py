def label_cleaner(label : str) -> str:

    return label.lower().replace("*", "").replace("<b>", "").replace("</b>", "").replace("<em>", "").replace("</em>", "").replace("<br>", " ").replace("\r", "").replace("</b<", "").replace("&amp;", "&")
