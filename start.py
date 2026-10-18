"""One-command setup and launch: python3 start.py (Windows: py start.py)."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
ENV = ROOT / '.venv'
PYTHON = ENV / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')


def run(*args):
    subprocess.run([str(arg) for arg in args], cwd=ROOT, check=True)


def main():
    if sys.version_info < (3, 11):
        raise RuntimeError('Demo cần Python 3.11 trở lên.')
    if not PYTHON.exists():
        print('Chuẩn bị môi trường Python...', flush=True)
        try:
            run(sys.executable, '-m', 'venv', ENV)
        except subprocess.CalledProcessError:
            uv = shutil.which('uv')
            if not uv:
                raise RuntimeError('Máy thiếu hỗ trợ venv. Cài python3-venv hoặc uv rồi chạy lại.') from None
            run(uv, 'venv', '--seed', '--python', sys.executable, ENV)
    check = subprocess.run(
        [str(PYTHON), '-c', 'import requests, bs4, numpy, pandas, streamlit, pytest'],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    if check.returncode:
        print('Cài thư viện cho lần chạy đầu...', flush=True)
        run(PYTHON, '-m', 'pip', 'install', '-r', ROOT / 'requirements.txt')
    if not all((ROOT / 'data' / name).exists() for name in ('traffic_counts.csv', 'source_metadata.json')):
        print('Chuẩn bị dữ liệu nguồn...', flush=True)
        run(PYTHON, ROOT / 'get_data.py')
    # Regenerate the small deterministic experiment to keep dashboard and code aligned.
    print('Chuẩn bị lượt xe và chạy mô phỏng...', flush=True)
    run(PYTHON, ROOT / 'prepare_arrivals.py')
    run(PYTHON, ROOT / 'run_demo.py')
    print('\nMở http://localhost:8501 để xem demo. Nhấn Ctrl+C để dừng.\n', flush=True)
    run(PYTHON, '-m', 'streamlit', 'run', ROOT / 'app.py',
        '--server.port', '8501', '--browser.gatherUsageStats', 'false')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nĐã dừng demo.')
    except (subprocess.CalledProcessError, RuntimeError) as error:
        print(f'Không thể khởi động: {error}', file=sys.stderr)
        sys.exit(1)
