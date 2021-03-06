from dataclasses import dataclass
from typing import Tuple
from util.dto import *


class overviewDict:
    first: Tuple[str] = ('This', 'The')
    second: Tuple[str] = ('bar', 'pie', 'line', 'chart', 'statistic', 'graph', 'survey', 'timeline', 'figure')
    third: Tuple[str] = ('shows', 'gives', 'depicts', 'displays', 'illustrates', 'represents', 'presents', 'reveals', 'follow', 'refer')


class diffDict:
    greater: Tuple[str] = (
        'increased', 'increase', 'increasing', 'increases',
        'up from', 'risen up', 'grew',  'gone up', 'growth',
        'growing', 'rose', 'rising', 'gained', 'gaining',
        'bigger', 'higher', 'rise from', "grow", 'increment'
    )

    less: Tuple[str] = (
        'decreased', 'decrease', 'decreasing', 'decreases',
        'down from', 'shrank', 'down', 'shrunk', 'gone down',
        'shrinking', 'fell', 'falling', 'lost', 'loss',
        'shrunken', 'shrinking', 'lower', 'lowering',
        'smaller', 'lower',
        'drop', 'dropped', 'dropping',
        'decline', 'declining', 'declined', 'declines',
        'diminished', 'diminishing', 'diminished',
        'reduce', 'fallen', 'decrement'
    )

    variety: Tuple[str] = (
        'varied', 'varying', 'fluctuated', 'fluctuation', 'fluctuations',
        'fluctuates', 'fluctuating', 'oscillated', 'oscillation',
    )


class appendDict:
    first: Tuple[str] = (
        "This was",
        "This is",
        "That is",
        "That was",
        "These were",
        "These are",
        "Those are",
        "Those were",      
        'This represent' 
    )


class trendDict:
    keyword: Tuple[str] = ()

    sinceKeyword: Tuple[str] = (
        'since', 'after', 'following years', 'coming years'
    )

    forKeyword: Tuple[str] = (
        'during', 'between',  
        'over the period', 'in that period', 'over the time period', 'over the observed period', 'in this time period',
        'in the period', 'in the time period',
        'over the last decades', 'observed period', 'observed time period', 'observed decades',
        'over this period'
    )

    beforeKeyword: Tuple[str] = (
        'prior', 'in recent years', 'preceding years',
        'past decades', 'past decade', 'past years',
        'till', 'until',

    )


class compareDict:
    keyword: Tuple[str] = (
        'compare', 'compared', 'comparing', 'comparison', 'comparisons',
    )
    prev_year: Tuple[str] = (
        'previous year', 'year earlier', 'quarter of the previous year', "prior year",
        'the year prior', 'previous quarter', 'the quarter prior', 'the quarter before',
    )
    next_year: Tuple[str] = (
        'following year', 'year later', 'quarter of the following year',
        'following quarter', 'the year following', 'next quarter', 'the quarter after',
    )


def is_overview(sentence: str):
    if sentence.startswith("How") and sentence.endswith("?"):
        return "overview"
    if not any(word in sentence for word in overviewDict.first):
        return False
    if not any(word in sentence.lower() for word in overviewDict.second):
        return False
    if not any(word in sentence.lower() for word in overviewDict.third):
        return False
    return "overview"


def has_keyword(dict : Union[trendDict, compareDict], sentence: str):
    if any(word in sentence.lower() for word in dict.keyword):
        return True
    else:
        return False


def has_next_year(sentence: str):
    if any(word in sentence.lower() for word in compareDict.next_year):
        return True
    else:
        return False


def has_prev_year(sentence: str):
    if any(word in sentence.lower() for word in compareDict.prev_year):
        return True
    else:
        return False


def is_append(sentence: str):
    if sentence.startswith(appendDict.first) and not is_overview(sentence):
        return True
    else:
        return False


def is_diff(sentence: str) -> str:
    if is_greater(sentence):
        return "greater"
    elif is_less(sentence):
        return "less"
    elif is_variety(sentence):
        return "fluctuate"
    else:
        return False


def is_greater(sentence: str):
    if any(word in sentence.lower() for word in diffDict.greater):
        return True
    else:
        return False


def is_less(sentence: str):
    if any(word in sentence.lower() for word in diffDict.less):
        return True
    else:
        return False


def is_variety(sentence: str):
    if any(word in sentence.lower() for word in diffDict.variety):
        return True
    else:
        return False


def has_period(sentence: str):
    if any(word in sentence.lower() for word in trendDict.sinceKeyword):
        return 'since'
    elif any(word in sentence.lower() for word in trendDict.forKeyword):
        return 'during'
    elif any(word in sentence.lower() for word in trendDict.beforeKeyword):
        return 'until'
    else:
        return False