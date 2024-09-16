
# Dodo Chat UI
# V2.1 update 240916

import customtkinter
import time
import pywinstyles
from gradio_client import Client, handle_file
import threading
import tkinter as tk  # 导入 tkinter 用于获取屏幕尺寸
import Dodo_msgbox
import subprocess
import os
from Dodo_config import *

# 设置 CustomTkinter 主题
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
cwd = os.getcwd()
root = customtkinter.CTk()
if not WINDOWED:
    root.overrideredirect(1)
    root.geometry(str(WIDTH + 20) + "x55")
else:
    root.geometry(str(WIDTH + 20) + "x90")  # 调整窗口大小
root.title("Dodo Chat")

# 应用透明样式
pywinstyles.apply_style(root, "acrylic")
if not DESKTOP and not WINDOWED:
    root.wm_attributes("-topmost", True)  # 保持窗口置顶
running = True

# 获取屏幕宽度和高度
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# 计算窗口左上角坐标，使其居中
x = (screen_width - WIDTH) // 2 + MOVE_RIGHT
y = (screen_height - 35) // 2 + MOVE_DOWN

# 设置窗口位置
root.geometry(f"+{x}+{y}")

# Gradio 客户端
try:
    client = Client(DSN_IP)
except Exception as e:
    print("无法连接到 DSN 后端。错误信息："+str(e))

# 关闭窗口
def close():
    global running
    running = False
    root.destroy()  # 关闭窗口

root.protocol("WM_DELETE_WINDOW", close)  # 绑定关闭窗口事件
if not DESKTOP and not WINDOWED:
    root.bind("<Escape>", lambda event: close())

# 用户输入框
user_input = customtkinter.CTkEntry(root, width=WIDTH, height=35,
                                    fg_color="gray30", text_color="white",
                                    font=("Microsoft YaHei", 15),
                                    placeholder_text="给 Dodo 发送指令...")  # 添加 placeholder
user_input.place(x=10, y=10)

#  白色的文字标签
text_label = customtkinter.CTkLabel(root, text="Dodo AI Action 1.2.0 - Powered by DSN",
                                     text_color="white", font=("Microsoft YaHei", 12))
if WINDOWED:
    text_label.place(x=10, y=55) 

# 绑定回车键到发送消息
user_input.bind("<Return>", lambda event: send_message(user_input.get()))

# 发送消息到 API
def send_message(message):
    if message:
        user_input.delete(0, "end")  # 清空输入框
        # 在新线程中调用 API 以避免阻塞 UI
        threading.Thread(target=get_ai_response, args=(message,)).start()


def get_ai_response(message):
    file_path = cwd + '\\TEMP\\latest_reply.txt'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8-sig") as f:
        f.write('')
    result = client.predict(
        message=message,
        audio=None,
        image=None,
        api_name="/predict"
    )
    print(result)
    ai_response = result[0][-1][-1]
    print(ai_response)
    parts = ai_response.split("[[")
    if len(parts) > 1:
        normal_text = parts[0]
        highlighted_parts = []
        for part in parts[1:]:
            highlighted_text, remaining_text = part.split("]]", 1)
            highlighted_parts.append(highlighted_text)
            highlighted_text = highlighted_parts[0]
            normal_text += remaining_text
    else:
        normal_text = ai_response
        highlighted_text = "Reply"
    with open(file_path, "w", encoding="utf-8-sig") as f:
        f.write(ai_response)
    subprocess.run('cmd /c ' + PYTHON + ' ' + cwd + '\\Dodo_msgbox.py "' + file_path + '"')

while running:
    root.update_idletasks()
    root.update()
    time.sleep(0.1)