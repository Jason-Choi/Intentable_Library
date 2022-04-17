from datetime import datetime as dt
from typing import List, Union
from pydantic import BaseModel
from inflect import engine

e = engine()


class DateInformation(BaseModel):
    year: int = None
    month: int = None
    day: int = None

    quarter: int = None
    half: int = None
    season: str = None

    is_fiscal_year: bool = False
    def __str__(self):
        return f'Year : {self.year}\n\
Month : {self.month}\n\
Day : {self.day}\n\
Quarter : {self.quarter}\n\
Half : {self.half}\n\
Season : {self.season}\n\
Is Fiscal Year : {self.is_fiscal_year}\n'

    def number_of_entity(self) -> int:
        n = 0
        if self.is_fiscal_year:
            n -= 1

        for key, values in self.__dict__.items():
            if values:
                n += 1
        return n

    def is_bigger(self, other: 'DateInformation') -> bool:
        if self.year and other.year and self.year < other.year:
            return False
        elif self.year and other.year and self.year > other.year:
            return True
        
        if self.month and other.month and self.month < other.month:
            return False
        elif self.month and other.month and self.month > other.month:
            return True

        if self.quarter and other.quarter and self.quarter < other.quarter:
            return False
        elif self.quarter and other.quarter and self.quarter > other.quarter:
            return True

        if self.half and other.half and self.half < other.half:
            return False
        elif self.half and other.half and self.half > other.half:
            return True

        return False


def yy_to_yyyy(yy: str) -> int:
    if len(yy) == 4:
        return int(yy)
    return int(dt.strptime(yy, '%y').strftime('%Y'))


def yyyy_to_yy(yyyy: int) -> str:
    if len(str(yyyy)) == 2:
        return str(yyyy)
    return dt.strptime(yyyy, '%Y').strftime('%y')


ordinal_words = {}
for i in range(1, 32):
    ordinal_words[e.number_to_words(e.ordinal(i))] = i
    ordinal_words[e.ordinal(i)] = i

month_words = {
    'january': 1,
    'jan': 1,
    'february': 2,
    'feb': 2,
    'march': 3,
    'mar': 3,
    'april': 4,
    'apr': 4,
    'may': 5,
    'june': 6,
    'jun': 6,
    'july': 7,
    'jul': 7,
    'august': 8,
    'aug': 8,
    'september': 9,
    'sep': 9,
    'october': 10,
    'oct': 10,
    'november': 11,
    'nov': 11,
    'december': 12,
    'dec': 12
}

ending_quarter_months = {
    1: "ending march",
    2: "ending june",
    3: "ending september",
    4: "ending december"
}

period_symbols = [
    "/",
    "-",
    " to ",
    " through ",
]

def get_month_name_from_number(month_number: int) -> List[str]:
    output = []
    for month_name, month_value in month_words.items():
        if month_value == month_number:
            output.append(month_name)
    return output


def get_ordinal_number_from_number(number: int) -> List[str]:
    return [e.number_to_words(e.ordinal(number)), e.ordinal(number)]


def clean_date(date: str) -> str:

    # Clean date
    clean_date = date.lower() \
        .replace(',', '') \
        .replace('\'', '') \
        .replace('of ', '') \
        .replace('year ', '') \
        .replace("in", "") \
        .replace('/', ' ') \
        .replace('-', ' ') \

    return clean_date


def extract_date(date: str) -> List[DateInformation]:
    extracted_date = DateInformation()
    extracted_list: List[DateInformation] = []

    # Check Fiscal Year
    if "fy" in date or "fiscal" in date:
        extracted_date.is_fiscal_year = True
        date = date.replace("fy ", "").replace("fiscal ", "")

    tokens: List[str] = date.split(" ")
    # Extract quarter information
    if "quarter" in tokens:
        year_index = None
        quarter_index = None

        for i, token in enumerate(tokens):
            if token == "quarter":
                pass
            elif ordinal_words.get(token, None):
                quarter_index = i
                extracted_date.quarter = ordinal_words.get(token)
            elif token.isnumeric() and len(token) == 4:
                year_index = i
            elif quarter_index == None:
                quarter_index = i
            elif year_index == None:
                year_index = i

        if tokens[quarter_index].isnumeric():
            extracted_date.quarter = int(tokens[quarter_index])
        else:
            ordinal_words.get(tokens[quarter_index])
        extracted_date.year = yy_to_yyyy(tokens[year_index])

    elif "ending" in tokens:
        if "march" in tokens:
            extracted_date.quarter = 1
            extracted_date.year = int(tokens[-1])
        elif "june" in tokens:
            extracted_date.quarter = 2
            extracted_date.year = int(tokens[-1])
        elif "september" in tokens:
            extracted_date.quarter = 3
            extracted_date.year = int(tokens[-1])
        elif "december" in tokens:
            extracted_date.quarter = 4
            extracted_date.year = int(tokens[-1])

    elif "q" in tokens[0]:
        q_number_index = 1 if tokens[0][0] == 'q' else 0
        extracted_date.quarter = int(tokens[0][q_number_index])
        if len(tokens[1]) == 2:
            extracted_date.year = yy_to_yyyy(tokens[1])
        else:
            extracted_date.year = int(tokens[1])
    
    elif len(tokens) > 1 and "q" in tokens[1]:
        extracted_date.quarter = int(tokens[1][1])
        if len(tokens[0]) == 2:
            extracted_date.year = yy_to_yyyy(tokens[0])

    # Extract half information
    elif "half" in tokens:
        extracted_date.half = ordinal_words.get(tokens[0], None)
        if extracted_date.half == None:
            extracted_date.half = ordinal_words.get(tokens[2], None)
            extracted_date.year = yy_to_yyyy(tokens[0])
        else:
            extracted_date.year = yy_to_yyyy(tokens[2])
    
    elif "h1" == tokens[0] or "h2" == tokens[0]:
        extracted_date.half = int(tokens[0][1])
        if len(tokens[1]) == 2:
            extracted_date.year = yy_to_yyyy(tokens[1])
        else:
            extracted_date.year = int(tokens[1])
    
    elif len(tokens) > 1 and ("h1" == tokens[1] or "h2" == tokens[1]):
        extracted_date.half = int(tokens[1][1])
        if len(tokens[0]) == 2:
            extracted_date.year = yy_to_yyyy(tokens[0])

    elif "s1" == tokens[0] or "s2" == tokens[0]:
        extracted_date.half = int(tokens[0][1])
        if len(tokens[1]) == 2:
            extracted_date.year = yy_to_yyyy(tokens[1])
    
    elif len(tokens) > 1 and ("s1" == tokens[1] or "s2" == tokens[1]):
        extracted_date.half = int(tokens[1][1])
        if len(tokens[0]) == 2:
            extracted_date.year = yy_to_yyyy(tokens[0])

    # Extract season information
    elif "spring" in tokens:
        extracted_date.season = "spring"
        extracted_date.year = yy_to_yyyy(tokens[-1])
    
    elif "summer" in tokens:
        extracted_date.season = "summer"
        extracted_date.year = yy_to_yyyy(tokens[-1])
    
    elif "fall" in tokens:
        extracted_date.season = "fall"
        extracted_date.year = yy_to_yyyy(tokens[-1])
    
    elif "autumn" in tokens:
        extracted_date.season = "autumn"
        extracted_date.year = yy_to_yyyy(tokens[-1])
    
    elif "winter" in tokens:
        extracted_date.season = "winter"
        extracted_date.year = yy_to_yyyy(tokens[-1])


    elif len(tokens) == 1:
        if month_words.get(tokens[0], None):
            extracted_date.month = month_words.get(tokens[0])
        elif tokens[0].isnumeric():
            extracted_date.year = yy_to_yyyy(tokens[0])
    
    elif len(tokens) == 2:
        #Month Word, Year and Month Word, Day
        for month_name, month_value in month_words.items():
            if month_name in tokens:
                month_index = tokens.index(month_name)
                another_index = 1 if month_index == 0 else 0
                extracted_date.month = month_value
                day = extracted_date.copy()
                day.day = int(tokens[another_index])
                year = extracted_date.copy()
                year.year = yy_to_yyyy(tokens[another_index])
                extracted_list.append(year)
                extracted_list.append(day)
                break
                
        #YYYY MM
        if tokens[0].isnumeric() and len(tokens[0]) == 4 and tokens[1].isnumeric() and int(tokens[1]) < 13:
            extracted_date.year = int(tokens[0])
            extracted_date.month = int(tokens[1])

        #YY/MM
        elif tokens[0].isnumeric() and len(tokens[0]) == 2 and tokens[1].isnumeric() and int(tokens[1]) < 13:
            extracted_date.year = yy_to_yyyy(tokens[0])
            extracted_date.month = int(tokens[1])
            
    elif len(tokens) == 3:
        month_index = None
        year_index = None
        day_index = None
        all_index = list(range(len(tokens)))
        for i, token in enumerate(tokens):
            if month_words.get(token, None):
                month_index = i
                extracted_date.month = month_words.get(token)
                all_index.remove(i)
            elif ordinal_words.get(token, None):
                day_index = i
                extracted_date.day = ordinal_words.get(token)
                all_index.remove(i)
            elif token.isnumeric() and len(token) == 4:
                year_index = i
                extracted_date.year = yy_to_yyyy(token)
                all_index.remove(i)

        if len(all_index) == 1:
            extracted_date.month = month_words.get(tokens[month_index])
            if day_index == None:
                extracted_date.day = int(tokens[all_index[0]])
            elif year_index == None:
                extracted_date.year = yy_to_yyyy(tokens[all_index[0]])

        elif len(all_index) == 2:
            type1 = extracted_date.copy()
            type2 = extracted_date.copy()
            type1.year = yy_to_yyyy(tokens[0])
            type1.month = month_words.get(tokens[1])
            type2.year = yy_to_yyyy(tokens[1])
            type2.month = month_words.get(tokens[0])
            extracted_list.append(type1)
            extracted_list.append(type2)

    if len(extracted_list):
        return extracted_list

    else:
        return [extracted_date]



fiscal_strings = ["fy", "fiscal", "fiscal year"]


def date_to_string(date_object: Union[DateInformation, List[DateInformation]]) -> List[str]:
    output : List[str] = []
    if type(date_object) == type([]):
        for date in date_object:
            output += date_object_to_strings(date)
    else:
        output += date_object_to_strings(date_object)
    return output

def date_object_to_strings(date_object: DateInformation) -> List[str]:
    n = date_object.number_of_entity()
    output_list: List[str] = []

    if n == 1:
        

        # Fiscal Year (e.g. "fy 2018", "fiscal year 2018", "fiscal 2018")
        if date_object.is_fiscal_year and date_object.year:
            output_list.append(f"fy {date_object.year}")
            output_list.append(f"fiscal year {date_object.year}")
            output_list.append(f"fiscal {date_object.year}")
            output_list.append(f"fy {yyyy_to_yy(str(date_object.year))}")
            output_list.append(f"fiscal year {yyyy_to_yy(str(date_object.year))}")
            output_list.append(f"fiscal {yyyy_to_yy(str(date_object.year))}")

        # Plain Year (e.g. "2018")
        elif date_object.year:
            output_list.append(str(date_object.year))
            # output_list.append(yyyy_to_yy(str(date_object.year)))
        # Month (e.g. "January")
        elif date_object.month:
            for month_name in get_month_name_from_number(date_object.month):
                output_list.append(month_name)
    
    elif n == 2:
        # Month, Day (e.g. january 1st, january 1, jan first ...)
        if date_object.month and date_object.day:
            month_strings = get_month_name_from_number(date_object.month)
            day_strings = get_ordinal_number_from_number(date_object.day)
            day_strings.append(str(date_object.day))
            day_strings.append("{:02}".format(date_object.day))

            for month_string in month_strings:
                for day_string in day_strings:
                    output_list.append(month_string + " " + day_string)

        # Month, Year (e.g. january 2018, january 2018, jan 2018, 2020/01, 2020-01, dec '17)
        elif date_object.month and date_object.year:
            month_strings = get_month_name_from_number(date_object.month)
            month_number = ["{:02}".format(date_object.month), str(date_object.month)]
            for month_string in month_strings:
                output_list.append(month_string + " " + str(date_object.year))
                output_list.append(month_string + " \'" + yyyy_to_yy(str(date_object.year)))
                output_list.append(month_string + " " + yyyy_to_yy(str(date_object.year)))

            for month_number in month_number:
                output_list.append(str(date_object.year) + "-" + month_number)
                output_list.append(str(date_object.year) + "/" + month_number)

        # Quarter, Year (e.g. q1 2020, 2020 q1, q1 '20, q1 20, first quarter 2020, first quarter of 2020...)
        elif date_object.quarter and date_object.year:
            quarter_strings = get_ordinal_number_from_number(date_object.quarter)
            for quarter_string in quarter_strings:
                # first quarter 2020, 1st quarter 2020
                output_list.append(quarter_string + " quarter " + str(date_object.year))
                # first quarter year 2020, 1st quarter year 2020
                output_list.append(quarter_string + " quarter year " + str(date_object.year))
                # first quarter of 2020, 1st quarter of 2020
                output_list.append(quarter_string + " quarter of " + str(date_object.year))
                # first quarter of year 2020, 1st quarter of year 2020
                output_list.append(quarter_string + " quarter of year " + str(date_object.year))

            # q1 2020
            output_list.append("q" + str(date_object.quarter) + " " + str(date_object.year))
            # q1 of 2020
            output_list.append("q" + str(date_object.quarter) + " of " + str(date_object.year))
            # q1 '20
            output_list.append("q" + str(date_object.quarter) + " \'" + yyyy_to_yy(str(date_object.year)))
            # q1 20
            output_list.append("q" + str(date_object.quarter) + " " + yyyy_to_yy(str(date_object.year)))
            # 2020 q1
            output_list.append(str(date_object.year) + " " + "q" + str(date_object.quarter))
            # 20 q1
            output_list.append(yyyy_to_yy(str(date_object.year)) + " " + "q" + str(date_object.quarter))
            # 2020 quarter 1
            output_list.append(str(date_object.year) + " quarter " + str(date_object.quarter))
            # ending march 2020
            output_list.append(ending_quarter_months.get(date_object.quarter) + " " + str(date_object.year))

        # Half, Year (e.g. half year 2020, half year of 2020, first half 2020, first half of 2020...)
        elif date_object.half and date_object.year:
            half_strings = get_ordinal_number_from_number(date_object.half)
            for half_string in half_strings:
                # first half 2020, 1st half 2020
                output_list.append(half_string + " half " + str(date_object.year))
                # first half year 2020, 1st half year 2020
                output_list.append(half_string + " half year " + str(date_object.year))
                # first half of 2020, 1st half of 2020
                output_list.append(half_string + " half of " + str(date_object.year))
                # first half of year 2020, 1st half of year 2020
                output_list.append(half_string + " half of year " + str(date_object.year))

            # half year 2020
            output_list.append("half year " + str(date_object.year))
            # half year of 2020
            output_list.append("half year of " + str(date_object.year))
            # half year '20
            output_list.append("half year \'" + yyyy_to_yy(str(date_object.year)))
            # half year 20
            output_list.append("half year " + yyyy_to_yy(str(date_object.year)))
            # 2020 half year
            output_list.append(str(date_object.year) + " half year")
            # 20 half year
            output_list.append(yyyy_to_yy(str(date_object.year)) + " half year")
            # ending march 2020
            output_list.append(ending_quarter_months.get(date_object.half * 2) + " " + str(date_object.year))

        # Season, Year (e.g. spring 2020, spring of 2020, first spring 2020, first spring of 2020...)
        elif date_object.season and date_object.year:
            output_list.append(date_object.season + " " + str(date_object.year))
            output_list.append(date_object.season + " of " + str(date_object.year))

        # Month, Fiscal, Year (e.g. january fiscal 2018, january fy 2018, jan fiscal year 2018)
        elif date_object.month and date_object.is_fiscal_year and date_object.is_fiscal_year:
            month_strings = get_month_name_from_number(date_object.month)
            for month_string in month_strings:
                output_list.append(month_string + " fiscal year " + str(date_object.year))
                output_list.append(month_string + " fy " + str(date_object.year))
                output_list.append(month_string + " fiscal " + str(date_object.year))
        
        # Quarter, Fiscal, Year (e.g. q1 fiscal 2020, q1 fy 2020, q1 fiscal year 2020, q1 fy 2020)
        elif date_object.quarter and date_object.is_fiscal_year and date_object.is_fiscal_year:
            quarter_strings = get_ordinal_number_from_number(date_object.quarter)
            for quarter_string in quarter_strings:
                output_list.append(quarter_string + " quarter fiscal year " + str(date_object.year))
                output_list.append(quarter_string + " quarter fy " + str(date_object.year))
                output_list.append(quarter_string + " quarter fiscal " + str(date_object.year))
            
            output_list.append("q" + str(date_object.quarter) + " fiscal year " + str(date_object.year))
            output_list.append("q" + str(date_object.quarter) + " fy " + str(date_object.year))
            output_list.append("q" + str(date_object.quarter) + " fiscal " + str(date_object.year))
        
        # Half, Fiscal, Year (e.g. half fiscal year 2020, half fy 2020, first half fiscal year 2020, first half fy 2020)
        elif date_object.half and date_object.is_fiscal_year and date_object.is_fiscal_year:
            half_strings = get_ordinal_number_from_number(date_object.half)
            for half_string in half_strings:
                output_list.append(half_string + " half fiscal year " + str(date_object.year))
                output_list.append(half_string + " half fy " + str(date_object.year))
    
    
    elif n == 3:
        # Day, Month, Year (e.g jan 20 2021, january 20 2021, jan 20 2021, jan 20 '21, jan 20 21, january 20 '21, january 20 21)
        if date_object.day and date_object.month and date_object.year:
            date = dt(date_object.year, date_object.month, date_object.day)
            dates = [
                date.strftime("%b %d %Y"),
                date.strftime("%b %d, %Y"),
                date.strftime("%b %d '%y"),
                date.strftime("%B %d %Y"),
                date.strftime("%B %d '%y"),
                date.strftime("%b %d \'%y"),
                date.strftime("%B %d \'%y"),
                date.strftime("%Y-%m-%d"),
                date.strftime("%Y/%m/%d"),  
                date.strftime("%y-%m-%d"),
                date.strftime("%y/%m/%d"),
                date.strftime("%d %b %Y"),
                date.strftime("%d %B %Y"),
                date.strftime("%d %b \'%y"),
                date.strftime("%d %B \'%y"),
                date.strftime("%B %d, %Y"),
                date.strftime("%B %d, \'%y"),
            ]
            output_list += dates
        
            

    return output_list





def date_formatter(date : str) -> List[str]:
    """
    Takes a date string and returns a list of possible date formats
    """
    output: List[str] = [date]
    date = str(date)

    for period_symbol in period_symbols:
        if period_symbol in date:
            for period_symbol_replace in period_symbols:
                output.append(date.replace(period_symbol, period_symbol_replace))
    
    cleaned_date : str = clean_date(date)
    extraced_dates: Union[DateInformation, List[DateInformation]] = extract_date(cleaned_date)
    for extraced_date in extraced_dates:
        output += date_to_string(extraced_date)
    return output

if __name__ == "__main__":
    test_set = [
        # "2018",
        # "january",
        # "jan",
        # "August 1",
        # "Aug 1",
        # "2020/01",
        # "2020-01",
        # "June 2021",
        # "Jan 10",
        # "january 10",
        # "dec '17",
        # "jan 26, 2021",
        # "31 December 2017",
        # "31/12/2017",
        # "6th march 2021",
        # "april 1, 1967",
        # "1st quarter 2011",
        # "second quarter 2020",
        # "2020 quarter 2",
        # "first quarter of fiscal year 2020"
        # "2020"
        # "q2 2021"
        "dec 20"
    ]

    for test in test_set:
        print(date_formatter(test))
