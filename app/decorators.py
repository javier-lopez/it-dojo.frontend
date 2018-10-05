from functools import wraps
from threading import Thread

from flask import flash, redirect, url_for
from flask_login import current_user

def threaded(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

def user_confirmed_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.confirmed:
            return redirect(url_for('user_unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function
