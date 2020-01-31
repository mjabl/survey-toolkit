# pylint:disable=missing-docstring,redefined-outer-name
from survey_toolkit.core import (Survey, NumericInputQuestion, TextInputQuestion,
                                 SingleChoiceQuestion)


def test_from_surveyjs_parses_numeric_question():
    survey_json = {
        "pages": [
            {
                "name": "page1",
                "elements": [
                    {
                        "type": "text",
                        "name": "age",
                        "title": "How old are you?",
                        "inputType": "number"
                    }
                ]
            }
        ]
    }
    survey_results = [
        '{"age": 20}',
        '{"age": 30}',
        '{"age": 35.5}',
        '{}',
    ]
    survey = Survey.from_surveyjs(survey_json, survey_results)
    question = survey.questions[0]
    assert type(question) == NumericInputQuestion
    assert question.name == 'age'
    assert question.label == "How old are you?"
    assert question.answers == [20, 30, 35.5, None]


def test_from_surveyjs_parses_text_question():
    survey_json = {
        "pages": [
            {
                "name": "page1",
                "elements": [
                    {
                        "type": "text",
                        "name": "surveyjsOpinion",
                        "title": "How do you like the surveyjs service?",
                    }
                ]
            }
        ]
    }
    survey_results = [
        '{"surveyjsOpinion": "it\'s fantastic!"}',
        '{"surveyjsOpinion": "sux!"}',
        '{"surveyjsOpinion": ""}',
        '{}',
    ]
    survey = Survey.from_surveyjs(survey_json, survey_results)
    question = survey.questions[0]
    assert type(question) == TextInputQuestion
    assert question.name == 'surveyjsOpinion'
    assert question.label == "How do you like the surveyjs service?"
    assert question.answers == ["it's fantastic!", "sux!", "", None]


def test_from_surveyjs_parses_text_question_with_numeric_validator():
    survey_json = {
        "pages": [
            {
                "name": "page1",
                "elements": [
                    {
                        "type": "text",
                        "name": "age",
                        "title": "How old are you?",
                        "validators": [
                            {
                                "type": "numeric",
                                "minValue": 5,
                                "maxValue": 105
                            }
                        ]
                    }
                ]
            }
        ]
    }
    survey_results = [
        '{"age": "20"}',
        '{"age": "30"}',
        '{"age": "35.5"}',
        '{"age": "35,5"}',
        '{}',
    ]
    survey = Survey.from_surveyjs(survey_json, survey_results)
    question = survey.questions[0]
    assert type(question) == NumericInputQuestion
    assert question.name == 'age'
    assert question.label == "How old are you?"
    assert question.answers == [20, 30, 35.5, 35.5, None]


def test_from_surveyjs_parses_radiogroup_question_when_choices_given_as_kv():
    survey_json = {
        "pages": [
            {
                "name": "page1",
                "elements": [
                    {
                        "type": "radiogroup",
                        "name": "gender",
                        "title": "What's your gender?",
                        "hasOther": True,
                        "choices": [
                            {
                                "value": "male",
                                "text": "Male"
                            },
                            {
                                "value": "female",
                                "text": "Female"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    survey_results = [
        '{"gender": "male"}',
        '{"gender": "female"}',
        '{"gender": "other"}',
        '{}',
    ]
    survey = Survey.from_surveyjs(survey_json, survey_results)
    question = survey.questions[0]
    assert type(question) == SingleChoiceQuestion
    assert question.name == 'gender'
    assert question.label == "What's your gender?"
    assert question.answers == ["Male", "Female", "other, which?", None]
