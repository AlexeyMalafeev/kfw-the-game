from abc import ABC, abstractmethod
import logging
from typing import Literal, Optional, Text, Union


logger = logging.getLogger()


class Validator(ABC):

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        value = self._validate(value, obj)
        setattr(obj, self.private_name, value)

    @abstractmethod
    def _validate(self, value, obj):
        pass


class ValidationError(Exception):
    pass


class BaseNumber(Validator):
    expected_type = None

    def __init__(
            self,
            minvalue: Optional[Union[int, float]] = None,
            maxvalue: Optional[Union[int, float]] = None,
            action: Literal['raise', 'warn', 'ignore'] = 'warn',
    ):
        self.minvalue = minvalue
        self.maxvalue = maxvalue
        if action == 'raise':
            self._act = self._raise
        elif action == 'warn':
            self._act = self._warn
        elif action == 'ignore':
            self._act = self._ignore
        else:
            raise ValueError(
                f"action needs to be one of the following: ['raise', 'warn', 'ignore']"
            )

    def _ignore(self, output_str: Text):
        pass

    def _raise(self, output_str: Text):
        raise ValidationError(output_str)

    def _validate(self, value, obj):
        if not isinstance(value, self.expected_type):
            self._act(
                f'Expected {self.private_name} {value!r} to be {self.expected_type!r}'
                f'for {obj}'
            )
            return self.expected_type(value)
        if self.minvalue is not None and value < self.minvalue:
            self._act(
                f'Expected {self.private_name} {value!r} to be at least {self.minvalue!r}'
                f'for {obj}'
            )
            return self.minvalue
        if self.maxvalue is not None and value > self.maxvalue:
            self._act(
                f'Expected {self.private_name} {value!r} to be no more than {self.maxvalue!r}'
                f'for {obj}')
            return self.maxvalue
        return value

    def _warn(self, output_str: Text):  # noqa
        print(output_str)
        logger.warning(output_str)


class Integer(BaseNumber):
    expected_type = int


class Float(BaseNumber):
    expected_type = float
