from flask import Blueprint, request, jsonify
from models import db, YouTubeChannel, GmailAccount, User
from auth import require_auth, require_manager

channel_bp = Blueprint('channel', __name__)


@channel_bp.route('', methods=['GET'])
@require_auth
def list_channels():
    user = request.current_user
    if user.role == 'manager':
        channels = YouTubeChannel.query.order_by(YouTubeChannel.created_at.desc()).all()
    else:
        # Nhân viên xem tất cả kênh của họ (kể cả active và pending_deletion)
        channels = YouTubeChannel.query.filter_by(employee_id=user.id).order_by(YouTubeChannel.created_at.desc()).all()
    return jsonify([c.to_dict() for c in channels])


@channel_bp.route('', methods=['POST'])
@require_auth
def create_channel():
    user = request.current_user
    data = request.get_json() or {}
    gmail_id = data.get('gmail_id')
    channel_name = data.get('channel_name', '').strip()

    if not gmail_id or not channel_name:
        return jsonify({'error': 'Thiếu gmail_id hoặc channel_name'}), 400
    
    gmail = GmailAccount.query.get(gmail_id)
    if not gmail:
        return jsonify({'error': 'Gmail không tồn tại'}), 404

    if user.role != 'manager' and gmail.employee_id != user.id:
        return jsonify({'error': 'Bạn không được phân công Gmail này'}), 403

    emp_id = data.get('employee_id') if user.role == 'manager' else user.id

    channel = YouTubeChannel(
        gmail_id=gmail_id,
        channel_name=channel_name,
        channel_id=data.get('channel_id', '').strip(),
        channel_url=data.get('channel_url', '').strip(),
        studio_url=data.get('studio_url', 'https://studio.youtube.com').strip(),
        video_storage_path=data.get('video_storage_path', '').strip(),
        next_video_number=int(data.get('next_video_number', 1)),
        notes=data.get('notes', '').strip(),
        employee_id=emp_id or None
    )
    db.session.add(channel)
    db.session.commit()

    if user.role != 'manager':
        from models import SystemNotification
        notif = SystemNotification(
            type='channel_created',
            message=f"Nhân viên {user.full_name} vừa tạo kênh '{channel_name}' trên Gmail {gmail.email}.",
            related_channel_id=channel.id
        )
        db.session.add(notif)
        db.session.commit()

    return jsonify(channel.to_dict()), 201


@channel_bp.route('/<int:cid>', methods=['GET'])
@require_auth
def get_channel(cid):
    channel = YouTubeChannel.query.get_or_404(cid)
    user = request.current_user
    if user.role != 'manager' and channel.employee_id != user.id:
        return jsonify({'error': 'Không có quyền'}), 403
    return jsonify(channel.to_dict())


@channel_bp.route('/<int:cid>', methods=['PUT'])
@require_auth
def update_channel(cid):
    channel = YouTubeChannel.query.get_or_404(cid)
    user = request.current_user
    data = request.get_json() or {}

    if user.role == 'manager':
        # Manager có thể sửa mọi trường
        if 'gmail_id' in data:
            if not GmailAccount.query.get(data['gmail_id']):
                return jsonify({'error': 'Gmail không tồn tại'}), 404
            channel.gmail_id = data['gmail_id']
        if 'channel_name' in data:
            channel.channel_name = data['channel_name'].strip()
        if 'channel_id' in data:
            channel.channel_id = data['channel_id'].strip()
        if 'channel_url' in data:
            channel.channel_url = data['channel_url'].strip()
        if 'studio_url' in data:
            channel.studio_url = data['studio_url'].strip()
        if 'next_video_number' in data:
            channel.next_video_number = int(data['next_video_number'])
        if 'notes' in data:
            channel.notes = data['notes'].strip()
        if 'is_active' in data:
            channel.is_active = bool(data['is_active'])
        if 'employee_id' in data:
            emp_id = data['employee_id']
            if emp_id and not User.query.get(emp_id):
                return jsonify({'error': 'Nhân viên không tồn tại'}), 404
            channel.employee_id = emp_id or None
    else:
        # Nhân viên có thể sửa thông tin kênh của mình (trừ gmail_id, is_active, employee_id, status)
        if channel.employee_id != user.id:
            return jsonify({'error': 'Không có quyền'}), 403
        
        if 'channel_name' in data:
            channel.channel_name = data['channel_name'].strip()
        if 'channel_id' in data:
            channel.channel_id = data['channel_id'].strip()
        if 'channel_url' in data:
            channel.channel_url = data['channel_url'].strip()
        if 'studio_url' in data:
            channel.studio_url = data['studio_url'].strip()
        if 'next_video_number' in data:
            channel.next_video_number = int(data['next_video_number'])
        if 'notes' in data:
            channel.notes = data['notes'].strip()
        if 'video_storage_path' in data:
            channel.video_storage_path = data['video_storage_path'].strip()

    from datetime import datetime
    channel.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(channel.to_dict())


