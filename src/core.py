#  ---------------------------------------------------------------------------------------------------------------------
#  core.py
#  Copyright (c) 2024. Jermaine Clarke
#  All rights reserved.
#  ---------------------------------------------------------------------------------------------------------------------
from typing import Any, Generator, Iterable, Optional, Sequence
from collections.abc import Callable

ParamTuple = tuple[str, ...]
"""A tuple of names for the parameters accepted by a Symbol"""
CommandCallable = Callable[..., Any]
"""A callable that implements the command represented by a Symbol"""
RuleCallable = Callable[..., Any]
"""A callable that checks for the conditions of a production rule and returns substitutions."""

SymbolProc = Callable[['symbol', dict], Any]
"""
The function signature for a symbol procedure. It is passed a reference to the symbol and a dictionary of arguments 
for a specific occurence of the symbol in a string.
"""
ListLike = tuple | list
ArgSpec = dict[str, type]


class Symbol:
    """
    A symbol is a glyph that represents a command or action in a Lindenmayer string, which is a sequence of symbols.
    """
    __slots__ = '_glyph', '_name', '_arg_spec', '_proc', '_regex'

    def __init__(self, glyph: str, name: str, args: ListLike=tuple(), argtypes: ListLike=tuple(),
                 proc: Optional[SymbolProc]=None):
        """
        Creates a new symbol.

        :param glyph: the single character that visual represents the symbol in a string.
        :param name: the name of the symbol that can be used to identify it.
        :param args: a list-like containing the names of all arguments required by each occurrence of the symbol in a
                     string.
        :param argtypes: a list-like containing the types of all arguments required by each occurrence of the symbol in
                         a string. Must be the same length and order as *args* if provided.
        :param proc: an optional callable that is invoked on each occurence of the symbol in the final
                     string.
        """
        assert isinstance(glyph, str), f"'glyph' is expected to be a string but type {type(glyph)} was passed."
        assert isinstance(name, str), f"'name' is expected to be a string but type {type(name)} was passed."
        assert len(glyph) == 1, f"expected a single character for 'glyph' but got {len(glyph)} characters."

        args = tuple(args)
        argtypes = tuple(argtypes)

        for arg in args:
            assert isinstance(arg, str), "elements in 'args' must be strings."
        for atype in argtypes:
            assert atype in (int, float, str), "elements in 'argtypes' must be one of (int, float, str) specifiers."

        self._glyph: str = glyph
        self._name: str = name
        self._arg_spec: ArgSpec = dict(zip(args, argtypes))
        self._proc: SymbolProc = proc
        self._regex: Optional[str] = None

        pass

    @property
    def glyph(self) -> str:
        """
        Returns the character that visually represents this symbol in a string.
        """
        return self._glyph

    @property
    def name(self) -> str:
        """
        Returns the name of this symbol.
        """
        return self._name

    @property
    def arglen(self) -> int:
        """Return the number of arguments required by each occurence of this symbol."""
        return len(self._arg_spec)

    @property
    def argnames(self) -> tuple[str, ...]:
        """Returns a tuple containing the names of all the required arguments of this symbol."""
        return tuple(self._arg_spec)

    @property
    def argtypes(self) -> tuple[type, ...]:
        """Returns a tuple containing the types of all the required arguments of this symbol."""
        return tuple(self._arg_spec.values())

    @property
    def argspec(self) -> dict[str, type]:
        """Returns a dictionary containing argument names as keys and argument types as values."""
        return dict(self._arg_spec)

    @property
    def proc(self) -> SymbolProc:
        """
        Returns a reference to the procedure attached to this symbol. This procedure is called every time this symbol
        is encountered in the final string.
        """
        return self._proc

    @property
    def regex(self) -> str:
        """
        Returns the regular expression that can be used to find occurences of this symbol in a 'str'.
        """
        if self._regex is None:
            whitespace = r'\s'
            alphanumeric = r'\w'
            open_parenthesis = r'\('
            closing_parenthesis = r'\)'

            # Add expressions for each argument
            res = ''
            for arg in self._arg_spec.keys():
                res += f'{whitespace}*(?P<{arg}>{alphanumeric}+),'

            # Remove the comma after the last argument and add brackets
            if len(res) > 0:
                res = f'{open_parenthesis}{res[:-1]}{closing_parenthesis}'

            self._regex = f'^{self.glyph}{res}'

        return self._regex

    def __hash__(self) -> int:
        """Returns the has of this symbol."""
        return hash(self._glyph)

    def __call__(self, *args, **kwargs):
        # TODO: implement
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        """Returns True if *other* is equal to this symbol. Two symbols are equal if they have the same glyph."""
        if isinstance(other, Symbol) and other._glyph == self._glyph:
            return True

        return False

    def __ne__(self, other):
        """
        Returns True if *other* is not equal to this symbol. Two symbols are not equal if they have distinct glyphs.
        """
        return not self.__eq__(other)

    def __repr__(self):
        return f'symbol[name=\'{self._name}\', glyph=\'{self._glyph}\', params={self.argnames}]'

    def __str__(self):
        return f"{self._glyph}{self.argnames}".replace(',)',')').replace('()','')

    def __getitem__(self, key) -> type:
        """
        Retrieves the type specification for an argument.
        :param key: the argument name.
        :return: the type specification for the argument.
        """
        return self._arg_spec.__getitem__(key)

