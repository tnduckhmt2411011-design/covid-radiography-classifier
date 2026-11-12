"""Chụp màn hình demo Streamlit đang chạy thật, bằng Chrome ở chế độ headless.

Luồng: mở trang Streamlit trên ``localhost:8501``, nạp một ảnh ``val`` qua đúng
ô tải tệp của ứng dụng, chờ mô hình trả kết quả, chụp một khung. Ứng dụng tự
chặn ảnh thuộc split ``test`` (cổng H2) nên ảnh chụp ra luôn là ảnh ``val``.

Cách chạy::

    python -m slides.capture_demo --image COVID-1006.png --out slides/assets/screenshot_demo.png
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
import time
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parents[1]
CXR_ROOT = Path(r"D:\cxr_data\COVID-19_Radiography_Dataset")
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
PORT = 9222
APP_URL = "http://127.0.0.1:8501/"

WAIT_READY = 60
WAIT_RESULT = 120


class Session:
    """Một kết nối CDP duy nhất: trạng thái DOM chỉ sống trong một phiên."""

    def __init__(self, session_id: str):
        import websocket

        self.socket = websocket.create_connection(
            f"ws://127.0.0.1:{PORT}/devtools/page/{session_id}", timeout=60
        )
        self.counter = 0

    def call(self, method: str, params: dict | None = None) -> dict:
        self.counter += 1
        self.socket.send(json.dumps({"id": self.counter, "method": method, "params": params or {}}))
        while True:
            payload = json.loads(self.socket.recv())
            if payload.get("id") == self.counter:
                if "error" in payload:
                    raise RuntimeError(f"{method} lỗi: {json.dumps(payload['error'])[:200]}")
                return payload.get("result", {})

    def evaluate(self, expression: str):
        return self.call("Runtime.evaluate", {"expression": expression,
                                              "returnByValue": True}).get("result", {}).get("value")

    def close(self) -> None:
        self.socket.close()


def find_session_id() -> str:
    response = requests.get(f"http://127.0.0.1:{PORT}/json", timeout=10).json()
    for entry in response:
        if entry.get("type") == "page" and entry.get("url", "").startswith("http://127.0.0.1:8501"):
            return entry["webSocketDebuggerUrl"].rsplit("/", 1)[-1]
    raise RuntimeError("không thấy trang Streamlit trong danh sách CDP")


def launch_browser(args) -> subprocess.Popen | None:
    """Đã có Chrome mở cổng debug thì dùng lại, nếu không thì mở mới."""
    try:
        requests.get(f"http://127.0.0.1:{PORT}/json/version", timeout=3).raise_for_status()
        return None
    except Exception:
        pass
    profile = Path.home() / "AppData/Local/Temp/opencode/chrome_deck_profile"
    profile.mkdir(parents=True, exist_ok=True)
    return subprocess.Popen([
        str(CHROME), "--headless=new", f"--remote-debugging-port={PORT}",
        f"--user-data-dir={profile}", f"--window-size={args.width},{args.height}",
        "--hide-scrollbars", "--no-first-run", "--disable-extensions", APP_URL,
    ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default="COVID-1006.png")
    parser.add_argument("--out", default=str(REPO / "slides/assets/screenshot_demo.png"))
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=1000)
    args = parser.parse_args()

    source = next(CXR_ROOT.rglob(args.image))
    print(f"ảnh nguồn: {source} (lớp {source.parent.parent.name})")

    try:
        import websocket  # noqa: F401
    except ImportError:
        print("thiếu gói websocket-client; cài bằng: pip install websocket-client")
        return 2

    browser = launch_browser(args)
    session = None
    try:
        deadline = time.time() + 30
        while True:
            try:
                requests.get(f"http://127.0.0.1:{PORT}/json/version", timeout=2).raise_for_status()
                break
            except Exception:
                if time.time() > deadline:
                    raise
                time.sleep(1)

        session = Session(find_session_id())
        session.call("Page.enable")
        deadline = time.time() + WAIT_READY
        while time.time() < deadline:
            if session.evaluate("!!document.querySelector('input[data-testid=\"stFileUploaderDropzoneInput\"]')"):
                break
            time.sleep(1)
        print("đã thấy ô tải tệp")

        node = None
        session.call("DOM.enable")
        for _ in range(6):
            document = session.call("DOM.getDocument")["root"]["nodeId"]
            node = session.call("DOM.querySelector", {
                "nodeId": document,
                "selector": "input[data-testid=\"stFileUploaderDropzoneInput\"]",
            }).get("nodeId")
            if node:
                break
            time.sleep(1)
        if not node:
            raise RuntimeError("không lấy được nút tải tệp của Streamlit")
        session.call("DOM.setFileInputFiles", {"nodeId": node, "files": [str(source)]})
        print("đã nạp ảnh", source.name)

        marker = time.time()
        text = ""
        while time.time() - marker < WAIT_RESULT:
            text = session.evaluate("document.body.innerText") or ""
            if "Xác suất" in text or ("Dự đoán" in text and "COVID" in text):
                break
            time.sleep(2)
        time.sleep(3)
        print("đợi kết quả xong; độ dài văn bản trang:", len(text))

        data = session.call("Page.captureScreenshot",
                            {"format": "png", "captureBeyondViewport": True}).get("data")
        if not data:
            print("chụp thất bại")
            return 3
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)))
        print("đã ghi", out, out.stat().st_size, "byte")
        return 0
    finally:
        if session is not None:
            session.close()
        if browser is not None:
            browser.terminate()


if __name__ == "__main__":
    sys.exit(main())
