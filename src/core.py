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
RuleCallable = Callable[..., Any]
"""A callable that checks for the conditions of a production rule and returns substitutions."""

class ProductionRule:
    """
    A rewrite rule that describe how instances of symbols are replaced with other instances of symbols from the same
    alphabet.
    """
    def __init__(self, handler, pre = 0, post = 0, name = None):
        """
        Create a new production rule.

        :param str name: the name of the rule
        :param int pre: the number of symbols to the left of the subject that are captured.
        :param int post: the number of symbols to the right of the subject that are captured.
        :param Callable[..., Any] handler: the callable that will handle the rule.
        """
        if name is not None and not isinstance(name, str):
            raise TypeError(f"expected 'name' to be a string but got a {type(name)} instead!")

        pre = int(pre)
        post = int(post)
        if pre < 0:
            raise ValueError(f"'pre' should be a positive integer, but got {pre} instead!")
        if post < 0:
            raise ValueError(f"'post' should be a positive integer, but got {post} instead!")
        if not callable(handler):
            raise TypeError("'handler' must be a callable.")

        self._name = handler.__name__ if name is None else name
        self._pre_capture = pre
        self._post_capture = post
        self._handler = handler


    @property
    def name(self) -> str:
        """Returns the name of the rule."""
        return self._name

    @property
    def pre(self) -> int:
        """Returns the number of symbols to the left of the subject that are captured."""
        return self._pre_capture

    @property
    def post(self) -> int:
        """Returns the number of symbols to the right of the subject that are captured."""
        return self._post_capture

    @property
    def handler(self) -> Callable[..., Any]:
        """Returns the handler for the rule."""
        return self._handler

    def __call__(self, *args, **kwargs):
        return self._handler(args, kwargs)

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


# TODO: the module string is implemented as a module tree that can be flattened into a string object.

class ModuleTree:
    """
    A Tree representation of the string processed by a Lindenmayer system.

    A ModuleTree may be parsed from a string or flattened into a string.
    """
    class _Module:
        """
        A node in a ModuleTree
        """
        def __init__(self,
                     symbol: Symbol,
                     parent: Optional['ModuleTree._Module'] = None,
                     left: Optional['ModuleTree._Module'] = None,
                     right: Optional['ModuleTree._Module'] = None,
                     params: Optional[dict[str, str]] = None):
            """
            Creates a node in a ModuleTree

            :param symbol: the symbol that this node represents.
            :param parent: the optional parent of this node.
            :param left: the immediate sibling to the left of this node.
            :param right: the immediate sibling to the right of this node.
            :param params: the parameters for the symbol instance represented by this node. Ignored if the symbol does
                           not take any parameters.
            :raises KeyError: if *params* does not match the parameters required by *symbol*
            """
            if not isinstance(symbol, Symbol):
                raise TypeError(f"'symbol' must be type Symbol but got {type(symbol)} instead!")
            if parent is not None and not isinstance(parent, type(self)):
                raise TypeError(f"expected 'parent' to be type {type(self)} but got {type(parent)} instead!")
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


            # Initialise instance variables.
            self._symbol: Symbol = symbol
            self._parent: Optional['ModuleTree._Module'] = parent
            self._child: Optional['ModuleTree._Module'] = None
            self._level: int = 0 if parent is None else parent._level + 1
            self._left: Optional['ModuleTree._Module'] = left
            self._right: Optional['ModuleTree._Module'] = right
            self._params: dict = dict() if params is None else params


        # --------------------------------------------------------------------------------------------------------------
        # Query

        @property
        def symbol(self) -> Symbol:
            """Returns a reference to the symbol that describes this instance."""
            return self._symbol

        @property
        def parent(self) -> Optional['ModuleTree._Module']:
            """Returns a reference to the parent node if any."""
            return self._parent

        @property
        def level(self) -> int:
            """Returns the depth of this node in the tree. The root node is 0."""
            return self._level

        @property
        def left(self) -> Optional['ModuleTree._Module']:
            """Returns the immediate sibling to the left of this node."""
            return self._left

        @property
        def right(self) -> Optional['ModuleTree._Module']:
            """Returns the immediate sibling to the right of this node."""
            return self._right

        @property
        def child(self) -> Optional['ModuleTree._Module']:
            """Returns the leftmost child of this node."""
            return self._child

        # --------------------------------------------------------------------------------------------------------------
        # Insertion and deletion

        def add_sibling(self, sibling: 'ModuleTree._Module', where: str = 'right') -> None:
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

                # If I was the leftmost child pre-call
                if getattr(self._parent, '_child', None) == self:
                    self._parent._child = sibling
            else:
                raise ValueError(f"expected 'where' to be 'left' or 'right' but got {where} instead!")

            sibling._level = self._level
            sibling._parent = self._parent

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
                    # Update parent if we dropped the leftmost sibling.
                    if getattr(self._parent, '_child', None) == self._left: # could be if self._parent is not None:
                        self._parent._child = self

                    self._left = None
                    return True
                # More than one sibling to the left.
                self._left._left._right = self
                self._left = self._left._left
                return True
            else:
                raise ValueError(f"expected 'where' to be 'left' or 'right' but got {where} instead!")

        def add_child(self, child: 'ModuleTree._Module') -> None:
            """
            Inserts a child node to the left of all previous child nodes.

            :param child: the child node to insert.
            """
            if not isinstance(child, self):
                raise TypeError(f"expected 'child' to be type: {type(self)} but got type: {type(child)} instead!")

            if self._child is not None:
                self._child.add_sibling(child, 'left')
            else:
                self._child = child

        def drop_child(self):
            pass

        def drop_children(self):
            pass


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

    def add_rule(self, symbol, handler, pre, post, name, p) -> ProductionRule:
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

    def get_rule(self, name, suppress=False) -> Optional[ProductionRule]:
        """
        Returns a reference to the rule.

        :param name: the identifier of the rule.
        :param suppress: suppresses KeyErrors when True (default: False).
        :return: a reference to the rule if found; **None** if the rule is not found and *suppress* is True.
        :raises KeyError: if the rule is not found in the ruleset and *suppress* is False.
        """
        raise NotImplementedError()

    def get_rules_for(self, glyph, *, name = None, suppress = False) -> Any:
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

    def iterate(self, axiom = None, iters=100) -> bool:
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
