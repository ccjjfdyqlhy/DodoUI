import customtkinter
from gradio_client import Client
import threading
import tkinter as tk
import pyaudio
import wave
import os
import re
import subprocess
import datetime
import pywinstyles
import time
from PIL import Image
from tkinter import filedialog
from Dodo_config import *

CONNECT = True

customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("dark-blue")
cwd = os.getcwd()
action_cnt = 0
p = pyaudio.PyAudio()
recording = False
audio_frames = []

# 函数定义

def play_audio(file_path):
    """播放音频文件"""
    try:
        wf = wave.open(file_path, 'rb')
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)

        stream.stop_stream()
        stream.close()

    except Exception as e:
        print(f"播放音频文件 {file_path} 出错: {e}")

def close():
    root.destroy()

def add_message_to_ui(message, sender):
    """将消息添加到 UI"""
    chat_history_text.configure(state="normal")  # 允许编辑
    for line in message.split("\n"):
        if line != "" and line != " " and line != "\n":
            if sender == "":
                chat_history_text.insert("end", f"{line}\n")
            elif sender == "user":
                chat_history_text.insert("end", f'"{line}"\n')
            elif sender == "AI":
                chat_history_text.insert("end", f"{line}\n\n", "ai")
            elif sender == "audio":  # 新增音频消息类型
                chat_history_text.insert("end", f"[发送了一段录音]\n")
            else:
                chat_history_text.insert("end", f"{sender}: {line}\n")
    chat_history_text.configure(state="disabled")  # 设置为只读
    chat_history_text.see("end")  # 滚动到最后

def send_message(message=None, audio_file=None, image_file=None):
    """发送消息，可以是文本、音频或图片"""
    if message or audio_file or image_file:
        if message:
            add_message_to_ui(message, "user")
            user_input.delete(0, "end")
        elif audio_file:
            add_message_to_ui("[发送了一段音频]", "audio")  # 添加音频消息提示
        elif image_file:
            add_message_to_ui("[发送了一张图片]", "")  # 添加图片消息提示
        threading.Thread(target=get_ai_response, args=(message, audio_file, image_file)).start()

def get_ai_response(message=None, audio_file=None, image_file=None, iostream=''):
    file_path = cwd + '\\TEMP\\latest_reply.txt'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8-sig") as f:
        f.write('')

    global chat_history
    try:
        print('Predicting with tts enabled: '+str(tts_enabled))
        result = client.predict(
            message=message,
            chat_history=chat_history,
            audio=audio_file,  # 传递音频文件路径
            image=image_file,  # 传递图片文件路径
            iostream=iostream,
            silent=not(tts_enabled),
            api_name="/predict"
        )
        chat_history, _, _ = result
        last_output = chat_history[-1][1]
        action_cnt = 0

        # 判断回复是否包含代码
        if is_code_response(last_output):
            # 运行代码并获取输出
            io = run_command_or_code(last_output,action_cnt)
            if io:
                get_ai_response(iostream=io)

        with open(file_path, "w", encoding="utf-8-sig") as f:
            f.write(last_output)

        chat_history[-1][1] = last_output
        if last_output.endswith("？  。") or last_output.endswith("！  。"):
            last_output = last_output[:-1]
        add_message_to_ui(last_output, "AI")

        if tts_enabled:
            for file in result[2]:
                play_audio(file)
        else:
            pass
    except Exception as e:
        ai_response = f"错误: {e}"
        chat_history[-1][1] = ai_response
        add_message_to_ui(ai_response, "系统")

def toggle_tts():
    """切换 TTS 启用/关闭状态"""
    global tts_enabled
    tts_enabled = not tts_enabled
    if tts_enabled:
        tts_button.configure(image=icons["📢"])
    else:
        tts_button.configure(image=icons["🔇"])

def reset_context():
    """重置上下文"""
    global chat_history
    chat_history = []
    chat_history_text.configure(state="normal")
    chat_history_text.delete("1.0", "end")
    chat_history_text.configure(state="disabled")
    print("重置上下文")

