"""Core survey toolkit"""
# pylint: disable=missing-docstring

import json
import re
from collections import OrderedDict, Counter
import pandas as pd
import many_stop_words


class Survey:

    def __init__(self, questions):
        question_names = [question.name for question in questions]
        duplicated_names = [name for name, count in Counter(question_names).items() if count > 1]
        if duplicated_names:
            raise ValueError(f"Question names must be unique. Duplicate names: {duplicated_names}")
        self.questions = questions

    @classmethod
    def from_surveyjs(cls, survey_json: dict, results: list = None,
                      default_other_text='other, which?', default_none_text='none'):
        """Builds Survey object from surveyjs' survey json and, optionally, a result set"""
        from .io.surveyjs import MetadataParser, process_result
        metadata_parser = MetadataParser(default_other_text=default_other_text,
                                         default_none_text=default_none_text)
        survey = cls(questions=metadata_parser.parse(survey_json))
        if results:
            results = [process_result(json.loads(row)) for row in results]
            survey.add_results(*results)
        return survey

    def add_result(self, **result):
        for question in self.questions:
            question.add_answer(result.get(question.name, None))

    def add_results(self, *results):
        for result in results:
            self.add_result(**result)

    # def get_results(self) -> OrderedDict:
    #     results = OrderedDict()
    #     for question in self.questions:
    #         key = question.label
    #         assert key not in results, f"Duplicate key: {key}"
    #         results[key] = question.answers
    #     return OrderedDict(results)

    def summary(self, language='en', **kwargs):
        return [question.summary(language=language, **kwargs)
                for question in self.questions]

    def clean_labels(self, regex):
        for question in self.questions:
            question.clean_labels(regex)

    def clean_html_labels(self):
        for question in self.questions:
            question.clean_html_labels()

    def to_pandas(self, to_labels=False, to_dummies=False) -> pd.DataFrame:
        """Creates pandas DataFrame from survey data"""
        return pd.DataFrame.from_dict(self.get_results())


class Question:

    def __init__(self, name, label=None, answers=None):
        self.name = name
        self._label = label
        self.answers = answers if answers else []
        self.data_type = str

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.__dict__)})"

    @property
    def label(self):
        if self._label:
            return self._label
        return self.name

    @property
    def answers(self):
        return self._answers

    @answers.setter
    def answers(self, value: list):
        self._answers = []  # pylint: disable=attribute-defined-outside-init
        for item in value:
            self._add_answer(item)

    def add_answer(self, value):
        self._add_answer(value)

    def get_unique_answers(self):
        return self._get_unique_answers(self.answers)

    def summary(self, **kwargs):
        return self._summary(**kwargs)

    def clean_labels(self, regex):
        self._clean_labels(regex)

    def clean_html_labels(self):
        self._clean_labels(regex='<.*?>')

    def to_series(self, to_labels=False):
        return self._to_series(answers=self.answers, to_labels=to_labels)

    def _clean_labels(self, regex):
        if self._label:
            self._label = re.sub(re.compile(regex), '', self._label)

    def _add_answer(self, value):
        if value is not None:
            value = self.data_type(value)
        self._answers.append(value)

    def _to_series(self, answers: list, to_labels: bool):
        return pd.Series(answers, name=self.label if to_labels else self.name)

    def _summary(self, **kwargs):  # pylint:disable=unused-argument
        name = self.label
        return f"Name: {name}, summary unavailable"

    @staticmethod
    def _get_unique_answers(answers):
        unique_answers = set(answers)
        unique_answers.discard(None)
        return sorted(unique_answers)


class NumericInputQuestion(Question):

    def __init__(self, name, label=None, answers=None):
        super(NumericInputQuestion, self).__init__(name, label=label, answers=answers)
        self.data_type = float

    def _add_answer(self, value):
        try:
            super(NumericInputQuestion, self)._add_answer(value)
        except ValueError:
            super(NumericInputQuestion, self)._add_answer(value.replace(',', '.'))

    def _summary(self, **kwargs):
        return self.to_series().describe()


class TextInputQuestion(Question):

    def _summary(self, **kwargs):
        str_corpus = " ".join(self.answers).lower()
        words = re.sub(r"[^\w]", " ", str_corpus).split()
        stop_words = many_stop_words.get_stop_words(kwargs.get('language', 'en'))
        filtered_words = [word for word in words if word not in stop_words]
        summary_series = pd.Series(filtered_words).value_counts()[:20]
        summary_series.name = self.label
        return summary_series