class Alphabet:
    """
    A set of symbols that can be combined to form Lindenmayer strings.
    """

    def __init__(self, symbols: list[Symbol] | tuple[Symbol] | None = None):
        sym = set()

        if symbols is not None:
            for s in symbols:
                assert isinstance(s, Symbol), f"elements in 'symbols' must be of type {Symbol.__name__}."
                sym.add(s)

        self._symbols: set[Symbol] = sym

    # ------------------------------------------------------------------------------------------------------------------
    # Membership and iteration

    def __contains__(self, item: Symbol | str) -> bool:
        """
        Test a symbol for membership in this alphabet.

        :param item: a symbol, character, or symbol name to test.
        :return: True if *symbol* is a member of this alphabet; False otherwise.
        :raises TypeError: if *symbol* is not an instance of class ``Symbol``.
        :raises ValueError: if *symbol* is an empty string.
        """
        assert isinstance(item, (str, Symbol)), f"expected 'item' to be a string or a symbol but got {type(item)} instead."

        if isinstance(item, Symbol):
            return item in self._symbols
        elif isinstance(item, str):
            if len(item) == 1:
                # Search by glyph
                for s in self._symbols:
                    if s.glyph == item:
                        return True
                return False
            elif len(item) > 1:
                # Search by name
                for s in self._symbols:
                    if s.name == item:
                        return True
                return False
            else:
                raise ValueError('an empty string is not acceptable!')

        raise TypeError(f"expected an instance of type 'Symbol' got {type(Symbol)} instead!")

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

    def add(self,
            symbol: Symbol | str, /,
            arg_spec: ArgSpec = None,
            proc: SymbolProc = None,
            name: Optional[str] = None) -> Symbol:
        """
        Adds a distinct symbol to the alphabet.

        :param symbol: a Symbol object or a character representing the glyph of the symbol. All other parameters are
                       ignored if a Symbol object is given.
        :param arg_spec: a dictionary of (name, type) pairs specifying symbol arguments and their types.
        :param proc: an optional callable that executes the command associated with the symbol.
        :param name: an optional friendly name to identify the symbol (default: *glyph*)
        :return: a reference to the newly added symbol.
        :raises KeyError: if the name or glyph is in use by another symbol in the alphabet.
        :raises PermissionError: if the alphabet has been marked finalised.
        """
        assert isinstance(symbol, (str, Symbol)), f"expected 'symbol' to be a string or a symbol but got type {type(symbol)} instead."

        # Create the symbol object
        if isinstance(symbol, str):
            if name is None:
                name = symbol

            if arg_spec is None:
                symbol = Symbol(symbol, name, proc=proc)
            else:
                symbol = Symbol(symbol, name, tuple(arg_spec.keys()), tuple(arg_spec.values()), proc)

        self._symbols.add(symbol)
        return symbol

    def drop(self, symbol: str) -> Symbol:
        """
        Removes the specified symbol from the alphabet.

        :param symbol: if a single character then it is treated as the glyph, otherwise it is treated as the name of the
                       symbol.
        :return: a reference to the dropped symbol.
        :raises TypeError: if *symbol* is not a str object.
        :raises KeyError: if the symbol is not found in the alphabet.
        """
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

    def get(self, symbol: str) -> Symbol:
        """
        Retrieves a reference to a symbol in this Alphabet.

        :param symbol: the glyph of the symbol if one character; the name of the symbol otherwise.
        :return: a reference to the Symbol
        :raises KeyError: if the symbol is not found.
        :raises TypeError: if *symbol* is not of type 'str'.
        :raises ValueError: if *symbol* is an empty string.
        """
        assert isinstance(symbol, str), f"expected 'symbol' to be a string but got type {type(symbol)} instead."

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

