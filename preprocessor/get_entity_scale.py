def get_entity_scale(title : str)-> int:
    if 'milion' in title:
        return 1000000
    elif 'thousand' in title:
        return 1000
    elif 'bilion' in title:
        return 1000000000
    elif 'trilion' in title:
        return 1000000000000
    else:
        return 1
