from flask import Flask
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Load environment variables from a .env file at the project root, if present,
# so SECRET_KEY and other config can live outside the shell and source control.
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise RuntimeError(
        'SECRET_KEY is not set. Copy .env.example to .env and set a strong '
        'SECRET_KEY (or export SECRET_KEY=...). See the README Configuration section.'
    )


##########################################################
################ DATABASE SETUP ##########################
##########################################################

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///'+os.path.join(basedir, 'data.sqlite'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)

###################################################################

#########.  LOGIN CONFIGS    ####################################

login_manager = LoginManager()

login_manager.init_app(app)
login_manager.login_view = 'users.login'




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