class _character_node:
    __slots__ = '_symbol', '_args', '_left', '_right'

    def __init__(self,
                 symbol: Symbol,
                 args: Optional[dict] = None,
                 left: 'Optional[_character_node]' = None,
                 right: 'Optional[_character_node]' = None):
        assert isinstance(symbol, Symbol), f"expected 'symbol' to be a Symbol object got type {type(symbol)} instead."

        # Validate arguments.
        if symbol.arglen > 0:
            assert isinstance(args, dict), f"expected a dictionary"

            # Check the types.
            for arg, argtype in symbol.argspec.items():
                if not isinstance(args[arg], argtype):
                    raise TypeError(f"expected argument '{arg}' to be type '{argtype}' got {type(args[arg])} instead!")

            # Check that args does not have extra arguments.
            if len(args) != symbol.arglen:
                raise KeyError(f"expected {symbol.arglen} arguments but 'args' has {len(args)}!")

        assert left is None or isinstance(left, _character_node), f"expected {type(self)} for 'left' but got {type(left)}!"
        assert right is None or isinstance(right, _character_node), f"expected {type(self)} for 'right' but got {type(right)}!"

        self._symbol: Symbol = symbol
        self._args: dict = dict() if args is None else dict(args)
        self._left: 'Optional[_character_node]' = left
        self._right: 'Optional[_character_node]' = right

    def clone(self) -> '_character_node':
        """
        Return a clone of this character node. Does not copy siblings.
        :return: a character node.
        """
        return _character_node(self._symbol, self._args)
    
    @property
    def symbol(self) -> Symbol:
        """Returns a reference to the symbol that this node represents."""
        return self._symbol
    
    @property
    def args(self) -> dict:
        """Returns a dictionary of argument-value pairs."""
        return dict(self._args)

    @property
    def right(self) -> 'Optional[_character_node]':
        """Returns the node to the right of this in a string."""
        return self._right

    @right.setter
    def right(self, value):
        raise NotImplementedError

    @property
    def left(self) -> 'Optional[_character_node]':
        """Returns the node to the left of this in a string."""
        return self._left

    @left.setter
    def left(self, value):
        raise NotImplementedError
    
    def __getitem__(self, arg) -> Any:
        """Returns the value of the specified argument."""
        return self._symbol[arg](self._args[arg])
    
    def __setitem__(self, arg, value):
        """Sets the value of the specified argument."""
        self._args[arg] = self._symbol[arg](value)
    
    def __eq__(self, other):
        """Returns True if *other* represents the same symbol and has the same argument values."""
        return isinstance(other, type(self)) and self._symbol == other._symbol and self._args == other._args
    
    def __ne__(self, other):
        """Returns True if *other* represents a different symbol or has different argument values."""
        return not self.__eq__(other)
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return self._symbol.glyph if self._symbol.arglen == 0 \
            else f"{self._symbol.glyph}{tuple(self._args.values())}".replace(',)', ')')

    def __call__(self):
        raise NotImplementedError

class string:
    __slots__ = '_alphabet', '_first', '_last', '_length'
    pass

class rule:
    pass

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
    def params(self) -> dict:
        """Returns a reference to the dictionary containing the parameter names as key and their values."""
        return self._params

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

    def clone(self) -> '_SymbolNode':
        """Returns a copy of this node."""
        return _SymbolNode(self._symbol, left=self._left, right=self._right, params=self._params.copy())


