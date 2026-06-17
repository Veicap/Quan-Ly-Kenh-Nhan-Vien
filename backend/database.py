import os
import sys
import bcrypt
from models import db, User


def init_db(app):
    """Khởi tạo database và tạo tài khoản mặc định."""
    with app.app_context():
        db.create_all()
        _seed_default_admin()


def _seed_default_admin():
    """Tạo tài khoản manager mặc định nếu chưa tồn tại."""
    existing = User.query.filter_by(username='admin').first()
    if not existing:
        hashed = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
        admin = User(
            username='admin',
            password_hash=hashed,
            full_name='Quản Lý',
            role='manager'
        )
        db.session.add(admin)
        db.session.commit()
        print('[OK] Da tao tai khoan manager mac dinh: admin / admin123')
    else:
        print('[INFO] Tai khoan admin da ton tai.')
