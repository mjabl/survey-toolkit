"""Parser for surveyjs' metadata json and result set"""
# pylint: disable=cyclic-import,too-few-public-methods
from typing import List
from ..core import (Question, SingleChoiceQuestion, MultipleChoiceQuestion,
                    NumericInputQuestion, TextInputQuestion)


class MetadataParser:  # pylint: disable=too-few-public-methods
    """Parser of metadata from surveyjs' survey json"""

    def __init__(self, default_other_text, default_none_text):
        self.default_other_text = default_other_text
        self.default_none_text = default_none_text
        self.question_list = []
        self.name_stack = []
        self.label_stack = []

    def parse(self, metadata):
        """Parses metadata from surveyjs' survey json"""
        if self.question_list:
            self.question_list = []
        self._parse(metadata)
        return self.question_list

    def _parse(self, metadata):
        if metadata.get('pages'):
            for page in metadata['pages']:
                for element in page.get('elements', []):
                    self._parse(element)
        elif metadata['type'] == 'panel':
            self.label_stack.append(metadata.get('title', ''))
            for element in metadata['elements']:
                self._parse(element)
            self.label_stack.pop()
        elif metadata['type'] == 'multipletext':
            self.name_stack.append(metadata['name'])
            self.label_stack.append(metadata.get('title', ''))
            for item in metadata['items']:
                item['type'] = 'text'
                self._handle_question(**item)
            self.name_stack.pop()
            self.label_stack.pop()
        elif metadata['type'] == 'matrix':
            self.name_stack.append(metadata['name'])
            self.label_stack.append(metadata.get('title', ''))
            metadata['choices'] = metadata['columns']
            metadata['rows'] = _parse_value_text_list(metadata['rows'])
            metadata['type'] = 'radiogroup'
            for row in metadata['rows']:
                metadata['name'] = row
                metadata['title'] = metadata['rows'][row]
                self._handle_question(**metadata)
            self.name_stack.pop()
            self.label_stack.pop()
        elif metadata['type'] == 'html':
            pass
        else:
            self._handle_question(**metadata)

    def _handle_question(self, **metadata) -> None:
        if self.name_stack:
            metadata['name'] = '_'.join(self.name_stack) + '_' + metadata['name']
        if self.label_stack:
            metadata['title'] = ': '.join(self.label_stack) + ': ' + metadata.get('title', '')
        metadata['defaultOtherText'] = self.default_other_text
        metadata['defaultNoneText'] = self.default_none_text
        question_parser = get_question_parser(**metadata)
        self.question_list.extend(question_parser.parse())


class QuestionParser:
    """Surveyjs question parser"""
    question_class = Question

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.label = kwargs.get('title')

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.__dict__)})"

    def parse(self) -> List[Question]:
        """Parses surveyjs question and returns relevant Question object(s)"""
        return self._parse()

    def _parse(self):
        return [self.question_class(**self.__dict__)]


class TextQuestionParser(QuestionParser):
    """Surveyjs text question parser"""
    question_class = TextInputQuestion


class NumericQuuestionParser(QuestionParser):
    """Surveyjs numeric question parser"""
    question_class = NumericInputQuestion


class RadiogroupQuestionParser(QuestionParser):
    """Surveyjs radiougroup question parser"""
    question_class = SingleChoiceQuestion

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.choices = _parse_value_text_list(kwargs['choices'])
        if kwargs.get('hasOther'):
            other_text = kwargs.get('otherText', kwargs.get('defaultOtherText', ''))
            self.choices['other'] = other_text

    def _parse(self) -> List[Question]:
        if self.choices.get('other'):
            comment_question = TextInputQuestion(name=self.name + '-Comment',
                                                 label=self.label + ' ' + self.choices['other'])
            return super()._parse() + [comment_question]
        return super()._parse()


class CheckboxQuestionParser(RadiogroupQuestionParser):
    """Surveyjs checkbox question parser"""
    question_class = MultipleChoiceQuestion

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if kwargs.get('hasNone'):
            self.choices['none'] = kwargs.get('noneText', kwargs.get('defaultNoneText', ''))


def get_question_parser(**kwargs) -> QuestionParser:
    """Question parser factory"""
    _type = kwargs['type']
    if _type == 'radiogroup':
        return RadiogroupQuestionParser(**kwargs)
    if _type == 'checkbox':
        return CheckboxQuestionParser(**kwargs)
    if _type == 'text':
        validators = kwargs.get('validators', [])
        if (kwargs.get('inputType') == 'number') or\
                (any(validator.get('type') == 'numeric' for validator in validators)):
            return NumericQuuestionParser(**kwargs)
        return TextQuestionParser(**kwargs)
    if _type in ['paneldynamic', 'matrixdynamic', 'sortablelist']:
        return QuestionParser(**kwargs)
    raise NotImplementedError(f"Cannot get parser for {_type}")


def process_result(result: dict):
    """Processes single surveyjs result"""
    target = {}
    for variable in result:
        if isinstance(result[variable], dict):
            for key in result[variable]:
                target[str(variable) + '_' + str(key)] = result[variable][key]
        else:
            target[variable] = result[variable]
    return target


def _parse_value_text_list(choices: list) -> dict:
    parsed_choices = {}
    for choice in choices:
        if isinstance(choice, dict):
            parsed_choices[choice['value']] = choice["text"]
        elif isinstance(choice, str):
            parsed_choices[choice] = choice
        else:
            raise ValueError
    return parsed_choices
