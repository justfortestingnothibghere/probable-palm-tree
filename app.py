from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import yt_dlp
import os
from models import db, User
from routes import *

app = Flask(__name__, template_folder='templates')  # Default templates folder
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Local SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# Error Handler
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Routes
app.add_url_rule('/', view_func=index)
app.add_url_rule('/search', view_func=search, methods=['GET', 'POST'])
app.add_url_rule('/play/<video_id>', view_func=play)
app.add_url_rule('/share/<share_id>', view_func=share_redirect)
app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
app.add_url_rule('/signup', view_func=signup, methods=['GET', 'POST'])
app.add_url_rule('/logout', view_func=logout)
app.add_url_rule('/t/a/admin', view_func=admin_panel)

if __name__ == '__main__':
    app.run(debug=True)