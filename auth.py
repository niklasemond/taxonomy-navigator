from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

# Simple user class
class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username

# Simulated user database (replace with real database later)
users = {
    'admin': generate_password_hash('admin123')
}

def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = '/login'

    @login_manager.user_loader
    def load_user(username):
        if username not in users:
            return None
        return User(username)

    return login_manager 