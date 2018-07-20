

from functools import wraps


from flask import abort
from flask_login import current_user
from flask_socketio import disconnect


def permission_required(permission):
    """Restrict a view to users with the given permission."""

    def decorator(f):
        @wraps(f)
        def decorated_functions(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        
        return decorated_functions
    return decorator

def admin_required(f):
    return permission_required('default')(f)


def authenticated_only(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped
