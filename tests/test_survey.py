# pylint:disable=missing-docstring,redefined-outer-name
import pytest
from survey_toolkit.core import (Survey, NumericInputQuestion, TextInputQuestion,
                                 SingleChoiceQuestion, MultipleChoiceQuestion)


@pytest.fixture()
def basic_surveyjs_json():
    return {"pages": [{"name": "page1", "elements": []}]}


def _get_surveyjs_json(basic_surveyjs_json: dict, question: dict):
    basic_surveyjs_json["pages"][0]["elements"].append(question)
    return basic_surveyjs_json


def test_from_surveyjs_parses_numeric_question(basic_surveyjs_json):
    survey_json = _get_surveyjs_json(
        basic_surveyjs_json,
        {"type": "text", "name": "age", "title": "How old are you?", "inputType": "number"}
    )
    survey_result = ['{"age": 20}', '{"age": 30}', '{"age": 35.5}', '{}']
    survey = Survey.from_surveyjs(survey_json, survey_result)
    question = survey.questions[0]
    assert type(question) == NumericInputQuestion
    assert question.name == 'age'
    assert question.label == "How old are you?"
    assert question.answers == [20, 30, 35.5, None]


def test_from_surveyjs_parses_text_question(basic_surveyjs_json):
    survey_json = _get_surveyjs_json(
        basic_surveyjs_json,
        {"type": "text", "name": "surveyjsOpinion",
         "title": "How do you like the surveyjs service?"}
    )
    survey_results = [
        '{"surveyjsOpinion": "it\'s fantastic!"}',
        '{"surveyjsOpinion": "sux!"}',
        '{"surveyjsOpinion": ""}',
        '{}',
    ]
    survey = Survey.from_surveyjs(survey_json, survey_results)
    question = survey.questions[0]
    assert type(question) == TextInputQuestion
    assert question.answers == ["it's fantastic!", "sux!", "", None]


def test_from_surveyjs_parses_text_question_with_numeric_validator(basic_surveyjs_json):
    question_json  = {"type": "text", "name": "age", "title": "How old are you?",
                      "validators": [{"type": "numeric", "minValue": 5, "maxValue": 105 }]}
    survey_json = _get_surveyjs_json(basic_surveyjs_json, question_json)
    survey_results = ['{"age": "20"}', '{"age": "30"}', '{"age": "35.5"}', '{"age": "35,5"}', '{}']
    survey = Survey.from_surveyjs(survey_json, survey_results)
    question = survey.questions[0]
    assert type(question) == NumericInputQuestion
    assert question.answers == [20, 30, 35.5, 35.5, None]


def test_from_surveyjs_parses_radiogroup_question_when_choices_given_as_kv(basic_surveyjs_json):
    question_json = {
        "type": "radiogroup", "name": "gender", "title": "What's your gender?", "hasOther": True,
        "choices": [
            {"value": "male", "text": "Male"},
            {"value": "female", "text": "Female"},
        ]
    }
    survey_json = _get_surveyjs_json(basic_surveyjs_json, question_json)
    survey_results = ['{"gender": "male"}', '{"gender": "female"}', '{"gender": "other"}', '{}']
    survey = Survey.from_surveyjs(survey_json, survey_results)
    question = survey.questions[0]
    assert type(question) == SingleChoiceQuestion
    assert question.answers == ["Male", "Female", "other, which?", None]


def test_from_surveyjs_parses_radiogroup_question_when_choices_given_as_list(basic_surveyjs_json):
    question_json = {
        "type": "radiogroup", "name": "gender", "title": "What's your gender?", "hasOther": True,
        "choices": ["Male", "Female"]
    }
    survey_json = _get_surveyjs_json(basic_surveyjs_json, question_json)
    survey_results = ['{"gender": "Male"}', '{"gender": "Female"}', '{"gender": "other"}', '{}']
    survey = Survey.from_surveyjs(survey_json, survey_results)
    question = survey.questions[0]
    assert type(question) == SingleChoiceQuestion
    assert question.answers == ["Male", "Female", "other, which?", None]


