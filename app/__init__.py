from flask import Flask

from .models import db
from .auth import auth_bp
from .offers import offers_bp


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///swaplah.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(offers_bp)

    with app.app_context():
        db.create_all()

    return app