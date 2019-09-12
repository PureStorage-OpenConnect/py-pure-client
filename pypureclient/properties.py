from .exceptions import PureError


class Property(object):
    """
    A Property object models a property of a resource and allows for easy
    compounding, sorting, and filtering with them. It is converted to a string
    when calling any API and can also be replaced by a string.
    """

    def __init__(self, value):
        """
        Initialize a Property.

        Args:
            value (str): The name of the property.
        """
        self.value = value

    def all(self):
        """
        Create a list Property indexed by "all".

        Returns:
            Property
        """
        return Property('{}[all]'.format(self.value))

    def any(self):
        """
        Create a list Property indexed by "any".

        Returns:
            Property
        """
        return Property('{}[any]'.format(self.value))

    def subproperty(self, other):
        """
        Create a subproperty.

        Args:
            other (Property): The Property to be the subproperty of the given
                Property.

        Returns:
            Property

        Raises:
            PureError: If other is not of the proper type.
        """
        if not isinstance(other, Property):
            raise PureError('Subproperty is not of type Property')
        return Property('{}.{}'.format(self.value, other.value))

    def ascending(self):
        """
        Create a Property that can be sorted in ascending order.

        Returns:
            Property
        """
        return self

    def descending(self):
        """
        Create a property that can be sorted in descending order.

        Returns:
            Property
        """
        return Property('{}-'.format(self.value))

    def exists(self):
        """
        Create a Filter that checks for existance of the given Property.

        Returns:
            Filter
        """
        return Filter.exists(self)

    def __add__(self, other):
        """
        The + operator. Create a subproperty.

        Args:
            other (Property): The Property to be the subproperty of the given
                Property.

        Returns:
            Property

        Raises:
            PureError: If other is not of the proper type.
        """
        return self.subproperty(other)

    def __eq__(self, other):
        """
        The == operator. Create a Filter that checks for equality.

        Args:
            other (str, int, bool): The value to compare to.

        Returns:
            Filter

        Raises:
            PureError: If other is not of the proper type.
        """
        return Filter.eq(self, other)

    def __ge__(self, other):
        """
        The >= operator. Create a Filter that checks for greater than or equal.

        Args:
            other (str, int): The value to compare to.

        Returns:
            Filter

        Raises:
            PureError: If other is not of the proper type.
        """
        return Filter.ge(self, other)

    def __gt__(self, other):
        """
        The > operator. Create a Filter that checks for greater than.

        Args:
            other (str, int): The value to compare to.

        Returns:
            Filter

        Raises:
            PureError: If other is not of the proper type.
        """
        return Filter.gt(self, other)

    def __le__(self, other):
        """
        The <= operator. Create a Filter that checks for less than or equal.

        Args:
            other (str, int): The value to compare to.

        Returns:
            Filter

        Raises:
            PureError: If other is not of the proper type.
        """
        return Filter.le(self, other)

    def __lt__(self, other):
        """
        The < operator. Create a Filter that checks for less than.

        Args:
            other (str, int): The value to compare to.

        Returns:
            Filter

        Raises:
            PureError: If other is not of the proper type.
        """
        return Filter.lt(self, other)

    def __ne__(self, other):
        """
        The != operator. Create a Filter that checks for inequality.

        Args:
            other (str, int, bool): The value to compare to.

        Returns:
            Filter

        Raises:
            PureError: If other is not of the proper type.
        """
        return Filter.ne(self, other)

    def __getitem__(self, index):
        """
        The [] operator. Create a list Property with the given index.

        Args:
            index (str): The list index to use.

        Returns:
            Property

        Raises:
            PureError: If index is not "all" or "any".
        """
        if index not in ['any', 'all']:
            raise PureError('Invalid Property index')
        return self.any() if index == 'any' else self.all()

    def __repr__(self):
        """
        Return the string value of the Property.

        Returns:
            str
        """
        return self.value


