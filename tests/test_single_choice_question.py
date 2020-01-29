#pylint:skip-file

from survey_toolkit.core import SingleChoiceQuestion


def test_to_series_when_no_choices_given():
    question = SingleChoiceQuestion(
        'favouritePhone', 'What is your favourite phone brand?',
        ['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi']
    )
    series = question.to_series()
    assert list(series.codes) == [2, 4, 1, 4, -1, 0, 3]
    assert list(series.categories) == ['Huawei', 'Nokia', 'Samsung', 'Xiaomi', 'iPhone']


def test_to_series_when_choices_given_as_list():
    question = SingleChoiceQuestion(
        'favouritePhone', 'What is your favourite phone brand?',
        ['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi'],
        ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
    )
    series = question.to_series()
    assert list(series.codes) == [3, 1, 2, 1, -1, 0, 4]
    assert list(series.categories) == ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
