import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from app import app

if __name__ == '__main__':
    print("=" * 55)
    print("  QUAN LY KENH NHAN SU - Server dang chay")
    print("=" * 55)
    print("  URL: http://localhost:5000")
    print("  Tai khoan mac dinh: admin / admin123")
    print("  Nhan Ctrl+C de dung")
    print("=" * 55)
    app.run(host='0.0.0.0', port=5000, debug=True)

