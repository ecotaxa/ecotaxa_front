# -*- coding: utf-8 -*-
# This file is part of Ecotaxa, see license.md in the application root directory for license informations.import functools
import collections
from flask import session, session_modified, request

BreadCrumb = collections.namedtuple("BreadCrumb", ["path", "title"])


def breadcrumb(view_title):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Also put previous breadcrumbs there, ready for view to use
            session_crumbs = session.setdefault("crumbs", [])
            # Call the view
            rv = f(*args, **kwargs)

            # Now add the request path and title for that view
            # to the list of crumbs we store in the session.
            session.modified = True
            session_crumbs.append((request.path, view_title))
            # Only keep most recent crumbs (number should be configurable)
            if len(session_crumbs) > 3:
                session_crumbs.pop(0)

            return rv

        return decorated_function

    return decorator
