from functools import wraps
from flask_login import current_user
from flask import abort

def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if current_user.role != role:
                abort(403)  # Forbidden
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper