## This file is part of Indico.
## Copyright (C) 2002 - 2014 European Organization for Nuclear Research (CERN).
##
## Indico is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
## License, or (at your option) any later version.
##
## Indico is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Indico; if not, see <http://www.gnu.org/licenses/>.

from itertools import product, imap


def bool_matrix(template, expect):
    """Creates a boolean matrix suitable for parametrized tests.

    This function lets you create a boolean matrix with certain columns being
    fixed to a static value or certain combinations being skipped. It also adds
    a last column with a value that's either fixed or depending on the other values.

    By default any `0` or `1` in the template results in its column being fixed
    to that value while any `.` column is dynamic and is used when creating all
    possible boolean values::

    >>> bool_matrix('10..', expect=True)
    ((True, False, True,  True,  True),
     (True, False, True,  False, True),
     (True, False, False, True,  True),
     (True, False, False, False, True))

    In exclusion mode any row matching the template is skipped. It can be enabled
    by prefixing the template with a `!` character::

    >>> bool_matrix('!00.', expect=all)
    ((True,  True,  True,  True),
     (True,  True,  False, False),
     (True,  False, True,  False),
     (True,  False, False, False),
     (False, True,  True,  False),
     (False, True,  False, False))

    The `expect` param can be a boolean value if you always want the same value,
    a tuple if you want only a single row to be true or a callable receiving the
    whole row. In some cases the builtin callables `any` or `all` are appropriate
    callables, in other cases a custom (lambda) function is necessary.

    :param template: row template
    :param expect: bool value, tuple or callable
    """
    # let people align definitions nicely
    template = template.replace(' ', '')
    exclude = False
    if template[0] == '!':
        exclude = True
        template = template[1:]
    mapping = {'0': False, '1': True, '.': None}
    template = tuple(imap(mapping.__getitem__, template))
    # full truth table
    iterable = product((True, False), repeat=len(template))
    if exclude:
        # only use rows which have values not matching the template
        iterable = (x for x in iterable if any(x[i] != v for i, v in enumerate(template) if v is not None))
    else:
        # only use rows where all values match the template
        iterable = (x for x in iterable if all(v is None or x[i] == v for i, v in enumerate(template)))
    # add the "expected" value which can depend on the other values
    if callable(expect):
        iterable = (x + (expect(x),) for x in iterable)
    elif isinstance(expect, (tuple, list)):
        iterable = (x + (x == expect,) for x in iterable)
    else:
        iterable = (x + (expect,) for x in iterable)
    return tuple(iterable)