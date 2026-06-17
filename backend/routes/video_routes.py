from datetime import datetime
from flask import Blueprint, request, jsonify
from models import db, VideoRecord, YouTubeChannel
from auth import require_auth, require_manager

video_bp = Blueprint('video', __name__)


@video_bp.route('', methods=['GET'])
@require_auth
def list_videos():
    user = request.current_user
    channel_id = request.args.get('channel_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    q = VideoRecord.query
    if user.role == 'manager':
        if channel_id:
            q = q.filter_by(channel_id=channel_id)
    else:
        # Nhân viên chỉ thấy video của kênh mình phụ trách
        my_channel_ids = [c.id for c in YouTubeChannel.query.filter_by(employee_id=user.id).all()]
        if channel_id:
            if channel_id not in my_channel_ids:
                return jsonify({'error': 'Không có quyền'}), 403
            q = q.filter_by(channel_id=channel_id)
        else:
            q = q.filter(VideoRecord.channel_id.in_(my_channel_ids))

    q = q.order_by(VideoRecord.channel_id, VideoRecord.video_number.desc())
    total = q.count()
    videos = q.offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        'total': total,
        'page': page,
        'per_page': per_page,
        'videos': [v.to_dict() for v in videos]
    })


@video_bp.route('', methods=['POST'])
@require_auth
def create_video():
    data = request.get_json() or {}
    channel_id = data.get('channel_id')
    user = request.current_user

    if not channel_id:
        return jsonify({'error': 'Thiếu channel_id'}), 400

    channel = YouTubeChannel.query.get_or_404(channel_id)

    # Kiểm tra quyền
    if user.role != 'manager' and channel.employee_id != user.id:
        return jsonify({'error': 'Không có quyền đăng video cho kênh này'}), 403

    # Lấy số thứ tự
    video_number = data.get('video_number', channel.next_video_number)
    
    title = data.get('title', '').strip()
    if not title:
        title = f"Video #{video_number}"

    video = VideoRecord(
        channel_id=channel_id,
        posted_by=user.id,
        video_number=int(video_number),
        title=title,
        youtube_url=data.get('youtube_url', '').strip(),
        thumbnail_url=data.get('thumbnail_url', '').strip(),
        notes=data.get('notes', '').strip(),
        posted_at=datetime.utcnow()
    )
    db.session.add(video)

    # Tăng số thứ tự tiếp theo
    if int(video_number) >= channel.next_video_number:
        channel.next_video_number = int(video_number) + 1

    channel.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(video.to_dict()), 201


@video_bp.route('/<int:vid>', methods=['PUT'])
@require_auth
def update_video(vid):
    video = VideoRecord.query.get_or_404(vid)
    user = request.current_user
    data = request.get_json() or {}

    if user.role != 'manager' and video.posted_by != user.id:
        return jsonify({'error': 'Không có quyền sửa video này'}), 403

    if 'title' in data:
        video.title = data['title'].strip()
    if 'youtube_url' in data:
        video.youtube_url = data['youtube_url'].strip()
    if 'thumbnail_url' in data:
        video.thumbnail_url = data['thumbnail_url'].strip()
    if 'notes' in data:
        video.notes = data['notes'].strip()
    if 'video_number' in data and user.role == 'manager':
        video.video_number = int(data['video_number'])

    db.session.commit()
    return jsonify(video.to_dict())


@video_bp.route('/<int:vid>', methods=['DELETE'])
@require_manager
def delete_video(vid):
    video = VideoRecord.query.get_or_404(vid)
    db.session.delete(video)
    db.session.commit()
    return jsonify({'message': 'Đã xóa video'})


@video_bp.route('/stats', methods=['GET'])
@require_manager
def get_stats():
    """Thống kê tổng quan cho dashboard manager."""
    from models import YouTubeChannel, GmailAccount, User
    from sqlalchemy import func

    total_channels = YouTubeChannel.query.filter_by(is_active=True).count()
    total_videos = VideoRecord.query.count()
    total_employees = User.query.filter_by(role='employee', is_active=True).count()
    total_gmails = GmailAccount.query.count()

    # Top kênh có nhiều video nhất
    top_channels = db.session.query(
        YouTubeChannel.channel_name,
        func.count(VideoRecord.id).label('video_count')
    ).join(VideoRecord, isouter=True).group_by(YouTubeChannel.id)\
     .order_by(func.count(VideoRecord.id).desc()).limit(5).all()

    # Video gần nhất
    recent_videos = VideoRecord.query.order_by(VideoRecord.created_at.desc()).limit(10).all()

    return jsonify({
        'total_channels': total_channels,
        'total_videos': total_videos,
        'total_employees': total_employees,
        'total_gmails': total_gmails,
        'top_channels': [{'name': r[0], 'count': r[1]} for r in top_channels],
        'recent_videos': [v.to_dict() for v in recent_videos]
    })
