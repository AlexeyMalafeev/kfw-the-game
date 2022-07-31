from abc import ABC, abstractmethod


class Validator(ABC):

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        self.validate(value)
        setattr(obj, self.private_name, value)

    @abstractmethod
    def validate(self, value):
        pass


class Integer(Validator):

    def __init__(self, minvalue=None, maxvalue=None):
        self.minvalue = minvalue
        self.maxvalue = maxvalue

    def validate(self, value):
        if not isinstance(value, int):
            raise TypeError(f'Expected {self.private_name} {value!r} to be an int')
        if self.minvalue is not None and value < self.minvalue:
            raise ValueError(
                f'Expected {self.private_name} {value!r} to be at least {self.minvalue!r}'
            )
        if self.maxvalue is not None and value > self.maxvalue:
            raise ValueError(
                f'Expected {self.private_name} {value!r} to be no more than {self.maxvalue!r}'
            )


class Float(Validator):

    def __init__(self, minvalue=None, maxvalue=None):
        self.minvalue = minvalue
        self.maxvalue = maxvalue

    def validate(self, value):
        if not isinstance(value, float):
            raise TypeError(f'Expected {self.private_name} {value!r} to be an float')
        if self.minvalue is not None and value < self.minvalue:
            raise ValueError(
                f'Expected {self.private_name} {value!r} to be at least {self.minvalue!r}'
            )
        if self.maxvalue is not None and value > self.maxvalue:
            raise ValueError(
                f'Expected {self.private_name} {value!r} to be no more than {self.maxvalue!r}'
            )
