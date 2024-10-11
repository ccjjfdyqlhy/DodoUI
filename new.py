# Dodo Chat UI
# V3.2 update 241011

CONNECT = False

import customtkinter
import pywinstyles
from gradio_client import Client, handle_file
import threading
import tkinter as tk
import tkinter.messagebox
import subprocess
import os
from Dodo_config import *
from PIL import Image, ImageTk

customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("dark-blue")
cwd = os.getcwd()

root = customtkinter.CTk()
root.geometry("950x600")
root.title("Dodo Hub")

if CONNECT:
    try:
        client = Client(DSN_IP)
    except Exception as e:
        print("无法连接到 DSN 后端。错误信息：" + str(e))

def close():
    root.destroy()

root.protocol("WM_DELETE_WINDOW", close)

sidebar = customtkinter.CTkFrame(root, width=35, corner_radius=0)
sidebar.pack(side="left", fill="y")

icon_paths = {
    "💬": cwd + "\\icons\\interact.png",
    "📞": cwd + "\\icons\\talk.png",
    "🖼️": cwd + "\\icons\\image.png",
    "🔍": cwd + "\\icons\\search.png",
    "✨": cwd + "\\icons\\apps.png",
    "👤": cwd + "\\icons\\account.png",
    "⚙️": cwd + "\\icons\\settings.png",
    "➕": cwd + "\\icons\\add.png",  # 添加新建交互图标
    "☑": cwd + "\\icons\\select.png",  # 添加批量选择图标
    "🗑️": cwd + "\\icons\\delete.png",  # 添加删除图标
    "❌": cwd + "\\icons\\cancel.png",  # 添加取消图标
    "🔄": cwd + "\\icons\\rename.png",  # 添加重命名图标
}

icons = {}
for text, path in icon_paths.items():
    try:
        img = Image.open(path)
        icons[text] = customtkinter.CTkImage(light_image=img, dark_image=img, size=(20, 20))
    except FileNotFoundError:
        print(f"找不到图标文件：{path}")
        icons[text] = None

all_buttons = []

for text, icon in icons.items():
    if text in ["👤", "⚙️", "➕", "☑", "🗑️", "❌", "🔄"]:
        continue

    button = customtkinter.CTkButton(
        master=sidebar,
        image=icon,
        width=30,
        text="",
        fg_color="transparent",
        hover_color="gray70",
        command=lambda icon=icon: switch_tab([b["image"] for b in all_buttons].index(icon))
    )
    all_buttons.append({"image": icon})
    button.pack(pady=(10, 0))

bottom_buttons = ["👤", "⚙️"]
for text in bottom_buttons:
    button = customtkinter.CTkButton(
        master=sidebar,
        image=icons[text],
        width=30,
        text="",
        fg_color="transparent",
        hover_color="gray70",
        command=lambda icon=icons[text]: switch_tab([b["image"] for b in all_buttons].index(icon))
    )
    all_buttons.append({"image": icons[text]})
    button.pack(side="bottom", pady=(0, 10), anchor="s")

content_frame = customtkinter.CTkFrame(root)
content_frame.pack(side="right", fill="both", expand=True)

tabs = []
for i in range(7):
    tab = customtkinter.CTkFrame(content_frame)
    tabs.append(tab)

current_tab = 0
tabs[current_tab].pack(fill="both", expand=True)

def switch_tab(tab_index):
    global current_tab
    tabs[current_tab].pack_forget()
    current_tab = tab_index
    tabs[current_tab].pack(fill="both", expand=True)

# 交互Tab左侧列表
interaction_list_frame = customtkinter.CTkFrame(tabs[0], width=250)
interaction_list_frame.pack(side="left", fill="y")

# 列表内容区域
interaction_list_content = customtkinter.CTkFrame(interaction_list_frame, width=250)
interaction_list_content.pack(pady=(10, 0), fill="both", expand=True)

# 使用枚举按钮显示列表
interaction_buttons = []
interaction_files = []
selected_files = set()  # 使用 set 存储选中的文件

# 批量操作模式标志
batch_mode = False

def refresh_interaction_list():
    """刷新交互记录列表"""
    global interaction_buttons, interaction_files
    for button in interaction_buttons:
        button.destroy()
    interaction_buttons.clear()
    interaction_files.clear()

    # 移除 "没有交互记录" 标签 (如果存在)
    for widget in interaction_list_content.winfo_children():
        if isinstance(widget, customtkinter.CTkLabel) and widget.cget("text") == "没有交互记录":
            widget.destroy()
            break  # 只移除第一个匹配的标签

    saves_dir = os.path.join(cwd, "saves")
    if not os.path.exists(saves_dir):
        os.makedirs(saves_dir)
    files = [f for f in os.listdir(saves_dir) if os.path.isfile(os.path.join(saves_dir, f)) and f.endswith(".din")]

    if not files:
        no_interactions_label = customtkinter.CTkLabel(interaction_list_content, text="没有交互记录", width=230)
        no_interactions_label.pack(pady=(10, 0))
    else:
        for file in files:
            interaction_files.append(file)
            button = customtkinter.CTkButton(
                interaction_list_content,
                text=file[:-4],
                width=230,  # 设置按钮宽度
                command=lambda fn=file: select_interaction(fn)  # 调用 select_interaction
            )
            button.pack(pady=(5, 0))
            interaction_buttons.append(button)


def add_interaction():
    """创建新的交互记录文件"""
    filename = "新交互会话.din"
    i = 1
    saves_dir = os.path.join(cwd, "saves")
    while os.path.exists(os.path.join(saves_dir, filename)):
        filename = f"新交互会话({i}).din"
        i += 1
    with open(os.path.join(saves_dir, filename), "w") as f:
        pass
    refresh_interaction_list()


def select_interaction(file):
    # TODO: 实现加载交互记录的功能
    print(f"选择了交互记录 {file}")
    if batch_mode:
        select_file(file)  # 仅在批量模式下调用 select_file


def batch_operation():
    """进入批量操作模式"""
    global batch_mode
    batch_mode = True
    new_interaction_button.pack_forget()
    batch_select_button.pack_forget()
    delete_button.pack(side="left", pady=(0, 10), padx=(0, 5))
    rename_button.pack(side="left", pady=(0, 10), padx=(0, 5))  # 显示重命名按钮
    cancel_button.pack(side="left", pady=(0, 10), padx=(5, 0))


def delete_interactions():
    """删除选中的交互记录文件"""
    global interaction_files
    if not selected_files:
        tk.messagebox.showwarning("警告", "请选择要删除的文件！")
        return

    if tk.messagebox.askyesno("确认删除", "确定要删除选中的文件吗？"):
        saves_dir = os.path.join(cwd, "saves")
        for filename in selected_files:
            os.remove(os.path.join(saves_dir, filename))
        selected_files.clear()
        refresh_interaction_list()
        exit_batch_mode()


def rename_interaction():
    """重命名选中的交互记录文件"""
    global interaction_files
    if len(selected_files) != 1:
        tk.messagebox.showwarning("警告", "请选择一个要重命名的文件！")
        return

    old_filename = list(selected_files)[0]
    new_filename = tk.simpledialog.askstring("重命名", f"请输入新的文件名 (不包含 .din 后缀):\n当前文件名: {old_filename[:-4]}")
    if new_filename is None or new_filename.strip() == "":
        return  # 用户取消或输入空文件名

    saves_dir = os.path.join(cwd, "saves")
    new_filename = new_filename.strip() + ".din"
    if os.path.exists(os.path.join(saves_dir, new_filename)):
        tk.messagebox.showwarning("警告", f"文件名 {new_filename} 已存在！")
        return

    os.rename(os.path.join(saves_dir, old_filename), os.path.join(saves_dir, new_filename))
    selected_files.clear()
    refresh_interaction_list()
    exit_batch_mode()


def cancel_batch():
    """取消批量操作"""
    exit_batch_mode()


def exit_batch_mode():
    """退出批量操作模式"""
    global batch_mode
    batch_mode = False
    delete_button.pack_forget()
    rename_button.pack_forget()  # 隐藏重命名按钮
    cancel_button.pack_forget()
    new_interaction_button.pack(side="left", pady=(0, 10), padx=(0, 5))
    batch_select_button.pack(side="left", pady=(0, 10), padx=(5, 0))
    selected_files.clear()
    refresh_interaction_list()


def select_file(filename):
    """选中或取消选中文件"""
    if filename in selected_files:
        selected_files.remove(filename)
    else:
        selected_files.add(filename)

    # 更新按钮颜色
    for button in interaction_buttons:
        if button.cget("text") == filename[:-4]:  # 去除 .din 后缀
            if filename in selected_files:
                button.configure(fg_color="gray")
            else:
                button.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
            break


