# pylint:disable=missing-docstring,redefined-outer-name
import pytest
import pandas as pd
from survey_toolkit.core import MultipleChoiceQuestion


@pytest.fixture
def question():
    return MultipleChoiceQuestion('favouritePhone', 'What are your favourite phone brands?',
                                  [['Samsung', 'iPhone'], [None], ['Nokia'], ['Huawei', 'Xiaomi']])


def test_add_answer_when_no_choices_given(question):
    question.add_answer(['Windows Phone', 'Nokia'])
    question.add_answer([None])
    assert question.answers[-2] == ['Windows Phone', 'Nokia']
    assert question.answers[-1] == [None]


def test_add_noniterable_answer(question):
    question.add_answer('Windows Phone')
    question.add_answer(None)
    assert question.answers[-2] == ['Windows Phone']
    assert question.answers[-1] == [None]


def test_add_answer_when_choices_given_as_list(question):
    question.choices = ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
    question.add_answer(['Huawei', 'iPhone'])
    question.add_answer(None)
    assert question.answers[-2] == ['Huawei', 'iPhone']
    assert question.answers[-1] == [None]


def test_add_answer_not_in_choices(question):
    with pytest.raises(ValueError):
        question.choices = ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
        question.add_answer('Windows Phone')


def test_add_answer_with_conversion_to_label(question):
    question.choices = {1:'Huawei', 2:'iPhone', 3:'Nokia', 4:'Samsung', 5:'Xiaomi'}
    question.add_answer([1, 2], convert_to_label=True)
    question.add_answer(None, convert_to_label=True)
    assert question.answers[-2] == ['Huawei', 'iPhone']
    assert question.answers[-1] == [None]


def test_to_series(question):
    expected = pd.Series([['Samsung', 'iPhone'], [None], ['Nokia'], ['Huawei', 'Xiaomi']])
    assert all(question.to_series() == expected)


def test_to_dummies(question):
    question.choices = ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
    expected = pd.DataFrame({
        'What are your favourite phone brands?: Huawei': [0, 0, 0, 1],
        'What are your favourite phone brands?: iPhone': [1, 0, 0, 0],
        'What are your favourite phone brands?: Nokia': [0, 0, 1, 0],
        'What are your favourite phone brands?: Samsung': [1, 0, 0, 0],
        'What are your favourite phone brands?: Xiaomi': [0, 0, 0, 1],
    })
    assert all(question.to_dummies() == expected)