class ChoiceQuestion(Question):

    def __init__(self, name, label=None, answers=None, choices=None):
        super(ChoiceQuestion, self).__init__(name, label=label, answers=answers)
        self.choices = choices

    @property
    def choices(self):
        return self._choices

    @choices.setter
    def choices(self, value):
        self._set_choices(value)

    def get_choice_labels(self):
        try:
            return list(self.choices.values())
        except AttributeError:
            return self.choices

    def optimize(self):
        """Converts answers and choice keys to numeric values. Useful for exporting data to SPSS/SAS
        """
        if self.data_type == int:
            return
        opt_map = self._get_optimization_map()
        self.choices = self._get_optimized_choices(opt_map)
        self.answers = self._get_optimized_answers(opt_map)

    def _clean_labels(self, regex):
        super(ChoiceQuestion, self)._clean_labels(regex)
        if self.choices:
            new_choices = {}
            for choice in self.choices:
                new_choices[choice] = re.sub(re.compile(regex), '', self.choices[choice])
            self.choices = new_choices

    def _set_choices(self, value):
        # pylint:disable=attribute-defined-outside-init
        if not value:
            self._choices = []
            return
        if isinstance(value, (list, tuple, set)):
            choices = {}
            for choice in value:
                choices[choice] = choice
        else:
            choices = value
        try:
            self._choices = {}
            for choice in choices:
                self._choices[int(choice)] = choices[choice]
        except ValueError:
            self._choices = choices

    def _get_optimization_map(self):
        current_vals = list(self.choices) if self.choices else self.get_unique_answers()
        return {val: nr + 1 for (nr, val) in enumerate(current_vals)}

    def _get_optimized_choices(self, optimization_map: dict):
        if self.choices:
            return {optimization_map[val]: self.choices[val] for val in self.choices}
        return {nr: val for (val, nr) in optimization_map.items()}

    def _get_optimized_answers(self, optimization_map: dict):
        return [optimization_map[val] if val is not None else None for val in self.answers]


class SingleChoiceQuestion(ChoiceQuestion):

    def _add_answer(self, value):
        if self.choices and value and self.data_type(value) not in list(self.choices):
            raise ValueError(f"Value {value} unavailable in question {self.name}")
        super(SingleChoiceQuestion, self)._add_answer(value)

    def _summary(self, **kwargs):
        summary_series = self.to_series(to_labels=True).value_counts()
        summary_series.name = self.label
        return summary_series

    def _set_choices(self, value):
        super(SingleChoiceQuestion, self)._set_choices(value)
        if self.choices and all(isinstance(choice, int) for choice in self.choices):
            self.data_type = int

    def _to_series(self, answers: list, to_labels: bool):
        if to_labels:
            series_name = self.label
            if self.choices:
                answers = [self.choices[answer] if answer is not None else None
                           for answer in self.answers]
                categories = self.get_choice_labels()
            else:
                categories = self.get_unique_answers()
        else:
            series_name = self.name
            categories = list(self.choices)
        series = pd.Categorical(answers, categories=categories, ordered=True)
        series.name = series_name
        return series


class MultipleChoiceQuestion(ChoiceQuestion):

    def __init__(self, name, label=None, answers=None, choices=None):
        super(MultipleChoiceQuestion, self).__init__(name, label=label, answers=answers,
                                                     choices=choices)
        self.data_type = list

    def to_dummies(self, to_labels=False):
        if to_labels:
            return self._to_dummies(self.get_choice_labels(), self.label, prefix_sep=': ')
        return self._to_dummies(list(self.choices), self.name, prefix_sep='_')

    def get_dummy_variables(self):
        if self.choices:
            return {self.name + '_' + choice: self.label + ': ' + self.choices[choice]
                    for choice in self.choices}
        return {self.name + '_' + answer: self.label + ': ' + answer
                for answer in self.get_unique_answers()}

    def _add_answer(self, value):
        if isinstance(value, (int, float, str)):
            value = [value]
        if value and self.choices and any(val not in list(self.choices) for val in value if val):
            raise ValueError(f"Value {value} unavailable in question {self.name}")
        super(MultipleChoiceQuestion, self)._add_answer(value)

    def _summary(self, **kwargs):
        flat_answers = [item for sublist in self.answers for item in sublist]
        series = pd.Categorical(flat_answers, categories=list(self.choices), ordered=True)
        summary_series = series.value_counts()
        summary_series.name = self.label
        return summary_series

    @staticmethod
    def _get_unique_answers(answers):
        flat_answers = []
        for answer_list in answers:
            if answer_list is not None:
                flat_answers.extend(answer_list)
        return sorted(set(flat_answers))

    def _to_series(self, answers: list, to_labels: bool):
        if to_labels:
            answers = []
            for answer_list in self.answers:
                if answer_list:
                    converted_answer_list = []
                    for answer in answer_list:
                        converted_answer = self.choices[answer] if answer is not None else None
                        converted_answer_list.append(converted_answer)
                    answers.append(converted_answer_list)
                else:
                    answers.append(None)
        else:
            answers = self.answers
        return super(MultipleChoiceQuestion, self)._to_series(answers, to_labels)

    def _to_dummies(self, choices: list, prefix: str, prefix_sep: str):
        choices = choices if choices else self.get_unique_answers()
        series = self.to_series()
        stacked_series = series.apply(pd.Series).stack(dropna=False)
        dummy_df = pd.get_dummies(stacked_series, prefix=prefix, prefix_sep=prefix_sep)\
            .sum(level=0)
        cols = [prefix + prefix_sep + choice for choice in choices]
        return dummy_df[cols]

    def _get_optimized_answers(self, optimization_map: dict):
        optimized_answers = []
        for answer_list in self.answers:
            if answer_list is not None:
                optimized_answers.append([optimization_map[val] for val in answer_list])
            else:
                optimized_answers.append(None)
        return optimized_answers