def extract_code(output):
    """提取代码块中的代码"""
    match = re.search(r"```python(.*?)```", output, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def run_command_or_code(output,action_cnt):
    """运行命令或代码并返回输出"""
    iostream = ""
    if output.startswith('cmd /c'):
        folder = cwd + "\\TEMP\\"
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(folder + 'latest_cmd.txt', "w", encoding="utf-8-sig") as f:
            f.write(output)
        subprocess.Popen([PYTHON, cwd + '\\cmdctrl.py'])  # 假设 cmdctrl.py 用于执行命令并输出到 cmd_output.txt
        try:
            open(folder + 'cmd_output.txt', "r")
        except FileNotFoundError:
            time.sleep(1)
        with open(folder + 'cmd_output.txt', "r", encoding="utf-8-sig") as f:
            iostream = f.read()
        print("Executed cmd")
    elif output.startswith('```python'):
        folder = cwd + "\\generated\\program_history"
        if not os.path.exists(folder):
            os.makedirs(folder)
        time_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        history_file_path = os.path.join(folder, f"program{time_str}.py")
        code_content = extract_code(output)
        with open(history_file_path, "w", encoding="utf-8-sig") as f:
            f.write(code_content)
        if not os.path.exists('TEMP'):
            os.makedirs('TEMP')
        with open(cwd + '\\TEMP\\historydest.txt', 'w', encoding='utf-8') as f:
            f.write(history_file_path)
        coderunner = subprocess.Popen([PYTHON, cwd + '\\coderunner.py'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # 假设 coderunner.py 用于执行Python代码并输出结果
        stdout, stderr = coderunner.communicate()
        iostream = stdout.decode('gbk') + stderr.decode('gbk')
        print('Executed code')
    if iostream == '' or iostream == '[]':
        iostream = '无输出，操作可能成功完成。'
    action_cnt += 1
    add_message_to_ui('[执行了 '+str(action_cnt)+' 个动作]', "")
    return iostream

def is_code_response(output):
    """判断回复是否包含代码"""
    return output.startswith('cmd /c') or output.startswith('```python')

def upload_image():
    """上传图片文件"""
    file_path = filedialog.askopenfilename(
        title="选择图片文件",
        filetypes=(("图片文件", "*.jpg;*.jpeg;*.png;*.bmp"))
    )
    if file_path:
        send_message(image_file=file_path)

# 主程序

root = customtkinter.CTk()
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
pywinstyles.apply_style(root, "acrylic")
root.geometry("600x400")
root.title("Interaction")

if CONNECT:
    try:
        client = Client(DSN_IP)
    except Exception as e:
        print("无法连接到 DSN 后端。错误信息：" + str(e)+'\n要以测试模式启动，请设置CONNECT = False。')

root.protocol("WM_DELETE_WINDOW", close)

# 图标
icon_paths = {
    "📢": cwd + "\\icons\\tts_on.png",  # 添加 TTS 启用图标
    "🔇": cwd + "\\icons\\tts_off.png", # 添加 TTS 关闭图标
    "🤔": cwd + "\\icons\\inference.png",  # 添加推理图标
    "🖼️": cwd + "\\icons\\image.png",  # 添加图片上传图标
}

icons = {}
for text, path in icon_paths.items():
    try:
        img = Image.open(path)
        icons[text] = customtkinter.CTkImage(light_image=img, dark_image=img, size=(20, 20))
    except FileNotFoundError:
        print(f"找不到图标文件：{path}")
        icons[text] = None

# 聊天记录框
chat_history_text = customtkinter.CTkTextbox(root, width=580, height=335, wrap="word", font=("Microsoft YaHei", 14), state="disabled")
chat_history_text.pack(pady=(10, 0), padx=10)

# 输入框和按钮框架
input_frame = customtkinter.CTkFrame(root)
input_frame.pack(side="bottom", fill="x", pady=(0, 10), padx=10)

# 输入框
user_input = customtkinter.CTkEntry(input_frame, width=400, height=35,
                                    fg_color="transparent", text_color="grey70",
                                    font=("Microsoft YaHei", 14),
                                    placeholder_text="输入消息...")
user_input.pack(side="left", padx=(0, 10), expand=True, fill="x")

# 发送按钮
send_button = customtkinter.CTkButton(input_frame, image=icons["🤔"], text="", width=30, height=30,
                                      fg_color="transparent",
                                      hover_color="gray10",
                                      command=lambda: send_message(user_input.get()))
send_button.pack(side="left", padx=(0, 10))

# TTS 按钮 (初始状态为启用)
tts_enabled = True
tts_button = customtkinter.CTkButton(input_frame, image=icons["📢"], text="", width=30, height=30,
                                      fg_color="transparent",
                                      hover_color="gray10",
                                      command=toggle_tts)
tts_button.pack(side="left", padx=(0, 10))

user_input.bind("<Return>", lambda event: send_message(user_input.get()))

# 初始化聊天历史
chat_history = []

root.mainloop()