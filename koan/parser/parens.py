class ParseError(RuntimeError):
    """ Raised when there's a problem parsing text as code.
    """
    pass


def first_sep(string):
    """ Given a string, return the index of the first paren (open or closed.)
        If the string contains no parens, return -1.
    """
    open = string.find('(')
    closed = string.find(')')
    return open if (closed == -1 or -1 < open < closed) else closed


_too_many_open = 'open paren without matching closed paren'
_too_many_closed = 'closed paren without matching open paren'


def nest_parens_recursive(string, _nested=False):
    """ Takes a string that may have nested pairs of parentheses and breaks it
        into a list of str and nested lists.
        Recursive implementation.

        Parameters
        ----------
        string: str
        _nested: bool
            True if the current expression was begun with an open paren.
            For internal use only.

        Returns
        -------
        tuple:
            nested list of (str | list): the input, partitioned by parentheses
            str: Empty if _nested is False. Otherwise is the remainder of the
                 string after the close paren.
    """
    expr = []
    while string and string[first_sep(string)] == '(':
        before, rest = string.split('(', maxsplit=1)
        if before:
            expr.append(before)
        complete, string = nest_parens_recursive(rest, _nested=True)
        expr.append(complete)

    try:
        inside, after = string.split(')', maxsplit=1)
    except ValueError:
        if _nested:
            raise ParseError(_too_many_open)
        inside, after = string, ''
    else:
        if not _nested:
            raise ParseError(_too_many_closed)

    if inside:
        expr.append(inside)
    return expr, after


def nest_parens_flat(string):
    """ Takes a string that may have nested pairs of parentheses and breaks it
        into a list of str and nested lists.
        Nonrecursive implementation.

        Parameters
        ----------
        string: str

        Returns
        -------
        nested list of (str | list): the input, partitioned by parentheses
    """
    partials = [[]]  # start with a single empty expression
    while string:
        sep = first_sep(string)
        if sep == -1:  # no more parens in the string
            partials[-1].append(string)
            string = ''

        elif string[sep] == '(':
            before, string = string.split('(', maxsplit=1)
            if before:
                partials[-1].append(before)
            partials.append([])  # new expression

        elif string[sep] == ')':
            inside, string = string.split(')', maxsplit=1)
            complete = partials.pop()  # current expression finished
            if inside:  # complete expression not empty
                complete.append(inside)
            try:
                partials[-1].append(complete)
            except IndexError:  # no more partial expressions to finish
                raise ParseError(_too_many_closed)

    if len(partials) > 1:  # not all partial expressions were finished
        raise ParseError(_too_many_open)
    else:
        return partials[0]


# nest_parens = nest_parens_flat
def nest_parens(string):
    return nest_parens_recursive(string)[0]
