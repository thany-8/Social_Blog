from flask import Flask
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

project_root = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

load_dotenv(os.path.join(project_root, ".env"))


# --------------------------------------------------
# CREATE THE FLASK APP
# --------------------------------------------------

app = Flask(__name__)


# --------------------------------------------------
# SECRET KEY
# --------------------------------------------------

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError(
        "SECRET_KEY is not set. Add SECRET_KEY to your "
        ".env file locally and to Render Environment Variables."
    )


# --------------------------------------------------
# DATABASE SETUP
# --------------------------------------------------

basedir = os.path.abspath(os.path.dirname(__file__))

database_url = os.environ.get("DATABASE_URL")


# Do not let Render silently use SQLite
if os.environ.get("RENDER") == "true" and not database_url:
    raise RuntimeError(
        "DATABASE_URL is missing on Render. "
        "Connect your Render PostgreSQL database."
    )


# Use SQLite only while working locally
if not database_url:
    database_url = (
        "sqlite:///" + os.path.join(basedir, "data.sqlite")
    )


# Explicitly use the psycopg2 PostgreSQL driver
if database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://",
        "postgresql+psycopg2://",
        1
    )

# Compatibility with older database URL formats
elif database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql+psycopg2://",
        1
    )


app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Helps reconnect if a PostgreSQL connection becomes stale
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True
}


db = SQLAlchemy(app)
migrate = Migrate(app, db)


# --------------------------------------------------
# LOGIN CONFIGURATION
# --------------------------------------------------

login_manager = LoginManager()

login_manager.init_app(app)
login_manager.login_view = "users.login"


# --------------------------------------------------
# IMPORT AND REGISTER BLUEPRINTS
# --------------------------------------------------

from socialblog.core.views import core
from socialblog.users.views import users
from socialblog.error_pages.handlers import error_pages
from socialblog.blog_posts.views import blog_posts
from socialblog.blog_posts.api import api_posts


app.register_blueprint(core)
app.register_blueprint(users)
app.register_blueprint(error_pages)
app.register_blueprint(blog_posts)
app.register_blueprint(api_posts)