#  ---------------------------------------------------------------------------------------------------------------------
#  core.py
#  Copyright (c) 2024. Jermaine Clarke
#  All rights reserved.
#  ---------------------------------------------------------------------------------------------------------------------
from typing import Optional, Iterable, Sequence, Any, Callable

ParamTuple = tuple[str, ...]
"""A tuple of names for the parameters accepted by a Symbol"""
CommandCallable = Callable[..., Any]
"""A callable that implements the command represented by a Symbol"""

class ProductionRule:
    """
    A rewrite rule that describe how instances of symbols are replaced with other instances of symbols from the same
    alphabet.
    """
    def __init__(self, name, pre, post, handler):
        """
        Create a new production rule.

        :param str name: the name of the rule
        :param int pre: the number of symbols to the left of the subject that are captured.
        :param int post: the number of symbols to the right of the subject that are captured.
        :param str handler: the callable that will handle the rule.
        """
        self._name = None
        self._pre_capture = None
        self._post_capture = None
        self._handler = None

class Symbol:
    """
    Describes a symbol that is part of a Lindenmayer system alphabet.

    Provides the specification that allows each instance of the symbol to be interpreted and parsed.
    """
    def __init__(
            self,
            glyph: str, /,
            name: Optional[str] = None,
            params: Iterable = None,*,
            call: Optional[CommandCallable] = None):
        """
        Creates a new symbol specification.

        :param name: the name of the symbol. If *glyph* is None then this is also used as the glyph.
        :param glyph: the glyph used to visually represent the symbol.
        :param params: the list of names for parameters associated with the symbol.
        :param call: the command corresponding to this symbol in the final string.
        """
        # Validate inputs
        if not isinstance(glyph, str):
            raise TypeError(f"'glyph' must be a 'str' not a {type(glyph)}!")
        if len(glyph) != 1:
            raise ValueError(f"expected a single character for 'glyph' but got {len(glyph)} instead!")

        if name is not None and not isinstance(name, str):
            raise TypeError(f"'name' must be a 'str' not a {type(name)}!")

        if params is not None:
            if not isinstance(params, Sequence) or isinstance(params, str):
                raise TypeError(f"expected 'params' to be a non-string sequence but got {type(params)} instead!")

            for param in params:
                if not isinstance(param, str):
                    raise TypeError(f"expected type 'str' for parameter name '{param}' but got {type(param)} instead!")

        if call is not None and not callable(call):
            raise TypeError(f"expected 'call' to be a callable but got {type(call)} instead!")

        # Initialise instance variables.
        self._name: str = glyph if name is None else name
        self._glyph: str = glyph
        self._parameter_names: ParamTuple = tuple(params) if params is not None else tuple()
        self._command: Optional[CommandCallable] = call
        self._ruleset: list = []
        self._regex: str = self._generate_regex()

    @property
    def name(self) -> str:
        """Returns the name of the symbol"""
        return self._name

    @property
    def glyph(self) -> str:
        """Returns the glyph used to represent the symbol"""
        return self._glyph

    @property
    def params(self) -> ParamTuple:
        """Returns a tuple containing the names of the parameters required by this parameter."""
        return self._parameter_names

    @property
    def size(self) -> int:
        """Returns the number of parameters required by this symbol."""
        return len(self._parameter_names)

    @property
    def callable(self) -> Optional[CommandCallable]:
        """Returns the optional callable object implementing the command represented by this symbol."""
        return self._command

    @property
    def regex(self) -> str:
        """Returns the regular expression string that will match an instance of this symbol and its parameters."""
        return self._regex

    def _generate_regex(self) -> str:
        """
        Generates the regular expression that will match an instance of this symbol and its parameters.

        :return: the regular expression for instances of this symbol.
        """
        whitespace = r'\s'
        alphanumeric = r'\w'
        open_parenthesis = r'\('
        closing_parenthesis = r'\)'

        # Add expressions for each argument
        res = ''
        for param in self.params:
            res += f'{whitespace}*(?P<{param}>{alphanumeric}+),'

        # Remove the comma after the last argument and add brackets
        if len(res) > 0:
            res = f'{open_parenthesis}{res[:-1]}{closing_parenthesis}'

        return f'^{self.glyph}{res}'

    def add_rule(self):
        # TODO: implement
        raise NotImplementedError()

    def drop_rule(self):
        # TODO: implement
        raise NotImplementedError()


    def __repr__(self):
        return f'symbol[name=\'{self.name}\', glyph=\'{self.glyph}\', params={self.params}]'

    def __eq__(self, other: 'Symbol') -> bool:

        if not isinstance(other, type(self)):
            raise TypeError(f"'other' must be a {type(self)} but got {type(other)} instead!")

        return self._glyph == other._glyph and self._parameter_names == other._parameter_names

    def __ne__(self, other):

        if not isinstance(other, type(self)):
            raise TypeError(f"'other' must be a {type(self)} but got {type(other)} instead!")

        return self._glyph != other._glyph or self._parameter_names != other._parameter_names