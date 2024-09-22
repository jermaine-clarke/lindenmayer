#  ---------------------------------------------------------------------------------------------------------------------
#  core.py
#  Copyright (c) 2024. Jermaine Clarke
#  All rights reserved.
#  ---------------------------------------------------------------------------------------------------------------------
from typing import Any, Callable, Iterable, Optional, Sequence

ParamTuple = tuple[str, ...]
"""A tuple of names for the parameters accepted by a Symbol"""
CommandCallable = Callable[..., Any]
"""A callable that implements the command represented by a Symbol"""
RuleCallable = Callable[..., Any]
"""A callable that checks for the conditions of a production rule and returns substitutions."""


class Symbol:
    """
    Describes a symbol that is part of a Lindenmayer system alphabet.

    Provides the specification that allows each instance of the symbol to be interpreted and parsed.
    """

    def __init__(
            self,
            glyph: str, /,
            name: Optional[str] = None,
            params: Iterable = None, *,
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

    def __repr__(self):
        return f'symbol[name=\'{self.name}\', glyph=\'{self.glyph}\', params={self.params}]'

    def __hash__(self):
        return hash(self.glyph)

    def __eq__(self, other: 'Symbol') -> bool:

        if not isinstance(other, type(self)):
            raise TypeError(f"'other' must be a {type(self)} but got {type(other)} instead!")

        return self._glyph == other._glyph and self._parameter_names == other._parameter_names

    def __ne__(self, other):

        if not isinstance(other, type(self)):
            raise TypeError(f"'other' must be a {type(self)} but got {type(other)} instead!")

        return self._glyph != other._glyph or self._parameter_names != other._parameter_names


class Alphabet:
    """
    A set of symbols that can be combined to form Lindenmayer strings.
    """

    def __init__(self):
        self._symbols: set[Symbol] = set()
        self._is_final: bool = False

    # ------------------------------------------------------------------------------------------------------------------
    # Membership and iteration

    def __contains__(self, symbol) -> bool:
        """
        Test a symbol for membership in this alphabet.

        :param Symbol | str symbol: a symbol, character, or symbol name to test.
        :return: True if *symbol* is a member of this alphabet; False otherwise.
        :raises TypeError: if *symbol* is not an instance of class ``Symbol``.
        :raises ValueError: if *symbol* is an empty string.
        """
        if isinstance(symbol, Symbol):
            return symbol in self._symbols
        elif isinstance(symbol, str):
            if len(symbol) == 1:
                # Search by glyph
                for s in self._symbols:
                    if s.glyph == symbol:
                        return True
                return False
            elif len(symbol) > 1:
                # Search by name
                for s in self._symbols:
                    if s.name == symbol:
                        return True
                return False
            else:
                raise ValueError('an empty string is not acceptable!')

        raise TypeError(f"expected an instance of type 'Symbol' got {type(symbol)} instead!")

    def __len__(self) -> int:
        """Return the number of symbols in this alphabet."""
        return len(self._symbols)

    def __iter__(self):
        return self._symbols.__iter__()

    def __lt__(self, other: 'Alphabet') -> bool:
        """Returns True if this alphabet is a proper subset of *other*."""
        if isinstance(other, Alphabet):
            return self._symbols < other._symbols

        raise TypeError(f'expected another Alphabet object for proper subset test got {type(other)} instead!')

    def __le__(self, other) -> bool:
        """Returns True if every symbol of this alphabet is in the *other* alphabet."""
        if isinstance(other, Alphabet):
            return self._symbols <= other._symbols

        raise TypeError(f'expected another Alphabet object for subset test got {type(other)} instead!')

    def __gt__(self, other) -> bool:
        """Returns True if this alphabet is a proper superset of *other*."""
        if isinstance(other, Alphabet):
            return self._symbols > other._symbols

        raise TypeError(f'expected another Alphabet object for proper superset test got {type(other)} instead!')

    def __ge__(self, other) -> bool:
        """Returns True if every Symbol in this alphabet is also in *other*."""
        if isinstance(other, Alphabet):
            return self._symbols >= other._symbols

        raise TypeError(f'expected another Alphabet object for superset test got {type(other)} instead!')

    def __and__(self, other) -> 'Alphabet':
        """Returns an Alphabet object with symbols common to this alphabet and *other*."""
        if isinstance(other, Alphabet):
            res = Alphabet()
            res._symbols = self._symbols & other._symbols
            return res

        raise TypeError(f'expected another Alphabet object for intersection operation got {type(other)} instead!')

    def __or__(self, other) -> 'Alphabet':
        """Returns an Alphabet object with symbols either in this alphabet or *other*."""
        if isinstance(other, Alphabet):
            res = Alphabet()
            res._symbols = self._symbols | other._symbols
            return res

        raise TypeError(f'expected another Alphabet object for union operation got {type(other)} instead!')

    def __sub__(self, other):
        """Returns an Alphabet object with symbols that are in this alphabet but not in *other*."""
        if isinstance(other, Alphabet):
            res = Alphabet()
            res._symbols = self._symbols - other._symbols
            return res

        raise TypeError(f'expected another Alphabet object for subtract operation got {type(other)} instead!')

    def isdisjoint(self, other: 'Alphabet') -> bool:
        """
        Tests if this alphabet and other have no symbols in common.

        :param other: an Alphabet object
        :return: True if the Alphabets are disjoint; False otherwise
        :raises TypeError: if *other* is not an Alphabet object.
        """
        if isinstance(other, Alphabet):
            return self._symbols.isdisjoint(other._symbols)

        raise TypeError(f'expected another Alphabet object for subtract operation got {type(other)} instead!')

    # ------------------------------------------------------------------------------------------------------------------
    # Modification

    def add(self, symbol, /, param_names=None, cmd=None, name=None) -> Symbol:
        """
        Adds a distinct symbol to the alphabet.

        :param Symbol | str symbol: a Symbol object or a character representing the glyph of the symbol. All other parameters are
                                    ignored if a Symbol object is given.
        :param Sequence param_names: the names of the arguments that the symbol requires.
        :param Callable cmd: an optional callable that executes the command associated with the symbol.
        :param str name: an optional friendly name to identify the symbol (default: *glyph*)
        :return: a reference to the newly added symbol.
        :raises KeyError: if the name or glyph is in use by another symbol in the alphabet.
        :raises PermissionError: if the alphabet has been marked finalised.
        :raises TypeError: if *symbol* is not a string or a Symbol object.
        """
        if self._is_final:
            raise PermissionError('this alphabet is read-only!')

        # Create the symbol object
        if isinstance(symbol, str):
            symbol = Symbol(symbol, name=name, params=param_names, call=cmd)

        if not isinstance(symbol, Symbol):
            raise TypeError(f"expected 'symbol' to be a string or Symbol object got {type(symbol)} instead!")

        self._symbols.add(symbol)
        return symbol

    def drop(self, symbol) -> Symbol:
        """
        Removes the specified symbol from the alphabet.

        :param symbol: if a single character then it is treated as the glyph, otherwise it is treated as the name of the
                       symbol.
        :return: a reference to the dropped symbol.
        :raises TypeError: if *symbol* is not a str object.
        :raises KeyError: if the symbol is not found in the alphabet.
        :raises PermissionError: if the alphabet has been marked finalised.
        """
        if self._is_final:
            raise PermissionError('this alphabet is read-only!')
        if not isinstance(symbol, str):
            raise TypeError(f"expected a 'str' got type {type(symbol)} instead!")

        # Since we don't know both the name and glyph we cannot create an identical Symbol to pass to the underlying set
        # we must search ourselves and remove (suboptimal).
        if len(symbol) > 1:
            for s in self._symbols:
                if symbol == s.name:
                    self._symbols.remove(s)
                    return s
        else:
            for s in self._symbols:
                if symbol == s.glyph:
                    self._symbols.remove(s)
                    return s

        raise KeyError('the given symbol name or glyph was not found!')

    # ------------------------------------------------------------------------------------------------------------------
    # Access and permission

    def get(self, symbol) -> Symbol:
        """
        Retrieves a reference to a symbol in this Alphabet.

        :param str symbol: the glyph of the sybmol if one character; the name of the symbol otherwise.
        :return: a reference to the Symbol
        :raises KeyError: if the symbol is not found.
        :raises TypeError: if *symbol* is not of type 'str'.
        :raises ValueError: if *symbol* is an empty string.
        """
        if isinstance(symbol, str):
            if len(symbol) == 1:
                # Search by glyph
                for s in self._symbols:
                    if s.glyph == symbol:
                        return s
                raise KeyError(f"the glyph '{symbol}' was not found!")
            elif len(symbol) > 1:
                # Search by name
                for s in self._symbols:
                    if s.name == symbol:
                        return s
                raise KeyError(f"the symbol name '{symbol}' was not found!")
            else:
                raise ValueError('an empty string is not acceptable!')

        raise TypeError(f"expected an instance of type 'Symbol' got {type(symbol)} instead!")

    def finalise(self):
        """Marks the alphabet as read-only."""
        self._is_final = True

    @property
    def is_final(self) -> bool:
        """Determine if the alphabet is read-only"""
        return self._is_final


class _SymbolNode:
    """
    An occurrence of a symbol in a LString.
    """

    def __init__(self,
                 symbol: Symbol,
                 left: Optional['_SymbolNode'] = None,
                 right: Optional['_SymbolNode'] = None,
                 params: Optional[dict[str, str]] = None):
        """
        Creates a _SymbolNode in an LString.

        :param symbol: the symbol that this node represents.
        :param left: the immediate sibling to the left of this node.
        :param right: the immediate sibling to the right of this node.
        :param params: the parameters for the symbol instance represented by this node. Ignored if the symbol does
                       not take any parameters.
        :raises KeyError: if *params* does not match the parameters required by *symbol*
        """
        if not isinstance(symbol, Symbol):
            raise TypeError(f"'symbol' must be type Symbol but got {type(symbol)} instead!")
        if left is not None and not isinstance(left, type(self)):
            raise TypeError(f"expected 'left' to be type {type(self)} but got {type(left)} instead!")
        if right is not None and not isinstance(right, type(self)):
            raise TypeError(f"expected 'right' to be type {type(self)} but got {type(right)} instead!")
        if len(symbol.params) > 0:
            if params is None:
                raise KeyError(f"expected {len(symbol.params)} entries in 'params' but got none instead!")
            for param in symbol.params:
                if param not in params:
                    raise KeyError(f"expected parameter named '{param}' was not found in 'params'")
            for param in params:
                if param not in symbol.params:
                    raise KeyError(f"unexpected parameter named '{param}' found in 'params'")
        elif len(symbol.params) == 0:
            params = None

        # TODO: if left or right are specified then ensure that the list references are adjusted.

        # Initialise instance variables.
        self._symbol: Symbol = symbol
        self._left: Optional['_SymbolNode'] = left
        self._right: Optional['_SymbolNode'] = right
        self._params: dict = dict() if params is None else params

    # --------------------------------------------------------------------------------------------------------------
    # Query

    @property
    def symbol(self) -> Symbol:
        """Returns a reference to the symbol that describes this instance."""
        return self._symbol

    @property
    def left(self) -> Optional['_SymbolNode']:
        """Returns the immediate sibling to the left of this node."""
        return self._left

    @left.setter
    def left(self, sibling):
        if isinstance(sibling, _SymbolNode):
            self._left = sibling

        raise TypeError(f"expected an object of type '_SymbolNode' got {type(sibling)} instead!")

    @property
    def right(self) -> Optional['_SymbolNode']:
        """Returns the immediate sibling to the right of this node."""
        return self._right

    @right.setter
    def right(self, sibling):
        if isinstance(sibling, _SymbolNode):
            self._right = sibling

        raise TypeError(f"expected an object of type '_SymbolNode' got {type(sibling)} instead!")

    # --------------------------------------------------------------------------------------------------------------
    # Insertion and deletion

    def add_sibling(self, sibling: '_SymbolNode', where: str = 'right') -> None:
        """
        Inserts a sibling to the left or right of this node.

        :param sibling: the sibling to insert.
        :param where: the direction to insert the sibling.
        """
        if where == 'right':
            if self._right is not None:
                sibling._right = self._right
                self._right._left = sibling

            self._right = sibling
            sibling._left = self
        elif where == 'left':
            if self._left is not None:
                sibling._left = self._left
                self._left._right = sibling

            self._left = sibling
            sibling._right = self
        else:
            raise ValueError(f"expected 'where' to be 'left' or 'right' but got {where} instead!")

    def drop_sibling(self, where: str = 'right') -> bool:
        """
        Removes a sibling node to the immediate left or right of this node.
        :param where: the direction to remove a node from.
        :return: True if a sibling was removed; False otherwise.
        """
        if where == 'right':
            # Nothing to drop
            if self._right is None:
                return False
            # Only one sibling to the right.
            if self._right._right is None:
                self._right = None
                return True
            # More than one sibling to the right.
            self._right._right._left = self
            self._right = self._right._right
            return True

        elif where == 'left':
            # Nothing to drop
            if self._left is None:
                return False
            # Only one sibling to the left.
            if self._left._left is None:
                self._left = None
                return True
            # More than one sibling to the left.
            self._left._left._right = self
            self._left = self._left._left
            return True
        else:
            raise ValueError(f"expected 'where' to be 'left' or 'right' but got {where} instead!")

    # --------------------------------------------------------------------------------------------------------------
    # Parameter access and modification

    def __getitem__(self, parameter):
        """
        Retrieves a parameter value.

        :param parameter: a string identifying the parameter.
        :return: the parameter value
        """
        return self._params[parameter]

    def __setitem__(self, parameter, value) -> None:
        """
        Sets a parameter.

        :param parameter: a string identifying the parameter.
        :param value: the new value of the parameter.
        """
        self._params[parameter] = value


class String:
    """
    The string processed by an LSystem.

    Implemented as a linked list where each node is an occurrence of a symbol and its parameters in the string.
    """

    def __init__(self, alphabet, string=None):
        """
        Initialises a new String object.

        :param Alphabet alphabet: the Alphabet containing the symbols used in the String.
        :param str string: an optional input string to be parsed.
        :raises TypeError: if *alphabet* is not an Alphabet object.
        """
        if not isinstance(alphabet, Alphabet):
            raise TypeError(f"expected 'alphabet' to be an Alphabet object got {type(alphabet)} instead!")
        if string is not None:
            raise NotImplementedError('parsing a string at initialisation not yet supported.')

        self._len: int = 0
        self._alphabet: Alphabet = alphabet
        self._first: Optional[_SymbolNode] = None
        self._last: Optional[_SymbolNode] = None

    @property
    def alphabet(self) -> Alphabet:
        """Returns the Alphabet of this String."""
        return self._alphabet

    def __len__(self) -> int:
        return self._len

    # ------------------------------------------------------------------------------------------------------------------
    # Insertion, removal, and modification

    def insert(self,
               item: 'String | str',
               loc: int,
               params: Optional[dict] = None) -> None:
        """
        Inserts a string at a location.

        :param str item: a 'String' of symbols in the alphabet or a 'str' representing the glyph or name of a symbol in
                         the alphabet. If the str is a single character then it is treated as the glyph of the symbol;
                         otherwise it is treated as the name.
        :param int loc: the position where *item* should be inserted. Negative numbers are referenced from the last
                        symbol in the string backwards.
        :param params: if *item* is a 'str' then these are the arguments captured by the referenced symbol; otherwise it
                       is ignored.
        :raises IndexError: if *loc* is out-of-bounds.
        :raises KeyError: if any inserted symbol is not in the string's alphabet.
        """
        # When loc is positive insert to the left of the node that is there, when negative insert to the right.
        raise NotImplementedError()

    def remove(self, start, stop=None) -> 'String':
        """
        Removes a substring from this string.

        :param int start: the index of the first symbol in the substring to remove.
        :param int stop: if **None** (default) then only one sybmol is removed; otherwise it is the index of the last
                         symbol in the substring to remove + 1.
        :return: a reference to the removed substring.
        :raises IndexError: if any index is out-of-bounds or if stop refers to a symbol before start.
        """
        raise NotImplementedError()

    def append(self, item: 'str | String', params: Optional[dict] = None) -> None:
        """
        Inserts a substring to the end of this string.

        Equivalent to:

        >>> self.insert(item, -1, params)
        :param str item: a 'String' of symbols in the alphabet or a 'str' representing the glyph or name of a symbol in
                         the alphabet. If the str is a single character then it is treated as the glyph of the symbol;
                         otherwise it is treated as the name.
        :param params: if *item* is a 'str' then these are the arguments captured by the referenced symbol; otherwise it
                       is ignored.
        :raises KeyError: if any inserted symbol is not in the string's alphabet.
        """
        self.insert(item, -1, params)

    def prepend(self, item: 'str | String', params: Optional[dict] = None) -> None:
        """
        Inserts a substring to the start of this string.

        Equivalent to:

        >>> self.insert(item, 0, params)
        :param str item: a 'String' of symbols in the alphabet or a 'str' representing the glyph or name of a symbol in
                         the alphabet. If the str is a single character then it is treated as the glyph of the symbol;
                         otherwise it is treated as the name.
        :param params: if *item* is a 'str' then these are the arguments captured by the referenced symbol; otherwise it
                       is ignored.
        :raises KeyError: if any inserted symbol is not in the string's alphabet.
        """
        self.insert(item, 0, params)

    def replace(self, loc: int | slice, item: 'str | String', params: Optional[dict] = None) -> 'String':
        """
        Replaces a substring with a symbol or another string of symbols.

        :param loc: the index or slice representing the symbols to remove.
        :param item: a 'String' of symbols in the alphabet or a 'str' representing the glyph or name of a symbol in
                     the alphabet. If the str is a single character then it is treated as the glyph of the symbol;
                     otherwise it is treated as the name.
        :param params: if *item* is a 'str' then these are the arguments captured by the referenced symbol; otherwise it
                       is ignored.
        :return: a reference to the removed substring.
        :raises IndexError: if *loc* is out-of-bounds.
        :raises KeyError: if *item* contains any symbols not in the alphabet.
        """
        raise NotImplementedError()

    def __setitem__(self, loc: int | slice, substring: 'String') -> 'String':
        """
        Replaces a substring with another substring or inserts a substring.

        :param loc: if an integer then the position to insert *substring*; if a slice then it identifies the substring
                    to replace.
        :param substring: the string of symbol instances to be inserted.
        :return: a reference to *substring*.
        """
        # Support slicing.
        raise NotImplementedError()

    # ------------------------------------------------------------------------------------------------------------------
    # Substring/parameter access

    def setparams(self, loc: int, params: dict) -> None:
        """
        Sets the parameters for a symbol at a location in the string.

        :param loc: the integer position of the symbol instance in the string. Negative numbers are referenced from the
                    end of the string backwards.
        :param params: the new parameter values.
        :raises IndexError: if *loc* is out-of-bounds.
        """
        raise NotImplementedError()

    def getparams(self, loc: int) -> Optional[dict]:
        """
        Retrieves the parameter values of a symbol instance at a location in the string.

        :param loc: the integer position of the symbol instance in the string. Negative numbers are referenced from the
                    end of the string backwards.
        :return: the parameter values for the symbol instance.
        :raises IndexError: if *loc* is out-of-bounds.
        """
        raise NotImplementedError()

    def symbol_at(self, loc: int) -> Symbol:
        """
        Retrieves the symbol specification for the instance at a location in the string.

        :param loc: the integer position of the symbol instance in the string. Negative numbers are referenced from the
                    end of the string backwards.
        :return: the symbol specification for the instance.
        :raises IndexError: if *loc* is out-of-bounds.
        """
        raise NotImplementedError()

    def __getitem__(self, loc: tuple[int, str] | slice) -> 'String | str':
        """
        Retrieves a substring or a parameter for a single symbol instance.

        :param loc: when a slice then it locates a substring to retrieve; when a tuple, the first item is the location
                    of a symbol instance and the second item is the name of a parameter to retrieve.
        :return: a substring or parameter value.
        """
        raise NotImplementedError()

    def substring(self, loc: int | slice) -> 'String':
        """
        Retrieves a reference to a String containing a contiguous subset of the symbol instances in this String.

        :param loc: the index or slice representing the start and ending locations of the substring.
        :return: the substring.
        :raises IndexError: if *loc* is out-of-bounds.
        """
        raise NotImplementedError()

    # ------------------------------------------------------------------------------------------------------------------
    # str conversion

    def __repr__(self):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    def parse(self, input):
        raise NotImplementedError()

    # ------------------------------------------------------------------------------------------------------------------
    # Iteration

    def __iter__(self):
        raise NotImplementedError()


class RuleResult:
    def __init__(self, symbol, status, replacement):
        raise NotImplementedError()


# TODO: a production rule handler is given a reference to the string. Remove the pre and post parameters, the handler
#   can act on the entire string. It also allows the handler to do global processing. One limitation is that this global
#   view is of the previous iteration. The current iteration is rewritten in post processing.

# Handler is given a reference to the string being iterated on, which is only replaced after all rules have finished
# processing, and the index of its subject. It returns a RuleResult object indicating if the rule was applied and a
# replacement string for the subject.
class Rule:
    """
    A rewrite rule that describe how instances of symbols are replaced with other instances of symbols from the same
    alphabet.
    """

    def __init__(self, subject, handler, name=None):
        """
        Create a new production rule.

        :param str name: the name of the rule
        :param Callable[..., Any] handler: the callable that will handle the rule.
        """
        if name is not None and not isinstance(name, str):
            raise TypeError(f"expected 'name' to be a string but got a {type(name)} instead!")
        if not callable(handler):
            raise TypeError("'handler' must be a callable.")

        self._name = handler.__name__ if name is None else name
        self._handler = handler

    @property
    def name(self) -> str:
        """Returns the name of the rule."""
        return self._name

    @property
    def handler(self) -> Callable[..., Any]:
        """Returns the handler for the rule."""
        return self._handler

    def __call__(self, string, idx):
        return self._handler(string, idx)


# TODO: rename to Alphabet??
class LSystem:
    """
    An implementation of a Lindenmayer system consisting of an alphabet, rewriting rules, and an initial axiom.
    """

    def __init__(self):
        self._symbols: set = set()
        # TODO: rules for a symbol are ordered. Keep track of how many p and none p's for each symbol to decide whether
        #  ordered or stochastic.
        self._rules: dict = dict()
        self._tree: Any = None

    # ------------------------------------------------------------------------------------------------------------------
    # Inserting/Deleting

    def add_symbol(self, glyph, params, cmd, name) -> Symbol:
        """
        Adds a distinct symbol to the alphabet.

        Rules can then be added that target the symbol for rewriting.

        Commands
        --------

        The :func:`execute` function will call the command function whenever an occurrence of the symbol is encountered
        in the final output string.

        :param glyph: the unique character that represents the symbol.
        :param params: a sequence containing the names of the parameters required by the symbol.
        :param cmd: an optional callable that executes the command associated with the symbol.
        :param name: an optional name to identify the symbol (default: *glyph*)
        :returns: a reference to the newly added symbol.
        :raises KeyError: if the name or glyph is in use by another symbol in the alphabet.
        """
        raise NotImplementedError()

    def drop_symbol(self, *, glyph, name):
        """
        Removes a symbol from the alphabet.

        Either the symbol name or glyph can be used for identification but if a glyph is specified then *name* is
        ignored.

        :param glyph: the glyph of the symbol to be removed.
        :param name: the name of the symbol to be removed.
        :raises KeyError: if the symbol is not found in the alphabet.
        """
        raise NotImplementedError()

    def add_rule(self, symbol, handler, pre, post, name, p) -> Rule:
        """
        Adds a production rule to the ruleset. The rule is added to the back of the queue for the subject symbol.

        On each iteration, only one rule is applied for each symbol. Rules are either attempted in the order they were
        added until the first successful application, or they are chosen randomly for stochastic systems. If every rule
        has an associated probability weighting then the selection process is stochastic.

        Handler
        ------

        The *handler* callable accepts the subject module, a sequence of modules preceding and succeeding the subject,
        and the name of the rule. It returns an object that signals whether the rule was applied, and if so, the
        replacement modules.

        :param symbol: the subject of the rule
        :param handler: the callable that will handle rule conditions, signalling, and execution.
        :param pre: the number of symbols immediately to the left of the subject that will be captured.
        :param post: the number of symbols immediately to the right of the subject that will be captured.
        :param name: the identifier of the rule.
        :param p: the probability weighting for the rule.
        :return: a reference to the newly added rule.
        :raises KeyError: if the symbol does not exist in the alphabet.
        """
        raise NotImplementedError()

    def drop_rule(self, name) -> None:
        """
        Removes a rule from the ruleset.

        :param name: the name of the rule.
        :raises KeyError: if the rule is not in the ruleset.
        """
        raise NotImplementedError()

    def update_rule_probability(self, name, p) -> None:
        """
        Updates the probability weighting of a rule.

        :param name: the name of the rule.
        :param p: the new probability weighting, if None then the weighting is removed from the rule.
        :raises KeyError: if the rule name is not found in the ruleset.
        """
        raise NotImplementedError()

    def add_post_processing(self, func):
        # Called after every iteration with the iteration number and the module tree.
        raise NotImplementedError()

    # ------------------------------------------------------------------------------------------------------------------
    # Membership and Searching

    def __contains__(self, key) -> bool:
        """
        Determines if a symbol or rule is in the lindenmayer system.
        :param key: a symbol object, rule object, or the name of either.
        :return: True if the symbol or rule is in the system; False otherwise.
        """
        raise NotImplementedError()

    @property
    def alphabet(self):
        """Returns the set of symbols in the alphabet."""
        raise NotImplementedError()

    @property
    def rules(self):
        """Returns the set of rules in the alphabet."""
        raise NotImplementedError()

    @property
    def variables(self):
        """Returns the set of symbols in the alphabet that have rules defined for them."""
        raise NotImplementedError()

    @property
    def constants(self):
        """Returns the set of symbols in the alphabet that do not have any rules defined for them."""
        raise NotImplementedError()

    def get_symbol(self, glyph, *, name=None, suppress=False) -> Optional[Symbol]:
        """
        Returns a reference to the symbol.

        :param glyph: the symbol's glyph.
        :param name: the symbol identifier. Used when *glyph* is **None**.
        :param suppress: suppresses KeyErrors when True (default: False).
        :return: a reference to the symbol if found; **None** if the symbol is not found and *suppress* is True.
        :raises KeyError: if the symbol is not found in the alphabet and *suppress* is False.
        """
        raise NotImplementedError()

    def get_rule(self, name, suppress=False) -> Optional[Rule]:
        """
        Returns a reference to the rule.

        :param name: the identifier of the rule.
        :param suppress: suppresses KeyErrors when True (default: False).
        :return: a reference to the rule if found; **None** if the rule is not found and *suppress* is True.
        :raises KeyError: if the rule is not found in the ruleset and *suppress* is False.
        """
        raise NotImplementedError()

    def get_rules_for(self, glyph, *, name=None, suppress=False) -> Any:
        """
        Returns an ordered set of rules for the specified symbol.

        :param glyph: the glyph representing the symbol.
        :param name: the symbol identifier. Used when *glyph* is **None**.
        :param suppress: suppresses KeyErrors when True (default: False).
        :return: an ordered set of rules for the symbol.
        :raises KeyError: if the symbol is not found in the alphabet and *suppress* is False.
        """
        raise NotImplementedError()

    # ------------------------------------------------------------------------------------------------------------------
    # Execution

    def iterate(self, axiom=None, iters=100) -> bool:
        """
        Recursively applies the ruleset to the module string.

        :param axiom: the starting module string to iterate on; if None then continue using the current string.
        :param iters: the maximum number of iterations.
        :return: True if no more iterations are possible; False otherwise.
        """
        raise NotImplementedError()

    def execute(self) -> None:
        """
        Executes the commands associated with each symbol as encountered in the current module string.
        """
        raise NotImplementedError()

    # ------------------------------------------------------------------------------------------------------------------
    # Printing/Representation

    def __repr__(self):
        raise NotImplementedError()

    @property
    def string(self):
        """
        Returns the current module string.
        :return: the current module string.
        """
        raise NotImplementedError()