class String:
    """
    The string processed by an LSystem.

    Implemented as a linked list where each node is an occurrence of a symbol and its parameters in the string.
    """

    def __init__(self, string: 'Optional[str | String]' = None, alphabet: Optional[Alphabet] = None,
                 copy: Optional[bool] = None):
        """
        Initialises a new String object.

        :param string: an optional String or built-in string (will be parsed). If *None* then an empty object is
                       created.
        :param alphabet: the Alphabet containing the symbols used in the String. Must be specified for empty String
                         objects or when *string* is a built-in string. When *string* is a String object then the
                         alphabet is inherited.
        :param copy: when *False* shares the underlying data with the input string where possible; when *True* this
                     string will own its data; when *None* it will share data where possible and create a copy when
                     attempts are made to edit the string.
        :raises TypeError: if *alphabet* is not an Alphabet object.
        """
        if not isinstance(copy, bool) and copy is not None:
            raise TypeError(f"attempted to input a {type(copy)} instead of a bool for 'copy'!")
        if isinstance(string, str):
            if not isinstance(alphabet, Alphabet):
                raise TypeError(f"expected 'alphabet' to be an Alphabet object got {type(alphabet)} instead!")
            # TODO: parse
            raise NotImplementedError
        if isinstance(string, String):
            if string._len == 0:
                self._first = None
                self._last = None
                self._len = 0
                self._alphabet = string._alphabet
                self._is_owner = True
                self._copy_on_write = False
            elif copy is None:
                self._first = string._first
                self._last = string._last
                self._len = string._len
                self._alphabet = string._alphabet
                self._is_owner = False
                self._copy_on_write = True
            elif copy:
                nd = string._first
                self._first = _SymbolNode(nd.symbol, params=nd.params)
                self._last = self._first
                for i in range(string._len - 1):
                    nd = nd.right
                    self._last.right = _SymbolNode(nd.symbol, params=nd.params)
                    self._last = self._last.right
                self._len = string._len
                self._alphabet = string._alphabet
                self._is_owner = True
                self._copy_on_write = False
            else:
                self._first = string._first
                self._last = string._last
                self._len = string._len
                self._alphabet = string._alphabet
                self._is_owner = False
                self._copy_on_write = False

        self._first: Optional[_SymbolNode] = None
        self._last: Optional[_SymbolNode] = None
        self._len: int = 0
        self._alphabet: Alphabet = alphabet
        self._is_owner: bool = True
        self._copy_on_write: bool = False

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
        Inserts a string at a location. The operation is destructive for the inserted string.

        :param str item: a 'String' of symbols in the alphabet or a 'str' representing the glyph or name of a symbol in
                         the alphabet. If the str is a single character then it is treated as the glyph of the symbol;
                         otherwise it is treated as the name.
        :param int loc: the position where *item* should be inserted. Insertion happens to the left of the node at the
                        location for positive numbers. Negative numbers are referenced from the last symbol in the
                        string backwards and insertion occurs to the right.
        :param params: if *item* is a 'str' then these are the arguments captured by the referenced symbol; otherwise it
                       is ignored.
        :raises IndexError: if *loc* is out-of-bounds.
        :raises KeyError: if any inserted symbol is not in the string's alphabet.
        :raises TypeError: if *item* is not an expected type.
        """
        if not isinstance(loc, int):
            raise TypeError(f"expected 'loc' to be an int object got {type(loc)} instead!")
        if (self._len == 0 and loc not in (0, -1)) or not -self._len <= loc < self._len:
            raise IndexError("'loc' is out-of-bounds!")

        if isinstance(item, str):
            new_node = _SymbolNode(self.alphabet.get(item), params=params)

            if new_node not in self.alphabet:
                raise KeyError("attempted to insert a symbol that is not in this string's alphabet!")

            if loc == 0:
                new_node.right = self._first
                self._first = new_node
                if self._len == 0:
                    self._last = new_node
                self._len += 1
            elif loc > 0:
                nd = self._first
                for i in range(loc):
                    nd = nd.right

                new_node.right = nd
                new_node.left = nd.left
                if nd.left is not None:
                    nd.left.right = new_node
                nd.left = new_node
                self._len += 1
            else:
                nd = self._last
                for i in range(-loc - 1):
                    nd = nd.left

                new_node.left = nd
                new_node.right = nd.right
                if nd.right is not None:
                    nd.right.left = new_node
                nd.right = new_node
                if self._last == nd:
                    self._last = new_node
                self._len += 1

        elif isinstance(item, String):
            if item.alphabet <= self.alphabet:
                if loc >= 0:
                    pass
                else:
                    pass
            else:
                raise KeyError("one or more symbols are not in this string's alphabet!")
        else:
            raise TypeError(f"expected 'item' to be a String or str object got {type(item)} instead!")

    def remove(self, start, stop=None) -> 'String':
        """
        Removes a substring from this string.

        :param int start: the index of the first symbol in the substring to remove.
        :param int stop: if **None** (default) then only one symbol is removed; otherwise it is the index of the last
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
        return _StringIterator(self._first, self._last)


class _StringIterator:
    def __init__(self, start: _SymbolNode, stop: _SymbolNode):
        self._next = start
        self._last = stop

    def __next__(self) -> _SymbolNode:
        if self._next is None:
            raise StopIteration

        res = self._next
        self._next = res.right if res.right is not self._last else None
        return res


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