class Filter(object):
    """
    A Filter object models a filter string by keeping track of operations
    between Properties, values, and other Filters. It is converted to a string
    when calling any API and can also be replaced by a string.
    """

    class _Operation(object):
        """
        A class used to track possible Filter operations.
        """
        and_ = 'and'
        contains = 'contains'
        eq = '='
        exists = 'exists'
        ge = '>='
        gt = '>'
        in_ = '='
        le = '<='
        lt = '<'
        ne = '!='
        not_ = 'not'
        or_ = 'or'
        tags = 'tags'

    def __init__(self, operation, operand1, operand2=None):
        """
        Initialize a Filter. Should not be used directly. Instead, use the
        static methods to create Filters.

        Args:
            operation (_Operation): The operation.
            operand1 (any): The first operand.
            operand2 (any, optional): The second operand, if the operation is
                binary. Defaults to None.
        """
        self.operation = operation
        self.operand1 = operand1
        self.operand2 = operand2

    @staticmethod
    def and_(operand1, operand2):
        """
        Create a Filter that is the AND of two Filters.

        Args:
            operand1 (Filter): The first Filter.
            operand2 (Filter): The second Filter.

        Returns:
            Filter

        Raises:
            PureError: If either operand is not of the proper type.
        """
        Filter._verify_operand(operand1, (Filter))
        Filter._verify_operand(operand2, (Filter))
        return Filter(Filter._Operation.and_, operand1, operand2)

    @staticmethod
    def contains(operand1, operand2):
        """
        Create a Filter that checks for substring containment.

        Args:
            operand1 (Property, str): The Property to check.
            operand2 (str): The value to check for.

        Returns:
            Filter

        Raises:
            PureError: If either operand is not of the proper type.
        """
        Filter._verify_operand(operand1, (Property, str))
        Filter._verify_operand(operand2, (str))
        return Filter(Filter._Operation.contains, operand1, operand2)

    @staticmethod
    def exists(operand1):
        """
        Create a Filter that checks for existance of a Property.

        Args:
            operand1 (Property, str): The Property to check for.

        Returns:
            Filter

        Raises:
            PureError: If the operand is not of the proper type.
        """
        Filter._verify_operand(operand1, (Property, str))
        return Filter(Filter._Operation.exists, operand1)

    @staticmethod
    def eq(operand1, operand2):
        """
        Create a Filter that checks for equality.

        Args:
            operand1 (Property, str): The Property to compare.
            operand2 (str, int, bool): The value to compare to.

        Returns:
            Filter

        Raises:
            PureError: If either operand is not of the proper type.
        """
        Filter._verify_operand(operand1, (Property, str))
        Filter._verify_operand(operand2, (str, int, bool))
        return Filter(Filter._Operation.eq, operand1, operand2)

    @staticmethod
    def ge(operand1, operand2):
        """
        Create a Filter that checks for greater than or equal.

        Args:
            operand1 (Property, str): The Property to compare.
            operand2 (str, int): The value to compare to.

        Returns:
            Filter

        Raises:
            PureError: If either operand is not of the proper type.
        """
        Filter._verify_operand(operand1, (Property, str))
        Filter._verify_operand(operand2, (str, int))
        return Filter(Filter._Operation.ge, operand1, operand2)

    @staticmethod
    def gt(operand1, operand2):
        """
        Create a Filter that checks for greater than.

        Args:
            operand1 (Property, str): The Property to compare.
            operand2 (str, int): The value to compare to.

        Returns:
            Filter

        Raises:
            PureError: If either operand is not of the proper type.
        """
        Filter._verify_operand(operand1, (Property, str))
        Filter._verify_operand(operand2, (str, int))
        return Filter(Filter._Operation.gt, operand1, operand2)

    @staticmethod
    def in_(operand1, operand2):
        """
        Create a Filter that checks if a Property is in a list of values.

        Args:
            operand1 (Property, str): The Property to check.
            operand2 (list[str], list[int]): The list of values.

        Returns:
            Filter

        Raises:
            PureError: If either operand is not of the proper type.
        """
        Filter._verify_operand(operand1, (Property, str))
        Filter._verify_operand(operand2, (list), (str, int))
        return Filter(Filter._Operation.in_, operand1, operand2)

    @staticmethod
    def le(operand1, operand2):
        """
        Create a Filter that checks for less than or equal.

        Args:
            operand1 (Property, str): The Property to compare.
            operand2 (str, int): The value to compare to.

        Returns:
            Filter

        Raises:
            PureError: If either operand is not of the proper type.
        """
        Filter._verify_operand(operand1, (Property, str))
        Filter._verify_operand(operand2, (str, int))
        return Filter(Filter._Operation.le, operand1, operand2)

    @staticmethod
    def lt(operand1, operand2):
        """
        Create a Filter that checks for less than.

        Args:
            operand1 (Property, str): The Property to compare.
            operand2 (str, int): The value to compare to.

        Returns:
            Filter

        Raises:
            PureError: If either operand is not of the proper type.
        """
        Filter._verify_operand(operand1, (Property, str))
        Filter._verify_operand(operand2, (str, int))
        return Filter(Filter._Operation.lt, operand1, operand2)

    @staticmethod
    def ne(operand1, operand2):
        """
        Create a Filter that checks for inequality.

        Args:
            operand1 (Property, str): The Property to compare.
            operand2 (str, int, bool): The value to compare to.

        Returns:
            Filter

        Raises:
            PureError: If either operand is not of the proper type.
        """
        Filter._verify_operand(operand1, (Property, str))
        Filter._verify_operand(operand2, (str, int, bool))
        return Filter(Filter._Operation.ne, operand1, operand2)

    @staticmethod
    def not_(operand1):
        """
        Create a Filter that is the inverse of another Filter.

        Args:
            operand1 (Filter): The Filter to invert.

        Returns:
            Filter

        Raises:
            PureError: If the operand is not of the proper type.
        """
        Filter._verify_operand(operand1, (Filter))
        return Filter(Filter._Operation.not_, operand1)

    @staticmethod
    def or_(operand1, operand2):
        """
        Create a Filter that is the OR of two Filters.

        Args:
            operand1 (Filter): The first Filter.
            operand2 (Filter): The second Filter.

        Returns:
            Filter

        Raises:
            PureError: If either operand is not of the proper type.
        """
        Filter._verify_operand(operand1, (Filter))
        Filter._verify_operand(operand2, (Filter))
        return Filter(Filter._Operation.or_, operand1, operand2)

    @staticmethod
    def tags(operand1, operand2):
        """
        Create a Filter that checks for a key-value tag.

        Args:
            operand1 (str): The key of the tag.
            operand2 (str): The value of the tag.

        Returns:
            Filter

        Raises:
            PureError: If either operand is not of the proper type.
        """
        Filter._verify_operand(operand1, (str))
        Filter._verify_operand(operand2, (str))
        return Filter(Filter._Operation.tags, operand1, operand2)

    def _to_string(self):
        """
        Convert the Filter object into a properly formatted string.
        Called recursively if the Filter object has Filters as operands.

        Returns:
            str
        """
        if self.operation in [Filter._Operation.eq, Filter._Operation.ne,
                              Filter._Operation.gt, Filter._Operation.ge,
                              Filter._Operation.lt, Filter._Operation.le]:
            return ('{}{}{}'
                    .format(self._operand_to_string(self.operand1, quotes=False),
                            self.operation,
                            self._operand_to_string(self.operand2)))
        elif self.operation in [Filter._Operation.and_, Filter._Operation.or_]:
            return ('{} {} {}'
                    .format(self._operand_to_string(self.operand1),
                            self.operation,
                            self._operand_to_string(self.operand2)))
        elif self.operation is Filter._Operation.not_:
            return ('{}({})'
                    .format(self.operation,
                            self._operand_to_string(self.operand1)))
        elif self.operation is Filter._Operation.contains:
            return ('{}({}, {})'
                    .format(self.operation,
                            self._operand_to_string(self.operand1, quotes=False),
                            self._operand_to_string(self.operand2)))
        elif self.operation in [Filter._Operation.contains,
                                Filter._Operation.tags]:
            return ('{}({}, {})'
                    .format(self.operation,
                            self._operand_to_string(self.operand1),
                            self._operand_to_string(self.operand2)))
        elif self.operation is Filter._Operation.exists:
            return self._operand_to_string(self.operand1, quotes=False)
        elif self.operation is Filter._Operation.in_:
            return ('{} {} ({})'
                    .format(self._operand_to_string(self.operand1, quotes=False),
                            self.operation,
                            self._operand_to_string(self.operand2)))
        else:
            return ''

    def _operand_to_string(self, operand, quotes=True):
        """
        Convert an operand to a valid string based on its type.

        Args:
            operand (Property, Filter, list, str, int, bool): The operand to
                convert.
            quotes (bool, optional): Whether to surround the string single
                quotes. Default to True. Single quotes are required by the API
                for string values.

        Returns:
            str
        """
        if isinstance(operand, list):
            inside = ','.join([self._operand_to_string(op) for op in operand])
            return '({})'.format(inside)
        elif isinstance(operand, Property):
            return str(operand)
        elif isinstance(operand, Filter):
            return operand._to_string()
        elif isinstance(operand, str) and quotes:
            return '\'{}\''.format(operand)
        elif operand is True:
            return 'true'
        elif operand is False:
            return 'false'
        elif isinstance(operand, int):
            return str(operand)
        else:
            return operand

    @staticmethod
    def _verify_operand(operand, types, list_types=None):
        """
        Verify an operand is of one of the types.

        Args:
            operand (): The operand to type check.
            types (tuple): Tuple of types that the operand can be.
            list_types (tuple, optional): If the operand is a list, to check
                that each element in the list is one of these types. Defaults
                to None.

        Returns:
            str
        """
        error = False
        if not isinstance(operand, types):
            error = True
        elif (operand is True or operand is False) and bool not in types:
            error = True
        elif isinstance(operand, list) and list_types is not None:
            if not all(Filter._verify_operand(op, list_types) is None
                       for op in operand):
                error = True
        if error:
            raise PureError('Invalid Filter operand type: {}'.format(operand))


    def __and__(self, other):
        """
        The & operator. Create a Filter that is the AND of two Filters.

        Args:
            other (Filter): The Filter to AND.

        Returns:
            Filter

        Raises:
            PureError: If other is not of the proper type.
        """
        return Filter.and_(self, other)

    def __invert__(self):
        """
        The ~ operator. Create a Filter that is the inverse of another Filter.

        Returns:
            Filter
        """
        return Filter.not_(self)

    def __or__(self, other):
        """
        The | operator. Create a Filter that is the OR of two Filters.

        Args:
            other (Filter): The Filter to OR.

        Returns:
            Filter

        Raises:
            PureError: If other is not of the proper type.
        """
        return Filter.or_(self, other)

    def __repr__(self):
        """
        Return the string value of the Filter.

        Returns:
            str
        """
        return self._to_string()
