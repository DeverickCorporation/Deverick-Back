from flask_sqlalchemy import SQLAlchemy

from src.app import init_app

app = init_app()
db = SQLAlchemy(app)


def create_app():
    from src.endpoints import all_routes

    app.db = db

    with app.app_context():
        app.db.create_all()

    [app.register_blueprint(rout) for rout in all_routes]

    return app