# 列表底部按钮框架
bottom_buttons_frame = customtkinter.CTkFrame(interaction_list_frame)
bottom_buttons_frame.pack(side="bottom", fill="x")

# 新建交互按钮
new_interaction_button = customtkinter.CTkButton(
    master=bottom_buttons_frame,
    image=icons["➕"],
    width=25,
    text="",
    fg_color="transparent",
    hover_color="gray70",
    command=add_interaction
)
new_interaction_button.pack(side="left", pady=(0, 10), padx=(0, 5))

# 批量选择按钮 (现在触发批量操作模式)
batch_select_button = customtkinter.CTkButton(
    master=bottom_buttons_frame,
    image=icons["☑"],
    width=25,
    text="",
    fg_color="transparent",
    hover_color="gray70",
    command=batch_operation  # 直接进入批量操作模式
)
batch_select_button.pack(side="left", pady=(0, 10), padx=(5, 0))

# 删除按钮
delete_button = customtkinter.CTkButton(
    master=bottom_buttons_frame,
    image=icons["🗑️"],
    width=25,
    text="",
    fg_color="transparent",
    hover_color="gray70",
    command=delete_interactions
)

# 重命名按钮
rename_button = customtkinter.CTkButton(
    master=bottom_buttons_frame,
    image=icons["🔄"],
    width=25,
    text="",
    fg_color="transparent",
    hover_color="gray70",
    command=rename_interaction
)

# 取消按钮
cancel_button = customtkinter.CTkButton(
    master=bottom_buttons_frame,
    image=icons["❌"],
    width=25,
    text="",
    fg_color="transparent",
    hover_color="gray70",
    command=cancel_batch
)

# 初始化交互记录列表
refresh_interaction_list()

# 交互区
interaction_frame = customtkinter.CTkFrame(tabs[0])
interaction_frame.pack(side="right", fill="both", expand=True)

ai_response_label = customtkinter.CTkLabel(interaction_frame, text="", wraplength=700)
ai_response_label.pack(pady=(10, 0))

# 交互输入框移动到交互区底部
user_input = customtkinter.CTkEntry(interaction_frame, width=700, height=35,
                                    fg_color="white", text_color="black",
                                    font=("Microsoft YaHei", 15),
                                    placeholder_text="给 Dodo 发送指令...")
user_input.pack(side="bottom", pady=(0, 10))

def send_message(message):
    if message:
        user_input.delete(0, "end")
        threading.Thread(target=get_ai_response, args=(message,)).start()

def get_ai_response(message):
    file_path = cwd + '\\TEMP\\latest_reply.txt'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8-sig") as f:
        f.write('')

    chat_history = []
    try:
        result = client.predict(
            message=message,
            chat_history=chat_history,
            audio=None,
            image=None,
            api_name="/predict"
        )
        chat_history = result[0]
        ai_response = result[0][-1][-1]
        audio_files = result[2]
    except Exception as e:
        ai_response = f"错误: {e}"
        audio_files = []


    with open(file_path, "w", encoding="utf-8-sig") as f:
        f.write(ai_response)

    ai_response_label.configure(text=ai_response)
    subprocess.run([PYTHON, cwd + '\\Dodo_msgbox.py', file_path] + audio_files)


user_input.bind("<Return>", lambda event: send_message(user_input.get()))

# 其他 Tab 内容不变
tabs[1].pack_propagate(0)
chat_history_label = customtkinter.CTkLabel(tabs[1], text="实时讨论功能开发中...", wraplength=900)
chat_history_label.pack(pady=(10, 0))

tabs[2].pack_propagate(0)
image_gen_label = customtkinter.CTkLabel(tabs[2], text="图片生成检索功能开发中...", wraplength=900)
image_gen_label.pack(pady=(10, 0))

tabs[3].pack_propagate(0)
search_label = customtkinter.CTkLabel(tabs[3], text="搜索功能开发中...", wraplength=900)
search_label.pack(pady=(10, 0))

tabs[4].pack_propagate(0)
extensions_label = customtkinter.CTkLabel(tabs[4], text="拓展应用功能开发中...", wraplength=900)
extensions_label.pack(pady=(10, 0))

tabs[5].pack_propagate(0)
user_label = customtkinter.CTkLabel(tabs[5], text="用户页面开发中...", wraplength=900)
user_label.pack(pady=(10, 0))

tabs[6].pack_propagate(0)
settings_label = customtkinter.CTkLabel(tabs[6], text="设置页面开发中...", wraplength=900)
settings_label.pack(pady=(10, 0))

root.mainloop()