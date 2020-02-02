# pylint:disable=missing-docstring,redefined-outer-name
import pytest
import pandas as pd
from survey_toolkit.core import SingleChoiceQuestion


@pytest.fixture
def question():
    return SingleChoiceQuestion('favouritePhone', 'What is your favourite phone brand?',
                                ['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi'])


def test_add_answer_when_no_choices_given(question):
    question.add_answer('Windows Phone')
    assert question.answers[-1] == 'Windows Phone'


def test_add_answer_when_choices_given_as_list(question):
    question.choices = ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
    question.add_answer('Huawei')
    question.add_answer(None)
    assert question.answers[-2] == 'Huawei'
    assert question.answers[-1] is None


def test_add_answer_not_in_choices(question):
    with pytest.raises(ValueError):
        question.choices = ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
        question.add_answer('Windows Phone')


def test_add_answer_when_choices_given_as_dict(question):
    question.choices = {1: 'Huawei', 2: 'iPhone', 3: 'Nokia', 4: 'Samsung', 5: 'Xiaomi'}
    question.add_answer(1)
    assert question.answers[-1] == 1


def test_to_series(question):
    series = question.to_series()
    expected = pd.Series(['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi'],
                         name='favouritePhone')
    assert all(series.dropna() == expected.dropna())
    assert series.name == expected.name

def test_to_label_series(question):
    series = question.to_label_series()
    expected = pd.Series(['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi'],
                         name='What is your favourite phone brand?')
    assert all(series.dropna() == expected.dropna())
    assert series.name == expected.name

