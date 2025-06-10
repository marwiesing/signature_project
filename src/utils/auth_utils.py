from functools import wraps
from flask import session, redirect, flash

def require_role(role):
    def wrapper(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if session.get("role") != role:
                flash("Access denied", "danger")
                return redirect("/")
            return view(*args, **kwargs)
        return wrapped_view
    return wrapper
