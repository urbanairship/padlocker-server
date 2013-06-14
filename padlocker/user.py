import bcrypt
import hashlib

import six

from dao import UserBackend

# TODO, make this configurable, from the padlocker config.
user_db = UserBackend()

# Stollen from Django's source
def constant_time_compare(val1, val2):
    """
    Returns True if the two strings are equal, False otherwise.

    The time taken is independent of the number of characters that match.
    """
    if len(val1) != len(val2):
        return False
    result = 0
    if six.PY3 and isinstance(val1, bytes) and isinstance(val2, bytes):
        for x, y in zip(val1, val2):
            result |= x ^ y
    else:
        for x, y in zip(val1, val2):
            result |= ord(x) ^ ord(y)
    return result == 0


class User(object):
    is_anonymous = True
    is_authenticated = False
    username = None
    user_id = None

    def __init__(self, username):
        self.user_id = hashlib.sha256(username).hexdigest()
        self.username = username

    def authenticate(self, password):
        pw_hash = bcrypt.hashpw(password, bcrypt.gensalt())
        user_data = user_db.get_user_data(self.user_id)
        if constant_time_compare(user_data['pw_hash'], pw_hash):
            # User is logged in!
            self.is_anonymous = False
            self.is_authenticated = True

            return True
        else:
            return None


    def get_id(self):
        return unicode(self.username)

    def is_authenticated(self):
        return self.is_authenticated

    def is_anonymous(self):
        return self.is_anonymous
