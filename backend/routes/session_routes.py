from flask import Blueprint, request, jsonify
from models import db, YouTubeSession, YouTubeChannel
from auth import require_auth, require_manager
from crypto import encrypt, decrypt

session_bp = Blueprint('session', __name__)


@session_bp.route('/<int:cid>', methods=['GET'])
@require_auth
def get_session(cid):
    channel = YouTubeChannel.query.get_or_404(cid)
    user = request.current_user

    if user.role != 'manager' and channel.employee_id != user.id:
        return jsonify({'error': 'Không có quyền'}), 403

    session = channel.yt_session
    if not session:
        return jsonify({'has_session': False})

    include_data = request.args.get('include_data') == '1' and user.role == 'manager'
    result = session.to_dict(include_data=include_data)
    if include_data and result.get('session_data'):
        result['session_data'] = decrypt(result['session_data'])
    result['has_session'] = True
    return jsonify(result)


@session_bp.route('/<int:cid>', methods=['POST'])
@require_auth
def save_session(cid):
    channel = YouTubeChannel.query.get_or_404(cid)
    user = request.current_user

    if user.role != 'manager' and channel.employee_id != user.id:
        return jsonify({'error': 'Không có quyền'}), 403

    data = request.get_json() or {}
    session_data = data.get('session_data', '').strip()
    session_note = data.get('session_note', '').strip()

    if not session_data:
        return jsonify({'error': 'Dữ liệu session không được để trống'}), 400

    encrypted = encrypt(session_data)

    session = channel.yt_session
    if session:
        session.session_data = encrypted
        session.session_note = session_note
        session.updated_by = user.id
    else:
        session = YouTubeSession(
            channel_id=cid,
            session_data=encrypted,
            session_note=session_note,
            updated_by=user.id
        )
        db.session.add(session)

    db.session.commit()
    return jsonify({'message': 'Đã lưu session thành công', 'has_session': True})


@session_bp.route('/<int:cid>', methods=['DELETE'])
@require_auth
def delete_session(cid):
    channel = YouTubeChannel.query.get_or_404(cid)
    user = request.current_user

    if user.role != 'manager' and channel.employee_id != user.id:
        return jsonify({'error': 'Không có quyền'}), 403

    session = channel.yt_session
    if session:
        db.session.delete(session)
        db.session.commit()
    return jsonify({'message': 'Đã xóa session'})
