# pylint:disable=missing-docstring,redefined-outer-name
import pytest
from survey_toolkit.core import (Survey, NumericInputQuestion, TextInputQuestion,
                                 SingleChoiceQuestion)


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


def test_from_surveyjs_parses_radiogroup_question(basic_surveyjs_json):
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
