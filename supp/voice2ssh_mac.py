# ====================== 配置 ======================
LINUX_HOST = "116.233.75.237"
LINUX_USER = "media"
LINUX_PASS = "media_bioinfo_biuh"
LINUX_PORT = 13579
REMOTE_OUTPUT_FILE = "/home/media/my_voice.txt"
REMOTE_OUTPUT_FILE_TMP = "/home/media/my_voice_tmp.txt"
SAMPLERATE = 16000
MODEL_PATH = "/Users/zhangfeng/Documents/models/turbo/turbo_model"        # 推荐改为 "small" 或 "turbo" 以获得极高准确率
INITIAL_PROMPT = "以下对话中英文都有"
BEAM_SIZE=5
MIN_CUT=0.001
LANG='zh'
TASK='transcribe'
DEBOUNCE_TIME = 0.5

# ===================================================
from datetime import datetime
import time
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import paramiko
import threading
from pynput import keyboard
import os
# ====================================================
is_processing = False 
last_action_time = 0
# ====================================================


def get_timestamp():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output='['+str(timestamp)+'] '
    return(output)

def print_ts(text):
    output=get_timestamp()+text
    print(output)


print(get_timestamp()+f"loading Faster-Whisper ...")
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
    print_ts("SSH connected")
except Exception as e:
    print_ts(f"SSH error: {e}"); exit()

def send_to_linux(text):
    try:
        if text.strip() !='':
            with sftp.open(REMOTE_OUTPUT_FILE, "a") as f:
                f.write(get_timestamp()+text.strip() + "\n")
            with sftp.open(REMOTE_OUTPUT_FILE_TMP, "w") as f:
                f.write(text.strip() + "\n")
            print_ts(f"Successfully sent")
        else:
            print_ts('Empty')
    except Exception as e:
        print_ts(f"Error: {e}")

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
        print_ts("Signal too weak, skipped.     ")
        return

    print_ts("Recogonizing...")
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
            print_ts("Recognized: "+text)
            send_to_linux(text)
        else:
            print(get_timestamp()+"No words detected")
    except Exception as e:
        print_ts(f"Error: {e}")

def on_press(key):
    global is_recording, audio_buffer, is_processing, last_action_time   
    if key == keyboard.Key.cmd_r:
        current_time = time.time()
        
        # --- 场景1：防抖过滤（防止连点） ---
        if current_time - last_action_time < DEBOUNCE_TIME:
            return # 间隔太短，忽略本次按键

        # --- 场景2：识别中保护 ---
        if is_processing:
            print_ts("Still processing, please wait...")
            return

        last_action_time = current_time # 更新最后操作时间

        if not is_recording:
            # 开始录音
            with lock: audio_buffer = []
            is_recording = True
            print_ts("Recording... (Press Right Command to stop)")
        else:
            # 停止录音并开始识别
            is_recording = False
            is_processing = True # 进入识别状态锁
            print_ts("Processing...")
            threading.Thread(target=wrapped_process_audio).start()

def wrapped_process_audio():
    global is_processing
    try:
        process_audio()
    finally:
        # 无论成功还是报错，最后都要释放锁
        print_ts("Ready for next command.")
        print_ts("Press [Right Command] to Record")
        is_processing = False

def on_release(key):
    pass
    #global is_recording
    #if key == keyboard.Key.cmd_r:
    #    is_recording = False
    #    print(get_timestamp()+"Processing...", end='\n')
    #    threading.Thread(target=process_audio).start()
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
    print_ts("Microphone is on (16kHz)")
    print_ts("Press [Right Command] to Record")
    
    # Mac 上监听非字符键通常不需要 suppress=True，避免了复杂的权限问题
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

print("Finished")
