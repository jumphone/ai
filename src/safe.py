from .common_imports import *
from .config import *


def fast_verify_key(api_key, base_url):
    try:
        # 手动构造请求，看看到底能不能连上你的 FastAPI
        headers = {"Authorization": f"Bearer {api_key}"}
        url = f"{base_url.rstrip('/')}/models"
        #print(url) 
        # 增加 verify=False 排除证书问题
        with httpx.Client(verify=False, timeout=5.0) as c:
            resp = c.get(url, headers=headers)
            #print(f"状态码: {resp.status_code}, 内容: {resp.text[:100]}")
            return resp.status_code == 200
    except Exception as e:
        #print(f"连接中转服务器失败: {e}")
        return False


def getpass_star(prompt="请输入密码："):
    """密码输入，显示 * 号"""
    print(prompt, end="", flush=True)
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        password = []
        while True:
            ch = sys.stdin.read(1)
            if ch == "\n" or ch == "\r":
                print()
                break
            if ch == "\x7f":
                if password:
                    password.pop()
                    print("\b \b", end="", flush=True)
                continue
            password.append(ch)
            print("*", end="", flush=True)
        return "".join(password)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("\n", end="", flush=True)

