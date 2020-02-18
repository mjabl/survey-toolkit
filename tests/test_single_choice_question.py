# pylint:disable=missing-docstring,redefined-outer-name
import pytest
import pandas as pd
from pandas.testing import assert_series_equal, assert_frame_equal
from survey_toolkit.core import SingleChoiceQuestion


@pytest.fixture
def question():
    return SingleChoiceQuestion('favouritePhone', 'What is your favourite phone brand?')


def test_constructor_when_no_choices_given():
    question = SingleChoiceQuestion('id', answers=['a', 'b', None, 'c'])
    assert question.name == 'id'
    assert question.answers == ['a', 'b', None, 'c']


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
    answers = ['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi']
    choices = ['iPhone', 'Samsung', 'Huawei', 'Xiaomi', 'Nokia']
    question.choices = choices
    question.answers = answers
    series = question.to_series()
    expected = pd.Series(pd.Categorical(answers, categories=choices, ordered=True),
                         name='favouritePhone')
    assert_series_equal(series, expected)


def test_to_label_series(question):
    answers = ['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi']
    choices = ['iPhone', 'Samsung', 'Huawei', 'Xiaomi', 'Nokia']
    question.choices = choices
    question.answers = answers
    series = question.to_series(to_labels=True)
    expected = pd.Series(pd.Categorical(answers, categories=choices, ordered=True),
                         name='What is your favourite phone brand?')
    assert_series_equal(series, expected)


def test_to_label_series_when_choices_given_as_dict(question):
    choices = {1: 'iPhone', 2: 'Samsung', 3: 'Huawei', 4: 'Xiaomi', 5: 'Nokia'}
    question.choices = choices
    question.answers = [2, 1, 5, 1, None, 3, 4]
    series = question.to_series(to_labels=True)
    expected = pd.Series(
        pd.Categorical(['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi'],
                       categories=list(choices.values()), ordered=True),
        name='What is your favourite phone brand?'
    )
    assert_series_equal(series, expected)

def test_optimize_when_choices_given_as_list(question):
    question.choices = ['iPhone', 'Samsung', 'Huawei', 'Xiaomi', 'Nokia']
    question.answers = ['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi']
    question.optimize()
    assert question.choices == {1: 'iPhone', 2: 'Samsung', 3: 'Huawei', 4: 'Xiaomi', 5: 'Nokia'}
    assert question.answers == [2, 1, 5, 1, None, 3, 4]


def test_optimize_when_no_choices_given(question):
    question.answers = ['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi']
    question.optimize()
    assert question.choices == {1: 'Huawei', 2: 'Nokia', 3: 'Samsung', 4: 'Xiaomi', 5: 'iPhone'}
    assert question.answers == [3, 5, 2, 5, None, 1, 4]


def test_to_frame_with_optimization(question):
    question.answers = ['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi']
    frame = question.to_frame(optimize=True)
    expected = pd.DataFrame(pd.Series(
        pd.Categorical([3, 5, 2, 5, None, 1, 4], [1, 2, 3, 4, 5], ordered=True),
        name='favouritePhone'
    ))
    assert question.answers == ['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi']
    assert_frame_equal(frame, expected)


def test_get_metadata_with_optimization(question):
    question.choices = ['Huawei', 'Nokia', 'Samsung', 'Xiaomi', 'iPhone']
    metadata = question.get_metadata(optimize=True)
    expected = {
        'name': 'favouritePhone', 'label': 'What is your favourite phone brand?',
        'choices': {1: 'Huawei', 2: 'Nokia', 3: 'Samsung', 4: 'Xiaomi', 5: 'iPhone'}
    }
    assert metadata == expected

def test_get_metadata_with_optimization_when_no_choices_given(question):
    question.answers = ['Samsung', 'Huawei', 'Nokia','Xiaomi', 'iPhone']
    metadata = question.get_metadata(optimize=True)
    expected = {
        'name': 'favouritePhone', 'label': 'What is your favourite phone brand?',
        'choices': {1: 'Huawei', 2: 'Nokia', 3: 'Samsung', 4: 'Xiaomi', 5: 'iPhone'}
    }
    assert metadata == expected
