from datetime import datetime
from flask import Flask, session, g
from controllers.configuration import config
from models import db
from controllers.user import user
from jinja2 import Undefined
from controllers.admin import admin

app = Flask(__name__, template_folder="templates")

app.config.from_object(config)
app.config['SECRET_KEY'] = 'qwertyuiop'

db.init_app(app)

@app.before_request
def setup_before_request():
    if 'init' not in session:
        session.clear()
        session['init'] = True
    
    g.user = user()
    g.admin = admin()
with app.app_context():
    db.create_all()

from controllers.handler import main_routes
app.register_blueprint(main_routes)

if __name__ == "__main__":
    app.run(debug=True, port=5050)
