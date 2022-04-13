from typing import List
from inflect import engine

e = engine()

percent_keyword = [
    "share",
    "percent",
    "percentage",
    "rate",
    "change",
    "growth",
]
big_number_dict = {
    "hundred": 100,
    "thousand": 1000,
    "million": 1000000,
    "billion": 1000000000,
    "trillion": 1000000000000,
    "quadrillion": 1000000000000000,
}


def number_to_word(number: int):
    return e.number_to_words(number)


def percent_formatter(input_entity: str) -> List[str]:
    formatted_numbers: List[str] = []
    formatted_numbers += [f"{i} percent" for i in nomal_number_formatter(input_entity)]
    formatted_numbers += [f"{abs(float(i))} percent" for i in nomal_number_formatter(input_entity)]
    formatted_numbers.append(f"{number_to_word(int(round(float(input_entity),0)))} percent")
    formatted_numbers.append(f"{number_to_word(abs(int(round(float(input_entity), 0))))} percent")
    formatted_numbers += [f"{i}%" for i in nomal_number_formatter(input_entity)]
    formatted_numbers += [f"{abs(float(i))}%" for i in nomal_number_formatter(input_entity)]
    formatted_numbers.append(f"{number_to_word(int(round(float(input_entity),0)))}%")
    formatted_numbers.append(f"{number_to_word(abs(int(round(float(input_entity), 0))))}%")
    formatted_numbers.append(f"{number_to_word(int(float(input_entity)))}%")
    formatted_numbers.append(f"{number_to_word(abs(int(float(input_entity))))}%")
    formatted_numbers += [f"{i}" for i in nomal_number_formatter(input_entity)]
    formatted_numbers += [f"{abs(float(i))}" for i in nomal_number_formatter(input_entity)]
    return formatted_numbers


def big_number_formatter(real_entity: float) -> List[str]:
    foramtted_numbers: List[str] = [f"{real_entity:,.{i}f}" for i in range(0, 3)]

    for word, number in big_number_dict.items():
        if real_entity // number >= 1:
            foramtted_numbers.append(f"{number_to_word(int(real_entity // number))} {word}")
            foramtted_numbers.append(f"{int(real_entity / (number*10)) * 10} {word}")
            foramtted_numbers.append(f"{real_entity / number:,.0f} {word}")
            foramtted_numbers.append(f"{real_entity / number:,.1f} {word}")
            foramtted_numbers.append(f"{real_entity / number:,.2f} {word}")

    return list(reversed(foramtted_numbers))


def nomal_number_formatter(input_entity: str) -> List[str]:
    formatted_entities: List[str] = [input_entity]
    real_entity = float(input_entity)

    if "." in input_entity:
        formatted_entities += [f"{real_entity:,.{i}f}" for i in range(2, -1, -1)]
        formatted_entities += [f"{real_entity:.{i}f}" for i in range(2, -1, -1)]
    else:
        formatted_entities += [f"{real_entity:,.0f}"]
        formatted_entities += [f"{real_entity:.0f}"]
        formatted_entities += [f"{round(real_entity, i):,.0f}" for i in range(0, -len(input_entity)-1, -1)]

    return [x for x in formatted_entities if x != "0"]


def format_with_axis_title(input_entity: str, axis_title: str) -> List[str]:
    axis_title = axis_title.replace("(", "").replace(")", "")
    if " in " not in axis_title:
        return []
    format_string = axis_title.lower().split(" in ")
    return [input_entity + " " + format_string[1]]


def is_percentage(input_entity: str, axis_title: str) -> bool:
    axis_title = axis_title.lower()
    for keyword in percent_keyword:
        if keyword in axis_title and abs(float(input_entity)) <= 100:
            return True
    return False


def entity_formatter(input_entity: str, axis_title: str) -> List[str]:
    axis_title = axis_title.lower()
    # Percent
    if is_percentage(input_entity, axis_title):
        return format_with_axis_title(input_entity, axis_title) + percent_formatter(input_entity)

    # Big Number
    for word, number in big_number_dict.items():
        if word in axis_title:
            real_entity: float = float(input_entity) * number
            return format_with_axis_title(input_entity, axis_title) + big_number_formatter(real_entity)

    # Normal Number
    if float(input_entity) > 100:
        return format_with_axis_title(input_entity, axis_title) + big_number_formatter(float(input_entity)) + nomal_number_formatter(input_entity)
    else:
        return format_with_axis_title(input_entity, axis_title) + nomal_number_formatter(input_entity)


if __name__ == "__main__":
    print(entity_formatter("9.07", "Average cost in U.S. dollars per million Btu"))
