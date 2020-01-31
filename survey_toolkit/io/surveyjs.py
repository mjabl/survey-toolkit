#pylint: disable=cyclic-import
"""Parser for surveyjs' metadata json and result set"""

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
            metadata['rows'] = self._parse_value_text_list(metadata['rows'])
            metadata['type'] = 'radiogroup'
            for row in metadata['rows']:
                metadata['name'] = row
                metadata['title'] = metadata['rows'][row]
                self._handle_question(**metadata)
            self.name_stack.pop()
            self.label_stack.pop()
        elif metadata['type'] == 'html':
            pass
        elif metadata['type'] in ['paneldynamic', 'matrixdynamic', 'html', 'sortablelist']:
            pass
        else:
            self._handle_question(**metadata)

    def _handle_question(self, **kwargs):
        """Question factory"""
        _type = kwargs['type']
        if _type == 'radiogroup':
            self._handle_radiogroup(**kwargs)
        elif _type == 'checkbox':
            self._handle_checkbox(**kwargs)

        elif _type == 'text':
            validators = kwargs.get('validators', [])
            if (kwargs.get('inputType') == 'number') or\
                    (any(validator.get('type') == 'numeric' for validator in validators)):
                self._handle_numeric(**kwargs)
            else:
                self._handle_text(**kwargs)
        elif _type in ['paneldynamic', 'matrixdynamic', 'sortablelist']:
            self._handle_other(**kwargs)
        else:
            raise NotImplementedError(f"Cannot handle {_type}")

    def _handle_text(self, **kwargs):
        if self.name_stack:
            kwargs['name'] = '_'.join(self.name_stack) + '_' + kwargs['name']
        if self.label_stack:  # FIXME: this is repeated so many times...
            kwargs['title'] = ': '.join(self.label_stack) + ': ' + kwargs.get('title', '')
        self.question_list.append(TextInputQuestion(kwargs['name'], label=kwargs['title']))

    def _handle_numeric(self, **kwargs):
        if self.name_stack:
            kwargs['name'] = '_'.join(self.name_stack) + '_' + kwargs['name']
        if self.label_stack:
            kwargs['title'] = ': '.join(self.label_stack) + ': ' + kwargs.get('title', '')
        self.question_list.append(NumericInputQuestion(kwargs['name'], label=kwargs['title']))

    def _handle_radiogroup(self, **kwargs):
        if self.name_stack:
            kwargs['name'] = '_'.join(self.name_stack) + '_' + kwargs['name']
        if self.label_stack:
            kwargs['title'] = ': '.join(self.label_stack) + ': ' + kwargs.get('title', '')
        choices = self._parse_value_text_list(kwargs['choices'])
        if kwargs.get('hasOther'):
            other_text = kwargs.get('otherText', self.default_other_text)
            choices['other'] = other_text
            self.question_list.append(SingleChoiceQuestion(kwargs['name'], label=kwargs['title'],
                                                           choices=choices))
            self.question_list.append(TextInputQuestion(kwargs['name'] + '-Comment',
                                                        kwargs['title'] + ' ' + other_text))
        else:
            self.question_list.append(SingleChoiceQuestion(kwargs['name'], label=kwargs['title'],
                                                           choices=choices))

    def _handle_checkbox(self, **kwargs):
        if self.name_stack:
            kwargs['name'] = '_'.join(self.name_stack) + '_' + kwargs['name']
        if self.label_stack:  # FIXME: solve repeating blocks with decorator or defined procedures
            kwargs['title'] = ': '.join(self.label_stack) + ': ' + kwargs.get('title', '')
        choices = self._parse_value_text_list(kwargs['choices'])
        if kwargs.get('hasNone'):
            choices['none'] = kwargs.get('noneText', self.default_none_text)
        if kwargs.get('hasOther'):
            other_text = kwargs.get('otherText', self.default_other_text)
            choices['other'] = other_text
            self.question_list.append(MultipleChoiceQuestion(kwargs['name'], label=kwargs['title'],
                                                             choices=choices))
            self.question_list.append(TextInputQuestion(kwargs['name'] + '-Comment',
                                                        kwargs['title'] + ' ' + other_text))
        else:
            self.question_list.append(MultipleChoiceQuestion(kwargs['name'], label=kwargs['title'],
                                                             choices=choices))

    def _handle_other(self, **kwargs):
        if self.name_stack:
            kwargs['name'] = '_'.join(self.name_stack) + '_' + kwargs['name']
        if self.label_stack:
            kwargs['title'] = ': '.join(self.label_stack) + ': ' + kwargs.get('title', '')
        self.question_list.append(Question(kwargs['name'], label=kwargs['title']))

    @staticmethod
    def _parse_value_text_list(choices):
        parsed_choices = {}
        for choice in choices:
            if isinstance(choice, dict):
                parsed_choices[choice['value']] = choice["text"]
            elif isinstance(choice, str):
                parsed_choices[choice] = choice
            else:
                raise ValueError
        return parsed_choices


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
