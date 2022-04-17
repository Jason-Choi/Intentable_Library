def get_raw_caption(caption: str, chart_type:str) -> str:
    caption=caption.replace("&amp;", "&").replace("percentage", "percent").replace("*", "")
    # if 'bar' in chart_type:
    #     caption = caption.replace("The statistic", "The bar chart")
    #     caption = caption.replace("This statistic", "This bar chart")
    # elif 'line' in chart_type:
    #     caption = caption.replace("The statistic", "The line chart")
    #     caption = caption.replace("This statistic", "This line chart")
    # elif 'pie' in chart_type:
    #     caption = caption.replace("The statistic", "The pie chart")
    #     caption = caption.replace("This statistic", "This pie chart")
    return caption