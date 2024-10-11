import os
import tkinter as tk
from tkinter import filedialog, messagebox

def refresh_list():
    """刷新文件列表"""
    listbox.delete(0, tk.END)
    for filename in os.listdir("saves"):
        if filename.endswith(".din"):
            listbox.insert(tk.END, filename)

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

def delete_files():
    """删除选中的文件"""
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("警告", "请选择要删除的文件！")
        return
    
    if messagebox.askyesno("确认删除", "确定要删除选中的文件吗？"):
        for index in selected[::-1]:  # 逆序删除，避免索引错乱
            filename = listbox.get(index)
            os.remove(f"saves/{filename}")
        refresh_list()

# 创建主窗口
root = tk.Tk()
root.title("DIN文件管理器")

# 创建列表框
listbox = tk.Listbox(root, selectmode=tk.EXTENDED)
listbox.pack(fill=tk.BOTH, expand=True)

# 创建按钮
create_button = tk.Button(root, text="创建新文件", command=create_file)
create_button.pack()

delete_button = tk.Button(root, text="删除选中文件", command=delete_files)
delete_button.pack()

# 初始化文件列表
if not os.path.exists("saves"):
    os.makedirs("saves")
refresh_list()

root.mainloop()