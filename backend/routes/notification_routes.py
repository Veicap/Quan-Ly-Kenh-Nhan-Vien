from flask import Blueprint, jsonify, request
from models import db, SystemNotification
from auth import require_manager

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('', methods=['GET'])
@require_manager
def list_notifications():
    # Only get the latest 50 notifications, unread first
    notifs = SystemNotification.query.order_by(
        SystemNotification.is_read.asc(),
        SystemNotification.created_at.desc()
    ).limit(50).all()
    return jsonify([n.to_dict() for n in notifs])

@notification_bp.route('/<int:nid>/read', methods=['POST'])
@require_manager
def mark_read(nid):
    notif = SystemNotification.query.get_or_404(nid)
    notif.is_read = True
    db.session.commit()
    return jsonify(notif.to_dict())

@notification_bp.route('/read-all', methods=['POST'])
@require_manager
def mark_all_read():
    SystemNotification.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'message': 'Đã đánh dấu tất cả là đã đọc'})
