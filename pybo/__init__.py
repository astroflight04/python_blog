from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flaskext.markdown import Markdown

import config

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()

db = SQLAlchemy()
migrate = Migrate()

def create_app():   #application factory
    app = Flask(__name__)
    app.config.from_object(config)
    app.config['UPLOAD_FOLDER'] = '..\\static\\upload'  # 20231230

    # ORM
    db.init_app(app)
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith("sqlite"):
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)
    from . import models

    # blueprint
    from .views import main_views, question_views, answer_views, auth_views, compiler_views, profile_views, user_views   # views 등록

    app.register_blueprint(main_views.bp)
    app.register_blueprint(question_views.bp)  #
    app.register_blueprint(answer_views.bp)  #
    app.register_blueprint(auth_views.bp)  #20230715
    app.register_blueprint(compiler_views.bp)  #20240901
    app.register_blueprint(profile_views.bp)  # 20240921
    app.register_blueprint(user_views.bp)  # 20240928

    #markdown 20240825
    Markdown(app, extensions=['nl2br', 'fenced_code'])

    return app