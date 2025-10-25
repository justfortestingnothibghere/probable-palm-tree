from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import yt_dlp
import os
from models import db, User

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')  # Render PostgreSQL or SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

def get_audio_url(video_id):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(id)s.%(ext)s',
        'noplaylist': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return info['url'], info['title'], info['thumbnail']
    except:
        return None, None, None

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('../index.html')

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        query = request.form['query']
        ydl_opts = {'quiet': True, 'default_search': 'ytsearch10'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            videos = [{'id': entry['id'], 'title': entry['title'], 'thumbnail': entry['thumbnail']} for entry in info['entries']]
        return render_template('../index.html', videos=videos, query=query)
    return render_template('../index.html')

@app.route('/play/<video_id>')
@login_required
def play(video_id):
    audio_url, title, thumbnail = get_audio_url(video_id)
    if not audio_url:
        flash('Video not found!')
        return redirect(url_for('index'))
    return render_template('../index.html', audio_url=audio_url, title=title, thumbnail=thumbnail, play=True)

@app.route('/share/<share_id>')
def share_redirect(share_id):
    video_id = share_id
    audio_url, title, _ = get_audio_url(video_id)
    if not audio_url:
        abort(404)
    return render_template('share.html', audio_url=audio_url, title=title, video_id=video_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():
            flash('Username exists!')
            return render_template('signup.html')
        user = User(username=request.form['username'])
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        flash('Signed up! Login now.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/t/a/admin')
def admin_panel():
    if request.args.get('username') != 'admin' or request.args.get('password') != 'ad':
        abort(401)
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
