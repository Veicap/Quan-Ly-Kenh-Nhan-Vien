"""
Mở Chrome với profile riêng cho từng kênh YouTube.
Mỗi kênh có 1 thư mục profile riêng → session được lưu tự động bởi Chrome.
"""
import os
import subprocess

# Thư mục lưu Chrome profiles (bên trong backend/data/)
PROFILES_DIR = os.path.join(os.path.dirname(__file__), 'data', 'chrome_profiles')


def get_profile_dir(channel_id: int) -> str:
    """Lấy đường dẫn profile Chrome cho kênh."""
    path = os.path.join(PROFILES_DIR, f'channel_{channel_id}')
    os.makedirs(path, exist_ok=True)
    return path


def find_chrome() -> str | None:
    """Tìm đường dẫn Chrome trên Windows."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        # Microsoft Edge (dự phòng nếu không có Chrome)
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def open_channel_browser(channel_id: int, studio_url: str) -> dict:
    """
    Mở Chrome với profile riêng cho kênh.
    Trả về dict với status và thông tin.
    """
    chrome_path = find_chrome()
    if not chrome_path:
        return {
            'success': False,
            'error': 'Không tìm thấy Chrome hoặc Edge trên máy tính này.'
        }

    profile_dir = get_profile_dir(channel_id)
    url = studio_url or 'https://studio.youtube.com'

    cmd = [
        chrome_path,
        f'--user-data-dir={profile_dir}',
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-extensions-except=',  # Không dùng extension của profile chính
        url
    ]

    try:
        subprocess.Popen(cmd)
        browser_name = 'Chrome' if 'chrome' in chrome_path.lower() else 'Edge'
        return {
            'success': True,
            'message': f'Đã mở {browser_name} với profile riêng cho kênh này.',
            'profile_dir': profile_dir,
            'browser': browser_name
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def reset_channel_profile(channel_id: int) -> dict:
    """Xóa profile Chrome của kênh (đăng xuất hoàn toàn)."""
    import shutil
    profile_dir = get_profile_dir(channel_id)
    try:
        shutil.rmtree(profile_dir)
        return {'success': True, 'message': 'Đã xóa profile, kênh sẽ cần đăng nhập lại.'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_profile_info(channel_id: int) -> dict:
    """Kiểm tra profile của kênh có tồn tại không."""
    profile_dir = os.path.join(PROFILES_DIR, f'channel_{channel_id}')
    exists = os.path.exists(profile_dir)
    size_mb = 0
    if exists:
        total = sum(
            os.path.getsize(os.path.join(dp, f))
            for dp, dn, fn in os.walk(profile_dir)
            for f in fn
        )
        size_mb = round(total / 1024 / 1024, 1)

    return {
        'has_profile': exists,
        'profile_dir': profile_dir,
        'size_mb': size_mb
    }
