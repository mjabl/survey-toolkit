# pylint:disable=missing-docstring,redefined-outer-name
import pytest
from survey_toolkit.core import SingleChoiceQuestion


@pytest.fixture
def question():
    return SingleChoiceQuestion('favouritePhone', 'What is your favourite phone brand?',
                                ['Samsung', 'iPhone', 'Nokia', 'iPhone', None, 'Huawei', 'Xiaomi'])


def test_add_answer_when_no_choices_given(question):
    question.add_answer('Windows Phone')
    assert question.answers[-1] == 'Windows Phone'


def test_add_answwer_when_choices_given_as_list(question):
    question.choices = ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
    question.add_answer('Huawei')
    question.add_answer(None)
    assert question.answers[-2] == 'Huawei'
    assert question.answers[-1] is None


def test_add_answer_not_in_choices(question):
    with pytest.raises(ValueError):
        question.choices = ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
        question.add_answer('Windows Phone')


def test_add_answer_with_conversion_to_label(question):
    question.choices = {1:'Huawei', 2:'iPhone', 3:'Nokia', 4:'Samsung', 5:'Xiaomi'}
    question.add_answer(1, convert_to_labels=True)
    assert question.answers[-1] == 'Huawei'


def test_to_series_when_choices_given_as_list(question):
    question.choices = ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']
    series = question.to_series()
    assert list(series.codes) == [3, 1, 2, 1, -1, 0, 4]
    assert list(series.categories) == ['Huawei', 'iPhone', 'Nokia', 'Samsung', 'Xiaomi']


def test_to_series_when_no_choices_given(question):
    series = question.to_series()
    assert list(series.codes) == [2, 4, 1, 4, -1, 0, 3]
    assert list(series.categories) == ['Huawei', 'Nokia', 'Samsung', 'Xiaomi', 'iPhone']
