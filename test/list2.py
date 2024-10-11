import os
import tkinter as tk
import tkinter.messagebox
import customtkinter as ctk


def refresh_list():
    """刷新文件列表"""
    # 清空按钮列表和容器
    for button in button_list:
        button.destroy()
    button_list.clear()

    # 遍历文件并创建按钮
    for filename in os.listdir("saves"):
        if filename.endswith(".din"):
            button = ctk.CTkButton(
                button_frame,
                text=filename,
                command=lambda fn=filename: select_file(fn),
            )
            button.pack(fill=tk.X, padx=10, pady=5)
            button_list.append(button)


def create_file():
    """创建新文件"""
    filename = "新交互会话.din"
    i = 1
    while os.path.exists(f"saves/{filename}"):
        filename = f"新交互会话({i}).din"
        i += 1
    with open(f"saves/{filename}", "w") as f:
        pass
    refresh_list()


def batch_operation():
    """进入批量操作模式"""
    global batch_mode
    batch_mode = True
    batch_button.configure(text="删除", command=delete_files)
    cancel_button.pack(pady=(0, 10))


def delete_files():
    """删除选中的文件"""
    if not selected_files:
        tk.messagebox.showwarning("警告", "请选择要删除的文件！")
        return

    if tk.messagebox.askyesno("确认删除", "确定要删除选中的文件吗？"):
        for filename in selected_files:
            os.remove(f"saves/{filename}")
        selected_files.clear()
        refresh_list()
        exit_batch_mode()


def cancel_batch():
    """取消批量操作"""
    exit_batch_mode()


def exit_batch_mode():
    """退出批量操作模式"""
    global batch_mode
    batch_mode = False
    batch_button.configure(text="批量操作", command=batch_operation)
    cancel_button.pack_forget()
    selected_files.clear()
    refresh_list()


def select_file(filename):
    """选中或取消选中文件"""
    if filename in selected_files:
        selected_files.remove(filename)
    else:
        selected_files.add(filename)

    # 更新按钮颜色
    for button in button_list:
        if button.cget("text") == filename:
            if filename in selected_files:
                button.configure(fg_color="gray")
            else:
                button.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
            break


# 设置外观模式和主题
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# 创建主窗口
root = ctk.CTk()
root.title("DIN文件管理器")

# 创建按钮容器
button_frame = ctk.CTkFrame(root)
button_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# 按钮列表和选中文件列表
button_list = []
selected_files = set()

# 批量操作模式标志
batch_mode = False

# 创建按钮
create_button = ctk.CTkButton(root, text="创建新文件", command=create_file)
create_button.pack(pady=(0, 10))

batch_button = ctk.CTkButton(root, text="批量操作", command=batch_operation)
batch_button.pack(pady=(0, 10))

cancel_button = ctk.CTkButton(root, text="取消", command=cancel_batch)

# 初始化文件列表
if not os.path.exists("saves"):
    os.makedirs("saves")
refresh_list()

root.mainloop()