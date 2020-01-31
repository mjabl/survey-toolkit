"""Core survey toolkit"""
# pylint: disable=missing-docstring

import json
import re
from collections import OrderedDict
import pandas as pd
import many_stop_words


class Survey:
    """A container for questions"""

    def __init__(self, questions):
        self.questions = questions

    @classmethod
    def from_surveyjs(cls, survey_json: dict, results: list = None, convert_to_labels=False,
                      default_other_text='other, which?', default_none_text='none'):
        """Builds Survey object from surveyjs' survey json and, optionally, a result set"""
        from .io.surveyjs import MetadataParser, process_result
        metadata_parser = MetadataParser(default_other_text=default_other_text,
                                         default_none_text=default_none_text)
        survey = cls(questions=metadata_parser.parse(survey_json))
        if results:
            results = [process_result(json.loads(row)) for row in results]
            survey.add_results(*results, convert_to_labels=convert_to_labels)
        return survey

    def add_result(self, convert_to_labels=False, **result):
        for question in self.questions:
            question.add_answer(result.get(question.name, None),
                                convert_to_labels=convert_to_labels)

    def add_results(self, *results, convert_to_labels=False):
        for result in results:
            self.add_result(**result, convert_to_labels=convert_to_labels)

    def get_results(self) -> OrderedDict:
        results = OrderedDict()
        for question in self.questions:
            key = question.label
            assert key not in results, f"Duplicate key: {key}"
            results[key] = question.answers
        return OrderedDict(results)

    def summary(self, language='en', **kwargs):
        return [question.summary(language=language, **kwargs)
                for question in self.questions]

    def clean_labels(self, regex):
        for question in self.questions:
            question.clean_labels(regex)

    def clean_html_labels(self):
        for question in self.questions:
            question.clean_html_labels()

    def filter(self):
        raise NotImplementedError

    def remove_duplicates(self, keep='ceil'):
        raise NotImplementedError

    def to_pandas(self) -> pd.DataFrame:
        """Creates pandas DataFrame from survey data """
        return pd.DataFrame.from_dict(self.get_results())


class Question:

    data_type = str

    def __init__(self, name, label=None, answers=None):
        self.name = name
        self._label = label
        self.answers = answers

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.__dict__)})"

    @property
    def label(self):
        if self._label:
            return self._label
        return self.name

    def add_answer(self, value, **kwargs): #pylint:disable=unused-argument
        if not self.answers:
            self.answers = []
        if value:
            value = self.data_type(value)
        self.answers.append(value)

    def get_unique_answers(self):
        unique_answers = set(self.answers)
        unique_answers.discard(None)
        return sorted(unique_answers)

    def summary(self, **kwargs):  # pylint:disable=unused-argument
        name = self.label
        return f"Name: {name}, summary unavailable"

    def clean_labels(self, regex):
        if self._label:
            self._label = re.sub(re.compile(regex), '', self._label)

    def clean_html_labels(self):
        self.clean_labels(regex='<.*?>')

    def to_series(self):
        series = pd.Series(self.answers)
        series.name = self.label
        return series


class NumericInputQuestion(Question):

    data_type = float

    def add_answer(self, value, **kwargs):  #pylint:disable=unused-argument
        try:
            super(NumericInputQuestion, self).add_answer(value)
        except ValueError:
            super(NumericInputQuestion, self).add_answer(value.replace(',', '.'))

    def summary(self, **kwargs):
        return self.to_series().describe()


class TextInputQuestion(Question):

    def add_answer(self, value, **kwargs):  #pylint:disable=unused-argument
        if not value:
            value = ''
        super(TextInputQuestion, self).add_answer(value)

    def summary(self, **kwargs):
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
        if self._choices:
            return list(self._choices.values())
        return self._choices

    @choices.setter
    def choices(self, value):
        if isinstance(value, (list, tuple, set)):
            self._choices = {} #pylint:disable=attribute-defined-outside-init
            for choice in value:
                self._choices[choice] = choice
        else:
            self._choices = value #pylint:disable=attribute-defined-outside-init

    def clean_labels(self, regex):
        super(ChoiceQuestion, self).clean_labels(regex)
        if self._choices:
            for choice in self._choices:
                self._choices[choice] = re.sub(re.compile(regex), '', self._choices[choice])

    def _convert_to_labels(self, value):
        assert self.choices, f"Choices not defined for question {self.name}"
        if value:
            try:
                return self._choices[value]
            except KeyError:
                raise ValueError(f"Value {value} unavailable in question {self.name}")
        return value


class SingleChoiceQuestion(ChoiceQuestion):

    def add_answer(self, value, **kwargs):
        if kwargs.get('convert_to_labels'):
            value = self._convert_to_labels(value)
        if self.choices and value and value not in self.choices:
            raise ValueError(f"Value {value} unavailable in question {self.name}")
        super(SingleChoiceQuestion, self).add_answer(value)

    def to_series(self):
        categories = self.choices if self.choices else self.get_unique_answers()
        series = pd.Categorical(self.answers, categories=categories, ordered=True)
        series.name = self.label
        return series

    def summary(self, **kwargs):
        summary_series = self.to_series().value_counts()
        summary_series.name = self.label
        return summary_series


class MultipleChoiceQuestion(ChoiceQuestion):

    data_type = list

    def add_answer(self, value, **kwargs):
        if not isinstance(value, (list, tuple, set)):
            value = [value]
        if kwargs.get('convert_to_labels'):
            value = [self._convert_to_labels(val) for val in value]
        if self.choices and any(val not in self.choices for val in value if val):
            raise ValueError(f"Value {value} unavailable in question {self.name}")
        super(MultipleChoiceQuestion, self).add_answer(value)

    def to_dummies(self):
        prefix_sep = ': '
        series = self.to_series()
        stacked_series = series.apply(pd.Series).stack(dropna=False)
        dummy_df = pd.get_dummies(stacked_series, prefix=self.label, prefix_sep=prefix_sep)\
            .sum(level=0)
        if self.choices:
            cols = [self.label + prefix_sep + choice for choice in self.choices]
            return dummy_df[cols]
        return dummy_df

    def summary(self, **kwargs):
        flat_answers = [item for sublist in self.answers for item in sublist]
        series = pd.Categorical(flat_answers, categories=list(self.choices), ordered=True)
        summary_series = series.value_counts()
        summary_series.name = self.label
        return summary_series
