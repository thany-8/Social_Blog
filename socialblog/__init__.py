from flask import Flask
import os
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from socialblog.blog_posts.api import api_posts



app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')


# register API blueprint AFTER app exists
app.register_blueprint(api_posts)

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

app.register_blueprint(core)
app.register_blueprint(users)
app.register_blueprint(error_pages)
app.register_blueprint(blog_posts)