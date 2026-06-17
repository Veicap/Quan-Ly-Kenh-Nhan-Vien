from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False, default='')
    role = db.Column(db.String(20), nullable=False, default='employee')  # 'manager' | 'employee'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    channels = db.relationship('YouTubeChannel', back_populates='assigned_employee', foreign_keys='YouTubeChannel.employee_id')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


class GmailAccount(db.Model):
    __tablename__ = 'gmail_accounts'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), default='')
    two_fa = db.Column(db.String(255), default='')
    display_name = db.Column(db.String(120), default='')
    notes = db.Column(db.Text, default='')
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    channels = db.relationship('YouTubeChannel', back_populates='gmail', cascade='all, delete-orphan')
    assigned_employee = db.relationship('User', foreign_keys=[employee_id])

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'two_fa': self.two_fa,
            'display_name': self.display_name,
            'notes': self.notes,
            'employee_id': self.employee_id,
            'employee_name': self.assigned_employee.full_name if self.assigned_employee else None,
            'channel_count': len(self.channels),
            'created_at': self.created_at.isoformat()
        }


class YouTubeChannel(db.Model):
    __tablename__ = 'youtube_channels'
    id = db.Column(db.Integer, primary_key=True)
    gmail_id = db.Column(db.Integer, db.ForeignKey('gmail_accounts.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    channel_name = db.Column(db.String(200), nullable=False)
    channel_id = db.Column(db.String(100), default='')        # YouTube Channel ID (UCxxxxxx)
    channel_url = db.Column(db.String(500), default='')       # https://youtube.com/channel/...
    studio_url = db.Column(db.String(500), default='https://studio.youtube.com')
    video_storage_path = db.Column(db.Text, default='')       # Đường dẫn kho video (nhân viên điền)
    next_video_number = db.Column(db.Integer, default=1)      # Số thứ tự video tiếp theo
    notes = db.Column(db.Text, default='')
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(50), default='active')       # 'active', 'pending_deletion'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    gmail = db.relationship('GmailAccount', back_populates='channels')
    assigned_employee = db.relationship('User', back_populates='channels', foreign_keys=[employee_id])
    videos = db.relationship('VideoRecord', back_populates='channel', cascade='all, delete-orphan')
    yt_session = db.relationship('YouTubeSession', back_populates='channel', uselist=False, cascade='all, delete-orphan')

    def to_dict(self, include_session=False):
        d = {
            'id': self.id,
            'gmail_id': self.gmail_id,
            'gmail_email': self.gmail.email if self.gmail else '',
            'employee_id': self.employee_id,
            'employee_name': self.assigned_employee.full_name if self.assigned_employee else None,
            'employee_username': self.assigned_employee.username if self.assigned_employee else None,
            'channel_name': self.channel_name,
            'channel_id': self.channel_id,
            'channel_url': self.channel_url,
            'studio_url': self.studio_url,
            'video_storage_path': self.video_storage_path,
            'next_video_number': self.next_video_number,
            'notes': self.notes,
            'is_active': self.is_active,
            'status': self.status,
            'video_count': len(self.videos),
            'has_session': self.yt_session is not None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        return d


class VideoRecord(db.Model):
    __tablename__ = 'video_records'
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('youtube_channels.id'), nullable=False)
    posted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    video_number = db.Column(db.Integer, nullable=False)      # Số thứ tự video
    title = db.Column(db.String(500), nullable=False)
    youtube_url = db.Column(db.String(500), default='')
    thumbnail_url = db.Column(db.String(500), default='')
    notes = db.Column(db.Text, default='')
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    channel = db.relationship('YouTubeChannel', back_populates='videos')
    poster = db.relationship('User', foreign_keys=[posted_by])

    def to_dict(self):
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'channel_name': self.channel.channel_name if self.channel else '',
            'posted_by': self.posted_by,
            'poster_name': self.poster.full_name if self.poster else '',
            'video_number': self.video_number,
            'title': self.title,
            'youtube_url': self.youtube_url,
            'thumbnail_url': self.thumbnail_url,
            'notes': self.notes,
            'posted_at': self.posted_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }


class YouTubeSession(db.Model):
    __tablename__ = 'youtube_sessions'
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('youtube_channels.id'), unique=True, nullable=False)
    session_data = db.Column(db.Text, nullable=False)          # Encrypted session/cookie string
    session_note = db.Column(db.String(500), default='')       # Ghi chú về session
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    channel = db.relationship('YouTubeChannel', back_populates='yt_session')
    updater = db.relationship('User', foreign_keys=[updated_by])

    def to_dict(self, include_data=False):
        d = {
            'id': self.id,
            'channel_id': self.channel_id,
            'session_note': self.session_note,
            'updated_by': self.updated_by,
            'updater_name': self.updater.full_name if self.updater else '',
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_data:
            d['session_data'] = self.session_data
        return d


class SystemNotification(db.Model):
    __tablename__ = 'system_notifications'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False) # e.g. 'channel_created'
    message = db.Column(db.String(500), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    related_channel_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'message': self.message,
            'is_read': self.is_read,
            'related_channel_id': self.related_channel_id,
            'created_at': self.created_at.isoformat()
        }
