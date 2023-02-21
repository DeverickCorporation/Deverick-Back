from .app import init_app

from flask_sqlalchemy import SQLAlchemy


app = init_app()
db = SQLAlchemy(app)


def create_app():
    from .endpoints import all_routes
    from .models import db

    app.db = db

    with app.app_context():
        app.db.create_all()

    [app.register_blueprint(rout) for rout in all_routes]

    return app
