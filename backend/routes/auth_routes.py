from flask import Blueprint, request, jsonify
from models import db, User
from auth import generate_token, hash_password, check_password, require_auth, require_manager

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Vui lòng nhập username và password'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password(password, user.password_hash):
        return jsonify({'error': 'Tài khoản hoặc mật khẩu không đúng'}), 401

    if not user.is_active:
        return jsonify({'error': 'Tài khoản đã bị vô hiệu hóa'}), 403

    token = generate_token(user.id, user.role)
    return jsonify({
        'token': token,
        'user': user.to_dict()
    })


@auth_bp.route('/me', methods=['GET'])
@require_auth
def me():
    return jsonify(request.current_user.to_dict())


@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    data = request.get_json() or {}
    old_pass = data.get('old_password', '')
    new_pass = data.get('new_password', '')

    if not old_pass or not new_pass:
        return jsonify({'error': 'Thiếu thông tin'}), 400

    user = request.current_user
    if not check_password(old_pass, user.password_hash):
        return jsonify({'error': 'Mật khẩu cũ không đúng'}), 400

    if len(new_pass) < 6:
        return jsonify({'error': 'Mật khẩu mới ít nhất 6 ký tự'}), 400

    user.password_hash = hash_password(new_pass)
    db.session.commit()
    return jsonify({'message': 'Đổi mật khẩu thành công'})


# ── Manager only ──────────────────────────────────────────────────────────────

@auth_bp.route('/users', methods=['GET'])
@require_manager
def list_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])


@auth_bp.route('/users', methods=['POST'])
@require_manager
def create_user():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    role = data.get('role', 'employee')

    if not username or not password or not full_name:
        return jsonify({'error': 'Thiếu thông tin bắt buộc'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Mật khẩu ít nhất 6 ký tự'}), 400
    if role not in ('manager', 'employee'):
        return jsonify({'error': 'Role không hợp lệ'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username đã tồn tại'}), 409

    user = User(
        username=username,
        password_hash=hash_password(password),
        full_name=full_name,
        role=role
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@auth_bp.route('/users/<int:uid>', methods=['PUT'])
@require_manager
def update_user(uid):
    user = User.query.get_or_404(uid)
    data = request.get_json() or {}

    if 'full_name' in data:
        user.full_name = data['full_name'].strip()
    if 'role' in data and data['role'] in ('manager', 'employee'):
        user.role = data['role']
    if 'is_active' in data:
        user.is_active = bool(data['is_active'])
    if 'password' in data and data['password']:
        if len(data['password']) < 6:
            return jsonify({'error': 'Mật khẩu ít nhất 6 ký tự'}), 400
        user.password_hash = hash_password(data['password'])

    db.session.commit()
    return jsonify(user.to_dict())


@auth_bp.route('/users/<int:uid>', methods=['DELETE'])
@require_manager
def delete_user(uid):
    user = User.query.get_or_404(uid)
    if user.username == 'admin':
        return jsonify({'error': 'Không thể xóa tài khoản admin'}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Đã xóa tài khoản'})
