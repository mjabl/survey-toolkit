# pylint:disable=missing-docstring,redefined-outer-name
import pytest
import pandas as pd
from pandas.testing import assert_series_equal, assert_frame_equal
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
    answers = [['Samsung', 'iPhone'], None, ['Nokia'], ['Huawei', 'Xiaomi']]
    question.choices = ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
    question.answers = answers
    series = question.to_series()
    expected = pd.Series(answers, name='favouritePhones')
    assert_series_equal(series, expected)


def test_to_label_series(question):
    question.choices = {1: 'iPhone', 2: 'Samsung', 3: 'Huawei', 4: 'Xiaomi', 5: 'Nokia'}
    question.answers = [[2, 1], None, [5], [3, 4]]
    series = question.to_series(to_labels=True)
    expected = pd.Series([['Samsung', 'iPhone'], None, ['Nokia'], ['Huawei', 'Xiaomi']],
                         name='What are your favourite phone brands?')
    assert_series_equal(series, expected)


def test_to_dummies(question):
    question.choices = ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
    question.answers = [['Samsung', 'iPhone'], None, ['Nokia'], ['Huawei', 'Xiaomi']]
    dummies = question.to_dummies()
    expected = pd.DataFrame({
        'favouritePhones_Huawei': [0, None, 0, 1],
        'favouritePhones_iPhone': [1, None, 0, 0],
        'favouritePhones_Nokia': [0, None, 1, 0],
        'favouritePhones_Samsung': [1, None, 0, 0],
        'favouritePhones_Xiaomi': [0, None, 0, 1],
    })
    assert_frame_equal(dummies, expected)


def test_to_dummies_with_unused_choices(question):
    question.choices = ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
    question.answers = [['Samsung', 'iPhone'], None, None, ['Huawei', 'Xiaomi']]
    dummies = question.to_dummies()
    expected = pd.DataFrame({
        'favouritePhones_Huawei': [0, None, None, 1],
        'favouritePhones_iPhone': [1, None, None, 0],
        'favouritePhones_Nokia': [0, None, None, 0],
        'favouritePhones_Samsung': [1, None, None, 0],
        'favouritePhones_Xiaomi': [0, None, None, 1],
    })
    assert_frame_equal(dummies, expected)


def test_to_dummies_with_empty_data(question):
    question.choices = ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
    question.answers = [None, None]
    dummies = question.to_dummies()
    expected = pd.DataFrame({
        'favouritePhones_Huawei': [None, None],
        'favouritePhones_iPhone': [None, None],
        'favouritePhones_Nokia': [None, None],
        'favouritePhones_Samsung': [None, None],
        'favouritePhones_Xiaomi': [None, None],
    })
    assert_frame_equal(dummies, expected)


def test_to_dummies_with_conversion_to_labels(question):
    question.choices = {1: 'Huawei', 2: 'iPhone', 3: 'Nokia', 4: 'Samsung', 5: 'Xiaomi'}
    question.answers = [[4, 2], None, [3], [1, 5]]
    dummies = question.to_dummies(to_labels=True)
    expected = pd.DataFrame({
        'What are your favourite phone brands?: Huawei': [0, None, 0, 1],
        'What are your favourite phone brands?: iPhone': [1, None, 0, 0],
        'What are your favourite phone brands?: Nokia': [0, None, 1, 0],
        'What are your favourite phone brands?: Samsung': [1, None, 0, 0],
        'What are your favourite phone brands?: Xiaomi': [0, None, 0, 1],
    })
    assert_frame_equal(dummies, expected)


def test_to_dummies_when_no_choices_given(question):
    question.answers = [['Samsung', 'iPhone'], None, ['Nokia'], ['Huawei', 'Xiaomi']]
    dummies = question.to_dummies()
    expected = pd.DataFrame({
        'favouritePhones_Huawei': [0, None, 0, 1],
        'favouritePhones_Nokia': [0, None, 1, 0],
        'favouritePhones_Samsung': [1, None, 0, 0],
        'favouritePhones_Xiaomi': [0, None, 0, 1],
        'favouritePhones_iPhone': [1, None, 0, 0],
    })
    assert_frame_equal(dummies, expected)


def test_get_dummy_variables(question):
    question.choices = ['Huawei', 'iPhone']
    assert question.get_dummy_variables() == {
        'favouritePhones_Huawei': 'What are your favourite phone brands?: Huawei',
        'favouritePhones_iPhone': 'What are your favourite phone brands?: iPhone'
    }


def test_get_dummy_variables_when_no_choices_given(question):
    question.answers = [['Samsung', 'iPhone'], None]
    assert question.get_dummy_variables() == {
        'favouritePhones_iPhone': 'What are your favourite phone brands?: iPhone',
        'favouritePhones_Samsung': 'What are your favourite phone brands?: Samsung'
    }


def test_optimize(question):
    question.choices = ['iPhone', 'Samsung', 'Huawei', 'Xiaomi', 'Nokia']
    question.answers = [['Samsung', 'iPhone'], None, ['Nokia'], ['Huawei', 'Xiaomi']]
    question.optimize()
    assert question.choices == {1: 'iPhone', 2: 'Samsung', 3: 'Huawei', 4: 'Xiaomi', 5: 'Nokia'}
    assert question.answers == [[2, 1],  None, [5], [3, 4]]
