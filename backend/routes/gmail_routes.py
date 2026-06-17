from flask import Blueprint, request, jsonify
from models import db, GmailAccount
from auth import require_auth, require_manager

gmail_bp = Blueprint('gmail', __name__)


@gmail_bp.route('', methods=['GET'])
@require_auth
def list_gmails():
    user = request.current_user
    if user.role == 'manager':
        gmails = GmailAccount.query.order_by(GmailAccount.created_at.desc()).all()
    else:
        gmails = GmailAccount.query.filter_by(employee_id=user.id).order_by(GmailAccount.created_at.desc()).all()
    return jsonify([g.to_dict() for g in gmails])


@gmail_bp.route('', methods=['POST'])
@require_manager
def create_gmail():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    display_name = data.get('display_name', '').strip()
    notes = data.get('notes', '').strip()

    if not email:
        return jsonify({'error': 'Email không được để trống'}), 400
    if GmailAccount.query.filter_by(email=email).first():
        return jsonify({'error': 'Email đã tồn tại trong hệ thống'}), 409

    gmail = GmailAccount(email=email, display_name=display_name, notes=notes)
    db.session.add(gmail)
    db.session.commit()
    return jsonify(gmail.to_dict()), 201


@gmail_bp.route('/<int:gid>', methods=['GET'])
@require_manager
def get_gmail(gid):
    gmail = GmailAccount.query.get_or_404(gid)
    return jsonify(gmail.to_dict())


@gmail_bp.route('/<int:gid>', methods=['PUT'])
@require_manager
def update_gmail(gid):
    gmail = GmailAccount.query.get_or_404(gid)
    data = request.get_json() or {}

    if 'email' in data:
        new_email = data['email'].strip().lower()
        existing = GmailAccount.query.filter_by(email=new_email).first()
        if existing and existing.id != gid:
            return jsonify({'error': 'Email đã tồn tại'}), 409
        gmail.email = new_email
    if 'display_name' in data:
        gmail.display_name = data['display_name'].strip()
    if 'notes' in data:
        gmail.notes = data['notes'].strip()
    if 'employee_id' in data:
        emp_id = data['employee_id']
        if emp_id:
            from models import User
            emp = User.query.get(emp_id)
            if not emp or emp.role != 'employee':
                return jsonify({'error': 'Nhân viên không hợp lệ'}), 400
        gmail.employee_id = emp_id or None

    db.session.commit()
    return jsonify(gmail.to_dict())


@gmail_bp.route('/<int:gid>', methods=['DELETE'])
@require_manager
def delete_gmail(gid):
    gmail = GmailAccount.query.get_or_404(gid)
    db.session.delete(gmail)
    db.session.commit()
    return jsonify({'message': 'Đã xóa Gmail'})
