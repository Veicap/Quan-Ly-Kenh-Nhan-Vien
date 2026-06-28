"""
backup_db.py — Script backup database tu dong
Chay: python backup_db.py
"""
import os
import shutil
import sqlite3
import sys
from datetime import datetime

# Fix encoding tren Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'db.sqlite3')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
MAX_BACKUPS = 30  # Giữ lại tối đa 30 bản backup


def backup():
    if not os.path.exists(DB_PATH):
        print(f"❌ Không tìm thấy database: {DB_PATH}")
        return False

    os.makedirs(BACKUP_DIR, exist_ok=True)

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    backup_filename = f"db_{timestamp}.sqlite3"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    # Dùng SQLite backup API để đảm bảo tính toàn vẹn dữ liệu (safe copy)
    try:
        src = sqlite3.connect(DB_PATH)
        dst = sqlite3.connect(backup_path)
        src.backup(dst)
        dst.close()
        src.close()

        size_kb = os.path.getsize(backup_path) / 1024
        print(f"✅ Backup thành công: {backup_filename} ({size_kb:.1f} KB)")
    except Exception as e:
        print(f"❌ Lỗi backup: {e}")
        return False

    # Xóa các bản backup cũ nếu vượt quá MAX_BACKUPS
    backups = sorted([
        f for f in os.listdir(BACKUP_DIR) if f.startswith('db_') and f.endswith('.sqlite3')
    ])
    if len(backups) > MAX_BACKUPS:
        to_delete = backups[:len(backups) - MAX_BACKUPS]
        for old in to_delete:
            os.remove(os.path.join(BACKUP_DIR, old))
            print(f"🗑️  Đã xóa bản backup cũ: {old}")

    print(f"📁 Tổng bản backup hiện có: {min(len(backups), MAX_BACKUPS)}/{MAX_BACKUPS}")
    return True


def list_backups():
    if not os.path.exists(BACKUP_DIR):
        print("Chưa có bản backup nào.")
        return
    backups = sorted([
        f for f in os.listdir(BACKUP_DIR) if f.startswith('db_') and f.endswith('.sqlite3')
    ], reverse=True)
    if not backups:
        print("Chưa có bản backup nào.")
        return
    print(f"\n📋 Danh sách backup ({len(backups)} bản):")
    for i, b in enumerate(backups):
        size_kb = os.path.getsize(os.path.join(BACKUP_DIR, b)) / 1024
        print(f"  {'*' if i == 0 else ' '} {b}  ({size_kb:.1f} KB){'  ← MỚI NHẤT' if i == 0 else ''}")


def restore(backup_filename):
    """Khôi phục từ một bản backup cụ thể."""
    src_path = os.path.join(BACKUP_DIR, backup_filename)
    if not os.path.exists(src_path):
        print(f"❌ Không tìm thấy bản backup: {backup_filename}")
        return False

    # Tạo backup của database hiện tại trước khi restore
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    pre_restore_backup = os.path.join(BACKUP_DIR, f"db_{timestamp}_before_restore.sqlite3")
    shutil.copy2(DB_PATH, pre_restore_backup)
    print(f"💾 Đã lưu database hiện tại: db_{timestamp}_before_restore.sqlite3")

    try:
        src = sqlite3.connect(src_path)
        dst = sqlite3.connect(DB_PATH)
        src.backup(dst)
        dst.close()
        src.close()
        print(f"✅ Đã khôi phục từ: {backup_filename}")
        print("⚠️  Hãy restart server backend để áp dụng!")
        return True
    except Exception as e:
        print(f"❌ Lỗi restore: {e}")
        return False


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'list':
            list_backups()
        elif cmd == 'restore' and len(sys.argv) > 2:
            restore(sys.argv[2])
        else:
            print("Dùng: python backup_db.py [list | restore <tên_file>]")
    else:
        backup()
        list_backups()
