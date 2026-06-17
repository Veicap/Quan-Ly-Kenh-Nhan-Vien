import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')
from app import app
from auth import check_password

with app.app_context():
    from models import User, SystemNotification, YouTubeChannel
    
    # Check user passwords
    men = User.query.filter_by(username='men').first()
    print(f"User men exists: {men is not None}")
    if men:
        print(f"  id={men.id}, role={men.role}")
        for pwd in ['123456', 'admin123', 'password', 'men', '123456789']:
            if check_password(pwd, men.password_hash):
                print(f"  Password is: {pwd}")
                break
        else:
            print("  Could not guess password")
    
    # Check all notifications
    notifs = SystemNotification.query.all()
    print(f"\nAll notifications ({len(notifs)}):")
    for n in notifs:
        print(f"  id={n.id}, type={n.type}, read={n.is_read}")
    
    # Check all channels
    channels = YouTubeChannel.query.all()
    print(f"\nAll channels ({len(channels)}):")
    for c in channels:
        print(f"  id={c.id}, name={c.channel_name}, status={c.status}, emp_id={c.employee_id}")
