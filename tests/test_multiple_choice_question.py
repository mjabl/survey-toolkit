# pylint:disable=missing-docstring,redefined-outer-name
import pytest
import pandas as pd
from survey_toolkit.core import MultipleChoiceQuestion


@pytest.fixture
def question():
    return MultipleChoiceQuestion('favouritePhones', 'What are your favourite phone brands?')


def test_add_answer_when_no_choices_given(question):
    question.add_answer(['Windows Phone', 'Nokia'])
    question.add_answer(None)
    assert question.answers[-2] == ['Windows Phone', 'Nokia']
    assert question.answers[-1] is None


def test_add_noniterable_answer(question):
    question.add_answer('Windows Phone')
    question.add_answer(None)
    assert question.answers[-2] == ['Windows Phone']
    assert question.answers[-1] is None


def test_add_answer_when_choices_given_as_list(question):
    question.choices = ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
    question.add_answer(['Huawei', 'iPhone'])
    question.add_answer(None)
    assert question.answers[-2] == ['Huawei', 'iPhone']
    assert question.answers[-1] is None


def test_add_answer_not_in_choices(question):
    with pytest.raises(ValueError):
        question.choices = ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
        question.add_answer('Windows Phone')


def test_add_answer_when_choices_given_as_dict(question):
    question.choices = {1: 'iPhone', 2: 'Samsung', 3: 'Huawei', 4: 'Xiaomi', 5: 'Nokia'}
    question.add_answer([1, 2])
    question.add_answer(None)
    assert question.answers[-2] == [1, 2]
    assert question.answers[-1] is None


def test_to_series(question):
    answers = [['Samsung', 'iPhone'], [None], ['Nokia'], ['Huawei', 'Xiaomi']]
    question.answers = answers
    question.choices = ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
    series = question.to_series()
    expected = pd.Series(answers, name='favouritePhones')
    assert all(series == expected)
    assert series.name == expected.name


def test_to_label_series(question):
    question.answers = [[2, 1], [None], [5], [3, 4]]
    question.choices = {1: 'iPhone', 2: 'Samsung', 3: 'Huawei', 4: 'Xiaomi', 5: 'Nokia'}
    series = question.to_label_series()
    expected = pd.Series([['Samsung', 'iPhone'], [None], ['Nokia'], ['Huawei', 'Xiaomi']],
                         name='What are your favourite phone brands?')
    assert all(series == expected)
    assert series.name == expected.name


# def test_to_dummies(question):
#     question.choices = ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
#     expected = pd.DataFrame({
#         'What are your favourite phone brands?: Huawei': [0, 0, 0, 1],
#         'What are your favourite phone brands?: iPhone': [1, 0, 0, 0],
#         'What are your favourite phone brands?: Nokia': [0, 0, 1, 0],
#         'What are your favourite phone brands?: Samsung': [1, 0, 0, 0],
#         'What are your favourite phone brands?: Xiaomi': [0, 0, 0, 1],
#     })
#     assert all(question.to_dummies() == expected)
#
#
# some_ans = [['Samsung', 'iPhone'], [None], ['Nokia'], ['Huawei', 'Xiaomi']]