@channel_bp.route('/<int:cid>', methods=['DELETE'])
@require_auth
def delete_channel(cid):
    channel = YouTubeChannel.query.get_or_404(cid)
    user = request.current_user

    if user.role == 'manager':
        db.session.delete(channel)
        db.session.commit()
        return jsonify({'message': 'Đã xóa kênh'})
    else:
        if channel.employee_id != user.id:
            return jsonify({'error': 'Không có quyền'}), 403
        channel.status = 'pending_deletion'
        
        from models import SystemNotification
        notif = SystemNotification(
            type='delete_request',
            message=f"Nhân viên {user.full_name} xin xóa kênh '{channel.channel_name}'.",
            related_channel_id=channel.id
        )
        db.session.add(notif)
        db.session.commit()
        return jsonify({'message': 'Đã gửi yêu cầu xóa kênh cho Quản lý duyệt'})

@channel_bp.route('/<int:cid>/approve-delete', methods=['POST'])
@require_manager
def approve_delete(cid):
    from models import SystemNotification
    channel = YouTubeChannel.query.get(cid)
    if channel:
        db.session.delete(channel)
        # Mark related notifications as read
        SystemNotification.query.filter_by(related_channel_id=cid).update({'is_read': True})
        db.session.commit()
    else:
        # Channel already deleted - just mark notifications as read (idempotent)
        SystemNotification.query.filter_by(related_channel_id=cid).update({'is_read': True})
        db.session.commit()
    return jsonify({'message': 'Đã duyệt và xóa kênh vĩnh viễn'})

@channel_bp.route('/<int:cid>/reject-delete', methods=['POST'])
@require_manager
def reject_delete(cid):
    from models import SystemNotification
    channel = YouTubeChannel.query.get(cid)
    if channel:
        channel.status = 'active'
        # Mark related notifications as read
        SystemNotification.query.filter_by(related_channel_id=cid, type='delete_request').update({'is_read': True})
        db.session.commit()
    else:
        # Channel doesn't exist anymore - just mark notifications as read
        SystemNotification.query.filter_by(related_channel_id=cid).update({'is_read': True})
        db.session.commit()
    return jsonify({'message': 'Đã từ chối yêu cầu xóa kênh'})


@channel_bp.route('/<int:cid>/assign', methods=['POST'])
@require_manager
def assign_employee(cid):
    channel = YouTubeChannel.query.get_or_404(cid)
    data = request.get_json() or {}
    employee_id = data.get('employee_id')

    if employee_id:
        emp = User.query.get(employee_id)
        if not emp or emp.role != 'employee':
            return jsonify({'error': 'Nhân viên không hợp lệ'}), 400
    channel.employee_id = employee_id or None
    db.session.commit()
    return jsonify(channel.to_dict())


@channel_bp.route('/<int:cid>/open-studio', methods=['POST'])
@require_auth
def open_studio(cid):
    """
    Mở Chrome với profile riêng cho kênh này.
    Mỗi kênh có 1 thư mục Chrome profile → session được Chrome lưu tự động.
    """
    from chrome_manager import open_channel_browser

    channel = YouTubeChannel.query.get_or_404(cid)
    user = request.current_user

    # Kiểm tra quyền
    if user.role != 'manager' and channel.employee_id != user.id:
        return jsonify({'error': 'Không có quyền'}), 403

    result = open_channel_browser(cid, channel.studio_url or 'https://studio.youtube.com')

    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 500


@channel_bp.route('/<int:cid>/profile-info', methods=['GET'])
@require_auth
def profile_info(cid):
    """Kiểm tra Chrome profile của kênh."""
    from chrome_manager import get_profile_info

    channel = YouTubeChannel.query.get_or_404(cid)
    user = request.current_user
    if user.role != 'manager' and channel.employee_id != user.id:
        return jsonify({'error': 'Không có quyền'}), 403

    return jsonify(get_profile_info(cid))


@channel_bp.route('/<int:cid>/reset-profile', methods=['POST'])
@require_auth
def reset_profile(cid):
    """Xóa Chrome profile của kênh (buộc đăng nhập lại)."""
    from chrome_manager import reset_channel_profile

    channel = YouTubeChannel.query.get_or_404(cid)
    user = request.current_user
    if user.role != 'manager' and channel.employee_id != user.id:
        return jsonify({'error': 'Không có quyền'}), 403

    return jsonify(reset_channel_profile(cid))

