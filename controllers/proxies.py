from werkzeug.local import LocalProxy
from flask import g

current_user = LocalProxy(lambda: g.user)

current_admin = LocalProxy(lambda: g.admin)