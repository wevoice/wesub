# Amara, universalsubtitles.org
#
# Copyright (C) 2013 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

"""util.behaviors -- Define extensible behavior functions

This module allows one app to define a "behavior function", which other apps
can then override to change the behavior.  Using the behavior mechanism allows
things to be loosely coupled, because the original function doesn't need to
have any specific knowledge about the override function.

An example of this is the video title.  The videos app defines
the make_title_display() behavior function, which by default just returns the
title.  Then we override it with the amaradotorg app to change the title for
certain teams.   Using the behaviors module allows this to be done without
videos ever importing from amaradotorg, which would cause a circular import

A typical example is one app defines an override function:
>>> @behavior
... def eat_ice_cream(flavor):
...     return 'Yum'
>>> eat_ice_cream('vanilla')  
'Yum'

Then another app overrides it to customize the behavior.
>>> @eat_ice_cream.override
... def eat_ice_cream_picky(flavor):
...     if flavor == 'vanilla':
...         return 'Yuck'
...     else:
...         return DONT_OVERRIDE
>>> eat_ice_cream('vanilla')
'Yuck'
>>> eat_ice_cream('chocolate')
'Yum'

By convention, behavior functions are put in a module named
<appname>.behaviors.
"""

from functools import wraps

DONT_OVERRIDE = object()

def behavior(func):
    """Declare a function as an overridable behavior.

    This allows other components to modify the behavior of the function by
    decorating them with func.override.  When invoked, the override function
    will be passed the arguments the original function was called with.

    The override function's return vaule will be used intead of the return
    value of the original.  If DONT_OVERRIDE is returned, then control will
    pass to other override functions, and finally the original function.

    Override functions are themselves behaviors, so they can be overriden
    again forming a chain of responsibility that handles the behaviors.  If
    the same function is overriden twice, then the override functions will be
    called in FIFO order.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if wrapper.override_func:
            rv = wrapper.override_func(*args, **kwargs)
            if rv is not DONT_OVERRIDE:
                return rv
        return func(*args, **kwargs)
    wrapper.override_func = None
    def override(override_func):
        override_func = behavior(override_func)
        # if we already have an override_func, make that function override the
        # second override.  This effectively insert the new function
        # between the original and the old override functions.
        if wrapper.override_func is not None:
            override_func.override(wrapper.override_func)
        wrapper.override_func = override_func
        return override_func
    wrapper.override = override
    return wrapper
