# pylint:disable=missing-docstring,redefined-outer-name
import pytest
import pandas as pd
from survey_toolkit.core import SingleChoiceQuestion


@pytest.fixture
def question():
    return SingleChoiceQuestion('favouritePhone', 'What is your favourite phone brand?')


def test_add_answer_when_no_choices_given(question):
    question.add_answer('Windows Phone')
    assert question.answers[-1] == 'Windows Phone'


def test_add_answer_when_choices_given_as_list(question):
    question.choices = ['iPhone', 'Samsung', 'Huawei', 'Xiaomi', 'Nokia']
    question.add_answer('Huawei')
    question.add_answer(None)
    assert question.answers[-2] == 'Huawei'
    assert question.answers[-1] is None


def test_add_answer_not_in_choices(question):
    with pytest.raises(ValueError):
        question.choices = ['iPhone', 'Samsung', 'Huawei', 'Xiaomi', 'Nokia']
        question.add_answer('Windows Phone')


def test_add_answer_when_choices_given_as_dict(question):
    question.choices = {1: 'iPhone', 2: 'Samsung', 3: 'Huawei', 4: 'Xiaomi', 5: 'Nokia'}
    question.add_answer(1)
    assert question.answers[-1] == 1


def test_to_series(question):
    question.answers = ['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi']
    question.choices = ['iPhone', 'Samsung', 'Huawei', 'Xiaomi', 'Nokia']
    series = question.to_series()
    expected = pd.Series(['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi'],
                         name='favouritePhone')
    assert all(series.dropna() == expected.dropna())
    assert series.name == expected.name
    assert list(series.categories) == list(question.choices)


def test_to_label_series(question):
    question.answers = ['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi']
    choices = ['iPhone', 'Samsung', 'Huawei', 'Xiaomi', 'Nokia']
    question.choices = choices
    series = question.to_label_series()
    expected = pd.Categorical(['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi'],
                              categories=choices, ordered=True)
    expected.name = 'What is your favourite phone brand?'
    assert all(series.dropna() == expected.dropna())
    assert series.name == expected.name
    assert list(series.categories) == list(question.choices)


# def test_to_label_series_when_choices_given_as_dict(question):
#     question.answers = ['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi']
#     series = question.to_label_series()
#     expected = pd.Series(['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi'],
#                          name='What is your favourite phone brand?')
#     assert all(series.dropna() == expected.dropna())
#     assert series.name == expected.name
