# ====================== 配置 ======================
LINUX_HOST = "116.233.75.237"
LINUX_USER = "media"
LINUX_PASS = "media_bioinfo_biuh"
LINUX_PORT = 13579
REMOTE_OUTPUT_FILE = "/home/media/my_voice.txt"
REMOTE_OUTPUT_FILE_TMP = "/home/media/my_voice_tmp.txt"
SAMPLERATE = 16000
MODEL_PATH = "./turbo/turbo_model"        # 推荐改为 "small" 或 "turbo" 以获得极高准确率
INITIAL_PROMPT = "以下对话中英文都有"
BEAM_SIZE=5
MIN_CUT=0.001
LANG='zh'
TASK='transcribe'

# ===================================================
from datetime import datetime
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import paramiko
import threading
from pynput import keyboard
import os

# ====================================================

print(f"loading Faster-Whisper ...")
# Mac 建议使用 cpu + int8，cpu_threads 建议设为核心数
model = WhisperModel(MODEL_PATH, device="cpu", compute_type="int8", cpu_threads=8)

audio_buffer = []
is_recording = False
lock = threading.Lock()

# --- SSH 连接逻辑 ---
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=LINUX_HOST, username=LINUX_USER, password=LINUX_PASS, port=LINUX_PORT)
    sftp = ssh.open_sftp()
    print("SSH connected")
except Exception as e:
    print(f"SSH error: {e}"); exit()

def send_to_linux(text):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sftp.open(REMOTE_OUTPUT_FILE, "a") as f:
            f.write('['+str(timestamp)+'] '+text.strip() + "\n")
        with sftp.open(REMOTE_OUTPUT_FILE_TMP, "w") as f:
            f.write(text.strip() + "\n")
        print(f"Successfully sent")
        print("Hold [Right Command] to Record")
    except Exception as e:
        print(f"Error: {e}")

def audio_callback(indata, frames, time_, status):
    global is_recording, audio_buffer
    if is_recording:
        with lock:
            audio_buffer.append(indata.copy())

def process_audio():
    global audio_buffer
    with lock:
        if not audio_buffer: return
        data = np.concatenate(audio_buffer, axis=0)
        audio_buffer = []

    audio = data.flatten().astype(np.float32)
    
    # 静音过滤阈值
    if np.abs(audio).mean() < MIN_CUT:
        print("Signal too weak, skipped.     ", end='\n')
        return

    print("Recogonizing...", end='\n')
    try:
        segments, info = model.transcribe(
            audio, 
            task=TASK,
            beam_size=BEAM_SIZE, 
            language=LANG, 
            initial_prompt=INITIAL_PROMPT,
            vad_filter=True, 
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        text = "".join([s.text for s in segments]).strip()
        
        if text:
            #print(f"Result: {text}      ")
            print(f"Result: ")
            print()
            print(text)
            print()
            send_to_linux(text)
        else:
            print("No words detected      ")
    except Exception as e:
        print(f"Error: {e}")

def on_press(key):
    global is_recording, audio_buffer
    # 改为使用左 Command 键 (cmd_l)
    #if key == keyboard.Key.cmd_l:
    # 改为使用右 Command 键 (cmd_r)
    if key == keyboard.Key.cmd_r:
        if not is_recording:
            with lock: audio_buffer = []
            is_recording = True
            print("Please speak (release Command to finish)", end='\n')

def on_release(key):
    global is_recording
    if key == keyboard.Key.cmd_r:
        is_recording = False
        print("Processing...          ", end='\n')
        threading.Thread(target=process_audio).start()
    #elif key == keyboard.Key.esc:
    #    print("\n quit...")
    #    return False

# ====================== 运行 ======================

stream = sd.InputStream(
    samplerate=SAMPLERATE,
    channels=1,
    dtype="float32",
    callback=audio_callback
)

with stream:
    print("Microphone is on (16kHz)")
    print("Hold [Right Command] to Record")
    
    # Mac 上监听非字符键通常不需要 suppress=True，避免了复杂的权限问题
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

print("Finished")