def test_from_surveyjs_parses_checkbox_question(basic_surveyjs_json):
    question_json = {
        "type": "checkbox", "name": "favouritePhoneBrands",
        "title": "What are your favourite phone brands?", "hasOther": True,
        "choices": ["iPhone", "Samsung", "Xiaomi", "Nokia", "Huawei"],
        "hasNone": True
    }
    survey_json = _get_surveyjs_json(basic_surveyjs_json, question_json)
    survey_results = [
        '{"favouritePhoneBrands": ["Samsung", "iPhone"]}',
        '{"favouritePhoneBrands": ["none"]}',
        '{"favouritePhoneBrands": ["other"]}',
        '{"favouritePhoneBrands": ["Nokia"]}',
        '{"favouritePhoneBrands": ["Huawei", "Xiaomi"]}',
        '{}'
    ]
    survey = Survey.from_surveyjs(survey_json, survey_results)
    question = survey.questions[0]
    assert type(question) == MultipleChoiceQuestion
    assert question.answers == [["Samsung", "iPhone"], ["none"], ["other, which?"], ["Nokia"],
                                ["Huawei", "Xiaomi"], None]


def test_from_surveyjs_parses_single_choice_matrix_question_with_lists(basic_surveyjs_json):
    q_name = "carBrandRatings"
    q_label = "How do you rate the following car brands?"
    question_json = {
        "type": "matrix", "name": q_name, "title": q_label, "columns": ["1", "2", "3", "4", "5"],
        "rows": ["Peugeot", "Skoda"]
    }
    survey_json = _get_surveyjs_json(basic_surveyjs_json, question_json)
    survey_results = [
        '{"carBrandRatings": {"Peugeot": "1", "Skoda": "5"}}',
        '{"carBrandRatings": {"Peugeot": "5"}}',
        '{"carBrandRatings": {"Skoda": "3"}}',
        '{}'
    ]
    survey = Survey.from_surveyjs(survey_json, survey_results)
    assert all(type(question) == SingleChoiceQuestion for question in survey.questions)
    assert [question.name for question in survey.questions] == [q_name + "_Peugeot",
                                                                q_name + "_Skoda"]
    assert [question.label for question in survey.questions] == [q_label + ": Peugeot",
                                                                 q_label + ": Skoda"]
    assert [question.answers for question in survey.questions] == [["1", "5", None, None],
                                                                   ["5", None, "3", None]]


def test_from_surveyjs_parses_single_choice_matrix_question_with_dicts(basic_surveyjs_json):
    q_name = "carBrandRatings"
    q_label = "How do you rate the following car brands?"
    question_json = {
        "type": "matrix", "name": q_name, "title": q_label,
        "columns": [
            {"value": "1", "text": "Very bad"},
            {"value": "2", "text": "Bad"},
            {"value": "3", "text": "So so"},
            {"value": "4", "text": "Good"},
            {"value": "5", "text": "Very good"}
        ],
        "rows":[
            {"value": "peugeot", "text": "Peugeot"},
            {"value": "skoda", "text": "Skoda"}
        ]
    }
    survey_json = _get_surveyjs_json(basic_surveyjs_json, question_json)
    survey_results = [
        '{"carBrandRatings": {"peugeot": "1", "skoda": "5"}}',
        '{"carBrandRatings": {"peugeot": "5"}}',
        '{"carBrandRatings": {"skoda": "3"}}',
        '{}'
    ]
    survey = Survey.from_surveyjs(survey_json, survey_results)
    assert all(type(question) == SingleChoiceQuestion for question in survey.questions)
    assert [question.name for question in survey.questions] == [q_name + "_peugeot",
                                                                q_name + "_skoda"]
    assert [question.label for question in survey.questions] == [q_label + ": Peugeot",
                                                                 q_label + ": Skoda"]
    assert [question.answers for question in survey.questions] == [
        ["Very bad", "Very good", None, None], ["Very good", None, "So so", None]]


def test_from_surveyjs_parses_multiple_text(basic_surveyjs_json):
    question_json = {
        "type": "multipletext", "name": "name", "title": "What's your name?",
        "items": [
          {"name": "firstName", "title": "First name"},
          {"name": "lastName", "title": "Last name"}
        ]
    }
    survey_json = _get_surveyjs_json(basic_surveyjs_json, question_json)
    survey_results = ['{"name_firstName": "John", "name_lastName": "Doe"}', '{}']
    survey = Survey.from_surveyjs(survey_json, survey_results)
    assert all(type(question) == TextInputQuestion for question in survey.questions)
    assert [question.name for question in survey.questions] == ['name_firstName', 'name_lastName']
    assert [question.label for question in survey.questions] == ["What's your name?: First name",
                                                                 "What's your name?: Last name"]
    assert [question.answers for question in survey.questions] == [["John", None], ["Doe", None]]
