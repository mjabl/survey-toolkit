"""Core survey toolkit"""
# pylint: disable=missing-docstring

import re
from collections import OrderedDict
import pandas as pd
import many_stop_words


class Survey:
    """A container for questions"""

    def __init__(self, questions):
        self.questions = questions

    def add_result(self, **kwargs):
        for question in self.questions:
            question.add_answer(kwargs.get(question.name, None))

    def add_results(self, *args):
        for result in args:
            self.add_result(**result)

    def get_results(self, labels=False) -> list:
        results = []
        for question in self.questions:
            key = question.label if labels else question.name
            results.append((key, question.get_answers(labels=labels)))
        return OrderedDict(results)

    def summary(self, labels=True, **kwargs):
        return [question.summary(labels=labels, **kwargs) for question in self.questions]

    def clean_labels(self, regex):
        for question in self.questions:
            question.clean_labels(regex)

    def clean_html_labels(self):
        for question in self.questions:
            question.clean_html_labels()

    def filter(self):
        pass

    def remove_duplicates(self, keep='ceil'):
        pass

    def to_pandas(self, labels=False) -> pd.DataFrame:
        """Creates pandas DataFrame from survey data """
        return pd.DataFrame.from_dict(self.get_results(labels))


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
        if hasattr(self, '_label'):
            return self._label
        return self.name

    def add_answer(self, value):
        if not self.answers:
            self.answers = []
        if value:
            value = self.data_type(value)
        self.answers.append(value)

    def get_answers(self, **kwargs):  # pylint:disable=unused-argument
        return self.answers

    def summary(self, labels=True, **kwargs):  # pylint:disable=unused-argument
        name = self.label if labels else self.name
        return f"Name: {name}, summary unavailable"

    def clean_labels(self, regex):
        if self._label:
            self._label = re.sub(re.compile(regex), '', self._label)

    def clean_html_labels(self):
        self.clean_labels(regex='<.*?>')

    def to_series(self, labels=False):
        series = pd.Series(self.get_answers(labels=labels))
        series.name = self.label if labels else self.name
        return series


class NumericInputQuestion(Question):

    data_type = float

    def add_answer(self, value):
        try:
            super(NumericInputQuestion, self).add_answer(value)
        except ValueError:
            value = value.replace(',', '.')
            super(NumericInputQuestion, self).add_answer(value)

    def summary(self, labels=True, **kwargs):
        return self.to_series(labels=labels).describe()


class TextInputQuestion(Question):
    """docstring for TextInputQuestion"""

    def add_answer(self, value):
        if not value:
            value = ''
        super(TextInputQuestion, self).add_answer(value)

    def summary(self, labels=True, **kwargs):
        str_corpus = " ".join(self.answers).lower()
        words = re.sub(r"[^\w]", " ", str_corpus).split()
        stop_words = many_stop_words.get_stop_words(kwargs.get('language', 'en'))
        filtered_words = [word for word in words if word not in stop_words]
        summary_series = pd.Series(filtered_words).value_counts()[:20]
        summary_series.name = self.label if labels else self.name
        return summary_series


class ChoiceQuestion(Question):

    def __init__(self, name, label=None, answers=None, choices=None):
        super(ChoiceQuestion, self).__init__(name, label=label, answers=answers)
        if isinstance(choices, (list, tuple, set)):
            self.choices = {}
            for choice in choices:
                self.choices[choice] = choice
        else:
            self.choices = choices

    def clean_labels(self, regex):
        super(ChoiceQuestion, self).clean_labels(regex)
        if self.choices:
            for choice in self.choices:
                self.choices[choice] = re.sub(re.compile(regex), '', self.choices[choice])


class SingleChoiceQuestion(ChoiceQuestion):

    def get_answers(self, **kwargs):
        if kwargs['labels']:
            return [self.choices.get(answer, answer) for answer in self.answers]
        return super(SingleChoiceQuestion, self).get_answers(**kwargs)

    def to_series(self, labels=False):
        categories = self.choices.values() if labels else self.choices.keys()
        series = pd.Categorical(self.get_answers(labels=labels), categories=list(categories),
                                ordered=True)
        series.name = self.label if labels else self.name
        return series

    def summary(self, labels=True, **kwargs):
        summary_series = self.to_series(labels=labels).value_counts()
        summary_series.name = self.label if labels else self.name
        return summary_series


class MultipleChoiceQuestion(ChoiceQuestion):

    data_type = list

    def get_answers(self, **kwargs):
        if kwargs['labels']:
            answers = []
            for answer_list in self.answers:
                answers.append([self.choices.get(item, item) for item in answer_list])
            return answers
        return super(MultipleChoiceQuestion, self).get_answers(**kwargs)

    def add_answer(self, value):
        if not value:
            value = [value]
        super(MultipleChoiceQuestion, self).add_answer(value)

    def summary(self, labels=True, **kwargs):
        categories = self.choices.values() if labels else self.choices.keys()
        flat_answers = [item for sublist in self.get_answers(labels=labels) for item in sublist]
        series = pd.Categorical(flat_answers, categories=list(categories), ordered=True)
        summary_series = series.value_counts()
        summary_series.name = self.label if labels else self.name
        return summary_series

    def get_dummies(self):
        pass
